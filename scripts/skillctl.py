#!/usr/bin/env python3
"""Validate and link only this repository's skills. No network or credentials."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCATIONS = {"codex": ".agents/skills", "claude": ".claude/skills"}


def inventory(root=ROOT):
    names = json.loads((root / "skills.json").read_text())["skills"]
    if not names or len(names) != len(set(names)):
        raise ValueError("Empty or duplicate inventory")
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r"gabriel-[a-z0-9-]{1,55}", name):
            raise ValueError("Invalid skill name")
        source = root / "skills" / name
        if source.is_symlink() or not source.is_dir():
            raise ValueError(f"Missing canonical directory: {name}")
    return names


def validate(root=ROOT):
    names = inventory(root)
    actual = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    if actual != set(names):
        raise ValueError("skills.json differs from canonical directories")
    if (root / "AGENTS.md").read_bytes() != (root / "CLAUDE.md").read_bytes():
        raise ValueError("AGENTS.md and CLAUDE.md differ")
    for name in names:
        text = (root / "skills" / name / "SKILL.md").read_text()
        parts = text.split("---\n", 2)
        if len(parts) != 3 or parts[0] or not parts[2].strip():
            raise ValueError(f"Invalid frontmatter/body: {name}")
        fields = dict(line.split(":", 1) for line in parts[1].splitlines() if line)
        if fields.get("name", "").strip() != name:
            raise ValueError(f"Name mismatch: {name}")
        description = json.loads(fields.get("description", "").strip())
        if not isinstance(description, str) or not 15 <= len(description) <= 240:
            raise ValueError(f"Invalid description: {name}")
        if "/home/" in text or "TODO" in text or "[INSERT" in text:
            raise ValueError(f"Nonportable path or unfinished scaffold: {name}")
        for link in re.findall(r"\]\((references/[^)]+)\)", parts[2]):
            reference = (root / "skills" / name / link.split("#", 1)[0]).resolve()
            shared = (root / "docs" / "tool-routing.md").resolve()
            inside_skill = reference.is_relative_to((root / "skills" / name).resolve())
            shared_link = link.split("#", 1)[0] == "references/tool-routing.md" and reference == shared and shared.is_relative_to(root.resolve())
            if not (inside_skill or shared_link) or not reference.is_file():
                raise ValueError(f"Missing or escaping reference: {name}/{link}")
        ui = (root / "skills" / name / "agents/openai.yaml").read_text()
        fields = dict(line.strip().split(":", 1) for line in ui.splitlines() if line.startswith("  "))
        short = json.loads(fields["short_description"].strip())
        prompt = json.loads(fields["default_prompt"].strip())
        if not 25 <= len(short) <= 64 or f"${name}" not in prompt:
            raise ValueError(f"Invalid interface metadata: {name}")
    retired_inventory(root)
    return names


def retired_inventory(root=ROOT):
    manifest = json.loads((root / "skills.json").read_text())
    names = manifest.get("retired", [])
    if len(names) != len(set(names)) or set(names) & set(manifest["skills"]):
        raise ValueError("Duplicate or active retired skill")
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r"gabriel-[a-z0-9-]{1,55}", name):
            raise ValueError("Invalid retired skill name")
    return names


def retired_plan(root, home, targets):
    rows = []
    for target in targets:
        for name in retired_inventory(root):
            src = (root / "skills" / name).resolve()
            dst = home / LOCATIONS[target] / name
            owned = dst.is_symlink() and dst.resolve() == src
            status = "linked" if owned else "conflict" if dst.exists() or dst.is_symlink() else "missing"
            rows.append({"target": target, "source": str(src), "link": str(dst), "status": status})
    return rows


def plan(root, home, targets):
    rows = []
    for target in targets:
        directory = home / LOCATIONS[target]
        if directory.exists() and not directory.is_dir():
            raise ValueError(f"Skill root is not a directory: {directory}")
        for name in validate(root):
            src = (root / "skills" / name).resolve()
            dst = directory / name
            owned = dst.is_symlink() and dst.resolve() == src
            status = "linked" if owned else "conflict" if dst.exists() or dst.is_symlink() else "missing"
            rows.append({"target": target, "source": str(src), "link": str(dst), "status": status})
    return rows


def install(rows):
    if any(r["status"] == "conflict" for r in rows):
        raise ValueError("Conflicting destinations; nothing installed")
    created = []
    try:
        for row in rows:
            dst, src = Path(row["link"]), Path(row["source"])
            if row["status"] == "linked":
                if not dst.is_symlink() or dst.resolve() != src:
                    raise ValueError(f"Destination changed: {dst}")
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(src, target_is_directory=True)
            created.append((dst, src))
    except Exception:
        for dst, src in reversed(created):
            if dst.is_symlink() and dst.resolve() == src:
                dst.unlink()
        raise


def uninstall(rows):
    for row in rows:
        dst, src = Path(row["link"]), Path(row["source"])
        if dst.is_symlink() and dst.resolve() == src:
            dst.unlink()


def migrate(rows, retired):
    # Install all replacements before retiring owned links. A failed install
    # leaves the old links alone; foreign retired destinations stay untouched.
    install(rows)
    uninstall(retired)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "status", "install", "uninstall"])
    parser.add_argument("--target", choices=["all", *LOCATIONS], default="all")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Alternate home for isolated tests")
    parser.add_argument("--apply", action="store_true", help="Apply install/uninstall; otherwise only show plan")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            print(f"Validated {len(validate())} skills and instruction parity")
            return 0
        targets = list(LOCATIONS) if args.target == "all" else [args.target]
        rows = plan(ROOT, args.home.expanduser().resolve(), targets)
        retired = retired_plan(ROOT, args.home.expanduser().resolve(), targets)
        print(json.dumps({"active": rows, "retired": retired}, indent=2, ensure_ascii=False))
        if args.command == "install" and args.apply:
            migrate(rows, retired)
        elif args.command == "uninstall" and args.apply:
            uninstall(rows + retired)
        elif args.command == "status":
            return int(any(r["status"] != "linked" for r in rows) or any(r["status"] == "linked" for r in retired))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
