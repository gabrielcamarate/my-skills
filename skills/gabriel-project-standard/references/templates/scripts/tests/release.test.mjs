// Release tooling contract: version, changelog and tag must agree, and
// preparation never touches the remote.
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const SCRIPT = fileURLToPath(new URL("../release.mjs", import.meta.url));

function repo({ version = "0.1.2", changelog = "# Changelog\n\n## 0.1.2 - 2026-10-14\n\n### Changed\n\n- Algo.\n" } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "project-release-"));
  const git = (...args) => execFileSync("git", args, { cwd: dir, stdio: "pipe" }).toString().trim();
  git("init", "-q", "-b", "main");
  git("config", "user.email", "t@example.com");
  git("config", "user.name", "t");
  writeFileSync(join(dir, "package.json"), JSON.stringify({ name: "x", version }, null, 2) + "\n");
  writeFileSync(join(dir, "CHANGELOG.md"), changelog);
  git("add", ".");
  git("commit", "-qm", "init");
  return { dir, git };
}

function run(dir, ...args) {
  try {
    return { code: 0, out: execFileSync("node", [SCRIPT, ...args], { cwd: dir, stdio: "pipe" }).toString() };
  } catch (error) {
    return { code: error.status, out: `${error.stdout}${error.stderr}` };
  }
}

test("check passes when version, changelog and absent tag agree", () => {
  const { dir } = repo();
  const result = run(dir, "check");
  assert.equal(result.code, 0, result.out);
  assert.match(result.out, /PASS\s+version\s+0\.1\.2/);
});

test("check fails when the latest changelog section differs from package.json", () => {
  const { dir } = repo({ version: "0.1.3" });
  const result = run(dir, "check");
  assert.notEqual(result.code, 0);
  assert.match(result.out, /changelog/i);
});

test("check --publish fails when the tag already points to another commit", () => {
  const { dir, git } = repo();
  git("tag", "v0.1.2");
  writeFileSync(join(dir, "x.txt"), "novo\n");
  git("add", ".");
  git("commit", "-qm", "next");
  const result = run(dir, "check", "--publish");
  assert.notEqual(result.code, 0);
  assert.match(result.out, /tag v0\.1\.2/);
});

test("check accepts a tag that already points to HEAD (idempotent publish)", () => {
  const { dir, git } = repo();
  git("tag", "v0.1.2");
  assert.equal(run(dir, "check").code, 0);
});

test("prepare bumps version and moves Unreleased notes without creating tags", () => {
  const { dir, git } = repo({
    changelog: "# Changelog\n\n## Unreleased\n\n### Fixed\n\n- Corrige X.\n\n## 0.1.2 - 2026-10-14\n\n- Algo.\n",
  });
  const result = run(dir, "prepare", "--bump", "patch", "--date", "2026-10-15");
  assert.equal(result.code, 0, result.out);
  assert.equal(JSON.parse(readFileSync(join(dir, "package.json"), "utf8")).version, "0.1.3");
  const changelog = readFileSync(join(dir, "CHANGELOG.md"), "utf8");
  assert.match(changelog, /## Unreleased\n\n## 0\.1\.3 - 2026-10-15\n\n### Fixed\n\n- Corrige X\./);
  assert.equal(git("tag", "--list"), "");
});

test("prepare refuses an empty Unreleased section", () => {
  const { dir } = repo();
  const result = run(dir, "prepare", "--bump", "patch");
  assert.notEqual(result.code, 0);
  assert.match(result.out, /Unreleased/);
});

test("notes prints only the current version section", () => {
  const { dir } = repo({
    changelog: "# Changelog\n\n## 0.1.2 - 2026-10-14\n\n- Novo.\n\n## 0.1.1 - 2026-10-08\n\n- Velho.\n",
  });
  const result = run(dir, "notes");
  assert.equal(result.code, 0, result.out);
  assert.match(result.out, /Novo/);
  assert.doesNotMatch(result.out, /Velho/);
});

test("prepare keeps literal $ sequences and works when Unreleased is the last section", () => {
  const { dir } = repo({ changelog: "# Changelog\n\n## Unreleased\n\n- Custo $& e $$ preservados.\n" });
  const result = run(dir, "prepare", "--bump", "minor", "--date", "2026-10-15");
  assert.equal(result.code, 0, result.out);
  assert.match(readFileSync(join(dir, "CHANGELOG.md"), "utf8"), /## 0\.2\.0 - 2026-10-15\n\n- Custo \$& e \$\$ preservados\./);
});

test("prepare requires the --bump flag", () => {
  const { dir } = repo({ changelog: "# Changelog\n\n## Unreleased\n\n- X.\n\n## 0.1.2 - 2026-10-14\n\n- Y.\n" });
  assert.notEqual(run(dir, "prepare", "patch").code, 0);
});

test("check --publish sees an annotated tag on another commit", () => {
  const { dir, git } = repo();
  git("tag", "-a", "v0.1.2", "-m", "release");
  writeFileSync(join(dir, "y.txt"), "novo\n");
  git("add", ".");
  git("commit", "-qm", "next");
  assert.notEqual(run(dir, "check", "--publish").code, 0);
});

test("check passes on staging after the version was released from a main merge commit", () => {
  const { dir, git } = repo();
  git("checkout", "-qb", "main-release");
  git("commit", "--allow-empty", "-qm", "merge staging into main");
  git("tag", "v0.1.2");
  git("checkout", "-q", "main");
  writeFileSync(join(dir, "z.txt"), "staging segue\n");
  git("add", ".");
  git("commit", "-qm", "staging work");
  const result = run(dir, "check");
  assert.equal(result.code, 0, result.out);
  assert.match(result.out, /released/);
});

test("prepare joins changes/ notes into the version and deletes them", () => {
  const { dir } = repo();
  mkdirSync(join(dir, "changes"));
  writeFileSync(join(dir, "changes", "12-audit.md"), "### Fixed\n\n- Audit respeita o nível.\n");
  writeFileSync(join(dir, "changes", "9-gate.md"), "### Changed\n\n- Gate só para no vermelho.\n\n### Fixed\n\n- Push sem prompt.\n");
  writeFileSync(join(dir, "changes", "15-plain.md"), "- Nota sem seção.\n");
  writeFileSync(join(dir, "changes", ".gitkeep"), "");
  const result = run(dir, "prepare", "--bump", "minor", "--date", "2026-10-22");
  assert.equal(result.code, 0, result.out);
  const changelog = readFileSync(join(dir, "CHANGELOG.md"), "utf8");
  assert.match(
    changelog,
    /## 0\.2\.0 - 2026-10-22\n\n- Nota sem seção\.\n\n### Changed\n\n- Gate só para no vermelho\.\n\n### Fixed\n\n- Push sem prompt\.\n- Audit respeita o nível\.\n\n## 0\.1\.2 - 2026-10-14/,
  );
  assert.equal(existsSync(join(dir, "changes", "12-audit.md")), false);
  assert.equal(existsSync(join(dir, "changes", "9-gate.md")), false);
  assert.equal(existsSync(join(dir, "changes", ".gitkeep")), true);
  assert.equal(run(dir, "check").code, 0);
});

test("prepare refuses when there are no notes in changes/ or Unreleased", () => {
  const { dir } = repo();
  mkdirSync(join(dir, "changes"));
  const result = run(dir, "prepare", "--bump", "patch");
  assert.notEqual(result.code, 0);
  assert.match(result.out, /changes\//);
});
