#!/bin/bash
# Run all rerun jobs with proper cleanup
# Deletes old rerun job directories before starting to avoid harbor thinking they're done
#
# Usage: ./scripts/run_rerun_jobs.sh [--interval 60] [--max-jobs 5]
set -e
cd "$(dirname "$0")/.."
source /Users/linxiangning/Desktop/projects/tb_adapter_project/.env

INTERVAL=${1:-60}
MAX_JOBS=${2:-5}

RERUN_DIR="outputs/adapter_experiments/batch1/contributors/Xiangning/phase4/rerun"
LOG_DIR="/tmp/job-logs-rerun-clean"
mkdir -p "$LOG_DIR"

started=0
for config in "$RERUN_DIR"/swe-lancer__*__rerun.yaml; do
  [ -f "$config" ] || continue

  job_name=$(grep "^job_name:" "$config" | awk '{print $2}')
  job_dir="jobs/$job_name"

  # KEY FIX: delete old rerun job dir so harbor starts fresh
  if [ -d "$job_dir" ]; then
    echo "Cleaning old dir: $job_dir"
    rm -rf "$job_dir"
  fi

  # Assign Daytona key
  if [[ "$job_name" == *claude-code* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"
  elif [[ "$job_name" == *codex* ]] || [[ "$job_name" == *gemini-cli* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_2"
  else
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_3"
  fi

  nohup .venv/bin/python3 -u scripts/run_job.py -c "$config" > "$LOG_DIR/${job_name}.log" 2>&1 &
  started=$((started + 1))
  echo "[$(date +%H:%M:%S)] START ($started): $job_name"

  # Respect max concurrent
  running=$(ps aux | grep run_job | grep -v grep | wc -l | tr -d ' ')
  while [ "$running" -ge "$MAX_JOBS" ]; do
    sleep 30
    running=$(ps aux | grep run_job | grep -v grep | wc -l | tr -d ' ')
  done

  sleep "$INTERVAL"
done

echo "[$(date +%H:%M:%S)] Done. Started: $started"
echo "Monitor: tail -f $LOG_DIR/*.log"
