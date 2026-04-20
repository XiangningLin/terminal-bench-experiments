#!/usr/bin/env python3
"""
Check ALL 28 agent+model combos across ALL benchmarks in Supabase.
Not limited to existing config files — checks every possible combination.

Usage:
    source .env
    .venv/bin/python3 scripts/check_all_combos.py
    .venv/bin/python3 scripts/check_all_combos.py --benchmark aime
    .venv/bin/python3 scripts/check_all_combos.py --incomplete-only
"""

import argparse
import os
from collections import defaultdict

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# All 28 combos
ALL_COMBOS = [
    ("terminus-2", "gpt-5.4"),
    ("codex", "gpt-5.4"),
    ("terminus-2", "gpt-5-mini"),
    ("codex", "gpt-5-mini"),
    ("terminus-2", "gpt-5-nano"),
    ("codex", "gpt-5-nano"),
    ("terminus-2", "claude-haiku-4-5-20251001"),
    ("claude-code", "claude-haiku-4-5-20251001"),
    ("terminus-2", "claude-sonnet-4-6"),
    ("claude-code", "claude-sonnet-4-6"),
    ("terminus-2", "claude-opus-4-6"),
    ("claude-code", "claude-opus-4-6"),
    ("terminus-2", "gemini-3.1-pro-preview"),
    ("gemini-cli", "gemini-3.1-pro-preview"),
    ("terminus-2", "gemini-3-flash-preview"),
    ("gemini-cli", "gemini-3-flash-preview"),
    ("terminus-2", "deepseek-reasoner"),
    ("claude-code", "deepseek-chat"),
    ("terminus-2", "kimi-k2.5"),
    ("claude-code", "kimi-k2.5"),
    ("terminus-2", "MiniMax-M2.5"),
    ("claude-code", "MiniMax-M2.5"),
    ("terminus-2", "glm-5"),
    ("claude-code", "glm-5"),
    ("terminus-2", "mimo-v2-pro"),
    ("claude-code", "mimo-v2-pro"),
    ("terminus-2", "qwen3-max"),
    ("qwen-coder", "qwen3-max"),
]

# model name variations in job_name vs Supabase
MODEL_ALIASES = {
    "MiniMax-M2.5": "minimax-m2.5",
}

BENCHMARKS = {
    "aime": {"phase3": 5, "phase4": 54},
    "arc-agi-2": {"phase3": 45, "phase4": 450},
    "compilebench": {"phase3": 1, "phase4": 13},
    "gpqa-diamond": {"phase2": 10, "phase3": 90, "phase4": 890},
    "humanevalfix": {"phase3": 75},
    "ineqmath": {"phase2": 1, "phase3": 9, "phase4": 90},
    "labbench": {"phase2": 10, "phase3": 90, "phase4": 810},
    "mmau": {"phase2": 10, "phase3": 90, "phase4": 900},
    "qcircuitbench": {"phase2": 1, "phase4": 25},
    "swe-lancer": {"phase2": 2, "phase3": 18, "phase4": 180},
}


def check_job(client, job_name, expected_tasks, min_trials=3):
    """Check a single job in Supabase."""
    try:
        jobs = client.table("job").select("id").eq("job_name", job_name).execute()
    except Exception as e:
        return 0, 0, f"QUERY_FAIL: {e}"

    if not jobs.data:
        return 0, 0, "NO_JOB"

    task_ok = defaultdict(int)
    total_trials = 0
    for job in jobs.data:
        try:
            trials = (
                client.table("trial")
                .select("task_checksum,reward")
                .eq("job_id", job["id"])
                .not_.is_("reward", "null")
                .execute()
            )
            total_trials += len(trials.data)
            for t in trials.data:
                tc = t.get("task_checksum", "")
                if tc:
                    task_ok[tc] += 1
        except:
            pass

    tasks_done = sum(1 for c in task_ok.values() if c >= min_trials)

    if tasks_done >= expected_tasks and expected_tasks > 0:
        return tasks_done, total_trials, "DONE"
    elif tasks_done > 0:
        return tasks_done, total_trials, "PARTIAL"
    else:
        return tasks_done, total_trials, "NEED"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", help="Filter by benchmark")
    parser.add_argument("--combo", help="Filter by combo (e.g., 'terminus-2+gpt-5.4')")
    parser.add_argument("--phase", help="Filter by phase")
    parser.add_argument("--incomplete-only", action="store_true")
    parser.add_argument("--min-trials", type=int, default=3)
    args = parser.parse_args()

    client = create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"]
    )

    results = []
    total_checks = 0

    for bench, phases in sorted(BENCHMARKS.items()):
        if args.benchmark and bench != args.benchmark:
            continue

        for phase, expected in sorted(phases.items()):
            if args.phase and phase != args.phase:
                continue

            for agent, model in ALL_COMBOS:
                if args.combo:
                    combo_str = f"{agent}+{model}"
                    if args.combo.lower() not in combo_str.lower():
                        continue

                # Build job_name using the alias for job naming
                model_in_name = MODEL_ALIASES.get(model, model)
                job_name = f"{bench}__{agent}__{model_in_name}__batch1__{phase}"

                tasks_done, total_trials, status = check_job(
                    client, job_name, expected, args.min_trials
                )
                results.append(
                    (bench, agent, model, phase, tasks_done, expected, total_trials, status)
                )

                total_checks += 1
                if total_checks % 50 == 0:
                    print(f"  Checked {total_checks}...", flush=True)

    # Summary per benchmark
    print()
    print("=" * 70)
    bench_stats = defaultdict(lambda: {"done": 0, "partial": 0, "need": 0})
    for bench, agent, model, phase, td, exp, tt, status in results:
        if status == "DONE":
            bench_stats[bench]["done"] += 1
        elif status == "PARTIAL":
            bench_stats[bench]["partial"] += 1
        else:
            bench_stats[bench]["need"] += 1

    total_done = sum(s["done"] for s in bench_stats.values())
    total_partial = sum(s["partial"] for s in bench_stats.values())
    total_need = sum(s["need"] for s in bench_stats.values())
    print(f"DONE: {total_done} | PARTIAL: {total_partial} | NEED: {total_need} | Total: {len(results)}")
    print("=" * 70)
    print()

    print(f"{'Benchmark':<18} {'Done':>6} {'Partial':>8} {'Need':>6}")
    print("-" * 40)
    for bench in sorted(bench_stats):
        s = bench_stats[bench]
        print(f"{bench:<18} {s['done']:>6} {s['partial']:>8} {s['need']:>6}")
    print()

    # Incomplete details
    incomplete = [r for r in results if r[7] != "DONE"]
    if incomplete and (args.incomplete_only or not args.benchmark):
        print("=== Incomplete ===")
        for bench, agent, model, phase, td, exp, tt, status in incomplete:
            if args.incomplete_only or status != "DONE":
                print(f"  {status:12s} {bench} {agent}+{model} {phase} ({td}/{exp} tasks, {tt} trials)")


if __name__ == "__main__":
    main()
