#!/bin/bash
# Check machine capacity for running experiments
# Usage: ./scripts/machine_capacity.sh

echo "=== Machine Capacity ==="
echo ""

# Memory
if command -v top &>/dev/null && [[ "$(uname)" == "Darwin" ]]; then
  MEM_LINE=$(top -l 1 -s 0 2>/dev/null | grep PhysMem)
  echo "Memory: $MEM_LINE"
  TOTAL_GB=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%.0f", $1/1024/1024/1024}')
elif command -v free &>/dev/null; then
  free -h | head -2
  TOTAL_GB=$(free -g | awk '/^Mem:/{print $2}')
fi
echo ""

# Disk
echo "Disk:"
df -h / | tail -1
if [ -d "jobs" ]; then
  echo "jobs/ size: $(du -sh jobs/ 2>/dev/null | awk '{print $1}')"
fi
echo ""

# CPU
echo "CPU: $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null) cores"
echo ""

# Current processes
PROCS=$(ps aux | grep run_job | grep -v grep | wc -l | tr -d ' ')
PROC_MEM=$(ps aux | grep run_job | grep -v grep | awk '{sum += $6} END {printf "%.1f", sum/1024/1024}')
echo "Current run_job processes: $PROCS (using ${PROC_MEM}GB)"
echo ""

# Estimate capacity (~300MB per process, leave 4GB for system)
if [ -n "$TOTAL_GB" ] && [ "$TOTAL_GB" -gt 0 ]; then
  AVAILABLE=$((TOTAL_GB - 4))
  MAX_PROCS=$((AVAILABLE * 1024 / 300))
  REMAINING=$((MAX_PROCS - PROCS))
  echo "=== Estimate ==="
  echo "  Total RAM: ${TOTAL_GB}GB"
  echo "  Available for jobs: ~${AVAILABLE}GB"
  echo "  Max processes (~300MB each): ~$MAX_PROCS"
  echo "  Currently running: $PROCS"
  echo "  Can add: ~$REMAINING more"
fi
