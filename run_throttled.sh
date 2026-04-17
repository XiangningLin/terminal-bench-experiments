#!/bin/bash
# Throttled job runner - respects Daytona 600 sandbox/min creation limit
# Launches jobs slowly and caps concurrent jobs
set -e
cd "$(dirname "$0")"
source /Users/linxiangning/Desktop/projects/tb_adapter_project/.env

MAX_CONCURRENT=60        # Max jobs running at once
CONCURRENT_PER_JOB=5     # Sandbox per job
LAUNCH_INTERVAL=10       # Seconds between launching new jobs
LOG_DIR="/tmp/job-logs-throttled"
mkdir -p "$LOG_DIR" /tmp/job-configs

FILTER="-f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError"

# Collect all unfinished jobs
JOBS=()
while IFS= read -r line; do
  JOBS+=("$line")
done < <(python3 -c "
import glob, yaml, os

for f in sorted(glob.glob('outputs/adapter_experiments/batch1/contributors/Xiangning/**/*.yaml', recursive=True)):
    if 'registries' in f or 'glm-5' in f: continue
    with open(f) as fh: cfg = yaml.safe_load(fh)
    jn = cfg.get('job_name','')
    rp = f'jobs/{jn}/result.json'
    if os.path.exists(rp) and os.path.getsize(rp) > 5: continue
    print(f)
")

TOTAL=${#JOBS[@]}
echo "============================================"
echo "Throttled Runner"
echo "  Total jobs to run: $TOTAL"
echo "  Max concurrent: $MAX_CONCURRENT"
echo "  Per job concurrent: $CONCURRENT_PER_JOB"
echo "  Launch interval: ${LAUNCH_INTERVAL}s"
echo "  Started: $(date)"
echo "============================================"

PIDS=()
NAMES=()
LAUNCHED=0

# Clean up finished processes
cleanup() {
  local new_pids=() new_names=()
  for i in "${!PIDS[@]}"; do
    if kill -0 "${PIDS[$i]}" 2>/dev/null; then
      new_pids+=("${PIDS[$i]}")
      new_names+=("${NAMES[$i]}")
    fi
  done
  PIDS=("${new_pids[@]}")
  NAMES=("${new_names[@]}")
}

launch_job() {
  local config="$1"
  local job_name
  job_name=$(grep "^job_name:" "$config" | awk '{print $2}')

  # Clean failed trials
  python3 -c "
import os, json, shutil
jd = 'jobs/$job_name'
if os.path.isdir(jd):
    for t in os.listdir(jd):
        rp = os.path.join(jd, t, 'result.json')
        if os.path.exists(rp):
            try:
                with open(rp) as f: r = json.load(f)
                if r.get('exception_info'): shutil.rmtree(os.path.join(jd, t))
            except: pass
    for f in ['config.json', 'result.json']:
        fp = os.path.join(jd, f)
        if os.path.exists(fp): os.remove(fp)
" 2>/dev/null

  # Patch config
  local dst="/tmp/job-configs/${job_name}.yaml"
  python3 -c "
import yaml
with open('$config') as f: cfg = yaml.safe_load(f)
cfg.setdefault('orchestrator', {})['n_concurrent_trials'] = $CONCURRENT_PER_JOB
with open('$dst', 'w') as f: yaml.dump(cfg, f, default_flow_style=False)
"

  # Assign key
  if [[ "$job_name" == *claude-code* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"
  elif [[ "$job_name" == *codex* ]] || [[ "$job_name" == *gemini-cli* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_2"
  else
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_3"
  fi

  nohup .venv/bin/python3 -u scripts/run_job.py -c "$dst" $FILTER > "$LOG_DIR/${job_name}.log" 2>&1 &
  PIDS+=($!)
  NAMES+=("$job_name")
  LAUNCHED=$((LAUNCHED + 1))
  echo "[$(date +%H:%M:%S)] START ($LAUNCHED/$TOTAL): $job_name (${#PIDS[@]} running)"
}

# Main loop
JOB_IDX=0
while [ $JOB_IDX -lt $TOTAL ] || [ ${#PIDS[@]} -gt 0 ]; do
  cleanup

  # Launch new jobs if under limit
  while [ $JOB_IDX -lt $TOTAL ] && [ ${#PIDS[@]} -lt $MAX_CONCURRENT ]; do
    launch_job "${JOBS[$JOB_IDX]}"
    JOB_IDX=$((JOB_IDX + 1))
    sleep $LAUNCH_INTERVAL
  done

  # Wait a bit before checking again
  if [ ${#PIDS[@]} -ge $MAX_CONCURRENT ] || [ $JOB_IDX -ge $TOTAL ]; then
    sleep 30
  fi
done

echo ""
echo "============================================"
echo "ALL DONE at $(date)"
echo "  Launched: $LAUNCHED"
echo "============================================"
