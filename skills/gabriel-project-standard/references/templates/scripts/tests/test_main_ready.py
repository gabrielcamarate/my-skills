from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "__PROJECT__-workflow.py"
SPEC = importlib.util.spec_from_file_location("project_workflow_main", SCRIPT)
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)
REAL_RUN = subprocess.run

MAIN = "d" * 40
PREVIOUS_MAIN = "c" * 40
STAGING = "e" * 40
TIP = "f" * 40
RUNS = f"actions/workflows/{workflow.HEAVY_WORKFLOW}/runs?event=push&head_sha={STAGING}&per_page=100"


def main_api(*, parents=(PREVIOUS_MAIN, STAGING), tree="t1", staging_tree="t1", compare="identical",
             status="completed", conclusion="success", run_sha=STAGING, event="push", branch="staging"):
    responses = {
        f"git/commits/{MAIN}": {"tree": {"sha": tree}, "parents": [{"sha": p} for p in parents]},
        f"git/commits/{STAGING}": {"tree": {"sha": staging_tree}},
        "git/ref/heads/staging": {"object": {"sha": TIP}},
        f"compare/{STAGING}...{TIP}": {"status": compare},
        RUNS: {"workflow_runs": [{"id": 7, "head_sha": run_sha, "event": event, "head_branch": branch,
                                  "path": f".github/workflows/{workflow.HEAVY_WORKFLOW}",
                                  "status": status, "conclusion": conclusion, "html_url": "run"}]},
    }
    return lambda path: responses[path]


class MainReadyTest(unittest.TestCase):
    """Deploy gate on main (my-skills#17, Maison #431): main is exactly the promoted green staging tip."""

    def ready(self, sha=MAIN, **changes):
        with patch.object(workflow, "gh_api", side_effect=main_api(**changes)):
            return workflow.main_ready(sha)

    def test_promotion_merge_with_identical_tree_passes(self):
        result = self.ready()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["staging_sha"], STAGING)
        # staging moved on after the promotion and still contains the promoted tip.
        self.assertTrue(self.ready(compare="ahead")["ok"])

    def test_direct_commit_or_octopus_blocks(self):
        for parents in ((PREVIOUS_MAIN,), (PREVIOUS_MAIN, STAGING, "f" * 40)):
            with self.subTest(parents=parents):
                result = self.ready(parents=parents)
                self.assertFalse(result["ok"])
                self.assertIn("not a staging promotion merge", " ".join(result["errors"]))

    def test_diverging_tree_blocks(self):
        result = self.ready(staging_tree="other")
        self.assertFalse(result["ok"])
        self.assertIn("tree diverges", " ".join(result["errors"]))

    def test_tip_outside_staging_blocks(self):
        for compare in ("diverged", "behind"):
            with self.subTest(compare=compare):
                result = self.ready(compare=compare)
                self.assertFalse(result["ok"])
                self.assertIn("not on staging", " ".join(result["errors"]))

    def test_heavy_suite_not_green_blocks(self):
        for changes in ({"status": "in_progress", "conclusion": None}, {"status": "queued", "conclusion": None},
                        {"conclusion": "failure"}, {"conclusion": "cancelled"}, {"run_sha": "0" * 40},
                        {"event": "pull_request"}, {"branch": "feature/1-x"}):
            with self.subTest(changes=changes):
                result = self.ready(**changes)
                self.assertFalse(result["ok"])
                self.assertIn("heavy staging suite", " ".join(result["errors"]))

    def test_invalid_sha_blocks_before_any_api_call(self):
        for bad in ("", None, "main", "HEAD", "a" * 39, "A" * 40, "x/../../" + "a" * 32):
            with self.subTest(sha=bad), patch.object(workflow, "gh_api", side_effect=AssertionError("API")):
                self.assertFalse(workflow.main_ready(bad)["ok"])

    def test_cli_requires_sha(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "main-ready"], capture_output=True, text=True,
                                timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("main-ready requires --sha", result.stderr)

    def test_cli_blocks_with_exit_one(self):
        out = io.StringIO()
        with patch.object(sys, "argv", ["w", "main-ready", "--sha", MAIN]), redirect_stdout(out), \
                patch.object(workflow, "gh_api", side_effect=main_api(staging_tree="other")):
            self.assertEqual(workflow.main(), 1)
        self.assertFalse(json.loads(out.getvalue())["ok"])


