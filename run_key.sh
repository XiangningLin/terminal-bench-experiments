#!/bin/bash
# Usage: ./run_key.sh <key_number> <job_list_file>
# Example: ./run_key.sh 1 /tmp/key1_jobs.txt
#
# Runs all jobs in the list sequentially, 2 at a time with 20 concurrent each.
# Skips already completed jobs.
set -e
cd "$(dirname "$0")"

KEY_NUM=$1
JOB_LIST=$2

if [ -z "$KEY_NUM" ] || [ -z "$JOB_LIST" ]; then
  echo "Usage: $0 <key_number> <job_list_file>"
  exit 1
fi

source /Users/linxiangning/Desktop/projects/tb_adapter_project/.env

case $KEY_NUM in
  1) export DAYTONA_API_KEY="$DAYTONA_API_KEY_1" ;;
  2) export DAYTONA_API_KEY="$DAYTONA_API_KEY_2" ;;
  3) export DAYTONA_API_KEY="$DAYTONA_API_KEY_3" ;;
  *) echo "Invalid key number: $KEY_NUM"; exit 1 ;;
esac

LOG_DIR="/tmp/job-logs-key${KEY_NUM}-auto"
mkdir -p "$LOG_DIR" /tmp/job-configs

CONCURRENT=20
FILTER="-f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError"

is_completed() {
  local job_name=$1
  local result="jobs/$job_name/result.json"
  if [ -f "$result" ]; then
    local size
    size=$(python3 -c "print(len(open('$result','rb').read()))" 2>/dev/null || echo 0)
    [ "$size" -gt 5 ] && return 0
  fi
  return 1
}

patch_config() {
  local src=$1
  local job_name
  job_name=$(grep "^job_name:" "$src" | awk '{print $2}')
  local dst="/tmp/job-configs/${job_name}.yaml"
  python3 -c "
import yaml
with open('$src') as f:
    cfg = yaml.safe_load(f)
cfg.setdefault('orchestrator', {})['n_concurrent_trials'] = $CONCURRENT
with open('$dst', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
  echo "$dst"
}

clean_failed_trials() {
  local job_name=$1
  local job_dir="jobs/$job_name"
  [ -d "$job_dir" ] || return
  python3 -c "
import os, json, shutil
job_dir = '$job_dir'
removed = 0
for trial in os.listdir(job_dir):
    rp = os.path.join(job_dir, trial, 'result.json')
    if os.path.exists(rp):
        try:
            with open(rp) as f: r = json.load(f)
            if r.get('exception_info'):
                shutil.rmtree(os.path.join(job_dir, trial)); removed += 1
        except: pass
for f in ['config.json', 'result.json']:
    fp = os.path.join(job_dir, f)
    if os.path.exists(fp): os.remove(fp)
if removed: print(f'  Cleaned {removed} failed trials from $job_name')
"
}

# Read job list
JOBS=()
while IFS= read -r line; do
  [ -n "$line" ] && JOBS+=("$line")
done < "$JOB_LIST"

TOTAL=${#JOBS[@]}
echo "============================================"
echo "Key $KEY_NUM Runner"
echo "  Jobs: $TOTAL"
echo "  Concurrent per job: $CONCURRENT"
echo "  Logs: $LOG_DIR/"
echo "  Started: $(date)"
echo "============================================"

# Run 2 jobs at a time
i=0
while [ $i -lt $TOTAL ]; do
  PIDS=()
  NAMES=()

  for j in 0 1; do
    idx=$((i + j))
    [ $idx -ge $TOTAL ] && break

    config="${JOBS[$idx]}"
    job_name=$(grep "^job_name:" "$config" | awk '{print $2}')

    if is_completed "$job_name"; then
      echo "[$(date +%H:%M:%S)] SKIP (done): $job_name"
      continue
    fi

    clean_failed_trials "$job_name"
    patched=$(patch_config "$config")
    log="$LOG_DIR/${job_name}.log"

    echo "[$(date +%H:%M:%S)] START: $job_name"
    .venv/bin/python3 -u scripts/run_job.py -c "$patched" $FILTER > "$log" 2>&1 &
    PIDS+=($!)
    NAMES+=("$job_name")
  done

  # Wait for this batch
  if [ ${#PIDS[@]} -gt 0 ]; then
    echo "[$(date +%H:%M:%S)] Waiting for ${#PIDS[@]} jobs: ${NAMES[*]}"
    for pid in "${PIDS[@]}"; do
      wait "$pid" 2>/dev/null || true
    done
    echo "[$(date +%H:%M:%S)] Batch done."
  fi

  i=$((i + 2))
done

echo ""
echo "============================================"
echo "Key $KEY_NUM ALL DONE at $(date)"
echo "============================================"
