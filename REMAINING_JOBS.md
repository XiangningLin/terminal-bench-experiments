# Remaining Jobs - Supabase Verified

Generated: 2026-04-17 from `scripts/check_supabase_completion.py`

Total: 127 DONE / 70 PARTIAL / 22 NEED = 219 jobs

## Already running on machine 1 (swe-lancer phase4)

16 swe-lancer phase4 jobs are running. Do NOT run these on machine 2.

## For machine 2 (92 incomplete jobs, skip mimo/mmau-phase4)

### Setup

```bash
git clone git@github.com:XiangningLin/terminal-bench-experiments.git
cd terminal-bench-experiments
git checkout adapter0312
uv sync
cp /path/to/.env .  # needs DAYTONA_API_KEY, ANTHROPIC_API_KEY, model keys
```

### Run command

```bash
.venv/bin/python3 -u scripts/run_job.py \
  -c <config_path> \
  -f DaytonaRateLimitError -f DaytonaError -f DaytonaAuthorizationError \
  -f DaytonaAuthenticationError -f NonZeroAgentExitCodeError \
  -f RuntimeError -f CancelledError -f APIConnectionError
```

### Phase 2 (5 PARTIAL)

| Config | Status |
|--------|--------|
| `phase2/gpqa-diamond__claude-code__claude-sonnet-4-6.yaml` | 2/10 |
| `phase2/gpqa-diamond__gemini-cli__gemini-3-flash-preview.yaml` | 2/10 |
| `phase2/labbench__terminus-2__kimi-k2.5.yaml` | 2/10 |
| `phase2/labbench__terminus-2__mimo-v2-pro.yaml` | 2/10 (mimo - skip?) |
| `phase2/labbench__terminus-2__minimax-m2.5.yaml` | 2/10 |

### Phase 3 (11 PARTIAL)

| Config | Status |
|--------|--------|
| `phase3/arc-agi-2__gemini-cli__gemini-3.1-pro-preview.yaml` | 9/45 |
| `phase3/arc-agi-2__terminus-2__gpt-5.4.yaml` | 9/45 |
| `phase3/gpqa-diamond__claude-code__minimax-m2.5.yaml` | 18/90 |
| `phase3/gpqa-diamond__codex__gpt-5-nano.yaml` | 18/90 |
| `phase3/gpqa-diamond__terminus-2__deepseek-reasoner.yaml` | 18/90 |
| `phase3/gpqa-diamond__terminus-2__gemini-3-flash-preview.yaml` | 18/90 |
| `phase3/gpqa-diamond__terminus-2__gemini-3.1-pro-preview.yaml` | 18/90 |
| `phase3/humanevalfix__terminus-2__minimax-m2.5.yaml` | 15/75 |
| `phase3/ineqmath__terminus-2__mimo-v2-pro.yaml` | 8/9 (mimo - skip?) |
| `phase3/labbench__claude-code__deepseek-chat.yaml` | 17/90 |
| `phase3/labbench__terminus-2__deepseek-reasoner.yaml` | 17/90 |

### Phase 4 - Small/Medium (not swe-lancer, not mmau)

