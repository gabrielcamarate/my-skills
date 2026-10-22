import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "slowest-tests.py"


def case(title, duration, ancestors=()):
    return {"ancestorTitles": list(ancestors), "title": title, "duration": duration, "status": "passed"}


class SlowestTestsTest(unittest.TestCase):
    def run_report(self, report, *args):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            if report is not None:
                path.write_text(json.dumps(report))
            return subprocess.run([sys.executable, str(SCRIPT), str(path), *args],
                                  capture_output=True, text=True, timeout=30, cwd=tmp)

    def test_lists_five_slowest_across_files_in_order(self):
        report = {"testResults": [
            {"name": "/repo/lib/a.test.ts", "assertionResults": [case("fast", 3), case("slowest", 4800, ["media"]), case("none", None)]},
            {"name": "/repo/lib/b.test.ts", "assertionResults": [case(f"t{ms}", ms) for ms in (10, 900, 50, 2100, 700, 20)]},
        ]}
        result = self.run_report(report)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line for line in result.stdout.splitlines() if " ms " in line]
        self.assertEqual(len(rows), 5)
        self.assertIn("4800 ms", rows[0])
        self.assertIn("media > slowest", rows[0])
        self.assertIn("a.test.ts", rows[0])
        self.assertEqual([r.split(" ms ")[0].strip() for r in rows], ["4800", "2100", "900", "700", "50"])

    def test_missing_report_is_reported_without_failing(self):
        result = self.run_report(None)
        self.assertEqual(result.returncode, 0)
        self.assertIn("no test report", result.stderr)


if __name__ == "__main__":
    unittest.main()
