# Terminal Bench Experiments - Xiangning's Workspace

## Quick Reference

### Supabase Access
- Credentials in `.env`: `SUPABASE_URL`, `SUPABASE_SECRET_KEY`
- REST API: `curl -s "$SUPABASE_URL/rest/v1/{table}?{filters}" -H "apikey: $SUPABASE_SECRET_KEY" -H "Authorization: Bearer $SUPABASE_SECRET_KEY"`
- Supabase username for Xiangning: `linxiangning`

### Xiangning's Adapters (10 total)
aime, swe-lancer, arc-agi-2, compilebench, gpqa-diamond, humanevalfix, ineqmath, labbench, mmau, qcircuitbench

### Check Job Status on Supabase
```bash
# Not started jobs
curl -s "$SUPABASE_URL/rest/v1/job?username=eq.linxiangning&started_at=is.null&select=job_name,n_trials" \
  -H "apikey: $SUPABASE_SECRET_KEY" -H "Authorization: Bearer $SUPABASE_SECRET_KEY"

# Jobs with errors (query per job_id)
curl -s "$SUPABASE_URL/rest/v1/trial?job_id=eq.{JOB_ID}&exception_info=not.is.null&select=exception_info" \
  -H "apikey: $SUPABASE_SECRET_KEY" -H "Authorization: Bearer $SUPABASE_SECRET_KEY"

# Count trials for a job (check Content-Range header)
curl -s "$SUPABASE_URL/rest/v1/trial?job_id=eq.{JOB_ID}&select=id" \
  -H "apikey: $SUPABASE_SECRET_KEY" -H "Authorization: Bearer $SUPABASE_SECRET_KEY" \
  -H "Prefer: count=exact" -H "Range-Unit: items" -H "Range: 0-0"
```

### Running a Job
```bash
source .env
uv run python scripts/run_job.py -c <config.yaml>
```
- Results auto-upload to Supabase after each trial
- Supports resume: re-run same command to continue from where it stopped

### Rerunning Failed Jobs (filter Daytona errors)
```bash
uv run python scripts/run_job.py -c <config.yaml> \
  -f DaytonaRateLimitError -f DaytonaAuthorizationError -f DaytonaError \
  -f DaytonaAuthenticationError -f DaytonaNotFoundError -f NonZeroAgentExitCodeError
```

### Parallel Execution
```bash
# Run multiple datasets in parallel, serial within each dataset
FILTER="-f DaytonaRateLimitError -f DaytonaAuthorizationError -f DaytonaError -f DaytonaAuthenticationError -f DaytonaNotFoundError -f NonZeroAgentExitCodeError"
DIR=outputs/adapter_experiments/batch1/contributors/Xiangning/phase4

for dataset in mmau swe-lancer compilebench ineqmath qcircuitbench; do
  (
    for config in $DIR/${dataset}__*.yaml; do
      uv run python scripts/run_job.py -c "$config" $FILTER
    done
  ) &
done
wait
```

### Config Structure
- Configs: `outputs/adapter_experiments/batch1/contributors/Xiangning/{phase}/{adapter}__{agent}__{model}.yaml`
- Registries: `outputs/adapter_experiments/batch1/contributors/Xiangning/{phase}/registries/{adapter}.json`
- Runner manifest (agent/model matrix): `outputs/adapter_experiments/batch1/runners.generated.yaml`
- Coordination manifest: `adapter_experiments/manifests/batch1_coordination.yaml`

### Generating New Configs
To generate a config for a new job, create a YAML like:
```yaml
jobs_dir: jobs
n_attempts: 5
timeout_multiplier: 1.0
orchestrator:
  type: local
  n_concurrent_trials: 32
  quiet: false
  retry:
    max_retries: 3
    exclude_exceptions: [BadRequestError, RateLimitError, AgentTimeoutError, VerifierTimeoutError, RewardFileNotFoundError]
    wait_multiplier: 1.0
    min_wait_sec: 1.0
    max_wait_sec: 60.0
environment:
  type: daytona          # change to "docker" for local execution
  force_build: false
  delete: true
job_name: {adapter}__{agent}__{model}__batch1__{phase}
agents:
- name: {agent}
  model_name: {provider}/{model}   # from runners.generated.yaml
datasets:
- registry:
    name: local
    path: outputs/adapter_experiments/batch1/contributors/Xiangning/{phase}/registries/{adapter}.json
  name: adapter-experiments-batch1-{phase}
  version: '1.0'
```

### Common Error Types
| Error | Cause | Action |
|-------|-------|--------|
| DaytonaRateLimitError | Daytona sandbox rate limit | Rerun with -f flag, or switch to docker |
| DaytonaAuthorizationError | Daytona auth issue | Rerun with -f flag |
| DaytonaError | Generic Daytona failure | Rerun with -f flag |
| AgentTimeoutError | Agent took too long | Expected for some tasks, usually not worth rerunning |
| NonZeroAgentExitCodeError | Agent crashed | May need investigation |

### Manual Import (if auto-upload failed)
```bash
uv run tbx validate --job-path jobs/<job_name>
uv run tbx import --job-path jobs/<job_name>
```
