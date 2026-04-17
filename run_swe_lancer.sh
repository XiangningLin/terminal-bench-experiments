#!/bin/bash
# Run all SWE-Lancer jobs with total ~500 concurrent sandboxes
# Staggered launch: 1 job per minute to avoid overwhelming Daytona
set -e
cd "$(dirname "$0")"
source .env

FILTER_FLAGS="-f DaytonaRateLimitError -f DaytonaError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError"
LOG_DIR="/tmp/swe-lancer-logs"
mkdir -p "$LOG_DIR"

# Phase4 jobs are the big ones (900 trials each) - they get most of the concurrency
# Phase2/3 are small and will finish fast
PHASE2_DIR="outputs/adapter_experiments/batch1/contributors/Xiangning/phase2"
PHASE3_DIR="outputs/adapter_experiments/batch1/contributors/Xiangning/phase3"
PHASE4_DIR="outputs/adapter_experiments/batch1/contributors/Xiangning/phase4"

TOTAL_CONCURRENT=500
PHASE4_CONCURRENT=30   # per job, ~21 phase4 jobs → ~630 peak, but they stagger finish
PHASE23_CONCURRENT=32  # per job, small jobs finish fast

PIDS=()
JOB_COUNT=0

launch_job() {
  local config="$1"
  local concurrent="$2"
  local name=$(basename "$config" .yaml)
  local log="$LOG_DIR/${name}.log"

  # Patch n_concurrent_trials in config on the fly
  local tmp_config="/tmp/swe-lancer-configs/${name}.yaml"
  mkdir -p /tmp/swe-lancer-configs
  python3 -c "
import yaml, sys
with open('$config') as f:
    cfg = yaml.safe_load(f)
cfg.setdefault('orchestrator', {})['n_concurrent_trials'] = $concurrent
with open('$tmp_config', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"

  echo "[$(date +%H:%M:%S)] START: $name (concurrent=$concurrent) → $log"
  .venv/bin/python3 scripts/run_job.py -c "$tmp_config" $FILTER_FLAGS > "$log" 2>&1 &
  PIDS+=($!)
  JOB_COUNT=$((JOB_COUNT + 1))
}

echo "============================================"
echo "SWE-Lancer Full Run"
echo "  Target concurrency: ~${TOTAL_CONCURRENT}"
echo "  Phase4 per-job: ${PHASE4_CONCURRENT}"
echo "  Phase2/3 per-job: ${PHASE23_CONCURRENT}"
echo "  Started: $(date)"
echo "============================================"

# --- Phase 2 jobs (small, 10 trials each) - launch first, they finish fast ---
echo ""
echo "=== Phase 2 (small jobs) ==="
for config in "$PHASE2_DIR"/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  launch_job "$config" "$PHASE23_CONCURRENT"
  sleep 30
done

# --- Phase 3 jobs (90 trials each) ---
echo ""
echo "=== Phase 3 ==="
for config in "$PHASE3_DIR"/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  launch_job "$config" "$PHASE23_CONCURRENT"
  sleep 30
done

# --- Phase 4 jobs (900 trials each) - the heavy ones ---
echo ""
echo "=== Phase 4 (heavy jobs) ==="
for config in "$PHASE4_DIR"/swe-lancer__*.yaml; do
  [ -f "$config" ] || continue
  launch_job "$config" "$PHASE4_CONCURRENT"
  sleep 60  # 1 minute between heavy jobs
done

echo ""
echo "============================================"
echo "All $JOB_COUNT jobs launched!"
echo "Logs: $LOG_DIR/"
echo ""
echo "Monitor with:"
echo "  watch 'for f in $LOG_DIR/*.log; do echo \"=== \$(basename \$f) ===\"; tail -3 \$f; echo; done'"
echo ""
echo "Check running: ps aux | grep run_job"
echo "============================================"

# Wait for all
echo "Waiting for all jobs to complete..."
FAILED=0
for pid in "${PIDS[@]}"; do
  wait "$pid" || FAILED=$((FAILED + 1))
done

echo ""
echo "============================================"
echo "SWE-Lancer DONE at $(date)"
echo "  Total jobs: $JOB_COUNT"
echo "  Failed: $FAILED"
echo "============================================"
