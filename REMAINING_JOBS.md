# Remaining Jobs

Generated: 2026-04-17

Running on machine 1: 16 swe-lancer phase4 jobs
Need to run: 70 jobs (46 qwen new + 24 rerun)

## Setup (new machine)

```bash
git clone git@github.com:XiangningLin/terminal-bench-experiments.git
cd terminal-bench-experiments
git checkout adapter0312
ln -s /path/to/harbor ../harbor  # harbor repo must be at ../harbor
uv sync

# Copy .env with all keys
cp /path/to/.env .

# Verify
.venv/bin/python3 -c "from harbor.job import Job; print('OK')"
```

## How to run a single job

```bash
source .env
export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"  # or _2 or _3

.venv/bin/python3 -u scripts/run_job.py \
  -c <config_path> \
  -f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError \
  -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError \
  -f RuntimeError -f CancelledError -f APIConnectionError
```

## Check status

```bash
.venv/bin/python3 scripts/status.py              # overall status
.venv/bin/python3 scripts/check_supabase_completion.py  # Supabase check
.venv/bin/python3 scripts/reimport_to_supabase.py       # upload missing results
bash scripts/machine_capacity.sh                         # machine capacity
```

---

## Qwen Jobs (46 new, never run)

### Qwen Phase2 (12 jobs, small ~5-50 trials each)

Config paths relative to `outputs/adapter_experiments/batch1/contributors/Xiangning/`

```
phase2/gpqa-diamond__qwen-coder__qwen3-max.yaml
phase2/gpqa-diamond__terminus-2__qwen3-max.yaml
phase2/ineqmath__qwen-coder__qwen3-max.yaml
phase2/ineqmath__terminus-2__qwen3-max.yaml
phase2/labbench__qwen-coder__qwen3-max.yaml
phase2/labbench__terminus-2__qwen3-max.yaml
phase2/mmau__qwen-coder__qwen3-max.yaml
phase2/mmau__terminus-2__qwen3-max.yaml
phase2/qcircuitbench__qwen-coder__qwen3-max.yaml
phase2/qcircuitbench__terminus-2__qwen3-max.yaml
phase2/swe-lancer__qwen-coder__qwen3-max.yaml
phase2/swe-lancer__terminus-2__qwen3-max.yaml
```

### Qwen Phase3 (18 jobs, medium ~5-450 trials each)

```
phase3/aime__qwen-coder__qwen3-max.yaml
phase3/aime__terminus-2__qwen3-max.yaml
phase3/arc-agi-2__qwen-coder__qwen3-max.yaml
phase3/arc-agi-2__terminus-2__qwen3-max.yaml
phase3/compilebench__qwen-coder__qwen3-max.yaml
phase3/compilebench__terminus-2__qwen3-max.yaml
phase3/gpqa-diamond__qwen-coder__qwen3-max.yaml
phase3/gpqa-diamond__terminus-2__qwen3-max.yaml
phase3/humanevalfix__qwen-coder__qwen3-max.yaml
phase3/humanevalfix__terminus-2__qwen3-max.yaml
phase3/ineqmath__qwen-coder__qwen3-max.yaml
phase3/ineqmath__terminus-2__qwen3-max.yaml
phase3/labbench__qwen-coder__qwen3-max.yaml
phase3/labbench__terminus-2__qwen3-max.yaml
phase3/mmau__qwen-coder__qwen3-max.yaml
phase3/mmau__terminus-2__qwen3-max.yaml
phase3/swe-lancer__qwen-coder__qwen3-max.yaml
phase3/swe-lancer__terminus-2__qwen3-max.yaml
```

### Qwen Phase4 (16 jobs, large ~25-900 trials each)

```
phase4/aime__qwen-coder__qwen3-max.yaml
phase4/aime__terminus-2__qwen3-max.yaml
phase4/arc-agi-2__qwen-coder__qwen3-max.yaml
phase4/arc-agi-2__terminus-2__qwen3-max.yaml
phase4/compilebench__qwen-coder__qwen3-max.yaml
phase4/compilebench__terminus-2__qwen3-max.yaml
phase4/gpqa-diamond__qwen-coder__qwen3-max.yaml
phase4/gpqa-diamond__terminus-2__qwen3-max.yaml
phase4/ineqmath__qwen-coder__qwen3-max.yaml
phase4/ineqmath__terminus-2__qwen3-max.yaml
phase4/labbench__qwen-coder__qwen3-max.yaml
phase4/labbench__terminus-2__qwen3-max.yaml
phase4/qcircuitbench__qwen-coder__qwen3-max.yaml
phase4/qcircuitbench__terminus-2__qwen3-max.yaml
phase4/swe-lancer__qwen-coder__qwen3-max.yaml
phase4/swe-lancer__terminus-2__qwen3-max.yaml
```

