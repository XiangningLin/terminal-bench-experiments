---
name: monitor-and-troubleshoot
description: Monitor running experiments, check Daytona/Supabase health, diagnose errors, manage concurrency, and handle reruns for Terminal Bench experiments.
---

# Monitor and Troubleshoot Experiments

Use this skill to monitor running experiments, diagnose issues, and manage reruns.

## Quick Status Check

```bash
# How many job processes running
ps aux | grep run_job | grep -v grep | wc -l

# How many sandboxes active (only in RUNNING jobs, not stale dirs)
python3 -c "
import os, glob, subprocess
running = set()
ps = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
for line in ps.stdout.split('\n'):
    if 'run_job' in line and 'grep' not in line:
        for part in line.split():
            if 'Xiangning' in part or 'job-configs' in part:
                running.add(part.split('/')[-1].replace('.yaml',''))
active = 0
for jd in glob.glob('jobs/*'):
    if not os.path.isdir(jd): continue
    name = os.path.basename(jd)
    if not any(name in r for r in running): continue
    for t in os.listdir(jd):
        tp = os.path.join(jd, t)
        if os.path.isdir(tp) and not os.path.exists(os.path.join(tp, 'result.json')):
            active += 1
print(f'{active} active sandboxes ({len(running)} processes)')
"
```

## Per Agent+Model Trial Progress

```bash
python3 -c "
import os, json, glob
from collections import defaultdict

combos = defaultdict(lambda: {'ok':0,'fail':0,'prog':0})
for jd in glob.glob('jobs/*'):
    if not os.path.isdir(jd): continue
    name = os.path.basename(jd)
    parts = name.split('__')
    if len(parts) < 3: continue
    agent_model = parts[1] + ' + ' + parts[2]
    for t in os.listdir(jd):
        tp = os.path.join(jd, t)
        if not os.path.isdir(tp): continue
        rp = os.path.join(tp, 'result.json')
        if os.path.exists(rp):
            try:
                with open(rp) as f: r = json.load(f)
                if r.get('exception_info'): combos[agent_model]['fail'] += 1
                else: combos[agent_model]['ok'] += 1
            except: combos[agent_model]['fail'] += 1
        else:
            combos[agent_model]['prog'] += 1

print(f'{\"Agent + Model\":<40} {\"OK\":>7} {\"Fail\":>7} {\"Prog\":>6}')
print('-' * 62)
for k in sorted(combos, key=lambda x: -combos[x]['ok']):
    s = combos[k]
    print(f'{k:<40} {s[\"ok\"]:>7} {s[\"fail\"]:>7} {s[\"prog\"]:>6}')
"
```

## Check Daytona Errors

```bash
# Recent errors (last 5 min)
python3 -c "
import os, json, glob, time
from collections import Counter
now = time.time()
recent = Counter()
for jd in glob.glob('jobs/*'):
    if not os.path.isdir(jd): continue
    for t in os.listdir(jd):
        rp = os.path.join(jd, t, 'result.json')
        if not os.path.exists(rp): continue
        if os.path.getmtime(rp) < now - 300: continue
        try:
            with open(rp) as f: r = json.load(f)
            exc = r.get('exception_info')
            if exc: recent[exc.get('exception_type','')] += 1
            else: recent['OK'] += 1
        except: pass
for k, v in recent.most_common():
    print(f'  {k}: {v}')
"
```

### Common Daytona Errors

| Error | Cause | Action |
|-------|-------|--------|
| `DaytonaRateLimitError` | Too many sandbox creations (>600/min) | Reduce concurrent jobs, stagger launches |
| `DaytonaAuthenticationError` | Invalid API key | Check DAYTONA_API_KEY in .env |
| `DaytonaAuthorizationError` | Key temporarily blocked | Wait or switch to different key |
| `Sandbox not found` | Stale trial dirs from previous runs | Clean with `-f` flags on rerun |

### When Rate Limited

1. Kill all processes: `kill $(ps aux | grep run_job | grep -v grep | awk '{print $2}')`
2. Wait 5 minutes for cooldown
3. Restart with fewer concurrent jobs and staggered launches (every 10-20 seconds)
4. Daytona limit is **600 sandbox creations per minute** — the danger is failed trials retrying immediately, creating a cascade

## Check Supabase DB Upload Status

```bash
# Count uploads and DB errors from logs
python3 -c "
import glob
uploads = db_err = 0
for d in ['/tmp/job-logs-key1-v2', '/tmp/job-logs-key2-fix', '/tmp/job-logs-key3',
          '/tmp/job-logs-other-benchmarks', '/tmp/job-logs-throttled', '/tmp/job-logs-rerun']:
    for log in glob.glob(f'{d}/*.log'):
        with open(log) as f: c = f.read()
        uploads += c.count('Successfully uploaded')
        db_err += c.count('Failed to insert trial')
print(f'Uploads: {uploads}  DB errors: {db_err}')
"
```

