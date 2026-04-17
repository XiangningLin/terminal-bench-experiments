#!/usr/bin/env python3
"""
Quick status check for running experiments.

Usage:
    source .env
    .venv/bin/python3 scripts/status.py
"""

import glob
import json
import os
import subprocess
import time
from collections import Counter, defaultdict


def get_running_jobs():
    running = set()
    ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    for line in ps.stdout.split("\n"):
        if "run_job" in line and "grep" not in line:
            for part in line.split():
                if "Xiangning" in part or "job-configs" in part:
                    running.add(part.split("/")[-1].replace(".yaml", ""))
    return running


def count_active_sandboxes(running):
    active = 0
    for jd in glob.glob("jobs/*"):
        if not os.path.isdir(jd):
            continue
        name = os.path.basename(jd)
        if not any(name in r for r in running):
            continue
        for t in os.listdir(jd):
            tp = os.path.join(jd, t)
            if os.path.isdir(tp) and not os.path.exists(
                os.path.join(tp, "result.json")
            ):
                active += 1
    return active


def recent_errors(minutes=5):
    now = time.time()
    recent = Counter()
    for jd in glob.glob("jobs/*"):
        if not os.path.isdir(jd):
            continue
        for t in os.listdir(jd):
            rp = os.path.join(jd, t, "result.json")
            if not os.path.exists(rp):
                continue
            if os.path.getmtime(rp) < now - minutes * 60:
                continue
            try:
                with open(rp) as f:
                    r = json.load(f)
                exc = r.get("exception_info")
                if not exc:
                    recent["OK"] += 1
                else:
                    recent[exc.get("exception_type", "")] += 1
            except:
                pass
    return recent


def benchmark_progress():
    stats = defaultdict(lambda: defaultdict(lambda: {"ok": 0, "fail": 0, "prog": 0}))
    for jd in glob.glob("jobs/*"):
        if not os.path.isdir(jd):
            continue
        name = os.path.basename(jd)
        parts = name.split("__")
        bench = parts[0]
        phase = parts[-1]
        for t in os.listdir(jd):
            tp = os.path.join(jd, t)
            if not os.path.isdir(tp):
                continue
            rp = os.path.join(tp, "result.json")
            if os.path.exists(rp):
                try:
                    with open(rp) as f:
                        r = json.load(f)
                    if r.get("exception_info"):
                        stats[bench][phase]["fail"] += 1
                    else:
                        stats[bench][phase]["ok"] += 1
                except:
                    stats[bench][phase]["fail"] += 1
            else:
                stats[bench][phase]["prog"] += 1
    return stats


def db_errors():
    uploads = db_err = 0
    for d in glob.glob("/tmp/job-logs-*"):
        for log in glob.glob(f"{d}/*.log"):
            try:
                with open(log) as f:
                    c = f.read()
                uploads += c.count("Successfully uploaded")
                db_err += c.count("Failed to insert trial")
            except:
                pass
    return uploads, db_err


def main():
    running = get_running_jobs()
    active = count_active_sandboxes(running)

    print(f"=== Processes: {len(running)} | Active sandbox: {active} ===")
    print()

    # Recent errors
    recent = recent_errors(5)
    print("=== Last 5 min ===")
    for k, v in recent.most_common():
        print(f"  {k}: {v}")
    print()

    # Benchmark progress
    stats = benchmark_progress()
    print(
        f'{"Benchmark":<18} {"Phase":>6} {"OK":>7} {"Fail":>7} {"InProg":>7}'
    )
    print("-" * 50)
    total_ok = total_fail = total_prog = 0
    for bench in sorted(stats):
        for phase in sorted(stats[bench]):
            s = stats[bench][phase]
            print(
                f'{bench:<18} {phase:>6} {s["ok"]:>7} {s["fail"]:>7} {s["prog"]:>7}'
            )
            total_ok += s["ok"]
            total_fail += s["fail"]
            total_prog += s["prog"]
    print("-" * 50)
    print(
        f'{"TOTAL":<18} {"":>6} {total_ok:>7} {total_fail:>7} {total_prog:>7}'
    )
    print()

    # DB errors
    uploads, db_err = db_errors()
    print(f"=== Supabase ===")
    print(f"  Total uploads: {uploads}")
    print(f"  Total DB errors: {db_err}")

    # Memory
    try:
        top = subprocess.run(
            ["top", "-l", "1", "-s", "0"], capture_output=True, text=True
        )
        for line in top.stdout.split("\n"):
            if "PhysMem" in line:
                print(f"\n=== Memory ===\n  {line.strip()}")
                break
    except:
        pass


if __name__ == "__main__":
    main()
