#!/usr/bin/env python3
"""
Check which benchmarks/combos still need trials by querying Supabase.

For each job_name under a given username, counts how many tasks have >= 3
successful trials (with non-null reward). Reports gaps that need rerunning.

Usage:
    source .env
    .venv/bin/python3 scripts/check_benchmark_gaps.py

    # Check specific benchmark
    .venv/bin/python3 scripts/check_benchmark_gaps.py --benchmark swe-lancer

    # Check specific phase
    .venv/bin/python3 scripts/check_benchmark_gaps.py --phase phase4

    # Show only incomplete
    .venv/bin/python3 scripts/check_benchmark_gaps.py --incomplete-only
"""

import argparse
import glob
import json
import os
from collections import defaultdict

import yaml
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

EXPECTED_TASKS = {
    ("ineqmath", "phase2"): 1, ("ineqmath", "phase3"): 9, ("ineqmath", "phase4"): 90,
    ("mmau", "phase2"): 10, ("mmau", "phase3"): 90, ("mmau", "phase4"): 900,
    ("swe-lancer", "phase2"): 2, ("swe-lancer", "phase3"): 18, ("swe-lancer", "phase4"): 180,
    ("compilebench", "phase2"): 5, ("compilebench", "phase3"): 1, ("compilebench", "phase4"): 13,
    ("qcircuitbench", "phase2"): 1, ("qcircuitbench", "phase4"): 25,
    ("aime", "phase3"): 5, ("aime", "phase4"): 54,
    ("gpqa-diamond", "phase2"): 10, ("gpqa-diamond", "phase3"): 90, ("gpqa-diamond", "phase4"): 890,
    ("labbench", "phase2"): 10, ("labbench", "phase3"): 90, ("labbench", "phase4"): 810,
    ("humanevalfix", "phase3"): 75,
    ("arc-agi-2", "phase3"): 45, ("arc-agi-2", "phase4"): 450,
}


def main():
    parser = argparse.ArgumentParser(description="Check benchmark gaps from Supabase")
    parser.add_argument("--benchmark", help="Filter by benchmark")
    parser.add_argument("--phase", help="Filter by phase")
    parser.add_argument("--incomplete-only", action="store_true", help="Only show incomplete jobs")
    parser.add_argument("--username", default="linxiangning")
    parser.add_argument(
        "--config-dir",
        default="outputs/adapter_experiments/batch1/contributors/Xiangning",
    )
    parser.add_argument("--min-trials", type=int, default=3, help="Min trials per task to count as done")
    args = parser.parse_args()

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])

    # Collect all configs
    configs = []
    for f in sorted(glob.glob(f"{args.config_dir}/**/*.yaml", recursive=True)):
        if "registries" in f or "glm-5" in f or "rerun" in f or "top100" in f:
            continue
        with open(f) as fh:
            cfg = yaml.safe_load(fh)
        jn = cfg.get("job_name", "")
        parts = jn.split("__")
        if len(parts) < 4:
            continue
        bench = parts[0]
        agent = parts[1]
        model = parts[2]
        phase = parts[-1]

        if args.benchmark and bench != args.benchmark:
            continue
        if args.phase and phase != args.phase:
            continue

        exp = EXPECTED_TASKS.get((bench, phase), 0)
        configs.append((jn, bench, agent, model, phase, exp))

    print(f"Checking {len(configs)} jobs in Supabase...")
    print()

    results = []
    for i, (jn, bench, agent, model, phase, exp) in enumerate(configs):
        try:
            jobs = client.table("job").select("id").eq("job_name", jn).execute()
        except Exception as e:
            results.append((jn, bench, agent, model, phase, 0, exp, "QUERY_FAIL"))
            continue

        if not jobs.data:
            results.append((jn, bench, agent, model, phase, 0, exp, "NO_JOB"))
            continue

        task_ok = defaultdict(int)
        for job in jobs.data:
            try:
                trials = (
                    client.table("trial")
                    .select("task_checksum,reward")
                    .eq("job_id", job["id"])
                    .not_.is_("reward", "null")
                    .execute()
                )
                for t in trials.data:
                    tc = t.get("task_checksum", "")
                    if tc:
                        task_ok[tc] += 1
            except:
                pass

        tasks_done = sum(1 for c in task_ok.values() if c >= args.min_trials)

        if tasks_done >= exp and exp > 0:
            status = "DONE"
        elif tasks_done > 0:
            status = "PARTIAL"
        else:
            status = "NEED"

        results.append((jn, bench, agent, model, phase, tasks_done, exp, status))

        if (i + 1) % 20 == 0:
            print(f"  Checked {i + 1}/{len(configs)}...", flush=True)

    # Summary
    done = sum(1 for r in results if r[7] == "DONE")
    partial = sum(1 for r in results if r[7] == "PARTIAL")
    need = sum(1 for r in results if r[7] in ("NEED", "NO_JOB", "QUERY_FAIL"))

    print()
    print("=" * 70)
    print(f"DONE: {done} | PARTIAL: {partial} | NEED: {need} | Total: {len(results)}")
    print("=" * 70)
    print()

    # Per benchmark summary
    bench_stats = defaultdict(lambda: {"done": 0, "partial": 0, "need": 0})
    for jn, bench, agent, model, phase, t_done, exp, status in results:
        if status == "DONE":
            bench_stats[bench]["done"] += 1
        elif status == "PARTIAL":
            bench_stats[bench]["partial"] += 1
        else:
            bench_stats[bench]["need"] += 1

    print(f"{'Benchmark':<18} {'Done':>6} {'Partial':>8} {'Need':>6}")
    print("-" * 40)
    for bench in sorted(bench_stats):
        s = bench_stats[bench]
        print(f"{bench:<18} {s['done']:>6} {s['partial']:>8} {s['need']:>6}")
    print()

    # Incomplete details
    incomplete = [r for r in results if r[7] != "DONE"]
    if args.incomplete_only or incomplete:
        print("=== Incomplete ===")
        for jn, bench, agent, model, phase, t_done, exp, status in incomplete:
            if args.incomplete_only or status != "DONE":
                print(f"  {status:12s} {agent}+{model} {phase} ({t_done}/{exp})")


if __name__ == "__main__":
    main()
