#!/bin/bash
# Run all remaining jobs: SWE-Lancer first, then other benchmarks
# Total concurrency target: ~300 sandboxes
# Staggered launch to avoid overwhelming Daytona
set -e
cd "$(dirname "$0")"
source .env

FILTER_FLAGS="-f DaytonaRateLimitError -f DaytonaError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError"
LOG_DIR="/tmp/job-logs-$(date +%Y%m%d-%H%M)"
mkdir -p "$LOG_DIR"

CONFIG_BASE="outputs/adapter_experiments/batch1/contributors/Xiangning"
TOTAL_TARGET=300

PIDS=()
RUNNING_JOBS=()
TOTAL_LAUNCHED=0
TOTAL_SKIPPED=0

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

launch_job() {
  local config="$1"
  local concurrent="$2"
  local job_name
  job_name=$(grep "^job_name:" "$config" | awk '{print $2}')

  # Skip completed jobs
  if is_completed "$job_name"; then
    echo "[$(date +%H:%M:%S)] SKIP (done): $job_name"
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
    return
  fi

  local log="$LOG_DIR/${job_name}.log"

  # Patch n_concurrent_trials
  local tmp_config="/tmp/job-configs/${job_name}.yaml"
  mkdir -p /tmp/job-configs
  python3 -c "
import yaml
with open('$config') as f:
    cfg = yaml.safe_load(f)
cfg.setdefault('orchestrator', {})['n_concurrent_trials'] = $concurrent
with open('$tmp_config', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"

  echo "[$(date +%H:%M:%S)] START: $job_name (concurrent=$concurrent)"
  .venv/bin/python3 -u scripts/run_job.py -c "$tmp_config" $FILTER_FLAGS > "$log" 2>&1 &
  PIDS+=($!)
  RUNNING_JOBS+=("$job_name")
  TOTAL_LAUNCHED=$((TOTAL_LAUNCHED + 1))
}

cleanup_finished() {
  local new_pids=()
  local new_jobs=()
  for i in "${!PIDS[@]}"; do
    if kill -0 "${PIDS[$i]}" 2>/dev/null; then
      new_pids+=("${PIDS[$i]}")
      new_jobs+=("${RUNNING_JOBS[$i]}")
    fi
  done
  PIDS=("${new_pids[@]}")
  RUNNING_JOBS=("${new_jobs[@]}")
}

count_running() {
  cleanup_finished
  echo "${#PIDS[@]}"
}

echo "============================================"
echo "Full Job Run"
echo "  Target concurrency: ~${TOTAL_TARGET} sandboxes"
echo "  Skip: glm-5 (key unavailable)"
echo "  Logs: $LOG_DIR/"
echo "  Started: $(date)"
echo "============================================"

# =============================================
# PHASE 1: SWE-Lancer (priority)
# =============================================
echo ""
echo "========== SWE-LANCER =========="

# Phase2 (small, ~10 trials each)
echo "--- swe-lancer phase2 ---"
for config in "$CONFIG_BASE"/phase2/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  [[ "$config" == *glm-5* ]] && continue
  launch_job "$config" 32
  sleep 15
done

# Phase3 (medium, ~90 trials)
echo "--- swe-lancer phase3 ---"
for config in "$CONFIG_BASE"/phase3/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  [[ "$config" == *glm-5* ]] && continue
  launch_job "$config" 32
  sleep 15
done

# Phase4 (heavy, ~900 trials each)
# 300 target / ~20 phase4 jobs ≈ 15 per job
echo "--- swe-lancer phase4 ---"
for config in "$CONFIG_BASE"/phase4/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  [[ "$config" == *glm-5* ]] && continue
  launch_job "$config" 15
  sleep 30
done

echo ""
echo "[$(date +%H:%M:%S)] SWE-Lancer: $TOTAL_LAUNCHED launched, $TOTAL_SKIPPED skipped"
echo "[$(date +%H:%M:%S)] Running processes: $(count_running)"

# =============================================
# PHASE 2: Other benchmarks (mmau, gpqa, etc.)
# Wait for some SWE-Lancer jobs to free up slots
# =============================================
echo ""
echo "========== OTHER BENCHMARKS =========="
echo "Waiting 2 minutes before starting other benchmarks..."
sleep 120

# Collect all non-swe-lancer, non-glm configs
OTHER_CONFIGS=()
for phase in phase2 phase3 phase4; do
  for config in "$CONFIG_BASE"/$phase/*.yaml; do
    [ -f "$config" ] || continue
    [[ "$config" == *swe-lancer* ]] && continue
    [[ "$config" == *glm-5* ]] && continue
    [[ "$(basename $(dirname $config))" == "registries" ]] && continue
    OTHER_CONFIGS+=("$config")
  done
done

echo "Other benchmark configs: ${#OTHER_CONFIGS[@]}"

# Launch other benchmarks, respecting concurrency limit
for config in "${OTHER_CONFIGS[@]}"; do
  # Wait if too many running
  while true; do
    running=$(count_running)
    if [ "$running" -lt 50 ]; then
      break
    fi
    echo "[$(date +%H:%M:%S)] $running jobs still running, waiting 60s..."
    sleep 60
  done

  # Determine concurrency based on phase
  concurrent=20
  if [[ "$config" == *phase2* ]]; then
    concurrent=32
  elif [[ "$config" == *phase3* ]]; then
    concurrent=25
  fi

  launch_job "$config" "$concurrent"
  sleep 10
done

echo ""
echo "============================================"
echo "All jobs launched!"
echo "  Total launched: $TOTAL_LAUNCHED"
echo "  Total skipped:  $TOTAL_SKIPPED"
echo "  Currently running: $(count_running)"
echo ""
echo "Monitor:"
echo "  tail -f $LOG_DIR/<job_name>.log"
echo "  watch 'ps aux | grep run_job | grep -v grep | wc -l'"
echo "============================================"

# Wait for everything
echo "Waiting for all jobs to complete..."
FAILED=0
for pid in "${PIDS[@]}"; do
  wait "$pid" 2>/dev/null || FAILED=$((FAILED + 1))
done

echo ""
echo "============================================"
echo "ALL DONE at $(date)"
echo "  Total launched: $TOTAL_LAUNCHED"
echo "  Failed: $FAILED"
echo "============================================"
