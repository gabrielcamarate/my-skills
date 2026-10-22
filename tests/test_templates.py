import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/gabriel-project-standard/references/templates/scripts"

FAKE_PNPM = r"""#!/bin/sh
echo "$PWD pnpm $*" >> "$PNPM_LOG"
case "$1" in
  test)
    for arg; do case "$arg" in --outputFile.json=*) report=${arg#--outputFile.json=} ;; esac; done
    printf '{"testResults":[{"name":"%s/lib/a.test.ts","assertionResults":[{"ancestorTitles":["media"],"title":"manifest","duration":1234}]}]}' "$PWD" > "$report" ;;
  build) mkdir "$BUSY" || exit 9; sleep 1; rmdir "$BUSY" ;;
esac
"""


class TemplateScriptTests(unittest.TestCase):
    def run_script(self, name):
        result = subprocess.run(["bash", str(SCRIPTS / name)], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ensure_node(self):
        self.run_script("test-ensure-node.sh")

    def test_share_machine(self):
        self.run_script("test-share-machine.sh")


class FastCheckTests(unittest.TestCase):
    """Two project sessions on one machine: capped workers, one build at a time."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        pinned = re.search(r"(?m)^NODE_VERSION=(\S+)$", (SCRIPTS / "ensure-node.sh").read_text()).group(1)
        stubs = self.tmp / "stubs"
        stubs.mkdir()
        for name, body in (("node", f'#!/bin/sh\necho v{pinned}\n'), ("pnpm", FAKE_PNPM)):
            (stubs / name).write_text(body)
            (stubs / name).chmod(0o755)
        self.log = self.tmp / "pnpm.log"
        self.env = {
            "HOME": str(self.tmp / "home"), "PATH": f"{stubs}:/usr/bin:/bin",
            "NODE_PREFIX": str(self.tmp / "prefix"), "HEAVY_LOCK": str(self.tmp / "heavy.lock"),
            "PNPM_LOG": str(self.log), "BUSY": str(self.tmp / "busy"),
        }

    def project(self, name):
        root = self.tmp / name
        shutil.copytree(SCRIPTS, root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        for script in (root / "scripts").glob("*.sh"):
            script.chmod(0o755)
        for doc in ("AGENTS.md", "README.md", "ARCHITECTURE.md", "CHANGELOG.md",
                    "docs/development/workflow.md", "docs/development/skills.md"):
            (root / doc).parent.mkdir(parents=True, exist_ok=True)
            (root / doc).write_text("# doc\n")
        (root / "CLAUDE.md").write_text("@AGENTS.md\n")
        (root / ".codex/environments").mkdir(parents=True)
        (root / ".codex/environments/environment.toml").write_text('[setup]\nscript = "bash .codex/scripts/setup.sh"\n')
        return root

    def start(self, root, **extra):
        return subprocess.Popen(["bash", str(root / "scripts/fast-check.sh")], env={**self.env, **extra},
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def finish(self, proc):
        out, _ = proc.communicate(timeout=120)
        self.assertEqual(proc.returncode, 0, out)
        return out

    def test_two_projects_in_parallel(self):
        a, b = self.project("a"), self.project("b")
        outputs = [self.finish(p) for p in (self.start(a), self.start(b))]
        self.assertTrue(any("wait  another session holds" in out for out in outputs), outputs)
        for out in outputs:
            self.assertIn("PASS  fast core", out)
            self.assertIn("slowest 5 unit tests:", out)
            self.assertIn("1234 ms  lib/a.test.ts  media > manifest", out)
        tests = [line for line in self.log.read_text().splitlines() if " pnpm test " in line]
        self.assertEqual(len(tests), 2)
        self.assertTrue(all("--maxWorkers=2" in line for line in tests), tests)

    def test_ci_uses_every_core(self):
        self.finish(self.start(self.project("a"), CI="true"))
        tests = [line for line in self.log.read_text().splitlines() if " pnpm test " in line]
        self.assertEqual(len(tests), 1)
        self.assertNotIn("--maxWorkers", tests[0])


if __name__ == "__main__":
    unittest.main()
