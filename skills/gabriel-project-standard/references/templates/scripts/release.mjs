#!/usr/bin/env node
// Versioned releases. package.json is canonical; CHANGELOG.md's first
// version section must match it; tag v<version> may be absent or on HEAD.
//   check [--publish]             validate (local only, no network). Without
//                                 --publish a tag on another commit means the
//                                 version is already released (normal on staging
//                                 after a promotion); --publish (release.yml)
//                                 requires the tag to be absent or on HEAD.
//   prepare --bump patch|minor|major [--date YYYY-MM-DD]
//                                 fold the changes/<N>-<slug>.md notes (and any
//                                 "## Unreleased" notes) into a new version,
//                                 merging "### Section" headings, then delete
//                                 the note files (the release PR commits both)
//   notes                         print the current version's changelog section
// Publication (tag + GitHub Release) is done by .github/workflows/release.yml
// after a push to main; this script never pushes or creates remote state.
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const SEMVER = /^(\d+)\.(\d+)\.(\d+)$/;
const SECTION = /^## (\d+\.\d+\.\d+) - (\d{4}-\d{2}-\d{2})\s*$/m;

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

function check(args = []) {
  const version = readVersion();
  const changelog = readFileSync("CHANGELOG.md", "utf8");
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

// changes/<N>-<slug>.md, oldest issue first; .gitkeep and README stay.
function changeNotes() {
  if (!existsSync("changes")) return [];
  return readdirSync("changes")
    .filter((name) => /^\d+-.+\.md$/.test(name))
    .sort((a, b) => parseInt(a, 10) - parseInt(b, 10) || a.localeCompare(b))
    .map((name) => join("changes", name));
}

// Merge notes by "### Heading" in first-seen order; lines before any heading lead.
function mergeNotes(texts) {
  const sections = new Map([["", []]]);
  for (const text of texts) {
    let heading = "";
    for (const line of text.split("\n")) {
      const match = line.match(/^### (.+?)\s*$/);
      if (match) heading = match[1];
      else if (line.trim()) {
        if (!sections.has(heading)) sections.set(heading, []);
        sections.get(heading).push(line);
      }
    }
  }
  return [...sections]
    .filter(([, lines]) => lines.length)
    .map(([heading, lines]) => (heading ? `### ${heading}\n\n` : "") + lines.join("\n"))
    .join("\n\n");
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

  const changelog = readFileSync("CHANGELOG.md", "utf8");
  const match = changelog.match(/^## Unreleased[ \t]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m);
  const files = changeNotes();
  const body = mergeNotes([match?.[1] ?? "", ...files.map((file) => readFileSync(file, "utf8"))]);
  if (body === "") fail("no notes: add changes/<N>-<slug>.md (or notes under '## Unreleased')");
  const entry = `## ${version} - ${date}\n\n${body}\n\n`;
  const updated = match
    ? changelog.replace(match[0], () => `## Unreleased\n\n${entry}`)
    : changelog.match(/^## /m)
      ? changelog.replace(/^## /m, () => `${entry}## `)
      : `${changelog.trimEnd()}\n\n${entry}`;

  const pkgText = readFileSync("package.json", "utf8");
  const pkg = JSON.parse(pkgText);
  pkg.version = version;
  writeFileSync("package.json", `${JSON.stringify(pkg, null, 2)}\n`);
  writeFileSync("CHANGELOG.md", updated);
  for (const file of files) unlinkSync(file);
  process.stdout.write(`PREPARED_NOT_PUBLISHED\t${version}\n`);
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
