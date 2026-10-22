import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "__PROJECT__-workflow.py"
SPEC = importlib.util.spec_from_file_location("project_workflow", SCRIPT)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)

TIP = "a" * 40
RED = {"number": 8, "title": f"staging vermelha: {TIP}"}
AUDIT = {"number": 9, "title": f"audit indisponível: {TIP}"}


def heavy(status="completed", conclusion="success"):
    return {"head_sha": TIP, "event": "push", "path": f".github/workflows/{workflow.HEAVY_WORKFLOW}",
            "status": status, "conclusion": conclusion, "id": 1, "html_url": "run"}


def fake_api(issues, runs):
    def api(path):
        if path == "git/ref/heads/staging":
            return {"object": {"sha": TIP}}
        if path.startswith("issues?"):
            return issues
        if path.startswith("actions/workflows/"):
            return {"workflow_runs": runs}
        raise AssertionError(path)
    return api


class StagingReadyTest(unittest.TestCase):
    def ready(self, issues=(), runs=None, promotion=False):
        original = workflow.gh_api
        workflow.gh_api = fake_api(list(issues), [heavy()] if runs is None else runs)
        try:
            return workflow.staging_ready(TIP, promotion=promotion)
        finally:
            workflow.gh_api = original

    def test_green_heavy_suite_without_issues_is_ready(self):
        self.assertTrue(self.ready()["ok"])
        self.assertTrue(self.ready(promotion=True)["ok"])

    def test_running_heavy_suite_does_not_stop_the_line(self):
        for status in ("queued", "in_progress"):
            with self.subTest(status=status):
                result = self.ready(runs=[heavy(status, None)])
                self.assertTrue(result["ok"], result)

    def test_heavy_suite_not_started_yet_does_not_stop_the_line(self):
        self.assertTrue(self.ready(runs=[])["ok"])

    def test_completed_heavy_failure_stops_the_line(self):
        for conclusion in ("failure", "cancelled", "timed_out"):
            with self.subTest(conclusion=conclusion):
                self.assertFalse(self.ready(runs=[heavy("completed", conclusion)])["ok"])

    def test_red_staging_issue_stops_the_line(self):
        self.assertFalse(self.ready([RED])["ok"])
        self.assertFalse(self.ready([RED], promotion=True)["ok"])

    def test_audit_unavailable_warns_on_staging_and_blocks_promotion(self):
        staging = self.ready([AUDIT])
        self.assertTrue(staging["ok"], staging)
        self.assertTrue(any("audit" in w for w in staging["warnings"]), staging)
        promotion = self.ready([AUDIT], promotion=True)
        self.assertFalse(promotion["ok"])
        self.assertTrue(any("audit" in error for error in promotion["errors"]), promotion)

    def test_promotion_requires_completed_green_heavy_suite(self):
        for runs in ([], [heavy("in_progress", None)], [heavy("queued", None)]):
            with self.subTest(runs=runs):
                self.assertFalse(self.ready(runs=runs, promotion=True)["ok"])

    def test_runs_from_other_workflows_or_events_are_ignored(self):
        stray = {**heavy("completed", "failure"), "event": "pull_request", "id": 2}
        self.assertTrue(self.ready(runs=[heavy(), stray])["ok"])
        self.assertFalse(self.ready(runs=[stray], promotion=True)["ok"])

    def test_cli_accepts_promotion_flag(self):
        self.assertIn("--promotion", SCRIPT.read_text())


if __name__ == "__main__":
    unittest.main()
