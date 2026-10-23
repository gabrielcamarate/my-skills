#!/usr/bin/env python3
"""Measure delivery time from GitHub Actions runs. Read-only: only `gh api` GETs.

  python3 scripts/delivery-time.py promotion --pr <N> [--comment <issue>]
  python3 scripts/delivery-time.py task --pr <N> [--comment <issue>]

promotion (PR staging -> main): heavy suite on the promoted SHA, promotion check,
merge, main CI, production deploy; totals (a) staging push -> deploy and (b)
promotion merge -> deploy. task (PR -> staging): open -> merge, check duration,
check runs (cancelled included) and pushes. A missing stage is "ausente", never 0.
A cancelled run is counted but never timed. --comment only prints the command.
"""

import argparse
from datetime import datetime
import json
import subprocess
import sys
from urllib.parse import urlencode

# --- Configuração do projeto: nome do workflow (ou arquivo .yml), evento e branch (None = qualquer).
# main_ci é o workflow do push na main; deploy, o que publica em produção. Ajuste aos nomes do projeto.
REPOSITORY = "__OWNER__/__REPO__"
STAGES = {
    "heavy": {"workflow": "Staging Heavy Quality", "event": "push", "branch": "staging"},
    "check": {"workflow": "Pull Request Quality", "event": "pull_request", "branch": None},
    "main_ci": {"workflow": "CI", "event": "push", "branch": "main"},
    "deploy": {"workflow": "Deploy production", "event": None, "branch": "main"},
}
# --- Fim da configuração.

MISSING = "ausente"


def gh_api(path):
    result = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/{path}"],
                            capture_output=True, text=True, check=True, timeout=60)
    return json.loads(result.stdout)


