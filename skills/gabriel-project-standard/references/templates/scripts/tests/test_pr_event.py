import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "__PROJECT__-workflow.py"
SPEC = importlib.util.spec_from_file_location("project_workflow", SCRIPT)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)

FIXTURES = Path(__file__).resolve().parent / "fixtures/pr-event"
HEAD = "c" * 40
RUN_ID = 500


def event(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


def run(id_, conclusion="success", base="staging", head=HEAD, status="completed"):
    return {"id": id_, "head_sha": head, "display_title": f"PR 31 into {base}", "status": status,
            "conclusion": conclusion, "path": f".github/workflows/{workflow.PR_WORKFLOW}", "html_url": f"run/{id_}"}


class PrEventTest(unittest.TestCase):
    """Text-only edits reuse the head's green run; a base change re-evaluates everything (#16)."""

    def classify(self, name, runs=()):
        calls = []

        def api(path):
            calls.append(path)
            assert path.startswith(f"actions/workflows/{workflow.PR_WORKFLOW}/runs?"), path
            assert f"head_sha={HEAD}" in path and "event=pull_request" in path, path
            return {"workflow_runs": list(runs)}
        original = workflow.gh_api
        workflow.gh_api = api
        try:
            return workflow.pr_event(event(name), RUN_ID), calls
        finally:
            workflow.gh_api = original

    def test_new_head_and_base_change_rerun_everything(self):
        for name in ("opened", "synchronize", "edited-base"):
            with self.subTest(event=name):
                result, calls = self.classify(name, [run(400)])
                self.assertEqual((result["reuse"], result["scope"]), (False, True))
                self.assertEqual(calls, [], "never reuse across a new head or base")

    def test_description_edit_reuses_green_run_and_rechecks_scope(self):
        result, _ = self.classify("edited-body", [run(400)])
        self.assertEqual((result["reuse"], result["scope"]), (True, True))
        self.assertEqual(result["run"], "run/400")

    def test_security_review_edit_rechecks_scope_without_the_suite(self):
        result, _ = self.classify("edited-security-review", [run(400)])
        self.assertEqual((result["reuse"], result["scope"]), (True, True))

    def test_title_edit_reuses_without_scope(self):
        result, _ = self.classify("edited-title", [run(400)])
        self.assertEqual((result["reuse"], result["scope"]), (True, False))

    def test_text_edit_without_green_proof_reruns_cheap_check(self):
        cases = {
            "no run": [],
            "latest red": [run(300), run(400, "failure")],
            "only cancelled": [run(400, "cancelled")],
            "other base": [run(400, base="main")],
            "other head": [run(400, head="a" * 40)],
            "own run": [run(RUN_ID)],
            "still running": [run(400, None, status="in_progress")],
        }
        for case, runs in cases.items():
            with self.subTest(case=case):
                result, _ = self.classify("edited-body", runs)
                self.assertFalse(result["reuse"], result)

    def test_cancelled_run_does_not_hide_the_earlier_verdict(self):
        result, _ = self.classify("edited-body", [run(300), run(400, "cancelled")])
        self.assertTrue(result["reuse"])

    def test_api_failure_reruns_cheap_check_and_never_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            fake = Path(tmp) / "gh"
            fake.write_text("#!/bin/sh\nexit 1\n")
            fake.chmod(0o755)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}", "GITHUB_OUTPUT": str(out),
                   "GITHUB_EVENT_PATH": str(FIXTURES / "edited-body.json"), "GITHUB_RUN_ID": str(RUN_ID)}
            result = subprocess.run([sys.executable, str(SCRIPT), "pr-event"], env=env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(out.read_text(), "reuse=false\nscope=true\n")


if __name__ == "__main__":
    unittest.main()
