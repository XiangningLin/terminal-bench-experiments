---
name: run-experiments
description: Run Terminal Bench experiments end-to-end — clone the experiments repo, set up the environment, configure jobs, and execute them via the Harbor CLI or batch scripts.
---

# Run Experiments

Use this skill to run Terminal Bench evaluation experiments using the [terminal-bench-experiments](https://github.com/XiangningLin/terminal-bench-experiments.git) repo and the Harbor framework.

## Overview

The experiments repo orchestrates benchmark evaluations across multiple agents (claude-code, codex, gemini-cli, terminus-2, etc.) and models. Each experiment run is called a **job**, which consists of multiple **trials** (one per task per agent/model combination).

## Prereqs

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Access to the sandbox environment (Daytona credentials or Docker)
- API keys for the agents/models you want to evaluate (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`)
- A `.env` file at the repo root with required credentials

## 1. Clone And Set Up

```bash
git clone https://github.com/XiangningLin/terminal-bench-experiments.git
cd terminal-bench-experiments
uv sync
source .venv/bin/activate
```

Make sure the Harbor package is also installed (it should be pulled in as a dependency via `pyproject.toml`).

Verify the setup:

```bash
harbor --help
harbor jobs --help
```

## 2. Configuration Files

Job configs live in `configs/` and are YAML files that define what to run. Key directories:

| Directory | Purpose |
|-----------|---------|
| `configs/tb2/` | Terminal Bench 2.0 experiment configs |
| `configs/rerun/` | Rerun configs for failed trials |
| `configs/leaderboard/` | Leaderboard submission configs |

### Config Structure

A config file (e.g., `configs/tb2/proprietary.yaml`) defines:

```yaml
job_name: proprietary
jobs_dir: jobs                    # Output directory for results
n_attempts: 5                     # Attempts per trial
timeout_multiplier: 1.0           # Must be 1.0 for leaderboard submissions
orchestrator:
  type: local
  n_concurrent_trials: 64         # How many trials run in parallel
  quiet: false
  retry:
    max_retries: 3
    exclude_exceptions:
      - BadRequestError
      - RateLimitError
      - AgentTimeoutError
      - VerifierTimeoutError
environment:
  type: daytona                   # or "docker" for local
  force_build: false
  delete: true                    # Clean up environments after completion
agents:
  - name: claude-code
    model_name: anthropic/claude-sonnet-4-5-20250929
    kwargs:
      version: "2.0.31"
  - name: codex
    model_name: openai/gpt-5-codex
    kwargs:
      version: "0.53.0"
  # ... more agents
datasets:
  - registry:
      name: harbor
      url: https://raw.githubusercontent.com/laude-institute/harbor/main/registry.json
    name: terminal-bench
    version: "2.0"
```

## 3. Running A Single Job

### Via Harbor CLI

```bash
# Run with a config file
harbor jobs start -c configs/tb2/proprietary.yaml

# Run a specific dataset with a specific agent
harbor jobs start \
  -d terminal-bench@2.0 \
  -a claude-code \
  -m anthropic/claude-sonnet-4-5-20250929 \
  -e daytona

# Run a single task
harbor jobs start \
  -p /path/to/task/directory \
  -a claude-code \
  -m anthropic/claude-sonnet-4-5-20250929

# Limit concurrency
harbor jobs start -c configs/tb2/proprietary.yaml -n 8

# Run quietly
harbor jobs start -c configs/tb2/proprietary.yaml -q
```

### Via run_job.py Script

```bash
.venv/bin/python3 scripts/run_job.py -c configs/tb2/proprietary.yaml
```

This is the wrapper used by batch scripts. It accepts the same `-c` flag for config files.

## 4. Running Batch Experiments

For running many experiments in parallel with controlled concurrency:

### run_batch2.sh

Runs all configs in a batch directory, splitting GLM-5 jobs (lower concurrency) from others:

```bash
./run_batch2.sh
```

Key behavior:
- Skips jobs that already have a valid `result.json`
- GLM-5 jobs run with batch size 3 (rate limit sensitive)
- Other jobs run with batch size 6
- Both groups run in parallel

### run_all_low_concurrency.sh

Runs all phases with rerun logic for failed trials:

```bash
./run_all_low_concurrency.sh
```

Key behavior:
- Fixes corrupted result files before each run
- Checks if jobs need reruns (filters specific error types)
- Uses a stall timeout of 90 minutes (for slow environment setups)
- Runs phase 2, 3, and 4 configs sequentially

## 5. Resuming Failed Jobs

```bash
# Resume a job, filtering out specific error types
harbor jobs resume \
  -p jobs/<job_name> \
  -f DaytonaRateLimitError \
  -f DaytonaError

# Resume with default filter (CancelledError)
harbor jobs resume -p jobs/<job_name>
```

## 6. Job Output Structure

Results are written to the `jobs/` directory:

```
jobs/
  <benchmark>__<agent>__<model>__<batch>__<phase>/
    config.json          # Job configuration snapshot
    result.json          # Aggregated job results
    <trial_name>/        # One directory per trial
      config.json        # Trial configuration
      result.json        # Trial result (reward, timing, errors)
```

The naming convention is: `<benchmark>__<agent>__<model>__<batch>__<phase>`

Example: `aime__claude-code__claude-sonnet-4-6__batch1__phase2`

## 7. Importing Results To Database

After jobs complete, import results into Supabase:

```bash
# Import all jobs
tbx import --jobs-dir ./jobs

# Import specific job paths
tbx import --job-path ./jobs/aime__claude-code__claude-sonnet-4-6__batch1__phase2

# Import with model overrides and leaderboard flag
tbx import \
  --jobs-dir ./jobs \
  -m claude-sonnet-4-6 -p anthropic \
  --adn "Claude Code" --ao "Anthropic" \
  --mdn "Claude Sonnet 4.6" --mo "Anthropic" \
  --lb
```

## 8. Viewing Results

```bash
# View job results
harbor view jobs/<job_name>
```

## Environment Variables

Required in `.env` or exported in shell:

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Claude models |
| `OPENAI_API_KEY` | GPT/Codex models |
| `GEMINI_API_KEY` | Gemini models |
| `DAYTONA_API_KEY` | Daytona sandbox environments |
| `DAYTONA_SERVER_URL` | Daytona server endpoint |
| `SUPABASE_URL` | Database for result imports |
| `SUPABASE_SECRET_KEY` | Database auth |

## Troubleshooting

### ModuleNotFoundError: terminal_bench_experiments

The `tbx` CLI requires the local package to be installed:

```bash
uv sync
# or
pip install -e .
```

### click/typer ImportError

If you see `ImportError: cannot import name 'Abort' from 'click.exceptions'`, the click and typer versions are incompatible:

```bash
uv sync   # This should resolve dependency conflicts
```

### Empty pyproject.toml or scripts/run_job.py

If core files appear empty, you may be on a shallow clone or wrong branch:

```bash
git fetch origin
git checkout main
# or to get full history:
git fetch --unshallow
```

### Stale index.lock

If git commands hang, check for a leftover lock file:

```bash
rm -f .git/index.lock
```
