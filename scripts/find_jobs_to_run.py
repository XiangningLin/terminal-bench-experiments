#!/usr/bin/env python3
"""
Find jobs that need to be run or rerun based on Supabase job table.

Usage:
    source .env
    uv run python scripts/find_jobs_to_run.py

Logic:
- Fetches all jobs for username=linxiangning from Supabase
- Deduplicates by job_name (keeps the one with most progress)
- Categorizes into: not_started, needs_rerun, completed
- Uses job.stats.evals.{eval_key}.n_trials and n_errors to determine status
- A job is "completed" if n_trials_done >= n_expected
- A job "needs_rerun" if it ended but n_trials_done < n_expected (has errors)
- Outputs JOBS_STATUS.md with full report

Scoring rules (for reference):
- Valid trial: reward IS NOT NULL, or exception is RewardFileNotFoundError
- Per (benchmark, task, model, agent): need >= 3 valid trials to qualify
- Trials from different owners are pooled together
- Up to 5 most recent valid trials are kept per task
- Benchmark score = mean of per-task scores (algotune uses harmonic mean)
- Score transforms: algotune: ln(max(1,x))/(ln(max(1,x))+1),
                    sldbench/ineqmath: (x+1)/2, others: raw reward
"""

import json
import subprocess
import os
import sys
from datetime import datetime


def query_supabase_paginated(url, key, endpoint):
    """Fetch all records from a Supabase endpoint with pagination."""
    all_data = []
    for offset in range(0, 10000, 1000):
        r = subprocess.run(
            ['curl', '-s',
             f'{url}/rest/v1/{endpoint}&offset={offset}&limit=1000'
             if '?' in endpoint else
             f'{url}/rest/v1/{endpoint}?offset={offset}&limit=1000',
             '-H', f'apikey: {key}',
             '-H', f'Authorization: Bearer {key}'],
            capture_output=True, text=True
        )
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            print(f"Error parsing response: {r.stdout[:200]}", file=sys.stderr)
            break
        if not data or isinstance(data, dict):
            break
        all_data.extend(data)
        if len(data) < 1000:
            break
    return all_data


def main():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SECRET_KEY')
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SECRET_KEY must be set in environment", file=sys.stderr)
        sys.exit(1)

    username = os.environ.get('SUPABASE_USERNAME', 'linxiangning')
    print(f"Fetching jobs for username={username}...", file=sys.stderr)

    # Fetch all jobs
    all_jobs = query_supabase_paginated(
        url, key,
        f'job?username=eq.{username}&select=job_name,n_trials,started_at,ended_at,stats'
    )
    print(f"Total records: {len(all_jobs)}", file=sys.stderr)

    # Deduplicate: keep the one with most progress per job_name
    job_best = {}
    for j in all_jobs:
        name = j['job_name']
        stats = j.get('stats')
        n_trials_done = 0
        n_errors = 0
        if stats and 'evals' in stats:
            for eval_val in stats['evals'].values():
                n_trials_done += eval_val.get('n_trials', 0)
                n_errors += eval_val.get('n_errors', 0)
        j['_n_trials_done'] = n_trials_done
        j['_n_errors'] = n_errors
        if name not in job_best or n_trials_done > job_best[name]['_n_trials_done']:
            job_best[name] = j

    print(f"Unique job names: {len(job_best)}", file=sys.stderr)

    # Categorize
    not_started = []
    needs_rerun = []
    completed = []

    for name, j in sorted(job_best.items()):
        n_expected = j['n_trials']
        n_done = j['_n_trials_done']
        n_err = j['_n_errors']
        remaining = n_expected - n_done

        parts = name.split('__')
        ph = [p for p in parts if p.startswith('phase')]
        phase = ph[0] if ph else 'unknown'

        entry = {
            'job_name': name,
            'phase': phase,
            'n_expected': n_expected,
            'n_done': n_done,
            'n_errors': n_err,
            'remaining': remaining,
        }

        if j['started_at'] is None:
            entry['status'] = 'not_started'
            not_started.append(entry)
        elif n_done < n_expected:
            entry['status'] = 'needs_rerun'
            needs_rerun.append(entry)
        else:
            entry['status'] = 'completed'
            completed.append(entry)

    # Print summary to stderr
    print(f"\nNot started: {len(not_started)}", file=sys.stderr)
    print(f"Needs rerun: {len(needs_rerun)}", file=sys.stderr)
    print(f"Completed: {len(completed)}", file=sys.stderr)
    print(f"Total to run: {len(not_started) + len(needs_rerun)}", file=sys.stderr)

    # Generate markdown
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    lines = []
    lines.append("# Jobs To Run - Status Report")
    lines.append("")
    lines.append(f"Generated: {now} from Supabase (username: {username})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Not started | {len(not_started)} |")
    lines.append(f"| Needs rerun (partial errors) | {len(needs_rerun)} |")
    lines.append(f"| Completed | {len(completed)} |")
    lines.append(f"| **Total to run** | **{len(not_started) + len(needs_rerun)}** |")
    lines.append("")

    # By phase summary
    for phase in ['phase2', 'phase3', 'phase4', 'unknown']:
        ns = [e for e in not_started if e['phase'] == phase]
        nr = [e for e in needs_rerun if e['phase'] == phase]
        if ns or nr:
            lines.append(f"### {phase}")
            lines.append(f"- Not started: {len(ns)}")
            lines.append(f"- Needs rerun: {len(nr)}")
            lines.append("")

    lines.append(f"## Not Started ({len(not_started)})")
    lines.append("")
    lines.append("| Job Name | Phase | Expected Trials |")
    lines.append("|----------|-------|-----------------|")
    for e in not_started:
        lines.append(f"| {e['job_name']} | {e['phase']} | {e['n_expected']} |")

    lines.append("")
    lines.append(f"## Needs Rerun ({len(needs_rerun)})")
    lines.append("")
    lines.append("| Job Name | Phase | Expected | Done | Errors | Remaining |")
    lines.append("|----------|-------|----------|------|--------|-----------|")
    for e in needs_rerun:
        lines.append(f"| {e['job_name']} | {e['phase']} | {e['n_expected']} | {e['n_done']} | {e['n_errors']} | {e['remaining']} |")

    lines.append("")
    lines.append(f"## Completed ({len(completed)})")
    lines.append("")
    lines.append(f"Total completed jobs: {len(completed)}")
    lines.append("")

    content = "\n".join(lines) + "\n"

    # Write to file
    outpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "JOBS_STATUS.md")
    with open(outpath, 'w') as f:
        f.write(content)
    print(f"\nWritten to {outpath}", file=sys.stderr)

    # Also output JSON for programmatic use
    result = {
        'not_started': not_started,
        'needs_rerun': needs_rerun,
        'summary': {
            'not_started': len(not_started),
            'needs_rerun': len(needs_rerun),
            'completed': len(completed),
            'total_to_run': len(not_started) + len(needs_rerun),
        }
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
