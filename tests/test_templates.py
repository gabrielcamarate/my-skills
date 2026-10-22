import subprocess
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/gabriel-project-standard/references/templates/scripts"


class TemplateScriptTests(unittest.TestCase):
    def run_script(self, name):
        result = subprocess.run(["bash", str(SCRIPTS / name)], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ensure_node(self):
        self.run_script("test-ensure-node.sh")


if __name__ == "__main__":
    unittest.main()
