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


def run(id_, conclusion="success", base="staging", head=HEAD, status="completed", number=31, repo="acme/app",
        started=None):
    return {"id": id_, "head_sha": head, "display_title": f"PR {number} into {base}", "status": status,
            "conclusion": conclusion, "path": f".github/workflows/{workflow.PR_WORKFLOW}", "html_url": f"run/{id_}",
            "head_repository": {"full_name": repo},
            "run_started_at": started or f"2026-10-23T{id_ // 60 % 24:02d}:{id_ % 60:02d}:00Z"}


class PrEventTest(unittest.TestCase):
    """Text-only edits reuse the head's newest run only if green; a base change reruns everything (#16)."""

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
                self.assertFalse(result["reuse"])
                self.assertEqual(calls, [], "never reuse across a new head or base")

    def test_text_edit_reuses_the_newest_green_run(self):
        for name in ("edited-body", "edited-title", "edited-security-review"):
            with self.subTest(event=name):
                result, _ = self.classify(name, [run(300, "failure"), run(400)])
                self.assertTrue(result["reuse"])
                self.assertEqual(result["run"], "run/400")

    def test_runs_of_other_prs_and_repos_are_ignored(self):
        result, _ = self.classify("edited-body", [run(400), run(450, "failure", number=32),
                                                  run(460, "failure", repo="fork/app")])
        self.assertTrue(result["reuse"])

    def test_text_edit_without_green_proof_reruns_cheap_check(self):
        cases = {
            "no run": [],
            "latest red": [run(300), run(400, "failure")],
            "only cancelled": [run(400, "cancelled")],
            # A pending body edit replaced by a later edit, or a cancelled newer run, never
            # lets an older green verdict through.
            "newest cancelled": [run(300), run(400, "cancelled")],
            "other base": [run(400, base="main")],
            "newest on other base": [run(300), run(400, base="main")],
            "other pr": [run(400, number=32)],
            "fork repo": [run(400, repo="fork/app")],
            "other head": [run(400, head="a" * 40)],
            "own run": [run(RUN_ID)],
            "still running": [run(400, None, status="in_progress")],
            # A re-run keeps its id but restarts: its latest attempt is the newest verdict (#27).
            "older run re-run red": [run(300, "failure", started="2026-10-23T23:00:00Z"), run(400)],
            "older run re-running": [run(300, None, status="in_progress", started="2026-10-23T23:00:00Z"),
                                     run(400)],
            "unknown start": [{**run(400), "run_started_at": None}],
        }
        for case, runs in cases.items():
            with self.subTest(case=case):
                result, _ = self.classify("edited-body", runs)
                self.assertFalse(result["reuse"], result)

    def test_deleted_head_fork_reruns_cheap_check(self):
        original = workflow.gh_api
        workflow.gh_api = lambda path: {"workflow_runs": [{**run(400), "head_repository": None}]}
        try:
            fork = event("edited-body")
            fork["pull_request"]["head"]["repo"] = None
            self.assertFalse(workflow.pr_event(fork, RUN_ID)["reuse"])
        finally:
            workflow.gh_api = original

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
            self.assertEqual(out.read_text(), "reuse=false\n")


if __name__ == "__main__":
    unittest.main()