### DB Error Explanation

- `Failed to insert trial ... RetryError` = trial ran successfully, tar.gz uploaded to Supabase Storage, but database record write failed
- **Trial data is safe** in local `result.json` — can be re-imported later
- Caused by Supabase overload when too many concurrent jobs write at the same time
- Fix: batch re-import after jobs finish (see Rerun section)

## Check Job Progress

```bash
# Overall progress
python3 -c "
import os, json, glob
ok = fail = prog = 0
for jd in glob.glob('jobs/*'):
    if not os.path.isdir(jd): continue
    for t in os.listdir(jd):
        tp = os.path.join(jd, t)
        if not os.path.isdir(tp): continue
        rp = os.path.join(tp, 'result.json')
        if os.path.exists(rp):
            try:
                with open(rp) as f: r = json.load(f)
                if r.get('exception_info'): fail += 1
                else: ok += 1
            except: fail += 1
        else: prog += 1
print(f'OK: {ok}  Failed: {fail}  In progress: {prog}  Total: {ok+fail+prog}')
"

# Per-benchmark completion
python3 -c "
import os, json, glob
from collections import defaultdict
stats = defaultdict(lambda: [0,0,0])
for jd in glob.glob('jobs/*'):
    if not os.path.isdir(jd): continue
    bench = os.path.basename(jd).split('__')[0]
    for t in os.listdir(jd):
        tp = os.path.join(jd, t)
        if not os.path.isdir(tp): continue
        rp = os.path.join(tp, 'result.json')
        if os.path.exists(rp):
            try:
                with open(rp) as f: r = json.load(f)
                if r.get('exception_info'): stats[bench][1] += 1
                else: stats[bench][0] += 1
            except: stats[bench][1] += 1
        else: stats[bench][2] += 1
for b in sorted(stats):
    ok, fail, prog = stats[b]
    print(f'{b:<18} ok={ok:>5} fail={fail:>5} prog={prog:>4}')
"
```

## Check System Resources

```bash
# Memory
top -l 1 -s 0 | grep PhysMem

# Disk
du -sh jobs/ && df -h / | tail -1

# Per-process memory
ps aux | grep run_job | grep -v grep | awk '{sum += $6} END {printf "run_job total: %.1fGB (%d processes)\n", sum/1024/1024, NR}'

# Top memory consumers (non-job)
ps aux | sort -k6 -rn | grep -v "run_job\|python3" | head -10 | awk '{printf "%6dMB %s\n", $6/1024, $11}'
```

### Memory Guidelines

- Each run_job process uses ~150-300 MB
- 60 processes ≈ 12-18 GB
- macOS compressor helps but >80 processes will be tight on 32GB machine
- Kill Chrome/WeChat to free 2-6 GB

## Concurrency Guidelines

### Daytona Rate Limit: 600 sandbox creations / minute

| Scenario | Safe Concurrent |
|----------|----------------|
| Stable (trials take 10+ min) | 60-80 jobs × 5 concurrent = 300-400 sandbox |
| With failures (fast retry) | 30-40 jobs × 5 concurrent = 150-200 sandbox |
| After rate limit hit | Wait 5 min, restart with 20 jobs |

### Three-Key Distribution

Distribute jobs across 3 Daytona API keys by agent type to avoid per-key rate limits:

```bash
if [[ "$job_name" == *claude-code* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"
elif [[ "$job_name" == *codex* ]] || [[ "$job_name" == *gemini-cli* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_2"
else
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_3"
fi
```

### Staggered Launch

Always launch jobs with delays to avoid burst creation:

```bash
# 10-20 seconds between launches
for config in configs/*.yaml; do
    nohup .venv/bin/python3 -u scripts/run_job.py -c "$config" &
    sleep 20
done
```

## Rerun Failed Trials

```bash
# Rerun with error filtering (cleans failed trials, reruns them)
.venv/bin/python3 -u scripts/run_job.py -c <config.yaml> \
    -f DaytonaRateLimitError \
    -f DaytonaError \
    -f DaytonaAuthorizationError \
    -f DaytonaAuthenticationError \
    -f NonZeroAgentExitCodeError \
    -f RuntimeError \
    -f CancelledError \
    -f APIConnectionError
```

**How `-f` works** (from `run_job.py` line 439-469):
1. Reads `result.json` in each trial directory
2. If `exception_info.exception_type` matches any `-f` type → deletes that trial directory
3. Harbor then treats it as a new trial and reruns it
4. Successful trials (no exception) are kept and skipped
5. Requires `config.json` in the job directory to exist

