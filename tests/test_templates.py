import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "skills/gabriel-project-standard/references/templates"
SCRIPTS = TEMPLATES / "scripts"
SHA = "b" * 40

# Stands in for `gh api`: answers reads from a fixture, logs every write.
FAKE_GH = r"""#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
path = args[1].split("/", 3)[3]
method = args[args.index("--method") + 1]
data = json.load(sys.stdin) if "--input" in args else None
if method != "GET":
    with open(os.environ["GH_LOG"], "a") as log:
        log.write(json.dumps({"method": method, "path": path, "data": data}) + "\n")
    print("{}")
elif path == "git/ref/heads/staging":
    print(json.dumps({"object": {"sha": os.environ["GITHUB_SHA"]}}))
elif path.startswith("issues?"):
    print(os.environ["OPEN_ISSUES"] if "page=1" in path else "[]")
elif "/jobs" in path:
    ok = os.environ["QUALITY_RESULT"] == "success"
    print(json.dumps({"jobs": [{"name": "staging-quality", "conclusion": "success" if ok else "failure",
                                "html_url": "job", "steps": []}]}))
else:
    print(json.dumps({"run_attempt": 1}))
"""

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

    def test_template_python_contracts(self):
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(SCRIPTS / "tests"),
                                 "-p", "test_*.py"], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)


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


class StagingReportTests(unittest.TestCase):
    """The staging reporter: an audit outage warns and never stops the line."""

    def report(self, quality, audit, issues=()):
        workflow = (TEMPLATES / "github/workflows/staging-quality.yml").read_text()
        script = textwrap.dedent(re.search(r"python3 - <<'PY'\n(.*?)\n *PY\n", workflow, re.S).group(1))
        with tempfile.TemporaryDirectory() as tmp:
            gh = Path(tmp, "gh")
            gh.write_text(FAKE_GH)
            gh.chmod(0o755)
            log = Path(tmp, "gh.log")
            env = {"PATH": f"{tmp}:/usr/bin:/bin", "GH_LOG": str(log), "GITHUB_REPOSITORY": "o/r",
                   "GITHUB_SHA": SHA, "GITHUB_RUN_ID": "7", "GITHUB_RUN_ATTEMPT": "1",
                   "QUALITY_RESULT": quality, "AUDIT_RESULT": audit, "OPEN_ISSUES": json.dumps(list(issues))}
            result = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def created(self, writes):
        return [w["data"]["title"] for w in writes if w["method"] == "POST" and w["path"] == "issues"]

    def test_audit_outage_warns_without_red_staging(self):
        writes = self.report("success", "unavailable")
        self.assertEqual(self.created(writes), [f"audit indisponível: {SHA}"])
        self.assertEqual(writes[0]["data"]["labels"], ["audit-indisponivel"])

    def test_passing_audit_closes_the_warning(self):
        writes = self.report("success", "ok", [{"number": 5, "title": "audit indisponível: old"}])
        self.assertIn({"method": "PATCH", "path": "issues/5", "data": {"state": "closed"}}, writes)
        self.assertEqual(self.created(writes), [])

    def test_failed_suite_is_still_red(self):
        self.assertEqual(self.created(self.report("failure", "vulnerable")), [f"staging vermelha: {SHA}"])


def permission(rules, command):
    """Claude Code precedence: deny beats ask beats allow; `:*` is a prefix, `*` any text."""
    def matches(rule):
        pattern = rule[len("Bash("):-1]
        if pattern.endswith(":*"):
            return command.startswith(pattern[:-2])
        return re.fullmatch(".*".join(map(re.escape, pattern.split("*"))), command) is not None
    for decision in ("deny", "ask", "allow"):
        if any(matches(rule) for rule in rules[decision] if rule.startswith("Bash(")):
            return decision
    return "ask"


class SettingsTemplateTests(unittest.TestCase):
    """A broad `ask` silently overrides the task-branch push allows."""

    rules = json.loads((TEMPLATES / "claude/settings.json").read_text())["permissions"]

    def test_no_broad_push_ask(self):
        self.assertNotIn("Bash(git push:*)", self.rules["ask"])

    def test_task_branch_push_needs_no_prompt(self):
        for command in ("git push -u origin fix/13-gate", "git push origin feature/7-x", "git push origin docs/2-a"):
            with self.subTest(command=command):
                self.assertEqual(permission(self.rules, command), "allow")

    def test_unusual_push_asks(self):
        for command in ("git push origin fix/13-a fix/14-b", "git -C ../other fix push origin x"):
            with self.subTest(command=command):
                self.assertEqual(permission(self.rules, command), "ask")

    def test_push_to_protected_branches_is_denied(self):
        for command in ("git push origin main", "git push origin staging", "git push -u origin main",
                        "git push origin HEAD:main", "git push origin fix/1-a:staging", "git push --force origin x"):
            with self.subTest(command=command):
                self.assertEqual(permission(self.rules, command), "deny")


class PromotionTemplateTests(unittest.TestCase):
    """Promotion reuses the heavy staging evidence instead of rerunning the suite."""

    pr = (TEMPLATES / "github/workflows/pr.yml").read_text()

    def test_promotion_checks_exact_green_staging_and_strict_audit(self):
        self.assertIn('staging-ready --expected-sha "$STAGING_SHA" --promotion', self.pr)
        audit = re.search(r"- name: Dependency audit \(strict\)\n(.*?)\n\n", self.pr, re.S).group(1)
        self.assertIn("github.base_ref == 'main'", audit)
        self.assertNotIn("--soft-unavailable", audit)

    def test_pr_to_main_does_not_run_the_full_suite(self):
        for step in ("pnpm test:coverage", "pnpm build", "pnpm e2e", "playwright install", "FULL_CI"):
            with self.subTest(step=step):
                self.assertNotIn(step, self.pr)

    def test_promotion_source_is_own_staging(self):
        self.assertIn('[[ $HEAD_REF == staging && $HEAD_REPO == "$GITHUB_REPOSITORY" ]]', self.pr)


if __name__ == "__main__":
    unittest.main()