---

## Other Incomplete Jobs (24, need rerun)

### Phase2 (4 jobs)

```
phase2/labbench__terminus-2__kimi-k2.5.yaml          # ok=0/3
phase2/labbench__terminus-2__minimax-m2.5.yaml        # ok=0/3
phase2/qcircuitbench__claude-code__claude-sonnet-4-6.yaml  # ok=0/3
phase2/qcircuitbench__terminus-2__deepseek-reasoner.yaml   # ok=0/3
```

### Phase3 - compilebench (12 jobs)

```
phase3/compilebench__claude-code__kimi-k2.5.yaml      # ok=5/10
phase3/compilebench__claude-code__minimax-m2.5.yaml    # ok=5/10
phase3/compilebench__codex__gpt-5-nano.yaml            # ok=5/10
phase3/compilebench__codex__gpt-5.4.yaml               # ok=5/10
phase3/compilebench__gemini-cli__gemini-3.1-pro-preview.yaml  # ok=5/10
phase3/compilebench__terminus-2__deepseek-reasoner.yaml       # ok=5/10
phase3/compilebench__terminus-2__gemini-3.1-pro-preview.yaml  # ok=5/10
phase3/compilebench__terminus-2__gpt-5-mini.yaml       # ok=5/10
phase3/compilebench__terminus-2__gpt-5-nano.yaml       # ok=7/10
phase3/compilebench__terminus-2__gpt-5.4.yaml          # ok=5/10
phase3/compilebench__terminus-2__kimi-k2.5.yaml        # ok=5/10
phase3/compilebench__terminus-2__minimax-m2.5.yaml     # ok=5/10
```

### Phase3 - labbench (2 jobs)

```
phase3/labbench__claude-code__deepseek-chat.yaml      # ok=3/10
phase3/labbench__terminus-2__deepseek-reasoner.yaml    # ok=0/10
```

### Phase4 (6 jobs)

```
phase4/arc-agi-2__terminus-2__deepseek-reasoner.yaml   # ok=3/50
phase4/compilebench__terminus-2__gpt-5-nano.yaml       # ok=33/50
phase4/compilebench__terminus-2__minimax-m2.5.yaml     # ok=28/50
phase4/labbench__claude-code__deepseek-chat.yaml       # ok=20/50
phase4/qcircuitbench__terminus-2__deepseek-reasoner.yaml  # ok=29/50
phase4/qcircuitbench__terminus-2__gpt-5-nano.yaml      # ok=26/50
```

---

## Batch run script

Run all jobs with staggered launch (recommended):

```bash
source .env

FILTER="-f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError -f APIConnectionError"
LOG_DIR="/tmp/job-logs"
mkdir -p "$LOG_DIR"

CONFIG_BASE="outputs/adapter_experiments/batch1/contributors/Xiangning"

for config in "$CONFIG_BASE"/phase2/*qwen*.yaml \
              "$CONFIG_BASE"/phase3/*qwen*.yaml \
              "$CONFIG_BASE"/phase4/*qwen*.yaml; do
  job_name=$(grep "^job_name:" "$config" | awk '{print $2}')

  # Assign Daytona key by agent
  if [[ "$job_name" == *claude-code* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"
  elif [[ "$job_name" == *codex* ]] || [[ "$job_name" == *gemini-cli* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_2"
  else
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_3"
  fi

  nohup .venv/bin/python3 -u scripts/run_job.py -c "$config" $FILTER \
    > "$LOG_DIR/${job_name}.log" 2>&1 &
  echo "START: $job_name"
  sleep 15  # stagger to avoid Daytona rate limit (600 creations/min)
done

echo "Check: ps aux | grep run_job | grep -v grep | wc -l"
```

## Notes

- Skip `glm-5` and `mimo` jobs (keys unavailable)
- Skip `mmau phase4` (postponed, too large)
- Daytona limit: 600 sandbox creations/minute - stagger launches
- After running: `scripts/reimport_to_supabase.py` to upload results
- Check completion: `scripts/check_supabase_completion.py`
- Machine capacity: `bash scripts/machine_capacity.sh`
