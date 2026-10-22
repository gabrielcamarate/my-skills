import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check-pr-scope.py"


class CheckPrScopeTest(unittest.TestCase):
    """Task PRs carry a changes/<N>-*.md note; only the release PR touches CHANGELOG.md."""

    def scope(self, files, branch="fix/12-audit-level", body="Refs #12", deleted=()):
        with tempfile.TemporaryDirectory() as tmp:
            git = lambda *args: subprocess.run(["git", "-C", tmp, *args], check=True, capture_output=True,
                                               text=True).stdout.strip()
            git("init", "-q", "-b", "staging")
            git("config", "user.email", "t@example.com")
            git("config", "user.name", "t")
            Path(tmp, "CHANGELOG.md").write_text("# Changelog\n")
            Path(tmp, "changes").mkdir()
            Path(tmp, "changes/7-old.md").write_text("### Fixed\n\n- Old.\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            for name in files:
                Path(tmp, name).parent.mkdir(parents=True, exist_ok=True)
                Path(tmp, name).write_text("change\n")
            for name in deleted:
                Path(tmp, name).unlink()
            git("add", "-A")
            git("commit", "-qm", "task")
            event = Path(tmp, "event.json")
            event.write_text(json.dumps({"pull_request": {
                "head": {"ref": branch, "sha": git("rev-parse", "HEAD")},
                "base": {"sha": base}, "body": body}}))
            return subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp, capture_output=True, text=True,
                                  env={"GITHUB_EVENT_PATH": str(event), "PATH": "/usr/bin:/bin"}, timeout=30)

    def test_task_with_its_change_note_passes(self):
        result = self.scope(["lib/a.ts", "changes/12-audit-level.md"])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_task_without_change_note_fails(self):
        result = self.scope(["lib/a.ts"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changes/12-", result.stderr)

    def test_note_for_another_issue_does_not_count(self):
        self.assertNotEqual(self.scope(["lib/a.ts", "changes/13-other.md"]).returncode, 0)

    def test_task_touching_changelog_fails(self):
        result = self.scope(["lib/a.ts", "changes/12-audit-level.md", "CHANGELOG.md"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CHANGELOG.md", result.stderr)

    def test_deleting_the_note_does_not_count(self):
        result = self.scope(["lib/a.ts"], branch="fix/7-old", body="Refs #7", deleted=["changes/7-old.md"])
        self.assertNotEqual(result.returncode, 0)

    def test_release_pr_updates_changelog_and_consumes_notes(self):
        result = self.scope(["CHANGELOG.md", "package.json"], branch="release/20-v0-2-0", body="Refs #20",
                            deleted=["changes/7-old.md"])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_release_pr_requires_changelog(self):
        result = self.scope(["package.json"], branch="release/20-v0-2-0", body="Refs #20")
        self.assertNotEqual(result.returncode, 0)

    def test_closing_keyword_fails(self):
        self.assertNotEqual(self.scope(["changes/12-a.md"], body="Refs #12\nCloses #12").returncode, 0)


if __name__ == "__main__":
    unittest.main()