def when(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else None


def clock(moment):
    return moment.strftime("%Y-%m-%d %H:%M:%S UTC") if moment else MISSING


def span(start, end):
    if not (start and end) or end < start:
        return MISSING
    seconds = int((end - start).total_seconds())
    hours, rest = divmod(seconds, 3600)
    return f"{hours}h {rest // 60:02d}m {rest % 60:02d}s" if hours else f"{rest // 60}m {rest % 60:02d}s"


def matches(run, stage):
    rule = STAGES[stage]
    workflow = rule["workflow"]
    if workflow not in (run.get("name"), (run.get("path") or "").rsplit("/", 1)[-1]):
        return False
    return all(rule[key] in (None, run.get(field))
               for key, field in (("event", "event"), ("branch", "head_branch")))


def list_runs(**query):
    """Every page of actions/runs: other workflows on the same SHA can push a stage off page 1."""
    runs, page = [], 1
    while True:
        batch = gh_api("actions/runs?" + urlencode({**query, "per_page": 100, "page": page}))["workflow_runs"]
        runs += batch
        if len(batch) < 100:
            return runs
        page += 1


def runs_for_sha(sha):
    return list_runs(head_sha=sha) if sha else []


def pick(runs, gate=None):
    """The run that measures the stage; cancelled runs are never timed.

    Without `gate`: the first successful run (a later redeploy or re-run does not stretch the
    delivery), else the first finished one. With `gate` (merge time): the last run finished by
    then, else the first finished one.
    """
    finished = sorted((r for r in runs if r.get("status") == "completed" and r.get("conclusion") != "cancelled"),
                      key=lambda r: when(r["updated_at"]))
    gated = [r for r in finished if gate and when(r["updated_at"]) <= gate]
    green = [r for r in finished if r.get("conclusion") == "success"]
    if gated:
        return gated[-1]
    if green and not gate:
        return green[0]
    if finished:
        return finished[0]
    pending = [r for r in runs if r.get("status") != "completed"]
    return max(pending, key=lambda r: when(r["created_at"])) if pending else None


def stage_row(label, runs, gate=None):
    run = pick(runs, gate)
    cancelled = sum(r.get("conclusion") == "cancelled" for r in runs)
    count = f"{len(runs)} ({cancelled} cancelado{'s' if cancelled != 1 else ''})" if cancelled else str(len(runs))
    if not run:
        return {"label": label, "start": None, "end": None, "result": MISSING, "runs": count}
    done = run.get("status") == "completed"
    result = run.get("conclusion") if done else run.get("status")
    attempt = run.get("run_attempt") or 1
    if attempt > 1:
        result += f", tentativa {attempt}"
    # A re-run keeps the first attempt's created_at; time only the last attempt.
    start = when(run.get("run_started_at") if attempt > 1 else run["created_at"])
    return {"label": label, "start": start, "end": when(run["updated_at"]) if done else None,
            "result": result, "runs": count, "ok": done and run.get("conclusion") == "success",
            "created": when(run["created_at"])}


def table(rows):
    lines = ["| Etapa | Início | Fim | Duração | Resultado | Runs |", "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        duration = row.get("duration") or span(row["start"], row["end"])
        lines.append(f"| {row['label']} | {clock(row['start'])} | {clock(row['end'])} | {duration} "
                     f"| {row['result']} | {row['runs']} |")
    return lines


def promotion(number):
    pr = gh_api(f"pulls/{number}")
    head, merged = pr["head"]["sha"], when(pr.get("merged_at"))
    merge_sha = pr.get("merge_commit_sha") if merged else None
    staging_runs, main_runs = runs_for_sha(head), runs_for_sha(merge_sha)
    heavy = stage_row("Pesada da staging", [r for r in staging_runs if matches(r, "heavy")])
    check = stage_row("Check do PR de promoção", [r for r in staging_runs if matches(r, "check")], merged)
    merge = {"label": "Merge na main", "start": merged, "end": merged, "duration": "—" if merged else MISSING,
             "result": "merged" if merged else MISSING, "runs": "—"}
    main_ci = stage_row("CI da main", [r for r in main_runs if matches(r, "main_ci")])
    deploy = stage_row("Deploy de produção", [r for r in main_runs if matches(r, "deploy")])
    shipped = deploy["end"] if deploy.get("ok") else None
    lines = [f"## Tempo de entrega: promoção #{number}", "",
             f"SHA promovido `{head[:12]}`; merge `{merge_sha[:12] if merge_sha else MISSING}`.", "",
             *table([heavy, check, merge, main_ci, deploy]), "",
             f"- **(a) push na staging → deploy de produção:** {span(heavy.get('created'), shipped)}",
             f"- **(b) merge da promoção → deploy de produção:** {span(merged, shipped)}", "",
             "Início = criação do run (inclui fila) ou, numa nova tentativa, o início dela; "
             "push na staging = criação da pesada no SHA promovido. "
             "Runs cancelados contam em Runs e ficam fora da duração; a espera pelo OK de Gabriel fica fora de (b)."]
    return "\n".join(lines)


def task(number):
    pr = gh_api(f"pulls/{number}")
    opened, merged = when(pr["created_at"]), when(pr.get("merged_at"))
    event = STAGES["check"]["event"]
    runs = list_runs(branch=pr["head"]["ref"], **({"event": event} if event else {}))
    runs = [r for r in runs if matches(r, "check") and when(r["created_at"]) >= opened
            and (merged is None or when(r["created_at"]) <= merged)]
    check = stage_row("Check do PR", runs, merged)
    life = {"label": "Abertura → merge", "start": opened, "end": merged,
            "result": "merged" if merged else "não mergeado", "runs": "—"}
    pushes = len({r["head_sha"] for r in runs})
    lines = [f"## Tempo de entrega: tarefa #{number}", "", *table([life, check]), "",
             f"- **Runs do check:** {check['runs']}", f"- **Pushes:** {pushes if runs else MISSING}", "",
             "Pushes = SHAs distintos com run do check. Runs cancelados contam e ficam fora da duração."]
    return "\n".join(lines)


def main(argv=None):
    global REPOSITORY
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("promotion", "task"))
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--repo", default=REPOSITORY, help="owner/repo (padrão: REPOSITORY)")
    parser.add_argument("--comment", type=int, metavar="ISSUE", help="imprime o comando gh issue comment")
    args = parser.parse_args(argv)
    REPOSITORY = args.repo
    try:
        report = (promotion if args.mode == "promotion" else task)(args.pr)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
        print(f"delivery-time: falha ao ler a API: {exc}", file=sys.stderr)
        return 1
    if args.comment:
        print(f"gh issue comment {args.comment} --repo {REPOSITORY} --body-file - <<'EOF'\n{report}\nEOF")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
