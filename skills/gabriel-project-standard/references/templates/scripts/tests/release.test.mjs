// Release tooling contract: version, changelog and tag must agree, and
// preparation never touches the remote. Notes live one per PR in changes/ (Maison #411).
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const SCRIPT = fileURLToPath(new URL("../release.mjs", import.meta.url));

function repo({ version = "0.1.2", changelog = "# Changelog\n\n## 0.1.2 - 2026-10-14\n\n### Changed\n\n- Algo.\n", notes = {} } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "project-release-"));
  const git = (...args) => execFileSync("git", args, { cwd: dir, stdio: "pipe" }).toString().trim();
  git("init", "-q", "-b", "main");
  git("config", "user.email", "t@example.com");
  git("config", "user.name", "t");
  writeFileSync(join(dir, "package.json"), JSON.stringify({ name: "x", version }, null, 2) + "\n");
  writeFileSync(join(dir, "CHANGELOG.md"), changelog);
  mkdirSync(join(dir, "changes"));
  writeFileSync(join(dir, "changes", "README.md"), "# Notas\n");
  for (const [file, text] of Object.entries(notes)) writeFileSync(join(dir, "changes", file), text);
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

test("prepare joins the notes by category in issue order and deletes them", () => {
  const { dir, git } = repo({
    notes: {
      "20-cupom.md": "### Corrigido\n- Corrige cupom.\n",
      "3-busca.md": "### Adicionado\n- Busca nova.\n",
      "100-frete.md": "### Adicionado\n- Frete grátis.\n  Linha de continuação.\n",
      "7-texto.md": "- Ajuste sem categoria.\n",
    },
  });
  const result = run(dir, "prepare", "--bump", "patch", "--date", "2026-10-15");
  assert.equal(result.code, 0, result.out);
  assert.equal(JSON.parse(readFileSync(join(dir, "package.json"), "utf8")).version, "0.1.3");
  const changelog = readFileSync(join(dir, "CHANGELOG.md"), "utf8");
  assert.equal(
    changelog,
    "# Changelog\n\n## 0.1.3 - 2026-10-15\n\n- Ajuste sem categoria.\n\n### Adicionado\n\n- Busca nova.\n" +
      "- Frete grátis.\n  Linha de continuação.\n\n### Corrigido\n\n- Corrige cupom.\n\n" +
      "## 0.1.2 - 2026-10-14\n\n### Changed\n\n- Algo.\n",
  );
  assert.deepEqual(readdirSync(join(dir, "changes")), ["README.md"]);
  assert.equal(git("tag", "--list"), "");
  assert.equal(run(dir, "check").code, 0);
});

test("prepare refuses when changes/ has no notes", () => {
  const { dir } = repo();
  const result = run(dir, "prepare", "--bump", "patch");
  assert.notEqual(result.code, 0);
  assert.match(result.out, /changes\//);
});

test("two parallel PRs with different notes merge without conflict and both reach the release", () => {
  const { dir, git } = repo();
  for (const [branch, file, line] of [["fix/41-a", "41-a.md", "- Nota A."], ["fix/42-b", "42-b.md", "- Nota B."]]) {
    git("checkout", "-qb", branch, "main");
    writeFileSync(join(dir, "changes", file), `${line}\n`);
    git("add", ".");
    git("commit", "-qm", branch);
  }
  git("checkout", "-q", "main");
  git("merge", "-q", "--no-ff", "-m", "a", "fix/41-a");
  git("merge", "-q", "--no-ff", "-m", "b", "fix/42-b");
  const result = run(dir, "prepare", "--bump", "minor", "--date", "2026-10-15");
  assert.equal(result.code, 0, result.out);
  assert.match(readFileSync(join(dir, "CHANGELOG.md"), "utf8"), /## 0\.2\.0 - 2026-10-15\n\n- Nota A\.\n- Nota B\.\n\n## 0\.1\.2/);
});

test("check refuses an invalid note name, category or line", () => {
  for (const [file, text] of [
    ["sem-numero.md", "- X.\n"],
    ["5-x.md", "### Changed\n- X.\n"],
    ["5-x.md", "Texto solto.\n"],
    ["5-x.md", "\n"],
    ["5-x.md", "### Adicionado\n"],
    ["5-x.md", "- X.\n\n  continuação solta.\n"],
  ]) {
    const { dir } = repo({ notes: { [file]: text } });
    const result = run(dir, "check");
    assert.notEqual(result.code, 0, `${file}: ${JSON.stringify(text)}`);
    assert.match(result.out, /changes\//);
  }
});

test("check refuses notes left under '## Unreleased' in CHANGELOG.md", () => {
  const { dir } = repo({ changelog: "# Changelog\n\n## Unreleased\n\n- Esquecida.\n\n## 0.1.2 - 2026-10-14\n\n- Algo.\n" });
  const result = run(dir, "check");
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

test("prepare keeps literal $ sequences and drops an empty Unreleased heading", () => {
  const { dir } = repo({
    changelog: "# Changelog\n\n## Unreleased\n\n## 0.1.2 - 2026-10-14\n\n- Y.\n",
    notes: { "9-custo.md": "- Custo $& e $$ preservados.\n" },
  });
  const result = run(dir, "prepare", "--bump", "minor", "--date", "2026-10-15");
  assert.equal(result.code, 0, result.out);
  const changelog = readFileSync(join(dir, "CHANGELOG.md"), "utf8");
  assert.match(changelog, /^# Changelog\n\n## 0\.2\.0 - 2026-10-15\n\n- Custo \$& e \$\$ preservados\.\n\n## 0\.1\.2/);
  assert.doesNotMatch(changelog, /Unreleased/);
});

test("prepare requires the --bump flag", () => {
  const { dir } = repo({ notes: { "1-x.md": "- X.\n" } });
  assert.notEqual(run(dir, "prepare", "patch").code, 0);
  assert.equal(existsSync(join(dir, "changes", "1-x.md")), true);
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
