#!/bin/bash
cd "$(dirname "$0")"

LOG_DIR=$(ls -dt /tmp/job-logs-* 2>/dev/null | head -1)

echo "============================================"
echo "Job Status Check - $(date)"
echo "============================================"

# Running processes
RUNNING=$(ps aux | grep run_job | grep -v grep | wc -l | tr -d ' ')
echo ""
echo "Running job processes: $RUNNING"

# Main script
if ps aux | grep run_all_jobs | grep -v grep > /dev/null; then
  echo "Main script: RUNNING"
else
  echo "Main script: FINISHED"
fi

# Count completed jobs (have result.json with content)
COMPLETED=0
FAILED=0
TOTAL=0
for dir in jobs/*/; do
  [ -d "$dir" ] || continue
  TOTAL=$((TOTAL + 1))
  if [ -f "$dir/result.json" ]; then
    size=$(wc -c < "$dir/result.json" | tr -d ' ')
    if [ "$size" -gt 5 ]; then
      COMPLETED=$((COMPLETED + 1))
    fi
  fi
done

echo ""
echo "Job directories: $TOTAL"
echo "Completed (have result.json): $COMPLETED"

# Check logs for errors and successes
if [ -d "$LOG_DIR" ]; then
  echo ""
  echo "=== Log Summary ($LOG_DIR) ==="

  LOGS_WITH_UPLOAD=0
  LOGS_WITH_ERROR=0
  LOGS_EMPTY=0

  for log in "$LOG_DIR"/*.log; do
    [ -f "$log" ] || continue
    size=$(wc -c < "$log" | tr -d ' ')
    if [ "$size" -eq 0 ]; then
      LOGS_EMPTY=$((LOGS_EMPTY + 1))
    elif grep -q "Successfully uploaded" "$log"; then
      LOGS_WITH_UPLOAD=$((LOGS_WITH_UPLOAD + 1))
    fi
    if grep -qi "error\|traceback\|exception\|failed" "$log"; then
      LOGS_WITH_ERROR=$((LOGS_WITH_ERROR + 1))
    fi
  done

  echo "Logs with successful uploads: $LOGS_WITH_UPLOAD"
  echo "Logs with errors: $LOGS_WITH_ERROR"
  echo "Logs still empty: $LOGS_EMPTY"

  # Show error details
  if [ "$LOGS_WITH_ERROR" -gt 0 ]; then
    echo ""
    echo "=== Jobs with errors ==="
    for log in "$LOG_DIR"/*.log; do
      [ -f "$log" ] || continue
      if grep -qi "error\|traceback\|exception\|failed" "$log"; then
        name=$(basename "$log" .log)
        last_error=$(grep -i "error\|traceback\|exception\|failed" "$log" | tail -1)
        echo "  $name"
        echo "    → $last_error"
      fi
    done
  fi
fi

echo ""
echo "============================================"