**Important**: when cleaning disk space, keep `result.json` AND `config.json` per job — both are needed for rerun.

## Batch Re-import to Supabase

After jobs finish, re-import trials that had DB write failures:

```python
# Run from project root with .venv
import os, json, glob, shutil
from decimal import Decimal
from pathlib import Path
from supabase import create_client
from harbor.models.trial.result import TrialResult

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

for job_dir in sorted(glob.glob('jobs/*')):
    for trial_name in os.listdir(job_dir):
        rp = os.path.join(job_dir, trial_name, 'result.json')
        if not os.path.exists(rp): continue
        result = TrialResult.model_validate_json(Path(rp).read_text())
        if result.exception_info: continue
        
        # Check if already in DB
        existing = client.table('trial').select('id').eq('id', str(result.id)).execute()
        if existing.data: continue
        
        # Insert trial, agent, model...
```

## Check Supabase Completion

Before rerunning jobs, ALWAYS check Supabase first — results may already exist from previous runs (especially when `config.json` was deleted, causing duplicate job_ids).

```bash
# Check all jobs
.venv/bin/python3 scripts/check_supabase_completion.py

# Check specific phase
.venv/bin/python3 scripts/check_supabase_completion.py --phase phase2

# Check specific benchmark
.venv/bin/python3 scripts/check_supabase_completion.py --benchmark mmau
```

A job is "DONE" when every task has >= 3 successful trials (with non-null reward) across ALL job_ids in Supabase. This handles duplicate job_ids caused by deleting `config.json` during reruns.

### Important: Never delete config.json

When rerunning with `-f` flags, **do NOT delete `config.json`** from the job directory. Deleting it causes harbor to create a new job_id and re-run ALL trials from scratch, including already successful ones. The `-f` flag alone handles cleaning failed trials.

## Supabase Batch Re-import (with task registration)

When `run_job.py` has DB errors, trials succeed locally but don't get written to Supabase. Use this to batch re-import:

```bash
source .env
.venv/bin/python3 scripts/reimport_to_supabase.py
```

The script does two steps:
1. **Register missing tasks** — some tasks may not be in the `task` table yet (foreign key constraint). It reads `config.json` from each trial to get `path`, `git_url`, etc.
2. **Import trials** — checks each successful trial by ID, skips if already in DB, inserts if missing.

### Common Supabase Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `foreign key constraint "trial_task_checksum_fkey"` | Task not in `task` table | Run task registration first (Step 1 of reimport script) |
| `null value in column "agent_timeout_sec"` | Missing required fields when inserting task | Include `agent_timeout_sec`, `verifier_timeout_sec`, `path` |
| `null value in column "path"` | Missing path field | Get path from trial's `config.json` |
| `UUID is not JSON serializable` | UUID objects not serialized | Use `json.dumps(data, default=str)` or `str(uuid)` |
| `502 Bad Gateway` | Supabase overloaded | Wait and retry later, reduce concurrent writes |

### Key Fields for Task Registration

The `task` table requires these non-null fields:
- `checksum` (from `result.task_checksum`)
- `name` (from `result.task_name`)
- `instruction` (can be empty string)
- `agent_timeout_sec` (default: 1800)
- `verifier_timeout_sec` (default: 600)
- `path` (from trial's `config.json` → `task.path`)

### Config Mismatch Error

`ValueError: Job directory already exists and cannot be resumed with a different config.`

This happens when `config.json` in the job directory doesn't match the config you're running with (e.g., different `n_concurrent_trials`).

**NEVER delete `config.json` to fix this.** Deleting it causes harbor to create a new job_id and re-run ALL trials from scratch, including already successful ones. This wastes compute and creates duplicates (e.g., 1004/900 trials).

**Correct fix:** Always use the original config YAML without modifications. Do not change `n_concurrent_trials` or any other parameter when restarting a crashed job. Just run:
```bash
.venv/bin/python3 -u scripts/run_job.py -c <original_config.yaml> -f <error_types>
```

If `config.json` was already deleted, the damage is done — harbor will create duplicate trials. The extra trials don't break anything (Supabase upsert handles it) but waste resources.

## Disk Cleanup (Safe)

For completed trials already uploaded to Supabase Storage, remove large files but keep `result.json` and job-level `config.json`:

```python
import os, shutil
for trial_dir in trial_dirs:
    for item in os.listdir(trial_dir):
        if item in ('result.json', 'config.json'): continue
        path = os.path.join(trial_dir, item)
        if os.path.isdir(path): shutil.rmtree(path)
        else: os.remove(path)
```

**Do NOT delete**: `result.json` (needed for rerun logic) and job-level `config.json` (needed for `-f` filter).
