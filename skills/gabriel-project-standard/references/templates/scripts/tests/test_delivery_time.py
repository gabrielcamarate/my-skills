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
# Recorded `gh api` answers, trimmed to the fields used and anonymized (owner, SHAs, ids, branches):
# my-finances 0.29.0 (#199) and xlondz v0.22.0 (#567), task PRs my-finances #209 and xlondz #651.
FIXTURES = HERE / "fixtures" / "delivery-time"


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


def rows(report):
    return {cells[0]: cells for cells in ([c.strip() for c in line.strip("| ").split(" | ")]
                                          for line in report.splitlines() if line.startswith("| "))
            if cells[0] not in ("Etapa", "---")}


def main_runs(data, number):
    """The recorded runs on the promotion's merge commit."""
    sha = data["responses"][f"pulls/{number}"]["merge_commit_sha"]
    return next(v["workflow_runs"] for k, v in data["responses"].items() if sha in k)


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
        # Attempt 1 failed and was re-run after the heavy suite: time only the last attempt.
        self.assertEqual(table["Check do PR de promoção"][1:5],
                         ["2026-10-22 03:27:19 UTC", "2026-10-22 03:38:22 UTC", "11m 03s", "success, tentativa 2"])
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
                         ["2026-10-20 21:50:29 UTC", "9m 02s", "2"])
        self.assertEqual(table["CI da main"][3], "9m 13s")
        self.assertEqual(table["Deploy de produção"][3], "1m 40s")
        self.assertIn("**(a) push na staging → deploy de produção:** 22m 48s", report)
        self.assertIn("**(b) merge da promoção → deploy de produção:** 10m 58s", report)

    def test_cancelled_run_is_counted_and_not_timed(self):
        data = fixture("my-finances-promotion-199")
        runs = main_runs(data, 199)
        deploy = next(r for r in runs if r["name"] == "Deploy")
        runs.append({**deploy, "id": 1, "conclusion": "cancelled", "updated_at": "2026-10-22T05:00:00Z"})
        table = rows(self.run_cli(data, "promotion", "--pr", "199"))
        self.assertEqual(table["Deploy de produção"][3], "1m 22s")
        self.assertEqual(table["Deploy de produção"][5], "2 (1 cancelado)")

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
        runs = main_runs(data, 199)
        runs[:] = [r for r in runs if r["name"] != "Deploy"]
        report = self.run_cli(data, "promotion", "--pr", "199")
        self.assertEqual(rows(report)["Deploy de produção"][1:5], ["ausente"] * 4)
        self.assertIn("**(a) push na staging → deploy de produção:** ausente", report)
        self.assertIn("**(b) merge da promoção → deploy de produção:** ausente", report)
        self.assertNotIn("0m 00s", report)

    def test_failed_deploy_leaves_totals_absent(self):
        data = fixture("xlondz-promotion-567")
        for run in main_runs(data, 567):
            if run["name"] == "Deploy production":
                run["conclusion"] = "failure"
        report = self.run_cli(data, "promotion", "--pr", "567")
        self.assertEqual(rows(report)["Deploy de produção"][4], "failure")
        self.assertIn("**(b) merge da promoção → deploy de produção:** ausente", report)

    def test_comment_only_prints_the_command(self):
        out = self.run_cli(fixture("my-finances-task-209"), "task", "--pr", "209", "--comment", "208")
        self.assertTrue(out.startswith("gh issue comment 208 --repo example/my-finances --body-file - <<'EOF'\n"))
        self.assertIn("## Tempo de entrega: tarefa #209", out)
        self.assertTrue(out.rstrip().endswith("EOF"))

    def test_later_redeploy_does_not_stretch_the_delivery(self):
        data = fixture("xlondz-promotion-567")
        runs = main_runs(data, 567)
        deploy = next(r for r in runs if r["name"] == "Deploy production")
        runs.insert(0, {**deploy, "id": 2, "event": "workflow_dispatch", "created_at": "2026-10-25T10:00:00Z",
                        "run_started_at": "2026-10-25T10:00:00Z", "updated_at": "2026-10-25T10:02:00Z"})
        report = self.run_cli(data, "promotion", "--pr", "567")
        self.assertEqual(rows(report)["Deploy de produção"][3], "1m 40s")
        self.assertIn("**(b) merge da promoção → deploy de produção:** 10m 58s", report)

    def test_stages_beyond_the_first_page_are_found(self):
        data = fixture("my-finances-promotion-199")
        sha = data["responses"]["pulls/199"]["merge_commit_sha"]
        first = next(k for k in data["responses"] if sha in k)
        noise = {"id": 3, "name": "Dependabot update", "path": "dynamic/dependabot/dependabot-updates",
                 "event": "dynamic", "head_branch": "main", "head_sha": sha, "status": "completed",
                 "conclusion": "success", "created_at": "2026-10-23T00:00:00Z",
                 "run_started_at": "2026-10-23T00:00:00Z", "updated_at": "2026-10-23T00:01:00Z", "run_attempt": 1}
        data["responses"][first.replace("&page=1", "&page=2")] = data["responses"][first]
        data["responses"][first] = {"workflow_runs": [noise] * 100}
        report = self.run_cli(data, "promotion", "--pr", "199")
        self.assertEqual(rows(report)["Deploy de produção"][3], "1m 22s")
        self.assertIn("**(b) merge da promoção → deploy de produção:** 9m 44s", report)

    def test_check_finished_after_merge_is_shown_not_absent(self):
        data = fixture("my-finances-task-209")
        runs = next(v["workflow_runs"] for k, v in data["responses"].items() if k.startswith("actions/runs"))
        for run in runs:
            if run["conclusion"] == "success":
                run["updated_at"] = "2026-10-22T22:40:00Z"
        table = rows(self.run_cli(data, "task", "--pr", "209"))
        self.assertEqual(table["Check do PR"][2:5], ["2026-10-22 22:40:00 UTC", "3m 17s", "success"])

    def test_unmerged_promotion_with_running_check(self):
        data = fixture("my-finances-promotion-199")
        data["responses"]["pulls/199"].update(merged_at=None, merge_commit_sha=None)
        staging = next(v["workflow_runs"] for k, v in data["responses"].items() if "head_sha=" in k)
        for run in staging:
            if run["name"] == "Pull Request Quality":
                run.update(status="in_progress", conclusion=None)
        report = self.run_cli(data, "promotion", "--pr", "199")
        table = rows(report)
        self.assertEqual(table["Check do PR de promoção"][2:5], ["ausente", "ausente", "in_progress, tentativa 2"])
        self.assertEqual(table["Merge na main"][1], "ausente")
        self.assertEqual(table["Deploy de produção"][1:5], ["ausente"] * 4)
        self.assertIn("**(a) push na staging → deploy de produção:** ausente", report)

    def test_gh_api_only_reads(self):
        done = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with mock.patch.object(delivery.subprocess, "run", return_value=done) as run:
            delivery.gh_api("pulls/1")
        argv = run.call_args.args[0]
        self.assertEqual(argv[:2], ["gh", "api"])
        self.assertFalse({"-X", "--method", "-f", "-F", "--field", "--input"} & set(argv))


if __name__ == "__main__":
    unittest.main()
