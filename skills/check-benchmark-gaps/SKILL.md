---
name: check-benchmark-gaps
description: Query Supabase to identify which benchmark/agent/model combinations still need trials, then generate rerun configs for missing tasks.
---

# Check Benchmark Gaps

Use this skill to find out which jobs are incomplete in Supabase and what needs to be rerun.

## Quick Check

```bash
source .env
.venv/bin/python3 scripts/check_benchmark_gaps.py
```

### Options

```bash
# Only show incomplete jobs
.venv/bin/python3 scripts/check_benchmark_gaps.py --incomplete-only

# Check specific benchmark
.venv/bin/python3 scripts/check_benchmark_gaps.py --benchmark swe-lancer

# Check specific phase
.venv/bin/python3 scripts/check_benchmark_gaps.py --phase phase4

# Change minimum trials threshold (default 3)
.venv/bin/python3 scripts/check_benchmark_gaps.py --min-trials 5
```

## How It Works

1. Reads all YAML configs from the contributor's directory
2. For each job_name, queries Supabase:
   - `SELECT id FROM job WHERE job_name = ?` → gets all job_ids (handles duplicates)
   - For each job_id: `SELECT task_checksum, reward FROM trial WHERE job_id = ? AND reward IS NOT NULL`
   - Counts unique task_checksums with >= N successful trials
3. Compares against expected task count per benchmark/phase
4. Reports: DONE (all tasks complete), PARTIAL (some done), NEED (none done)

## Understanding Results

```
Benchmark           Done   Partial   Need
------------------------------------------
aime                  14        0      1
swe-lancer             3       15      2
```

- **DONE**: All expected tasks have >= min_trials successful trials in Supabase
- **PARTIAL**: Some tasks done, some missing
- **NEED**: No successful trials found (or job not in DB)

## Key Concepts

- **task_checksum**: Unique hash of a task. Each task has one checksum across all runs.
- **job_id**: Each time `run_job.py` starts, it creates a new job_id. Same job_name can have multiple job_ids.
- **reward IS NOT NULL**: Only counts trials that completed successfully (have a score).

## Generating Rerun Configs

After identifying gaps, create filtered registries:

```python
# Example: create registry with only missing tasks for a specific combo
from collections import defaultdict
from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Get all job_ids for this job_name
jobs = client.table("job").select("id").eq("job_name", job_name).execute()

# 2. Count trials per task_checksum across all job_ids
task_ok = defaultdict(int)
for job in jobs.data:
    trials = client.table("trial").select("task_checksum,reward") \
        .eq("job_id", job["id"]).not_.is_("reward", "null").execute()
    for t in trials.data:
        task_ok[t["task_checksum"]] += 1

# 3. Find tasks needing more trials
done_checksums = {cs for cs, count in task_ok.items() if count >= 5}

# 4. Filter registry to exclude done tasks
# (need checksum-to-taskname mapping from task table)
```

## Common Issues

- **Query timeout**: Some jobs have too many trials. Use `--benchmark` to limit scope.
- **Multiple job_ids**: Normal — caused by restarts. Script handles this by querying all.
- **Supabase 502**: Retry later, the script will show errors.
- **Local vs Supabase mismatch**: Local may show "done" but Supabase doesn't. Always trust Supabase as source of truth for scoring.

## Workflow

1. Run `check_benchmark_gaps.py` to identify what's missing
2. Create filtered registry with only missing tasks (see `swe-lancer-top100.json` as example)
3. Create config pointing to filtered registry
4. Run on this or another machine:
   ```bash
   .venv/bin/python3 -u scripts/run_job.py -c <config.yaml>
   ```
5. After completion, verify with `check_supabase_completion.py`
