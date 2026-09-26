import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("skillctl", Path(__file__).resolve().parents[1] / "scripts/skillctl.py")
ctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ctl)


class LinksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def rows(self):
        return ctl.plan(ctl.ROOT, self.home, ["codex", "claude"])

    def test_install_idempotent_and_round_trip(self):
        ctl.install(self.rows())
        rows = self.rows()
        self.assertEqual(len(rows), len(ctl.inventory()) * 2)
        self.assertTrue(all(r["status"] == "linked" for r in rows))
        ctl.install(rows)
        ctl.uninstall(self.rows())
        self.assertTrue(all(r["status"] == "missing" for r in self.rows()))
        self.assertTrue((ctl.ROOT / "skills" / ctl.inventory()[0] / "SKILL.md").exists())

    def test_conflict_prevents_any_install(self):
        rows = self.rows()
        conflict = Path(rows[-1]["link"])
        conflict.mkdir(parents=True)
        (conflict / "user.txt").write_text("preserve")
        with self.assertRaises(ValueError):
            ctl.install(self.rows())
        self.assertFalse(Path(rows[0]["link"]).exists())
        self.assertEqual((conflict / "user.txt").read_text(), "preserve")

    def test_foreign_and_broken_links_preserved(self):
        ctl.install(self.rows())
        rows = self.rows()
        foreign = Path(rows[0]["link"])
        foreign.unlink()
        foreign.symlink_to(self.home / "unrelated-missing")
        ctl.uninstall(self.rows())
        self.assertTrue(foreign.is_symlink())
        self.assertEqual(foreign.readlink(), self.home / "unrelated-missing")

    def test_mid_install_collision_rolls_back_owned_links(self):
        rows = self.rows()
        collision = Path(rows[-1]["link"])
        collision.mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            ctl.install(rows)
        self.assertTrue(collision.is_dir())
        self.assertFalse(Path(rows[0]["link"]).is_symlink())

    def retired(self):
        return ctl.retired_plan(ctl.ROOT, self.home, ["codex", "claude"])

    def seed_old_links(self):
        for row in self.retired():
            dst = Path(row["link"])
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(row["source"])

    def test_migration_removes_only_owned_old_links_after_install(self):
        self.seed_old_links()
        foreign = Path(self.retired()[-1]["link"])
        foreign.unlink()
        foreign.symlink_to(self.home / "user-owned-source")
        ctl.migrate(self.rows(), self.retired())
        self.assertTrue(all(r["status"] == "linked" for r in self.rows()))
        self.assertTrue(all(r["status"] != "linked" for r in self.retired()))
        self.assertTrue(foreign.is_symlink())
        self.assertEqual(foreign.readlink(), self.home / "user-owned-source")
        ctl.migrate(self.rows(), self.retired())
        self.assertTrue(foreign.is_symlink())

    def test_migration_conflict_preserves_all_old_links(self):
        self.seed_old_links()
        destination = Path(self.rows()[-1]["link"])
        destination.mkdir(parents=True)
        with self.assertRaises(ValueError):
            ctl.migrate(self.rows(), self.retired())
        self.assertTrue(all(r["status"] == "linked" for r in self.retired()))
        self.assertFalse(Path(self.rows()[0]["link"]).is_symlink())

    def test_migration_mid_install_failure_preserves_old_links(self):
        self.seed_old_links()
        rows = self.rows()
        Path(rows[-1]["link"]).mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            ctl.migrate(rows, self.retired())
        self.assertTrue(all(r["status"] == "linked" for r in self.retired()))
        self.assertFalse(Path(rows[0]["link"]).is_symlink())


if __name__ == "__main__":
    unittest.main()
