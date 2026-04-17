#!/bin/bash
# Auto-queue: monitors running jobs, adds new ones as others finish
# Keeps total processes at MAX_PROCESSES
cd "$(dirname "$0")"
source /Users/linxiangning/Desktop/projects/tb_adapter_project/.env

MAX_PROCESSES=35
LOG_DIR="/tmp/job-logs-auto-queue"
mkdir -p "$LOG_DIR"
FILTER="-f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError -f RuntimeError -f CancelledError -f APIConnectionError"

echo "Auto-queue started at $(date)"
echo "Max processes: $MAX_PROCESSES"

while true; do
  # Count current run_job processes
  current=$(ps aux | grep run_job | grep -v grep | wc -l | tr -d ' ')

  if [ "$current" -ge "$MAX_PROCESSES" ]; then
    sleep 60
    continue
  fi

  # Find next job to run (phase2/3 first, then phase4, skip glm-5)
  next_config=$(python3 -c "
import glob, yaml, os, subprocess, json, sys

running = set()
ps = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
for line in ps.stdout.split('\n'):
    if 'run_job' in line and 'grep' not in line:
        for part in line.split():
            if 'job-configs/' in part or 'Xiangning' in part:
                name = part.split('/')[-1].replace('.yaml','')
                running.add(name)

# Priority: phase2 > phase3 > phase4 (skip mmau phase4)
for phase_dir in ['phase2', 'phase3', 'phase4']:
    for f in sorted(glob.glob(f'outputs/adapter_experiments/batch1/contributors/Xiangning/{phase_dir}/*.yaml')):
        if 'registries' in f or 'glm-5' in f: continue
        with open(f) as fh: cfg = yaml.safe_load(fh)
        jn = cfg.get('job_name', '')
        if jn in running: continue
        # Skip mmau phase4 (too large)
        if 'mmau' in jn and 'phase4' in jn: continue
        # Skip mimo (key has no funds)
        if 'mimo' in jn: continue
        # Check if job has enough successful trials locally
        jd = f'jobs/{jn}'
        if os.path.isdir(jd):
            ok = sum(1 for t in os.listdir(jd)
                     if os.path.isdir(os.path.join(jd, t))
                     and os.path.exists(os.path.join(jd, t, 'result.json'))
                     and not json.load(open(os.path.join(jd, t, 'result.json'))).get('exception_info'))
            # Rough expected: phase2=5-50, phase3=25-450, phase4=65-900
            parts2 = jn.split('__')
            phase2 = parts2[-1] if parts2 else ''
            min_ok = {'phase2': 3, 'phase3': 10, 'phase4': 50}.get(phase2, 5)
            if ok >= min_ok: continue
        # Remove stale config.json
        cfg_path = f'jobs/{jn}/config.json'
        if os.path.exists(cfg_path): os.remove(cfg_path)
        print(f)
        sys.exit(0)
" 2>/dev/null)

  if [ -z "$next_config" ]; then
    echo "[$(date +%H:%M)] No more jobs to run. Waiting..."
    sleep 120
    # Check if all done
    remaining=$(python3 -c "
import glob, yaml, os, json
count = 0
for f in sorted(glob.glob('outputs/adapter_experiments/batch1/contributors/Xiangning/**/*.yaml', recursive=True)):
    if 'registries' in f or 'glm-5' in f: continue
    with open(f) as fh: cfg = yaml.safe_load(fh)
    jn = cfg.get('job_name', '')
    if 'mmau' in jn and 'phase4' in jn: continue
    if 'mimo' in jn: continue
    jd = f'jobs/{jn}'
    if os.path.isdir(jd):
        ok = 0
        for t in os.listdir(jd):
            rp2 = os.path.join(jd, t, 'result.json')
            if os.path.exists(rp2):
                try:
                    if not json.load(open(rp2)).get('exception_info'): ok += 1
                except: pass
        parts = jn.split('__')
        phase = parts[-1] if parts else ''
        min_ok = {'phase2': 3, 'phase3': 10, 'phase4': 50}.get(phase, 5)
        if ok >= min_ok: continue
    count += 1
print(count)
" 2>/dev/null)
    if [ "$remaining" = "0" ]; then
      echo "[$(date +%H:%M)] ALL JOBS DONE!"
      break
    fi
    continue
  fi

  job_name=$(grep "^job_name:" "$next_config" | awk '{print $2}')

  if [[ "$job_name" == *claude-code* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"
  elif [[ "$job_name" == *codex* ]] || [[ "$job_name" == *gemini-cli* ]]; then
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_2"
  else
    export DAYTONA_API_KEY="$DAYTONA_API_KEY_3"
  fi

  nohup .venv/bin/python3 -u scripts/run_job.py -c "$next_config" $FILTER > "$LOG_DIR/${job_name}.log" 2>&1 &
  echo "[$(date +%H:%M)] START: $job_name (processes: $((current + 1))/$MAX_PROCESSES)"
  sleep 15
done
