import contextlib
import copy
import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("delivery_time", HERE.parent / "delivery-time.py")
delivery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delivery)
# Recorded `gh api` answers (trimmed): my-finances 0.29.0 (#199) and xlondz v0.22.0 (#567).
FIXTURES = HERE / "fixtures" / "delivery-time"


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


def rows(report):
    return {line.split(" | ")[0].lstrip("| "): line.split(" | ") for line in report.splitlines()
            if line.startswith("| ") and not line.startswith("| Etapa") and not line.startswith("| ---")}


class DeliveryTimeTest(unittest.TestCase):
    def run_cli(self, data, *argv):
        def api(path):
            self.assertIn(path, data["responses"], f"unrecorded request: {path}")
            return copy.deepcopy(data["responses"][path])
        out = io.StringIO()
        with mock.patch.object(delivery, "gh_api", api), mock.patch.object(delivery, "STAGES", data["stages"]), \
                mock.patch.object(delivery, "REPOSITORY", data["repository"]), \
                mock.patch.object(delivery.subprocess, "run", side_effect=AssertionError("network")), \
                contextlib.redirect_stdout(out):
            code = delivery.main(list(argv))
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_promotion_stages_and_totals_my_finances(self):
        report = self.run_cli(fixture("my-finances-promotion-199"), "promotion", "--pr", "199")
        table = rows(report)
        self.assertEqual(table["Pesada da staging"][1:4],
                         ["2026-10-22 03:15:32 UTC", "2026-10-22 03:27:03 UTC", "11m 31s"])
        self.assertEqual(table["Check do PR de promoção"][3:5], ["22m 47s", "success, tentativa 2"])
        self.assertEqual(table["Merge na main"][1], "2026-10-22 03:38:51 UTC")
        self.assertEqual(table["CI da main"][3], "8m 16s")
        self.assertEqual(table["Deploy de produção"][1:4],
                         ["2026-10-22 03:47:13 UTC", "2026-10-22 03:48:35 UTC", "1m 22s"])
        self.assertIn("**(a) push na staging → deploy de produção:** 33m 03s", report)
        self.assertIn("**(b) merge da promoção → deploy de produção:** 9m 44s", report)

    def test_promotion_stages_and_totals_xlondz_with_one_workflow_name(self):
        report = self.run_cli(fixture("xlondz-promotion-567"), "promotion", "--pr", "567")
        table = rows(report)
        self.assertEqual(table["Pesada da staging"][3], "9m 35s")
        # The second PR run started after the merge: counted, but not the gate.
        self.assertEqual([table["Check do PR de promoção"][i] for i in (2, 3, 5)],
                         ["2026-10-20 21:50:29 UTC", "9m 02s", "2 |"])
        self.assertEqual(table["CI da main"][3], "9m 13s")
        self.assertEqual(table["Deploy de produção"][3], "1m 40s")
        self.assertIn("**(a) push na staging → deploy de produção:** 22m 48s", report)
        self.assertIn("**(b) merge da promoção → deploy de produção:** 10m 58s", report)

    def test_cancelled_run_is_counted_and_not_timed(self):
        data = fixture("my-finances-promotion-199")
        runs = data["responses"]["actions/runs?head_sha=1b9e170f1588b9da70cd3e9bc5cdd79b7545b21c&per_page=100"]
        deploy = next(r for r in runs["workflow_runs"] if r["name"] == "Deploy")
        runs["workflow_runs"].append({**deploy, "id": 1, "conclusion": "cancelled", "updated_at": "2026-10-22T05:00:00Z"})
        table = rows(self.run_cli(data, "promotion", "--pr", "199"))
        self.assertEqual(table["Deploy de produção"][3], "1m 22s")
        self.assertEqual(table["Deploy de produção"][5], "2 (1 cancelado) |")

    def test_task_counts_cancelled_runs_and_pushes(self):
        for name, number, life, check in (("my-finances-task-209", "209", "3m 16s", "0m 38s"),
                                          ("xlondz-task-651", "651", "1h 34m 15s", "1m 34s")):
            with self.subTest(name=name):
                report = self.run_cli(fixture(name), "task", "--pr", number)
                table = rows(report)
                self.assertEqual(table["Abertura → merge"][3], life)
                self.assertEqual(table["Check do PR"][3:5], [check, "success"])
                self.assertIn("**Runs do check:** 2 (1 cancelado)", report)
                self.assertIn("**Pushes:** 1", report)

    def test_missing_stage_is_absent_never_zero(self):
        data = fixture("my-finances-promotion-199")
        path = "actions/runs?head_sha=1b9e170f1588b9da70cd3e9bc5cdd79b7545b21c&per_page=100"
        data["responses"][path]["workflow_runs"] = [
            r for r in data["responses"][path]["workflow_runs"] if r["name"] != "Deploy"]
        report = self.run_cli(data, "promotion", "--pr", "199")
        self.assertEqual(rows(report)["Deploy de produção"][1:5], ["ausente"] * 4)
        self.assertIn("**(a) push na staging → deploy de produção:** ausente", report)
        self.assertIn("**(b) merge da promoção → deploy de produção:** ausente", report)
        self.assertNotIn("0m 00s", report)

    def test_failed_deploy_leaves_totals_absent(self):
        data = fixture("xlondz-promotion-567")
        path = "actions/runs?head_sha=54d78b2966a6c2aa47520558b80d5123f25debe6&per_page=100"
        for run in data["responses"][path]["workflow_runs"]:
            if run["name"] == "Deploy production":
                run["conclusion"] = "failure"
        report = self.run_cli(data, "promotion", "--pr", "567")
        self.assertEqual(rows(report)["Deploy de produção"][4], "failure")
        self.assertIn("**(b) merge da promoção → deploy de produção:** ausente", report)

    def test_comment_only_prints_the_command(self):
        out = self.run_cli(fixture("my-finances-task-209"), "task", "--pr", "209", "--comment", "208")
        self.assertTrue(out.startswith("gh issue comment 208 --repo camaratetech/my-finances --body-file - <<'EOF'\n"))
        self.assertIn("## Tempo de entrega: tarefa #209", out)
        self.assertTrue(out.rstrip().endswith("EOF"))

    def test_gh_api_only_reads(self):
        done = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with mock.patch.object(delivery.subprocess, "run", return_value=done) as run:
            delivery.gh_api("pulls/1")
        argv = run.call_args.args[0]
        self.assertEqual(argv[:2], ["gh", "api"])
        self.assertFalse({"-X", "--method", "-f", "-F", "--field", "--input"} & set(argv))


if __name__ == "__main__":
    unittest.main()
