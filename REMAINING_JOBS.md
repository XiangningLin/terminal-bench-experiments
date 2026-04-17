# Remaining Jobs

Updated: 2026-04-17 16:30

Running on machine 1: 16 swe-lancer phase4 + 2 terminus-2 qwen phase2/3
Remaining to run: 42 jobs

## Setup (new machine)

```bash
git clone git@github.com:XiangningLin/terminal-bench-experiments.git
cd terminal-bench-experiments && git checkout adapter0312
ln -s /path/to/harbor ../harbor
uv sync && cp /path/to/.env .
.venv/bin/python3 -c "from harbor.job import Job; print('OK')"
```

## Run command

```bash
source .env
export DAYTONA_API_KEY="$DAYTONA_API_KEY_1"  # or _2 or _3

.venv/bin/python3 -u scripts/run_job.py -c <config_path> \
  -f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError \
  -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError \
  -f RuntimeError -f CancelledError -f APIConnectionError
```

**Important: Launch with 60 second intervals to avoid Daytona rate limit (600/min)**

## Phase2 (4 jobs)

```
phase2/labbench__terminus-2__kimi-k2.5.yaml                    # ok=0/3
phase2/labbench__terminus-2__minimax-m2.5.yaml                  # ok=0/3
phase2/qcircuitbench__claude-code__claude-sonnet-4-6.yaml       # ok=0/3
phase2/qcircuitbench__terminus-2__deepseek-reasoner.yaml        # ok=0/3
```

## Phase3 (18 jobs)

```
phase3/compilebench__claude-code__kimi-k2.5.yaml               # ok=5/10
phase3/compilebench__claude-code__minimax-m2.5.yaml             # ok=5/10
phase3/compilebench__codex__gpt-5-nano.yaml                     # ok=5/10
phase3/compilebench__codex__gpt-5.4.yaml                        # ok=5/10
phase3/compilebench__gemini-cli__gemini-3.1-pro-preview.yaml    # ok=5/10
phase3/compilebench__terminus-2__deepseek-reasoner.yaml          # ok=5/10
phase3/compilebench__terminus-2__gemini-3.1-pro-preview.yaml     # ok=5/10
phase3/compilebench__terminus-2__gpt-5-mini.yaml                # ok=5/10
phase3/compilebench__terminus-2__gpt-5-nano.yaml                # ok=7/10
phase3/compilebench__terminus-2__gpt-5.4.yaml                   # ok=5/10
phase3/compilebench__terminus-2__kimi-k2.5.yaml                 # ok=5/10
phase3/compilebench__terminus-2__minimax-m2.5.yaml              # ok=5/10
phase3/compilebench__terminus-2__qwen3-max.yaml                 # ok=5/10
phase3/labbench__claude-code__deepseek-chat.yaml                # ok=3/10
phase3/labbench__terminus-2__deepseek-reasoner.yaml              # ok=0/10
phase3/swe-lancer__qwen-coder__qwen3-max.yaml                  # ok=9/10
```

## Phase4 (20 jobs)

```
# Qwen (new, 0%)
phase4/aime__qwen-coder__qwen3-max.yaml                        # ok=0/50
phase4/aime__terminus-2__qwen3-max.yaml                         # ok=0/50
phase4/arc-agi-2__qwen-coder__qwen3-max.yaml                   # ok=0/50
phase4/arc-agi-2__terminus-2__qwen3-max.yaml                    # ok=0/50
phase4/compilebench__qwen-coder__qwen3-max.yaml                # ok=0/50
phase4/compilebench__terminus-2__qwen3-max.yaml                 # ok=0/50
phase4/gpqa-diamond__qwen-coder__qwen3-max.yaml                # ok=0/50
phase4/gpqa-diamond__terminus-2__qwen3-max.yaml                 # ok=0/50
phase4/ineqmath__qwen-coder__qwen3-max.yaml                    # ok=0/50
phase4/ineqmath__terminus-2__qwen3-max.yaml                     # ok=0/50
phase4/labbench__qwen-coder__qwen3-max.yaml                    # ok=0/50
phase4/labbench__terminus-2__qwen3-max.yaml                     # ok=0/50
phase4/qcircuitbench__qwen-coder__qwen3-max.yaml               # ok=0/50
phase4/qcircuitbench__terminus-2__qwen3-max.yaml                # ok=0/50
phase4/swe-lancer__qwen-coder__qwen3-max.yaml                  # ok=0/50
phase4/swe-lancer__terminus-2__qwen3-max.yaml                   # ok=0/50

# Other incomplete
phase4/arc-agi-2__terminus-2__deepseek-reasoner.yaml            # ok=3/50
phase4/compilebench__terminus-2__gpt-5-nano.yaml                # ok=33/50
phase4/compilebench__terminus-2__minimax-m2.5.yaml              # ok=28/50
phase4/labbench__claude-code__deepseek-chat.yaml                # ok=20/50
phase4/qcircuitbench__terminus-2__deepseek-reasoner.yaml        # ok=29/50
phase4/qcircuitbench__terminus-2__gpt-5-nano.yaml               # ok=26/50
```

## SWE-Lancer Phase4 (running on machine 1, can split to machine 2)

These are already running but will take ~65 hours. Split some to machine 2 to speed up:

```
phase4/swe-lancer__codex__gpt-5.4.yaml                         # ok=356/900
phase4/swe-lancer__gemini-cli__gemini-3-flash-preview.yaml      # ok=322/900
phase4/swe-lancer__gemini-cli__gemini-3.1-pro-preview.yaml      # ok=146/900
phase4/swe-lancer__terminus-2__gemini-3-flash-preview.yaml      # ok=253/900
phase4/swe-lancer__terminus-2__gpt-5-mini.yaml                  # ok=343/900
phase4/swe-lancer__terminus-2__gpt-5-nano.yaml                  # ok=178/900
phase4/swe-lancer__terminus-2__kimi-k2.5.yaml                   # ok=238/900
phase4/swe-lancer__terminus-2__minimax-m2.5.yaml                # ok=243/900
```

## Notes

- All config paths relative to `outputs/adapter_experiments/batch1/contributors/Xiangning/`
- Skip `glm-5`, `mimo` (keys unavailable)
- Skip `mmau phase4` (postponed)
- For terminus-2 + qwen3-max: api_key is in `kwargs.llm_kwargs.api_key`
- For qwen-coder + qwen3-max: api_key is in `env.OPENAI_API_KEY`
- After running: `scripts/reimport_to_supabase.py`
- Check completion: `scripts/check_supabase_completion.py`
- Machine capacity: `bash scripts/machine_capacity.sh`
- Status: `.venv/bin/python3 scripts/status.py`
