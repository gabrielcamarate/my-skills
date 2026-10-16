#!/usr/bin/env node
// Versioned releases. package.json is canonical; CHANGELOG.md's first
// version section must match it; tag v<version> may be absent or on HEAD.
//   check [--publish]             validate (local only, no network). Without
//                                 --publish a tag on another commit means the
//                                 version is already released (normal on staging
//                                 after a promotion); --publish (release.yml)
//                                 requires the tag to be absent or on HEAD.
//   prepare --bump patch|minor|major [--date YYYY-MM-DD]
//                                 move "## Unreleased" notes into a new version
//   notes                         print the current version's changelog section
// Publication (tag + GitHub Release) is done by .github/workflows/release.yml
// after a push to main; this script never pushes or creates remote state.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";

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
  if (!match || match[1].trim() === "") fail("CHANGELOG.md needs notes under '## Unreleased'");
  const updated = changelog.replace(
    match[0],
    () => `## Unreleased\n\n## ${version} - ${date}\n\n${match[1].trim()}\n\n`,
  );

  const pkgText = readFileSync("package.json", "utf8");
  const pkg = JSON.parse(pkgText);
  pkg.version = version;
  writeFileSync("package.json", `${JSON.stringify(pkg, null, 2)}\n`);
  writeFileSync("CHANGELOG.md", updated);
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
