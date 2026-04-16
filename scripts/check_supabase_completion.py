#!/usr/bin/env python3
"""
Check job completion status in Supabase.

For each job config, queries Supabase to count how many tasks have >= 3 successful
trials across ALL job_ids (handles duplicate job_ids from reruns).

Usage:
    source .env
    .venv/bin/python3 scripts/check_supabase_completion.py

    # Check only specific phase
    .venv/bin/python3 scripts/check_supabase_completion.py --phase phase2

    # Check only specific benchmark
    .venv/bin/python3 scripts/check_supabase_completion.py --benchmark mmau
"""

import argparse
import glob
import os
import sys
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


def check_completion(client, job_name, expected_tasks):
    """Check how many tasks have >= 3 successful trials in Supabase."""
    try:
        jobs = client.table("job").select("id").eq("job_name", job_name).execute()
    except Exception as e:
        return 0, f"QUERY_FAIL: {e}"

    if not jobs.data:
        return 0, "NO_JOB"

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
        except Exception:
            pass

    tasks_with_3 = sum(1 for c in task_ok.values() if c >= 3)

    if tasks_with_3 >= expected_tasks and expected_tasks > 0:
        status = "DONE"
    elif tasks_with_3 > 0:
        status = "PARTIAL"
    else:
        status = "NEED"

    return tasks_with_3, status


def main():
    parser = argparse.ArgumentParser(description="Check job completion in Supabase")
    parser.add_argument("--phase", help="Filter by phase (phase2, phase3, phase4)")
    parser.add_argument("--benchmark", help="Filter by benchmark name")
    parser.add_argument(
        "--config-dir",
        default="outputs/adapter_experiments/batch1/contributors/Xiangning",
        help="Path to config directory",
    )
    args = parser.parse_args()

    client = create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"]
    )

    # Collect configs
    configs = []
    for f in sorted(glob.glob(f"{args.config_dir}/**/*.yaml", recursive=True)):
        if "registries" in f or "glm-5" in f:
            continue
        with open(f) as fh:
            cfg = yaml.safe_load(fh)
        jn = cfg.get("job_name", "")
        parts = jn.split("__")
        bench = parts[0]
        phase = parts[-1]

        if args.phase and phase != args.phase:
            continue
        if args.benchmark and bench != args.benchmark:
            continue

        exp = EXPECTED_TASKS.get((bench, phase), 0)
        configs.append((jn, bench, phase, exp))

    print(f"Checking {len(configs)} jobs in Supabase...")
    print()

    results = []
    for i, (jn, bench, phase, exp) in enumerate(configs):
        tasks_with_3, status = check_completion(client, jn, exp)
        results.append((jn, phase, tasks_with_3, exp, status))

        if (i + 1) % 20 == 0:
            print(f"  Checked {i + 1}/{len(configs)}...", flush=True)

    # Summary
    done = sum(1 for r in results if r[4] == "DONE")
    partial = sum(1 for r in results if r[4] == "PARTIAL")
    need = sum(1 for r in results if r[4] in ("NEED", "NO_JOB", "QUERY_FAIL"))

    print()
    print("=" * 60)
    print(f"DONE (Supabase complete):  {done}")
    print(f"PARTIAL (some trials):     {partial}")
    print(f"NEED (no/few trials):      {need}")
    print(f"Total:                     {len(results)}")
    print("=" * 60)
    print()

    for phase in ["phase2", "phase3", "phase4"]:
        pr = [r for r in results if r[1] == phase]
        if not pr:
            continue
        pd = sum(1 for r in pr if r[4] == "DONE")
        print(f"  {phase}: {pd}/{len(pr)} done")
    print()

    # Show incomplete
    incomplete = [r for r in results if r[4] != "DONE"]
    if incomplete:
        print("=== Incomplete jobs ===")
        for jn, phase, t3, exp, status in incomplete:
            print(f"  {status:12s} {jn} ({t3}/{exp} tasks with >=3 trials)")
    else:
        print("All jobs complete!")


if __name__ == "__main__":
    main()