class RepositoryTest(unittest.TestCase):
    """GitHub checks follow GITHUB_REPOSITORY in Actions, else origin (Maison #443)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        root = patch.object(workflow, "ROOT", self.root, create=True)
        root.start()
        self.addCleanup(root.stop)
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        for key in ("GITHUB_ACTIONS", "GITHUB_REPOSITORY"):
            os.environ.pop(key, None)
        self.paths = []

    def origin(self, url):
        subprocess.run(["git", "-C", str(self.root), "remote", "remove", "origin"], capture_output=True)
        if url:
            subprocess.run(["git", "-C", str(self.root), "remote", "add", "origin", url], check=True)

    def run_gh(self, *args, **kwargs):
        """Real git, fake gh: record the API path and fail the rest of the check."""
        argv = args[0]
        if argv[0] != "gh":
            return REAL_RUN(*args, **kwargs)
        self.paths.append(argv[2])
        raise subprocess.CalledProcessError(1, argv)

    def test_main_ready_queries_the_origin_repository(self):
        self.origin("https://github.com/acme/shop.git")
        with patch.object(workflow.subprocess, "run", side_effect=self.run_gh):
            with self.assertRaises(subprocess.CalledProcessError):
                workflow.main_ready(MAIN)
        self.assertEqual(self.paths, [f"repos/acme/shop/git/commits/{MAIN}"])

    def test_accepts_common_github_remote_forms(self):
        for url in ("https://github.com/acme/shop", "https://x-access-token:SECRET@github.com/acme/shop.git",
                    "git@github.com:acme/shop.git", "ssh://git@github.com/acme/shop.git"):
            with self.subTest(url=url):
                self.origin(url)
                self.assertEqual(workflow.repository(), "acme/shop")

    def test_unresolvable_origin_fails_closed_before_github(self):
        for url in (None, "https://gitlab.com/acme/shop.git", "https://github.com/acme",
                    "/srv/mirror/shop.git", "https://github.com/acme/shop/extra", "https://github.com/acme/..git"):
            with self.subTest(url=url):
                self.origin(url)
                with patch.object(workflow.subprocess, "run", side_effect=self.run_gh):
                    with self.assertRaises(ValueError):
                        workflow.main_ready(MAIN)
                self.assertEqual(self.paths, [])

    def test_cli_never_echoes_the_remote(self):
        self.origin("https://user:SECRET@gitlab.com/x/y.git")
        out = io.StringIO()
        with patch.object(sys, "argv", ["w", "main-ready", "--sha", MAIN]), redirect_stdout(out), \
                patch.object(workflow.subprocess, "run", side_effect=self.run_gh):
            self.assertEqual(workflow.main(), 1)
        self.assertNotIn("SECRET", out.getvalue())
        self.assertEqual(self.paths, [])

    def test_actions_uses_github_repository_and_fails_closed_when_invalid(self):
        self.origin("https://github.com/someone/fork.git")
        os.environ.update(GITHUB_ACTIONS="true", GITHUB_REPOSITORY="acme/shop")
        self.assertEqual(workflow.repository(), "acme/shop")
        for value in ("", "shop", "a/b/c", "../x", "acme/.."):
            with self.subTest(value=value):
                os.environ["GITHUB_REPOSITORY"] = value
                with self.assertRaises(ValueError):
                    workflow.repository()


if __name__ == "__main__":
    unittest.main()