| Config | Status |
|--------|--------|
| `phase4/arc-agi-2__terminus-2__deepseek-reasoner.yaml` | 90/450 |
| `phase4/compilebench__gemini-cli__gemini-3-flash-preview.yaml` | 11/13 |
| `phase4/compilebench__gemini-cli__gemini-3.1-pro-preview.yaml` | 11/13 |
| `phase4/compilebench__terminus-2__gpt-5-mini.yaml` | 12/13 |
| `phase4/compilebench__terminus-2__gpt-5-nano.yaml` | 9/13 |
| `phase4/compilebench__terminus-2__mimo-v2-pro.yaml` | 0/13 (mimo - skip?) |
| `phase4/compilebench__terminus-2__minimax-m2.5.yaml` | 5/13 |
| `phase4/gpqa-diamond__terminus-2__gemini-3-flash-preview.yaml` | 178/890 |
| `phase4/gpqa-diamond__terminus-2__mimo-v2-pro.yaml` | 37/890 (mimo - skip?) |
| `phase4/ineqmath__claude-code__deepseek-chat.yaml` | 38/90 |
| `phase4/ineqmath__claude-code__kimi-k2.5.yaml` | 36/90 |
| `phase4/ineqmath__claude-code__mimo-v2-pro.yaml` | 12/90 (mimo - skip?) |
| `phase4/ineqmath__claude-code__minimax-m2.5.yaml` | 64/90 |
| `phase4/ineqmath__codex__gpt-5-mini.yaml` | 34/90 |
| `phase4/ineqmath__codex__gpt-5-nano.yaml` | 54/90 |
| `phase4/ineqmath__codex__gpt-5.4.yaml` | 30/90 |
| `phase4/ineqmath__gemini-cli__gemini-3-flash-preview.yaml` | 42/90 |
| `phase4/ineqmath__gemini-cli__gemini-3.1-pro-preview.yaml` | 28/90 |
| `phase4/ineqmath__terminus-2__deepseek-reasoner.yaml` | 55/90 |
| `phase4/ineqmath__terminus-2__gemini-3-flash-preview.yaml` | 35/90 |
| `phase4/ineqmath__terminus-2__gemini-3.1-pro-preview.yaml` | 48/90 |
| `phase4/ineqmath__terminus-2__gpt-5-mini.yaml` | 85/90 |
| `phase4/ineqmath__terminus-2__gpt-5-nano.yaml` | 76/90 |
| `phase4/ineqmath__terminus-2__gpt-5.4.yaml` | 36/90 |
| `phase4/ineqmath__terminus-2__kimi-k2.5.yaml` | 22/90 |
| `phase4/ineqmath__terminus-2__mimo-v2-pro.yaml` | 12/90 (mimo - skip?) |
| `phase4/ineqmath__terminus-2__minimax-m2.5.yaml` | 89/90 |
| `phase4/labbench__claude-code__deepseek-chat.yaml` | 162/810 |
| `phase4/labbench__claude-code__kimi-k2.5.yaml` | 162/810 |
| `phase4/labbench__terminus-2__gpt-5-mini.yaml` | 162/810 |
| `phase4/qcircuitbench__claude-code__deepseek-chat.yaml` | 24/25 |
| `phase4/qcircuitbench__codex__gpt-5.4.yaml` | 23/25 |
| `phase4/qcircuitbench__gemini-cli__gemini-3-flash-preview.yaml` | 24/25 |
| `phase4/qcircuitbench__gemini-cli__gemini-3.1-pro-preview.yaml` | 23/25 |
| `phase4/qcircuitbench__terminus-2__deepseek-reasoner.yaml` | 24/25 |
| `phase4/qcircuitbench__terminus-2__gemini-3-flash-preview.yaml` | 24/25 |
| `phase4/qcircuitbench__terminus-2__gemini-3.1-pro-preview.yaml` | 23/25 |
| `phase4/qcircuitbench__terminus-2__gpt-5-mini.yaml` | 24/25 |
| `phase4/qcircuitbench__terminus-2__gpt-5-nano.yaml` | 24/25 |
| `phase4/qcircuitbench__terminus-2__gpt-5.4.yaml` | 24/25 |
| `phase4/qcircuitbench__terminus-2__mimo-v2-pro.yaml` | 0/25 (mimo - skip?) |

### Phase 4 - SWE-Lancer (running on machine 1, but can split)

| Config | Status |
|--------|--------|
| `phase4/swe-lancer__claude-code__deepseek-chat.yaml` | 93/180 |
| `phase4/swe-lancer__claude-code__kimi-k2.5.yaml` | 98/180 |
| `phase4/swe-lancer__claude-code__mimo-v2-pro.yaml` | 0/180 (mimo) |
| `phase4/swe-lancer__claude-code__minimax-m2.5.yaml` | 26/180 |
| `phase4/swe-lancer__codex__gpt-5-nano.yaml` | 151/180 |
| `phase4/swe-lancer__codex__gpt-5.4.yaml` | 6/180 |
| `phase4/swe-lancer__gemini-cli__gemini-3-flash-preview.yaml` | 68/180 |
| `phase4/swe-lancer__gemini-cli__gemini-3.1-pro-preview.yaml` | 0/180 |
| `phase4/swe-lancer__terminus-2__deepseek-reasoner.yaml` | 7/180 |
| `phase4/swe-lancer__terminus-2__gemini-3-flash-preview.yaml` | 4/180 |
| `phase4/swe-lancer__terminus-2__gemini-3.1-pro-preview.yaml` | 162/180 |
| `phase4/swe-lancer__terminus-2__gpt-5-mini.yaml` | 4/180 |
| `phase4/swe-lancer__terminus-2__gpt-5-nano.yaml` | 0/180 |
| `phase4/swe-lancer__terminus-2__gpt-5.4.yaml` | 0/180 |
| `phase4/swe-lancer__terminus-2__kimi-k2.5.yaml` | 0/180 |
| `phase4/swe-lancer__terminus-2__mimo-v2-pro.yaml` | 0/180 (mimo) |
| `phase4/swe-lancer__terminus-2__minimax-m2.5.yaml` | 0/180 |

## Notes

- All config paths are relative to `outputs/adapter_experiments/batch1/contributors/Xiangning/`
- Skip `mimo` jobs (key has no funds)
- Skip `mmau phase4` (postponed, too large)
- Skip `glm-5` jobs (key unavailable)
- After running, use `scripts/reimport_to_supabase.py` to ensure all results are in DB
- Use `scripts/check_supabase_completion.py` to verify
