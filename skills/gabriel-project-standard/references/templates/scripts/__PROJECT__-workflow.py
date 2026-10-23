#!/usr/bin/env python3
"""Bounded local workflow checks. Never switches branches or loads credentials."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib

LOCAL_SKILLS = ()  # skills de domínio do projeto, se houver
SHARED_SKILLS = (
    "gabriel-iss-audit", "gabriel-github-resolution", "gabriel-pr-audit",
    "gabriel-pr-bump", "gabriel-release",
)
DOCS = (
    "AGENTS.md", "CLAUDE.md", "README.md", "ARCHITECTURE.md", "CHANGELOG.md",
    "docs/development/workflow.md", "docs/development/skills.md",
)
LEGACY_PATTERN = re.compile(r"(?i)(\bgsd\b|gsd[-_:]|get-shit-done|\.planning[/\\])")


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True, timeout=60
    ).stdout.strip()


def status(root):
    try:
        main = git(root, "rev-parse", "--verify", "origin/main")
    except subprocess.CalledProcessError:
        main = None
    try:
        base = git(root, "rev-parse", "--verify", "origin/staging")
        ahead, behind = map(int, git(root, "rev-list", "--left-right", "--count",
                                    "HEAD...origin/staging").split())
    except subprocess.CalledProcessError:
        base, ahead, behind = None, None, None
    return {
        "root": str(root), "branch": git(root, "branch", "--show-current") or "DETACHED",
        "head": git(root, "rev-parse", "HEAD"), "origin_main": main,
        "origin_staging": base, "base_ref": "origin/staging",
        "ahead": ahead, "behind": behind,
        "dirty": bool(git(root, "status", "--porcelain")),
        "freshness": "unverified",
    }


REPOSITORY = "__OWNER__/__REPO__"
HEAVY_WORKFLOW = "staging-quality.yml"
PR_WORKFLOW = "pr.yml"


def gh_api(path):
    result = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/{path}"],
                            capture_output=True, text=True, check=True, timeout=30)
    return json.loads(result.stdout)


def staging_ready(expected_sha=None, promotion=False):
    """Stop the line only on red; promotion also needs the heavy suite done and green.

    Without promotion (task start, before each staging merge) a heavy run still queued or
    in progress passes, otherwise merges queue up one by one. Red is a completed heavy run
    without success at the exact tip or an open "staging vermelha" issue.
    """
    tip = gh_api("git/ref/heads/staging")["object"]["sha"]
    if expected_sha and tip != expected_sha:
        return {"ok": False, "sha": tip, "errors": ["staging tip changed; refresh candidate"]}
    # Search is indexed asynchronously; list issues directly and paginate instead.
    red, audit = [], []
    for page in range(1, 101):
        batch = gh_api(f"issues?state=open&per_page=100&page={page}")
        issues = [i for i in batch if not i.get("pull_request")]
        red.extend(i["number"] for i in issues if i["title"].lower().startswith("staging vermelha"))
        audit.extend(i["number"] for i in issues if i["title"].lower().startswith("audit indisponível"))
        if len(batch) < 100:
            break
    else:
        return {"ok": False, "errors": ["issue pagination limit reached"]}
    runs = gh_api(f"actions/workflows/{HEAVY_WORKFLOW}/runs?event=push&head_sha={tip}&per_page=100")["workflow_runs"]
    runs = [r for r in runs if r.get("head_sha") == tip and r.get("event") == "push"
            and r.get("path") == f".github/workflows/{HEAVY_WORKFLOW}"]
    # The API's run is updated in place on rerun (including run_attempt/status).
    run = max(runs, key=lambda item: item["id"], default={})
    done = run.get("status") == "completed"
    errors, warnings = [], []
    if red:
        errors.append(f"staging vermelha issues open: {red}")
    # The reporter skips a failing run once the tip has moved on, so while merges keep
    # landing the newest finished staging run is the red signal, not only the tip's.
    last = gh_api(f"actions/workflows/{HEAVY_WORKFLOW}/runs?event=push&branch=staging"
                  "&status=completed&per_page=1")["workflow_runs"][:1]
    if last and last[0].get("head_sha") != tip and last[0].get("conclusion") != "success":
        errors.append(f"latest finished heavy staging run {last[0].get('conclusion')} at {last[0].get('head_sha')}")
    if done and run.get("conclusion") != "success":
        errors.append(f"heavy staging suite {run.get('conclusion')} at exact tip")
    elif not done and promotion:
        errors.append("promotion needs the heavy staging suite completed and green at exact tip")
    elif not done:
        warnings.append("heavy staging suite still running or not started at tip")
    # Audit outage only warns on staging; promotion waits for a passing audit.
    if audit:
        (errors if promotion else warnings).append(
            f"audit indisponível issues open (audit must pass before promotion): {audit}")
    if gh_api("git/ref/heads/staging")["object"]["sha"] != tip:
        errors.append("staging tip changed during verification")
    return {"ok": not errors, "sha": tip, "promotion": promotion, "run": run.get("html_url"),
            "run_status": run.get("status"), "errors": errors, "warnings": warnings}


def pr_run_title(pr):
    """Same text as `run-name` in pr.yml: identifies the head's runs per PR and base."""
    return f"PR {pr['number']} into {pr['base']['ref']}"


