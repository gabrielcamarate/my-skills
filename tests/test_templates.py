import importlib.util
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
[ "$1" = --version ] && echo "$PNPM_VERSION" && exit 0
echo "$PWD pnpm $* node=$(node --version)" >> "$PNPM_LOG"
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

    def test_cloud_setup(self):
        self.run_script("test-cloud-setup.sh")

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
        self.pinned = pinned = re.search(r"(?m)^NODE_VERSION=(\S+)$", (SCRIPTS / "ensure-node.sh").read_text()).group(1)
        self.pnpm = re.search(r"(?m)^PNPM_VERSION=(\S+)$", (SCRIPTS / "ensure-pnpm.sh").read_text()).group(1)
        stubs = self.tmp / "stubs"
        stubs.mkdir()
        for name, body in (("node", f'#!/bin/sh\necho v{pinned}\n'), ("pnpm", FAKE_PNPM)):
            (stubs / name).write_text(body)
            (stubs / name).chmod(0o755)
        self.log = self.tmp / "pnpm.log"
        self.env = {
            "HOME": str(self.tmp / "home"), "PATH": f"{stubs}:/usr/bin:/bin",
            "NODE_PREFIX": str(self.tmp / "prefix"), "HEAVY_LOCK": str(self.tmp / "heavy.lock"),
            "PNPM_LOG": str(self.log), "BUSY": str(self.tmp / "busy"), "PNPM_VERSION": self.pnpm,
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

    def test_pinned_node_and_pnpm_win_over_shared_bin(self):
        """Another project's node and pnpm in ~/.local/bin, first on PATH (#12)."""
        home = self.tmp / "home"
        shared = home / ".local/bin"
        shared.mkdir(parents=True)
        (shared / "node").write_text("#!/bin/sh\necho v22.22.0\n")
        (shared / "pnpm").write_text("#!/bin/sh\n[ \"$1\" = --version ] && echo 9.0.0 && exit 0\nexit 1\n")
        node_bin = home / f".local/lib/pinned-node/node-v{self.pinned}-linux-x64/bin"
        pnpm_bin = home / f".local/lib/pinned-pnpm/{self.pnpm}/bin"
        for path, body in ((shared / "node", None), (shared / "pnpm", None),
                           (node_bin / "node", f"#!/bin/sh\necho v{self.pinned}\n"), (pnpm_bin / "pnpm", FAKE_PNPM)):
            if body:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            path.chmod(0o755)
        before = {p.name: p.read_bytes() for p in shared.iterdir()}
        del self.env["NODE_PREFIX"]  # the default prefix, ~/.local
        out = self.finish(self.start(self.project("a"), PATH=f"{shared}:/usr/bin:/bin", NODE_DIST_PLATFORM="linux-x64"))
        self.assertIn("PASS  fast core", out)
        calls = self.log.read_text().splitlines()
        self.assertTrue(calls and all(line.endswith(f"node=v{self.pinned}") for line in calls), calls)
        self.assertEqual({p.name: p.read_bytes() for p in shared.iterdir()}, before)

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

    def test_no_claude_attribution(self):
        settings = json.loads((TEMPLATES / "claude/settings.json").read_text())
        self.assertEqual(settings["attribution"]["commit"], "")
        self.assertEqual(settings["attribution"]["pr"], "")

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

    def test_merge_commit_forms_ask(self):
        for command in ("gh pr merge 12 --merge", "gh pr merge 12 -m", "gh pr merge 12 -dm", "gh pr merge 12 -md",
                        "gh pr merge -dm 12", "gh pr merge 12 --merge --match-head-commit abc"):
            with self.subTest(command=command):
                self.assertEqual(permission(self.rules, command), "ask")

    def test_squash_merges_need_no_prompt(self):
        for command in ("gh pr merge 12 --squash", "gh pr merge 12 --squash --match-head-commit abc",
                        "gh pr merge 12 --squash --delete-branch", "gh pr merge 12 --squash -d"):
            with self.subTest(command=command):
                self.assertEqual(permission(self.rules, command), "allow")

    def test_push_to_protected_branches_is_denied(self):
        for command in ("git push origin main", "git push origin staging", "git push -u origin main",
                        "git push origin HEAD:main", "git push origin fix/1-a:staging", "git push --force origin x",
                        "git push origin feature/1-x:refs/heads/main", "git push -u origin fix/1-x:refs/heads/staging",
                        "git push origin feature/1-x:heads/main", "git push origin HEAD:refs/heads/main",
                        "git push origin feature/1-x --force", "git push origin feature/1-x --force-with-lease",
                        "git push origin feature/1-x -f", "git push origin feature/1-x --delete"):
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


class MainGuardTemplateTests(unittest.TestCase):
    """my-skills#17: main only takes the promotion merge; deploy checks its tree, never reruns."""

    rulesets = (TEMPLATES.parent / "rulesets.md").read_text()
    deploy = (TEMPLATES / "github/workflows/deploy.yml").read_text() \
        if (TEMPLATES / "github/workflows/deploy.yml").exists() else ""

    def test_main_merge_commit_only_ruleset_recipe(self):
        recipe = re.search(r"```bash\n(R=[^`]*?Promoção: main só merge commit[^`]*)```", self.rulesets)
        self.assertIsNotNone(recipe, "missing ruleset recipe")
        body = re.search(r"<<J\n(.*?)\nJ\n", recipe.group(1), re.S).group(1).replace("$R", "o/r")
        ruleset = json.loads(body)
        self.assertEqual(ruleset["conditions"]["ref_name"]["include"], ["refs/heads/main"])
        self.assertEqual(ruleset["enforcement"], "active")
        [rule] = ruleset["rules"]
        self.assertEqual(rule["type"], "pull_request")
        self.assertEqual(rule["parameters"]["allowed_merge_methods"], ["merge"])
        self.assertIn("gh api -X POST repos/$R/rulesets", recipe.group(1))
        # The reason: squash into main skipped the merge-commit ask and could ship untested content.
        self.assertIn("ask", self.rulesets)
        self.assertIn("não testado", self.rulesets)

    def test_deploy_checks_main_tree_before_install(self):
        self.assertIn("main-ready --sha \"$GITHUB_SHA\"", self.deploy)
        step = self.deploy.split("- name: Require approved staging tree", 1)[1].split("\n      - ", 1)[0]
        self.assertIn("python3 scripts/__PROJECT__-workflow.py main-ready --sha \"$GITHUB_SHA\"", step)
        self.assertIn("GH_TOKEN: ${{ github.token }}", step)
        order = [self.deploy.index(name) for name in (
            "- name: Checkout exact main commit", "- name: Require approved staging tree",
            "- name: Install dependencies", "- name: Deploy")]
        self.assertEqual(order, sorted(order))
        self.assertIn("ref: ${{ github.sha }}", self.deploy)
        self.assertIn("persist-credentials: false", self.deploy)
        self.assertIn("actions: read", self.deploy)
        self.assertNotIn(": write", self.deploy)

    def test_deploy_never_reruns_the_suite(self):
        for step in ("pnpm test", "pnpm e2e", "pnpm lint", "pnpm typecheck", "playwright"):
            with self.subTest(step=step):
                self.assertNotIn(step, self.deploy)

    def test_pr_template_no_longer_promises_a_full_suite_on_main(self):
        pr = (TEMPLATES / "github/workflows/pr.yml").read_text()
        self.assertNotIn("runs the full suite only if they diverge", pr)
        self.assertIn("main-ready", pr)


class NoStagingPathTests(unittest.TestCase):
    """my-skills#17: projects without staging skip staging and promotion (QRcode-menu#34)."""

    skill = (TEMPLATES.parents[1] / "SKILL.md").read_text()

    def test_no_staging_path_is_documented(self):
        section = re.search(r"\*\*Sem staging\*\*(.*?)\n\n", self.skill, re.S)
        self.assertIsNotNone(section, "missing no-staging path")
        text = section.group(1)
        for phrase in ("Padrão: staging", "promoção", "main-ready", "local", "export", "QRcode-menu#34"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_skill_states_the_main_guard_and_merge_commit_ruleset(self):
        self.assertIn("main-ready --sha", self.skill)
        self.assertIn("Promoção: main só merge commit", self.skill)
        self.assertNotIn("se divergir, roda a suíte completa", self.skill)


def gh_expr(text, context):
    """Tiny GitHub Actions expression evaluator: paths, literals, !, ==, !=, &&, ||, ()."""
    tokens = re.findall(r"'(?:[^']|'')*'|&&|\|\||==|!=|!|\(|\)|[A-Za-z_][\w.-]*", text)
    assert "".join(tokens) == re.sub(r"\s+", "", text), text
    pos = 0

    def take():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def atom():
        token = take()
        if token == "!":
            return not atom()
        if token == "(":
            value = either()
            assert take() == ")"
            return value
        if token.startswith("'"):
            return token[1:-1].replace("''", "'")
        if token in ("true", "false", "null"):
            return {"true": True, "false": False, "null": None}[token]
        value = context
        for key in token.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        return value

    def compare():
        left = atom()
        while peek() in ("==", "!="):
            op, right = take(), atom()
            same = (left.lower() == right.lower() if isinstance(left, str) and isinstance(right, str)
                    else left == right)
            left = same if op == "==" else not same
        return left

    def both():
        left = compare()
        while peek() == "&&":
            take()
            right = compare()
            left = left and right
        return left

    def either():
        left = both()
        while peek() == "||":
            take()
            right = both()
            left = left or right
        return left

    value = either()
    assert peek() is None, text
    return value


class PrEditedEventTests(unittest.TestCase):
    """my-skills#16: only a base change cancels; a text edit reuses the head's green run."""

    pr = (TEMPLATES / "github/workflows/pr.yml").read_text()
    fixtures = SCRIPTS / "tests/fixtures/pr-event"
    spec = importlib.util.spec_from_file_location("project_workflow", SCRIPTS / "__PROJECT__-workflow.py")
    workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow)

    def context(self, name):
        event = json.loads((self.fixtures / f"{name}.json").read_text())
        return {"github": {"event_name": "pull_request", "event": event, "ref": "refs/pull/31/merge",
                           "base_ref": event["pull_request"]["base"]["ref"]}}

    def value(self, key, context):
        raw = re.search(rf"^concurrency:\n(?:  .*\n)*?  {key}: (.*)$", self.pr, re.M).group(1)
        return re.sub(r"\$\{\{(.*?)\}\}", lambda m: str(gh_expr(m.group(1), context)), raw) \
            if key == "group" else gh_expr(re.fullmatch(r"\$\{\{(.*)\}\}", raw).group(1), context)

    def steps_run(self, name):
        """Steps of the required job that run, with a green earlier run of the same head and base."""
        context = self.context(name)
        pr = context["github"]["event"]["pull_request"]
        green = {"id": 1, "head_sha": pr["head"]["sha"], "status": "completed", "conclusion": "success",
                 "display_title": self.workflow.pr_run_title(pr), "path": ".github/workflows/pr.yml",
                 "head_repository": pr["head"]["repo"]}
        original = self.workflow.gh_api
        self.workflow.gh_api = lambda path: {"workflow_runs": [green]}
        try:
            outputs = self.workflow.pr_event(context["github"]["event"], 2)
        finally:
            self.workflow.gh_api = original
        context["steps"] = {"event": {"outputs": {"reuse": str(outputs["reuse"]).lower()}}}
        ran = []
        for block in re.split(r"\n(?=      - name: )", self.pr.split("\n    steps:\n", 1)[1]):
            step = re.match(r"      - name: (.*)", block).group(1)
            cond = re.search(r"^        if: (.*)$", block, re.M)
            if cond is None or gh_expr(cond.group(1), context):
                ran.append(step)
        return ran

    def test_run_name_matches_pr_event_lookup(self):
        self.assertIn('run-name: "PR ${{ github.event.pull_request.number }} into ${{ github.base_ref }}"', self.pr)
        pr = self.context("opened")["github"]["event"]["pull_request"]
        self.assertEqual(self.workflow.pr_run_title(pr), "PR 31 into staging")

    def test_all_events_share_the_pr_group(self):
        groups = {self.value("group", self.context(name)) for name in
                  ("opened", "synchronize", "edited-body", "edited-title", "edited-base", "edited-security-review")}
        self.assertEqual(groups, {"pr-quality-31"})

    def test_description_edit_does_not_cancel(self):
        for name in ("edited-body", "edited-title", "edited-security-review"):
            with self.subTest(event=name):
                self.assertIs(self.value("cancel-in-progress", self.context(name)), False)

    def test_new_head_and_base_change_cancel(self):
        for name in ("opened", "synchronize", "edited-base"):
            with self.subTest(event=name):
                self.assertIs(self.value("cancel-in-progress", self.context(name)), True)

    def test_base_change_reevaluates_the_promotion_gate(self):
        ran = self.steps_run("edited-base")
        for step in ("Require green staging tip for promotion", "Dependency audit (strict)",
                     "Install dependencies", "Scan committed secrets"):
            self.assertIn(step, ran)

    def test_description_edit_reuses_the_suite(self):
        ran = self.steps_run("edited-body")
        self.assertIn("Classify PR event", ran)
        self.assertIn("Verify task scope", ran)
        for step in ("Install dependencies", "Scan committed secrets", "Run release gate",
                     "Verify local workflow and domain skills"):
            self.assertNotIn(step, ran)

    def test_security_review_edit_reevaluates_scope_only(self):
        # Also a title edit: a quick body edit before it may have been replaced while pending.
        for name in ("edited-security-review", "edited-title"):
            with self.subTest(event=name):
                ran = self.steps_run(name)
                self.assertIn("Verify task scope", ran)
                self.assertNotIn("Run release gate", ran)
                self.assertNotIn("Install dependencies", ran)

    def test_synchronize_runs_the_whole_cheap_check(self):
        ran = self.steps_run("synchronize")
        for step in ("Verify task scope", "Install dependencies", "Run release gate"):
            self.assertIn(step, ran)

    def test_required_job_has_no_if(self):
        job = self.pr.split("\n  release-quality:\n", 1)[1].split("\n    steps:\n", 1)[0]
        self.assertNotRegex(job, r"(?m)^    if:")


if __name__ == "__main__":
    unittest.main()
