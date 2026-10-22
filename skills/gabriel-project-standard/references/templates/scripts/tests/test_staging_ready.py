import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "__PROJECT__-workflow.py"
SPEC = importlib.util.spec_from_file_location("project_workflow", SCRIPT)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)

TIP = "a" * 40


def fake_api(issues):
    run = {"head_sha": TIP, "event": "push", "path": f".github/workflows/{workflow.HEAVY_WORKFLOW}",
           "status": "completed", "conclusion": "success", "id": 1, "html_url": "run"}

    def api(path):
        if path == "git/ref/heads/staging":
            return {"object": {"sha": TIP}}
        if path.startswith("issues?"):
            return issues
        if path.startswith("actions/workflows/"):
            return {"workflow_runs": [run]}
        raise AssertionError(path)
    return api


class StagingReadyTest(unittest.TestCase):
    def ready(self, issues):
        original = workflow.gh_api
        workflow.gh_api = fake_api(issues)
        try:
            return workflow.staging_ready(TIP)
        finally:
            workflow.gh_api = original

    def test_green_heavy_suite_without_issues_is_ready(self):
        self.assertTrue(self.ready([])["ok"])

    def test_audit_unavailable_blocks_promotion(self):
        result = self.ready([{"number": 9, "title": f"audit indisponível: {TIP}"}])
        self.assertFalse(result["ok"])
        self.assertTrue(any("audit" in error for error in result["errors"]), result)

    def test_red_staging_blocks_promotion(self):
        self.assertFalse(self.ready([{"number": 8, "title": f"staging vermelha: {TIP}"}])["ok"])


if __name__ == "__main__":
    unittest.main()