def pr_event(event, run_id):
    """Decide whether a pull_request run may reuse an earlier verdict (my-skills#16).

    Only a base change re-evaluates the whole gate; pr.yml cancels the old run for it.
    A text-only `edited` (title/body) never cancels. It reuses only when the newest
    earlier run of this PR and head, whatever its base or conclusion, is the green run
    of the current base; a cancelled, red or other-base newest run reruns the cheap
    check. pr.yml re-checks scope on every edit (Security-Review:, Refs #N).
    """
    changes = event.get("changes") or {}
    pr = event["pull_request"]
    if event.get("action") != "edited" or changes.get("base"):
        return {"ok": True, "reuse": False, "reason": "new head, base or reopen"}
    head, title = pr["head"]["sha"], pr_run_title(pr)
    repo = (pr["head"].get("repo") or {}).get("full_name")  # None once the head fork is deleted
    runs = gh_api(f"actions/workflows/{PR_WORKFLOW}/runs?event=pull_request&head_sha={head}"
                  "&per_page=100")["workflow_runs"]
    runs = [r for r in runs if r.get("head_sha") == head and r.get("id", run_id) < run_id
            and r.get("path") == f".github/workflows/{PR_WORKFLOW}"
            and repo and (r.get("head_repository") or {}).get("full_name") == repo
            and str(r.get("display_title")).startswith(f"PR {pr['number']} into ")]
    last = max(runs, key=lambda item: item["id"], default={})
    reuse = (last.get("display_title") == title and last.get("status") == "completed"
             and last.get("conclusion") == "success")
    return {"ok": True, "reuse": reuse, "run": last.get("html_url"),
            "reason": "text-only edit; " + ("newest run of this head and base is green" if reuse
                                            else "newest run of this head is not green for this base, rerun the cheap check")}


def start(root, resume=False):
    # Fetch only: no checkout, pull, reset, stash, clean, credentials or remote writes.
    subprocess.run(["git", "-C", str(root), "fetch", "origin"], check=True, capture_output=True, timeout=60)
    result = status(root)
    if not resume and result["origin_staging"] is None:
        raise subprocess.CalledProcessError(1, "missing origin/staging integration base")
    line = staging_ready(expected_sha=result["origin_staging"])
    result.update(ok=line["ok"], staging_quality=line)
    result.update(freshness="fetched", mode="resume" if resume else "new",
                  policy=str(root / "AGENTS.md"))
    result["next_action"] = (
        "Preserve owned work/checkpoint; reread candidate policy and changed evidence."
        if resume else
        "Read candidate policy; use an isolated task branch from origin/staging."
    )
    return result


