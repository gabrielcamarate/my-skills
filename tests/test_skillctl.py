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
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(r["status"] == "linked" for r in rows))
        ctl.install(rows)
        ctl.uninstall(self.rows())
        self.assertTrue(all(r["status"] == "missing" for r in self.rows()))
        self.assertTrue((ctl.ROOT / "skills/gabriel-triage/SKILL.md").exists())

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


if __name__ == "__main__":
    unittest.main()
