#!/usr/bin/env python3
"""
Clean up disk space by removing large files from completed trials.
Keeps result.json and config.json, removes agent/, verifier/, trial.log etc.
Only cleans trials in non-running jobs.

Usage:
    .venv/bin/python3 scripts/cleanup_disk.py
    .venv/bin/python3 scripts/cleanup_disk.py --dry-run  # preview only
"""

import argparse
import glob
import os
import shutil
import subprocess


def get_running_jobs():
    running = set()
    ps = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    for line in ps.stdout.split("\n"):
        if "run_job" in line and "grep" not in line:
            for part in line.split():
                if "Xiangning" in part or "job-configs" in part:
                    running.add(part.split("/")[-1].replace(".yaml", ""))
    return running


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    running = get_running_jobs()
    cleaned_bytes = 0
    cleaned_count = 0

    for jd in sorted(glob.glob("jobs/*")):
        if not os.path.isdir(jd):
            continue
        name = os.path.basename(jd)
        if any(name in r for r in running):
            continue

        for t in os.listdir(jd):
            tp = os.path.join(jd, t)
            if not os.path.isdir(tp):
                continue
            rp = os.path.join(tp, "result.json")
            if not os.path.exists(rp):
                continue

            for item in os.listdir(tp):
                if item in ("result.json", "config.json"):
                    continue
                ip = os.path.join(tp, item)
                size = 0
                if os.path.isdir(ip):
                    for dp, dn, fns in os.walk(ip):
                        for fn in fns:
                            size += os.path.getsize(os.path.join(dp, fn))
                    if not args.dry_run:
                        shutil.rmtree(ip, ignore_errors=True)
                elif os.path.isfile(ip):
                    size = os.path.getsize(ip)
                    if not args.dry_run:
                        os.remove(ip)
                cleaned_bytes += size

            cleaned_count += 1

    action = "Would clean" if args.dry_run else "Cleaned"
    print(
        f"{action}: {cleaned_count} trials, {cleaned_bytes / 1024 / 1024 / 1024:.1f} GB"
    )


if __name__ == "__main__":
    main()
