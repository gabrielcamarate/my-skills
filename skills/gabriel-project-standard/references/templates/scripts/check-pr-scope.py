#!/usr/bin/env python3
"""Cheap task metadata/diff boundary. Does not fetch PR content with a token."""
import json
import os
from pathlib import Path
import re
import subprocess


def check(event):
    pr = event['pull_request']
    branch = pr['head']['ref']
    match = re.fullmatch(r'(feature|fix|chore|docs|test|refactor|release)/(\d+)-[a-z0-9-]+', branch)
    if not match or not re.search(rf'\bRefs #{match[2]}\b', pr.get('body') or ''):
        raise ValueError('Task branch must identify an issue and PR body must contain Refs #N')
    if re.search(r'(?i)\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#\d+', pr.get('body') or ''):
        raise ValueError('Use Refs #N, never a closing keyword: the issue closes after acceptance')
    base, head = pr['base']['sha'], pr['head']['sha']
    if not all(re.fullmatch(r'[0-9a-f]{40}', sha) for sha in (base, head)):
        raise ValueError('Invalid commit SHA')
    subprocess.run(['git', 'diff', '--check', base, head], check=True, timeout=30)
    paths = subprocess.check_output(['git', 'diff', '--name-only', base, head], text=True, timeout=30).splitlines()
    if not paths:
        raise ValueError('Empty task')
    if any(Path(p).name.startswith('.env') and Path(p).name != '.env.example' for p in paths):
        raise ValueError('Environment files are outside PR scope')
    # One note per task in changes/: parallel PRs never touch the same file. Only the
    # release PR folds the notes into CHANGELOG.md (release.mjs prepare) and deletes them.
    if match[1] == 'release':
        if 'CHANGELOG.md' not in paths:
            raise ValueError('Release PR requires CHANGELOG.md (node scripts/release.mjs prepare)')
        return
    if 'CHANGELOG.md' in paths:
        raise ValueError('Only the release PR edits CHANGELOG.md; add a changes/<N>-<slug>.md note instead')
    added = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=d', base, head, '--', 'changes/'],
                                    text=True, timeout=30).splitlines()
    if not any(re.fullmatch(rf'changes/{match[2]}-[a-z0-9-]+\.md', p) for p in added):
        raise ValueError(f'Task requires a change note: changes/{match[2]}-<slug>.md')

if __name__ == '__main__':
    check(json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()))
