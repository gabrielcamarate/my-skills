import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

STANDARD = Path(__file__).resolve().parents[1] / "skills/gabriel-project-standard/references"
CLAUDE_SETTINGS = STANDARD / "templates/claude/settings.json"
CODEX_RULES = STANDARD / "global/codex/gabriel-guardrails.rules"

# An agent removes what its own task created, by exact ID or name, without asking (my-skills#33).
OWN_CLEANUP = [
    "docker stop 3f2a9c1b7d4e",
    "docker rm 3f2a9c1b7d4e",
    "docker rm xlondz-issue639-db xlondz-issue639-api",
    "docker rm xlondz-fixture-db prune-target",
    "docker network rm xlondz-issue639_default",
    "docker network rm xlondz-fixture_default",
    "git worktree remove .claude/worktrees/fix-33",
    "git branch -D fix/33-agent-own-cleanup",
]
# Never: prune, broad filters, forced removal, recursive rm, volumes.
FORBIDDEN = [
    "docker rm -f 3f2a9c1b7d4e",
    "docker rm --force 3f2a9c1b7d4e",
    "docker rm -vf 3f2a9c1b7d4e",
    "docker rm -v 3f2a9c1b7d4e",
    "docker rm --volumes 3f2a9c1b7d4e",
    "docker rm -lf 3f2a9c1b7d4e",
    "docker rm --force=true 3f2a9c1b7d4e",
    "docker network rm -f xlondz-issue639_default",
    "docker network rm --force=true xlondz-issue639_default",
    "docker system prune -af",
    "docker container prune -f",
    "docker network prune -f",
    "docker image prune -a",
    "docker builder prune -af",
    "docker buildx prune -af",
    "docker volume rm xlondz_db",
    "docker container rm -f 3f2a9c1b7d4e",
    "docker container stop 3f2a9c1b7d4e",
    "docker compose down -v",
    "xargs docker rm",
    "xargs -r docker network rm",
    "git worktree remove --force .claude/worktrees/fix-33",
    "git worktree remove -f .claude/worktrees/fix-33",
    "rm -rf .claude/worktrees/fix-33",
]
# Claude also sees the whole command line, so substitutions and flags after the ID are caught there.
CLAUDE_ONLY_FORBIDDEN = [
    "docker rm $(docker ps -aq --filter label=xlondz)",
    "docker network rm $(docker network ls -q)",
    "docker rm `docker ps -aq`",
    "docker rm 3f2a9c1b7d4e -f",
    "docker rm 3f2a9c1b7d4e -vf",
    "docker rm $IDS",
    "docker stop $(docker ps -q)",
    "docker stop `docker ps -q`",
    "git branch -D $(git branch --format=%(refname:short))",
    "git worktree remove $(git worktree list --porcelain)",
    "docker rm 3f2a9c1b7d4e --force",
    "docker network rm xlondz-issue639_default -f",
    "git worktree remove .claude/worktrees/fix-33 --force",
]


def claude_decision(settings, command):
    """Claude Code order: deny, then ask, then allow; unlisted commands ask."""
    def matches(rule):
        body = rule[len("Bash("):-1]
        if body.endswith(":*"):
            prefix = body[:-2]
            return command == prefix or command.startswith(prefix + " ")
        return re.fullmatch(".*".join(map(re.escape, body.split("*"))), command) is not None

    for decision in ("deny", "ask", "allow"):
        rules = [r for r in settings["permissions"][decision] if r.startswith("Bash(")]
        if any(matches(r) for r in rules):
            return decision
    return "ask"


class ClaudeTemplatePermissionTests(unittest.TestCase):
    settings = json.loads(CLAUDE_SETTINGS.read_text())

    def test_own_cleanup_is_allowed(self):
        for command in OWN_CLEANUP:
            self.assertEqual(claude_decision(self.settings, command), "allow", command)

    def test_broad_or_forced_removal_is_denied(self):
        for command in FORBIDDEN + CLAUDE_ONLY_FORBIDDEN:
            self.assertEqual(claude_decision(self.settings, command), "deny", command)


@unittest.skipUnless(shutil.which("codex"), "codex CLI not installed")
class CodexGuardrailTests(unittest.TestCase):
    def check(self, command):
        result = subprocess.run(["codex", "execpolicy", "check", "-r", str(CODEX_RULES), *command.split()],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout).get("decision")

    def test_own_cleanup_is_allowed(self):
        for command in OWN_CLEANUP:
            self.assertEqual(self.check(command), "allow", command)

    def test_broad_or_forced_removal_is_forbidden(self):
        for command in FORBIDDEN:
            self.assertEqual(self.check(command), "forbidden", command)


if __name__ == "__main__":
    unittest.main()