def legacy_paths(root):
    found = []
    for name in (".planning", ".gsd", "get-shit-done"):
        if (root / name).exists():
            found.append(name)
    for dirname in (".codex", ".claude", ".agents", ".github"):
        folder = root / dirname
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            rel = path.relative_to(root).as_posix()
            # Nested worktrees and installed dependencies are not project policy.
            if rel.startswith(".claude/worktrees/") or "node_modules" in path.parts:
                continue
            # Never read env, dumps, archives, binary assets or credentials.
            if path.is_symlink():
                if LEGACY_PATTERN.search(rel):
                    found.append(rel)
                continue
            if path.is_dir():
                if LEGACY_PATTERN.search(rel):
                    found.append(rel)
            elif (path.suffix in (".md", ".toml", ".yaml", ".yml", ".sh")
                  or path.name in ("settings.json", "config.json")):
                if LEGACY_PATTERN.search(rel) or LEGACY_PATTERN.search(path.read_text(errors="ignore")):
                    found.append(rel)
    for name in DOCS:
        path = root / name
        if path.is_file() and LEGACY_PATTERN.search(path.read_text(errors="ignore")):
            found.append(name)
    return sorted(set(found))


def doctor(root, shared=False, home=None):
    errors = []
    for name in DOCS:
        if not (root / name).is_file():
            errors.append(f"missing document: {name}")
    bridge = root / "CLAUDE.md"
    if bridge.is_file() and "@AGENTS.md" not in bridge.read_text():
        errors.append("CLAUDE.md must import @AGENTS.md")
    for name in LOCAL_SKILLS:
        path = root / ".agents" / "skills" / name / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing local skill: {name}")
        elif not re.search(rf"(?m)^name: {re.escape(name)}$", path.read_text()):
            errors.append(f"skill name mismatch: {name}")
    for name in legacy_paths(root):
        errors.append(f"legacy workflow integration: {name}")
    config = root / ".codex" / "environments" / "environment.toml"
    try:
        value = tomllib.loads(config.read_text())
        setup = value["setup"]["script"]
        if ".codex/scripts/setup.sh" not in setup:
            errors.append("environment setup must use the versioned script")
        if "cleanup" in value:
            errors.append("automatic artifact cleanup requires explicit ownership")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"invalid Codex environment: {type(exc).__name__}")
    if shared:
        # File presence only; not runtime catalog, Cloud or invocation evidence.
        skills_root = (home or Path.home()) / ".agents" / "skills"
        for name in SHARED_SKILLS:
            if not (skills_root / name / "SKILL.md").is_file():
                errors.append(f"missing shared skill: {name}")
    return {"ok": not errors, "errors": errors,
            "shared_presence_checked": shared, "runtime_discovery_proven": False,
            "memory_capture_configured": (root / ".ai-memory.toml").exists()}


def pr_event_main():
    """Writes reuse to $GITHUB_OUTPUT; any doubt reruns the cheap check, never red."""
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        result = pr_event(event, int(os.environ["GITHUB_RUN_ID"]))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
        result = {"ok": True, "reuse": False,
                  "reason": f"could not prove a green run of this head ({type(exc).__name__}); rerun the cheap check"}
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write(f"reuse={str(result['reuse']).lower()}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "status", "doctor", "staging-ready", "pr-event"))
    parser.add_argument("--expected-sha")
    parser.add_argument("--promotion", action="store_true",
                        help="staging-ready for the PR into main: heavy suite and audit must be green")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--shared-skills", action="store_true")
    args = parser.parse_args()
    if args.resume and args.command != "start":
        parser.error("--resume is only valid for start")
    if args.shared_skills and args.command != "doctor":
        parser.error("--shared-skills is only valid for doctor")
    if args.promotion and args.command != "staging-ready":
        parser.error("--promotion is only valid for staging-ready")
    root = Path(__file__).resolve().parent.parent
    if args.command == "pr-event":
        return pr_event_main()
    try:
        result = (staging_ready(args.expected_sha, args.promotion) if args.command == "staging-ready" else
                  doctor(root, args.shared_skills) if args.command == "doctor" else
                  start(root, args.resume) if args.command == "start" else status(root))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
        # Do not print Git stderr: credential helpers/URLs may include secrets.
        print(json.dumps({"ok": False, "error": "Git/GitHub verification failed; stop the line",
                          "freshness": "unverified", "exit_code": getattr(exc, "returncode", 1)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
