#!/bin/bash
source $HOME/.local/bin/env
source /users/shining/workplace/terminal-bench-experiments/.env
cd /users/shining/workplace/terminal-bench-experiments

FILTER="-f DaytonaRateLimitError -f DaytonaAuthorizationError -f DaytonaError -f DaytonaAuthenticationError -f DaytonaNotFoundError -f NonZeroAgentExitCodeError"
DIR=outputs/adapter_experiments/batch1/contributors/Xiangning
DATASET=$1

for phase in phase4 phase3 phase2; do
  for config in $DIR/$phase/${DATASET}__*.yaml; do
    [ -f "$config" ] || continue
    echo "[$(date)] Starting $config"
    uv run python scripts/run_job.py -c "$config" $FILTER
    echo "[$(date)] Finished $config"
  done
done
