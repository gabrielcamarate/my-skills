#!/usr/bin/env python3
"""Print the slowest unit tests from a vitest JSON report.

A unit test near the 5 s timeout does real I/O or too much work. Fix it (smaller
fixture, mock, or move it to the heavy suite); never raise the timeout.
  python3 scripts/slowest-tests.py REPORT.json [N]
"""
import json
import os
import sys


def main(argv):
    path = argv[1]
    limit = int(argv[2]) if len(argv) > 2 else 5
    try:
        with open(path, encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"note  no test report at {path} ({error})", file=sys.stderr)
        return 0
    rows = []
    for suite in report.get("testResults", []):
        name = suite.get("name", "")
        file = os.path.relpath(name) if os.path.isabs(name) else name
        for test in suite.get("assertionResults", []):
            if isinstance(test.get("duration"), (int, float)):
                title = " > ".join([*test.get("ancestorTitles", []), test.get("title", "")])
                rows.append((test["duration"], file, title))
    rows.sort(key=lambda row: row[0], reverse=True)
    print(f"slowest {limit} unit tests:")
    for duration, file, title in rows[:limit]:
        print(f"  {duration:6.0f} ms  {file}  {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
