#!/usr/bin/env python3
"""Dependency audit that tells a vulnerability apart from an audit source outage.

  python3 scripts/dependency-audit.py [--soft-unavailable] [-- PNPM_AUDIT_ARGS...]

PNPM_AUDIT_ARGS defaults to `--prod --audit-level moderate`. pnpm 10 `audit --json`
exits 1 on any advisory and ignores --audit-level, so the verdict comes from
metadata.vulnerabilities, summing the levels at or above --audit-level (pnpm's
default level is low). Missing or non-numeric counts fail closed; the exit code
only tells an execution failure (anything but 0/1) apart.

Exit 0: clean. Exit 1: vulnerability found or unexpected failure (fail closed).
Exit 3: the audit endpoint timed out or answered 5xx/network error. With
--soft-unavailable (staging only) an outage is a warning and exits 0, so the
line keeps moving; promotion to main runs strict and blocks until audit passes.
Writes audit=ok|vulnerable|unavailable|failed to $GITHUB_OUTPUT when set.
"""
import json
import os
import re
import signal
import subprocess
import sys

UNAVAILABLE = re.compile(
    r"responded with 5\d\d|ETIMEDOUT|ESOCKETTIMEDOUT|ECONNRESET|ECONNREFUSED|EAI_AGAIN|ENOTFOUND"
    r"|ERR_SOCKET_TIMEOUT|UND_ERR_CONNECT_TIMEOUT|UND_ERR_HEADERS_TIMEOUT|socket hang up")

LEVELS = ("info", "low", "moderate", "high", "critical")
DEFAULT_ARGS = ("--prod", "--audit-level", "moderate")


def audit_level(args):
    level = "low"
    for index, arg in enumerate(args):
        if arg.startswith("--audit-level="):
            level = arg.split("=", 1)[1]
        elif arg == "--audit-level" and index + 1 < len(args):
            level = args[index + 1]
    if level not in LEVELS:
        raise ValueError(f"unknown --audit-level {level}")
    return level


def run_audit(args, timeout):
    proc = subprocess.Popen(["pnpm", "audit", "--json", *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return None, "", f"no answer within {timeout}s"
    return proc.returncode, out, err


def classify(code, out, err, level="low"):
    if code is None:
        return "unavailable"
    try:
        report = json.loads(out)
    except ValueError:
        report = None
    if isinstance(report, dict) and "metadata" in report and "error" not in report:
        if code not in (0, 1):
            return "failed"
        found = report["metadata"].get("vulnerabilities") if isinstance(report["metadata"], dict) else None
        counts = [found.get(name) for name in LEVELS[LEVELS.index(level):]] if isinstance(found, dict) else [None]
        if not all(type(count) is int and count >= 0 for count in counts):
            return "failed"
        return "vulnerable" if sum(counts) else "ok"
    return "unavailable" if UNAVAILABLE.search(out + err) else "failed"


def main(argv):
    split = argv.index("--") if "--" in argv else len(argv)
    soft, extra = "--soft-unavailable" in argv[1:split], argv[split + 1:] or list(DEFAULT_ARGS)
    timeout = int(os.environ.get("AUDIT_TIMEOUT", "120"))
    level = audit_level(extra)
    code, out, err = run_audit(extra, timeout)
    state = classify(code, out, err, level)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(f"audit={state}\n")
    if state == "ok":
        print(f"PASS  dependency audit (level {level})")
        return 0
    if state == "vulnerable":
        sys.stdout.write(out)
        print(f"FAIL  dependency audit found vulnerabilities at or above {level}", file=sys.stderr)
        return 1
    detail = (err.strip() or out.strip())[-500:]
    if state == "unavailable":
        print(f"WARN  audit source unavailable: {detail}", file=sys.stderr)
        if soft:
            print("::warning title=audit indisponível::audit source unavailable; promotion to main stays blocked until audit passes")
            return 0
        return 3
    print(f"FAIL  dependency audit failed: {detail or f'exit {code}'}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
