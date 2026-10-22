#!/usr/bin/env node
// Versioned releases. package.json is canonical; CHANGELOG.md's first
// version section must match it; tag v<version> may be absent or on HEAD.
// Each task PR adds one note changes/<issue>-<slug>.md (Maison #411): "- " items,
// indented continuation lines and optional "### <category>" headings.
//   check [--publish]             validate (local only, no network). Without
//                                 --publish a tag on another commit means the
//                                 version is already released (normal on staging
//                                 after a promotion); --publish (release.yml)
//                                 requires the tag to be absent or on HEAD.
//                                 Also validates every note in changes/.
//   prepare --bump patch|minor|major [--date YYYY-MM-DD]
//                                 join changes/ notes into a new version section
//                                 (by category, in issue order) and delete them
//   notes                         print the current version's changelog section
// Publication (tag + GitHub Release) is done by .github/workflows/release.yml
// after a push to main; this script never pushes or creates remote state.
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";

const SEMVER = /^(\d+)\.(\d+)\.(\d+)$/;
const SECTION = /^## (\d+\.\d+\.\d+) - (\d{4}-\d{2}-\d{2})\s*$/m;
const CHANGES = "changes";
const NOTE_NAME = /^(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$/;
// Categories follow the project CHANGELOG language; keep changes/README.md in sync.
const CATEGORIES = ["Adicionado", "Alterado", "Corrigido", "Removido", "Segurança"];
const UNRELEASED = /^## Unreleased[ \t]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m;

function fail(message) {
  process.stderr.write(`FAIL  ${message}\n`);
  process.exit(1);
}

function readVersion() {
  const version = JSON.parse(readFileSync("package.json", "utf8")).version;
  if (!SEMVER.test(version ?? "")) fail(`package.json version is not SemVer: ${version}`);
  return version;
}

function git(...args) {
  return execFileSync("git", args, { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
}

function tagCommit(tag) {
  try {
    return git("rev-list", "-n", "1", tag);
  } catch {
    return null;
  }
}

function section(changelog, version) {
  const start = changelog.search(new RegExp(`^## ${version.replaceAll(".", "\\.")} - `, "m"));
  if (start === -1) return null;
  const rest = changelog.slice(start);
  const next = rest.slice(3).search(/^## /m);
  return (next === -1 ? rest : rest.slice(0, next + 3)).trim();
}

// Returns [{ category: string | null, body }] for one note, or fails.
function parseNote(file, text) {
  const segments = [];
  let current = null;
  let lastItem = false;
  for (const [index, line] of text.split("\n").entries()) {
    const where = `${CHANGES}/${file}:${index + 1}`;
    const heading = line.match(/^###\s+(.+?)\s*$/);
    if (heading) {
      if (!CATEGORIES.includes(heading[1])) fail(`${where} category must be one of ${CATEGORIES.join(", ")}`);
      current = { category: heading[1], lines: [] };
      segments.push(current);
      lastItem = false;
    } else if (line.trim() === "") {
      current?.lines.push("");
      lastItem = false;
    } else if (line.startsWith("- ") || (lastItem && /^\s+\S/.test(line))) {
      if (!current) {
        current = { category: null, lines: [] };
        segments.push(current);
      }
      current.lines.push(line.trimEnd());
      lastItem = true;
    } else {
      fail(`${where} must be "- item", an indented continuation or "### <category>"`);
    }
  }
  const parsed = segments.map(({ category, lines }) => ({ category, body: lines.join("\n").trim() }));
  if (parsed.length === 0 || parsed.some(({ body }) => body === "")) fail(`${CHANGES}/${file} needs "- " items under each heading`);
  return parsed;
}

// Notes in issue order; README.md documents the directory and is not a note.
function readNotes() {
  let entries;
  try {
    entries = readdirSync(CHANGES, { withFileTypes: true });
  } catch {
    return [];
  }
  const notes = [];
  for (const entry of entries) {
    if (entry.name === "README.md" && entry.isFile()) continue;
    const match = entry.name.match(NOTE_NAME);
    if (!match || !entry.isFile()) fail(`${CHANGES}/${entry.name} is not a note named <issue>-<slug>.md`);
    notes.push({ file: entry.name, issue: Number(match[1]), segments: parseNote(entry.name, readFileSync(`${CHANGES}/${entry.name}`, "utf8")) });
  }
  return notes.sort((a, b) => a.issue - b.issue || a.file.localeCompare(b.file));
}

function check(args = []) {
  const version = readVersion();
  const changelog = readFileSync("CHANGELOG.md", "utf8");
  if (changelog.match(UNRELEASED)?.[1].trim()) fail(`CHANGELOG.md '## Unreleased' must be empty; notes go in ${CHANGES}/`);
  readNotes();
  const latest = changelog.match(SECTION);
  if (!latest) fail("CHANGELOG.md has no '## X.Y.Z - YYYY-MM-DD' section");
  if (latest[1] !== version) {
    fail(`changelog section ${latest[1]} does not match package.json ${version}`);
  }
  const tagged = tagCommit(`v${version}`);
  if (tagged && tagged !== git("rev-parse", "HEAD")) {
    if (args.includes("--publish")) {
      fail(`tag v${version} already exists on another commit; prepare a new version`);
    }
    process.stdout.write(`PASS\tversion\t${version}\treleased\n`);
    return;
  }
  process.stdout.write(`PASS\tversion\t${version}\n`);
}

function prepare(args) {
  const bumpIndex = args.indexOf("--bump");
  const bump = bumpIndex === -1 ? undefined : args[bumpIndex + 1];
  if (!["patch", "minor", "major"].includes(bump)) fail("use --bump patch|minor|major");
  const dateIndex = args.indexOf("--date");
  const now = new Date();
  const local = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
  const date = dateIndex === -1 ? local : args[dateIndex + 1];
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date ?? "")) fail("use --date YYYY-MM-DD");

  const current = readVersion().split(".").map(Number);
  const next =
    bump === "major" ? [current[0] + 1, 0, 0]
    : bump === "minor" ? [current[0], current[1] + 1, 0]
    : [current[0], current[1], current[2] + 1];
  const version = next.join(".");

  const notes = readNotes();
  if (notes.length === 0) fail(`${CHANGES}/ has no notes to release`);
  const uncategorized = [];
  const grouped = new Map(CATEGORIES.map((category) => [category, []]));
  for (const { segments } of notes) {
    for (const { category, body } of segments) (category ? grouped.get(category) : uncategorized).push(body);
  }
  const parts = [];
  if (uncategorized.length) parts.push(uncategorized.join("\n"));
  for (const [category, bodies] of grouped) if (bodies.length) parts.push(`### ${category}\n\n${bodies.join("\n")}`);
  const entry = `## ${version} - ${date}\n\n${parts.join("\n\n")}\n\n`;

  let changelog = readFileSync("CHANGELOG.md", "utf8");
  const unreleased = changelog.match(UNRELEASED);
  if (unreleased?.[1].trim()) fail(`CHANGELOG.md '## Unreleased' must be empty; notes go in ${CHANGES}/`);
  if (unreleased) changelog = changelog.replace(unreleased[0], "");
  const first = changelog.search(/^## /m);
  const updated = first === -1 ? `${changelog.trimEnd()}\n\n${entry}`.replace(/\n+$/, "\n")
    : `${changelog.slice(0, first)}${entry}${changelog.slice(first)}`;

  const pkgText = readFileSync("package.json", "utf8");
  const pkg = JSON.parse(pkgText);
  pkg.version = version;
  writeFileSync("package.json", `${JSON.stringify(pkg, null, 2)}\n`);
  writeFileSync("CHANGELOG.md", updated);
  for (const { file } of notes) unlinkSync(`${CHANGES}/${file}`);
  process.stdout.write(`PREPARED_NOT_PUBLISHED\t${version}\t${notes.length} notes\n`);
}

function notes() {
  const version = readVersion();
  const body = section(readFileSync("CHANGELOG.md", "utf8"), version);
  if (!body) fail(`CHANGELOG.md has no section for ${version}`);
  process.stdout.write(`${body.split("\n").slice(1).join("\n").trim()}\n`);
}

const [command, ...rest] = process.argv.slice(2);
if (command === "check") check(rest);
else if (command === "prepare") prepare(rest);
else if (command === "notes") notes();
else fail("usage: release.mjs check | prepare --bump patch|minor|major | notes");
