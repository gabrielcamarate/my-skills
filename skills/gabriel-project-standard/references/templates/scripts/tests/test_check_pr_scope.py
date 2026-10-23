import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check-pr-scope.py"
LOG = "# Changelog\n\n## 0.1.4 - 2026-10-15\n\n- X.\n"
RELEASE_BODY = "Refs #20\nSecurity-Review: version bump only"
OLD_LOG = "# Changelog\n\n## Unreleased\n\n- Antiga.\n\n## 0.1.4 - 2026-10-15\n\n- X.\n"


class CheckPrScopeTest(unittest.TestCase):
    """Task PRs add exactly one changes/<N>-<slug>.md; only a version bump edits CHANGELOG.md."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.git("init", "-q", "-b", "staging")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.dir), *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def commit(self, files=None, deleted=(), message="c"):
        for name, text in (files or {}).items():
            (self.dir / name).parent.mkdir(parents=True, exist_ok=True)
            (self.dir / name).write_text(text)
        for name in deleted:
            (self.dir / name).unlink()
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def scope(self, files=None, deleted=(), branch="fix/12-audit-level", body=None, log=LOG, notes=(),
              staging_after=None):
        self.commit({"package.json": '{"version": "0.1.4"}\n', "CHANGELOG.md": log, "changes/README.md": "# Notas\n",
                     **{f"changes/{n}": "- Old.\n" for n in notes}}, message="base")
        self.git("checkout", "-qb", branch)
        head = self.commit(files, deleted, "task")
        self.git("checkout", "-q", "staging")
        if staging_after:
            self.commit(staging_after, message="parallel")
        event = self.dir / ".git" / "event.json"
        issue = branch.split("/")[1].split("-")[0]
        event.write_text(json.dumps({"pull_request": {
            "head": {"ref": branch, "sha": head}, "base": {"sha": self.git("rev-parse", "staging")},
            "body": f"Refs #{issue}" if body is None else body}}))
        return subprocess.run([sys.executable, str(SCRIPT)], cwd=self.dir, capture_output=True, text=True,
                              env={"GITHUB_EVENT_PATH": str(event), "PATH": "/usr/bin:/bin"}, timeout=30)

    def assertRefused(self, result, text=""):
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn(text, result.stderr)

    def test_task_with_its_own_note_passes(self):
        result = self.scope({"lib/a.ts": "a\n", "changes/12-audit-level.md": "- A.\n"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_editing_its_own_note_passes(self):
        result = self.scope({"changes/12-audit-level.md": "- B.\n", "changes/README.md": "# Notas 2\n"},
                            notes=["12-audit-level.md"])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_task_without_note_is_refused(self):
        self.assertRefused(self.scope({"lib/a.ts": "a\n"}), "changes/12-")

    def test_exactly_one_own_note(self):
        for files, deleted, notes in (
                ({"changes/13-other.md": "- A.\n"}, (), ()),
                ({"changes/12-a.md": "- A.\n", "changes/12-b.md": "- B.\n"}, (), ()),
                ({"changes/12-a.md": "- A.\n", "changes/7-old.md": "- C.\n"}, (), ["7-old.md"]),
                ({"changes/12-a.md": "- A.\n"}, ["changes/7-old.md"], ["7-old.md"]),
                ({"changes/12_Audit.md": "- A.\n"}, (), ())):
            with self.subTest(files=files, deleted=deleted):
                self.setUp()
                self.assertRefused(self.scope(files, deleted, notes=notes))

    def test_task_touching_changelog_is_refused(self):
        result = self.scope({"changes/12-a.md": "- A.\n", "CHANGELOG.md": LOG + "\n- Nova.\n"})
        self.assertRefused(result, "CHANGELOG.md")

    def test_release_branch_type_is_not_a_task(self):
        self.assertRefused(self.scope({"CHANGELOG.md": "x\n"}, branch="release/20-v0-2-0"))

    def test_version_bump_is_the_release_and_consumes_every_note(self):
        bump = {"package.json": '{"version": "0.1.5"}\n', "CHANGELOG.md": "# Changelog\n\n## 0.1.5 - 2026-10-22\n"}
        notes = ["7-a.md", "9-b.md"]
        ok = self.scope(bump, ["changes/7-a.md", "changes/9-b.md"], branch="chore/20-release", notes=notes,
                        body=RELEASE_BODY)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.setUp()
        self.assertRefused(self.scope(bump, ["changes/7-a.md"], branch="chore/20-release", notes=notes,
                                      body=RELEASE_BODY), "9-b")
        self.setUp()
        self.assertRefused(self.scope({**bump, "changes/20-x.md": "- X.\n"}, branch="chore/20-release",
                                      body=RELEASE_BODY))

    def test_release_must_raise_the_version(self):
        for version in ("0.1.3", "0.1.4-rc.1", "x"):
            with self.subTest(version=version):
                self.setUp()
                result = self.scope({"package.json": f'{{"version": "{version}"}}\n', "lib/a.ts": "a\n"},
                                    branch="chore/20-release", body=RELEASE_BODY)
                self.assertRefused(result, "version")
        self.setUp()
        self.assertRefused(self.scope({"lib/a.ts": "a\n"}, ["package.json"], branch="chore/20-release",
                                      body=RELEASE_BODY))

    def test_sensitive_paths_require_a_security_review_line(self):
        for path in (".github/workflows/pr.yml", "scripts/fast-check.sh", "package.json"):
            with self.subTest(path=path):
                self.setUp()
                files = {path: '{"version": "0.1.4", "scripts": {}}\n' if path == "package.json" else "x\n",
                         "changes/12-a.md": "- A.\n"}
                self.assertRefused(self.scope(files), "Security-Review:")
                self.setUp()
                for body in ("Refs #12\nSecurity-Review:", "Refs #12\nSecurity-Review:   ", "Refs #12 Security-Review: x"):
                    with self.subTest(body=body):
                        self.setUp()
                        self.assertRefused(self.scope(files, body=body), "Security-Review:")
                self.setUp()
                ok = self.scope(files, body="Refs #12\n\nSecurity-Review: no new token, gate or permission\n")
                self.assertEqual(ok.returncode, 0, ok.stderr)

    def test_agent_and_executable_paths_require_a_security_review_line(self):
        # my-skills#17: bin/ runs code; .claude/, .codex/ and root AGENTS.md/CLAUDE.md steer agents.
        # A bare "bin" is how git lists a symlink or submodule at that name.
        for path in ("bin/ci", ".claude/settings.json", ".codex/scripts/setup.sh", "AGENTS.md", "CLAUDE.md",
                     "bin", ".claude", ".codex"):
            with self.subTest(path=path):
                self.setUp()
                files = {path: "x\n", "changes/12-a.md": "- A.\n"}
                self.assertRefused(self.scope(files), "Security-Review:")
                self.setUp()
                ok = self.scope(files, body="Refs #12\nSecurity-Review: only narrows agent permissions\n")
                self.assertEqual(ok.returncode, 0, ok.stderr)

    def test_deploy_and_install_config_require_a_security_review_line(self):
        # my-skills#25: wrangler build.command, .npmrc node-options, pnpm settings and patches/ run
        # during install or deploy, next to the deploy token. Wrangler/npm config counts in any package.
        for path in ("wrangler.jsonc", "wrangler.json", "wrangler.toml", "apps/web/wrangler.jsonc", ".npmrc",
                     "packages/a/.npmrc", "pnpm-workspace.yaml", "patches/left-pad@1.3.0.patch", "patches",
                     ".pnpmfile.cjs", ".wrangler/deploy/config.json", "apps/web/.wrangler/deploy/config.json"):
            with self.subTest(path=path):
                self.setUp()
                files = {path: "x\n", "changes/12-a.md": "- A.\n"}
                self.assertRefused(self.scope(files), "Security-Review:")
                self.setUp()
                ok = self.scope(files, body="Refs #12\nSecurity-Review: no new build command or install hook\n")
                self.assertEqual(ok.returncode, 0, ok.stderr)

    def test_lockfile_and_nested_agent_docs_need_no_security_review_line(self):
        # The strict audit covers pnpm-lock.yaml; only the root AGENTS.md/CLAUDE.md count.
        for path in ("pnpm-lock.yaml", "docs/AGENTS.md", "packages/a/CLAUDE.md", "binaries/x", "lib/bin/x",
                     "docs/wrangler.md", "lib/patches/x.ts", "packages/a/pnpm-workspace.yaml.md"):
            with self.subTest(path=path):
                self.setUp()
                result = self.scope({path: "x\n", "changes/12-a.md": "- A.\n"})
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_release_bump_also_needs_the_security_review_line(self):
        bump = {"package.json": '{"version": "0.1.5"}\n', "CHANGELOG.md": "# Changelog\n\n## 0.1.5 - 2026-10-22\n"}
        self.assertRefused(self.scope(bump, branch="chore/20-release"), "Security-Review:")

    def test_parallel_note_merged_into_staging_is_not_this_prs_change(self):
        result = self.scope({"changes/12-a.md": "- A.\n"}, staging_after={"changes/600-b.md": "- B.\n"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_legacy_migration_moves_only_a_non_empty_unreleased(self):
        migration = {"CHANGELOG.md": LOG, "changes/0-unreleased-legacy.md": "- Antiga.\n", "changes/12-a.md": "- A.\n"}
        ok = self.scope(migration, log=OLD_LOG)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.setUp()
        self.assertRefused(self.scope({**migration, "CHANGELOG.md": LOG + "- Y.\n"}, log=OLD_LOG), "CHANGELOG")
        self.setUp()
        self.assertRefused(self.scope({k: v for k, v in migration.items() if k != "CHANGELOG.md"}))

    def test_legacy_migration_expires_once_staging_tip_has_migrated(self):
        migration = {"CHANGELOG.md": LOG, "changes/0-unreleased-legacy.md": "- Antiga.\n", "changes/12-a.md": "- A.\n"}
        result = self.scope(migration, log=OLD_LOG, staging_after={"CHANGELOG.md": LOG})
        self.assertRefused(result, "CHANGELOG")

    def test_refs_closing_keyword_and_env_files(self):
        self.assertRefused(self.scope({"changes/12-a.md": "- A.\n"}, body="Refs #13"))
        self.setUp()
        self.assertRefused(self.scope({"changes/12-a.md": "- A.\n"}, body="Refs #12\nCloses #12"))
        self.setUp()
        self.assertRefused(self.scope({"changes/12-a.md": "- A.\n", ".env.local": "X=1\n"}))


if __name__ == "__main__":
    unittest.main()
