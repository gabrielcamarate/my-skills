#!/usr/bin/env python3
"""Cheap task metadata/diff boundary. Does not fetch PR content with a token.

Changelog notes (Maison #411): a task PR adds one note changes/<N>-<slug>.md for its own
issue and never edits CHANGELOG.md, so parallel PRs do not conflict. Only the
release cut (package.json version changes) edits CHANGELOG.md and deletes notes.
Note contents are validated by `node scripts/release.mjs check`.
"""
import json
import os
from pathlib import Path
import re
import subprocess

NOTE = re.compile(r'changes/(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md')
NOTES_README = 'changes/README.md'
LEGACY_NOTE = 'changes/0-unreleased-legacy.md'
UNRELEASED = re.compile(r'^## Unreleased[ \t]*\n(.*?)(?=^## |\Z)', re.M | re.S)


def merge_base(base, head):
    """The PR's own changes start where the branch left staging, not at the staging tip."""
    return subprocess.check_output(['git', 'merge-base', base, head], text=True, timeout=30).strip()


def diff_status(base, head):
    out = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', base, head], text=True, timeout=30)
    fields = out.split('\0')[:-1]
    return list(zip(fields[0::2], fields[1::2]))


def pending_notes(sha):
    out = subprocess.check_output(['git', 'ls-tree', '--name-only', '-z', sha, 'changes/'], text=True, timeout=30)
    return [path for path in out.split('\0') if path and path != NOTES_README]


def blob(sha, path):
    result = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True, timeout=30)
    return result.stdout if result.returncode == 0 else None


def version(sha):
    return json.loads(blob(sha, 'package.json') or '{}').get('version')


def has_unreleased_notes(sha):
    match = UNRELEASED.search(blob(sha, 'CHANGELOG.md') or '')
    return match is not None and match[1].strip() != ''


def legacy_migration(tip, base, head, changes):
    """One-time move of a non-empty '## Unreleased' into LEGACY_NOTE; nothing else in CHANGELOG.

    Expires once the staging tip has migrated, even for branches cut before it."""
    old = blob(base, 'CHANGELOG.md') or ''
    match = UNRELEASED.search(old)
    return (('A', LEGACY_NOTE) in changes and has_unreleased_notes(tip) and has_unreleased_notes(base)
            and blob(head, 'CHANGELOG.md') == old.replace(match[0], '', 1))


def check(event):
    pr = event['pull_request']
    branch = pr['head']['ref']
    match = re.fullmatch(r'(feature|fix|chore|docs|test|refactor)/(\d+)-[a-z0-9-]+', branch)
    if not match or not re.search(rf'\bRefs #{match[2]}\b', pr.get('body') or ''):
        raise ValueError('Task branch must identify an issue and PR body must contain Refs #N')
    if re.search(r'(?i)\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#\d+', pr.get('body') or ''):
        raise ValueError('Use Refs #N, never a closing keyword: the issue closes after acceptance')
    issue = match[2]
    base, head = pr['base']['sha'], pr['head']['sha']
    if not all(re.fullmatch(r'[0-9a-f]{40}', sha) for sha in (base, head)):
        raise ValueError('Invalid commit SHA')
    tip, base = base, merge_base(base, head)
    subprocess.run(['git', 'diff', '--check', base, head], check=True, timeout=30)
    changes = diff_status(base, head)
    paths = [path for _, path in changes]
    if not paths:
        raise ValueError('Empty task')
    if any(Path(p).name.startswith('.env') and Path(p).name != '.env.example' for p in paths):
        raise ValueError('Environment files are outside PR scope')
    notes = [(status, path) for status, path in changes if path.startswith('changes/') and path != NOTES_README]
    if version(base) != version(head):
        # Release cut: joins the notes into CHANGELOG.md and deletes them.
        if any(status != 'D' for status, _ in notes):
            raise ValueError('Release PR only deletes notes from changes/')
        if left := pending_notes(head):
            raise ValueError(f'Release PR must consume every note; left: {", ".join(left)}')
        return
    migration = legacy_migration(tip, base, head, changes)
    if 'CHANGELOG.md' in paths and not migration:
        raise ValueError(f'Task PRs do not edit CHANGELOG.md; add changes/{issue}-<slug>.md instead')
    own = [path for status, path in notes
           if status in ('A', 'M') and (m := NOTE.fullmatch(path)) and m[1] == issue]
    if len(own) != 1:
        raise ValueError(f'Task requires exactly one note changes/{issue}-<slug>.md')
    foreign = [path for status, path in notes if path not in own and not (migration and (status, path) == ('A', LEGACY_NOTE))]
    if foreign:
        raise ValueError(f'Task PR may only touch its own note, not: {", ".join(foreign)}')


if __name__ == '__main__':
    check(json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()))
