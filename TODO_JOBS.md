# Jobs To Run (450 total)

## Machine Assignment Suggestion

| Machine | Datasets | Job Count |
|---------|----------|----------|
| Machine 1 | mmau, swe-lancer | 91 |
| Machine 2 | aime, compilebench, ineqmath | 155 |
| Machine 3 | arc-agi-2, gpqa-diamond, humanevalfix, labbench, qcircuitbench | 204 |

## Run Command

```bash
source .env
FILTER="-f DaytonaRateLimitError -f DaytonaAuthorizationError -f DaytonaError -f DaytonaAuthenticationError -f DaytonaNotFoundError -f NonZeroAgentExitCodeError"
DIR=outputs/adapter_experiments/batch1/contributors/Xiangning

# Replace DATASETS with your assigned datasets
DATASETS="mmau swe-lancer"

for dataset in $DATASETS; do
  (
    for phase in phase2 phase3 phase4; do
      for config in $DIR/$phase/${dataset}__*.yaml; do
        [ -f "$config" ] || continue
        echo "[$(date)] Starting $config"
        uv run python scripts/run_job.py -c "$config" $FILTER
        echo "[$(date)] Finished $config"
      done
    done
  ) &
done
wait
echo "All done!"
```

## Full Job List by Dataset

### aime (51)
- aime__claude-code__deepseek-chat__batch1__phase2
- aime__claude-code__deepseek-chat__batch1__phase3
- aime__claude-code__deepseek-chat__batch1__phase4
- aime__claude-code__glm-5__batch1__phase4
- aime__claude-code__kimi-k2.5__batch1__phase2
- aime__claude-code__kimi-k2.5__batch1__phase3
- aime__claude-code__kimi-k2.5__batch1__phase4
- aime__claude-code__mimo-v2-pro__batch1__phase2
- aime__claude-code__mimo-v2-pro__batch1__phase3
- aime__claude-code__mimo-v2-pro__batch1__phase4
- aime__claude-code__minimax-m2.5__batch1__phase2
- aime__claude-code__minimax-m2.5__batch1__phase4
- aime__codex__gpt-5-mini__batch1__phase2
- aime__codex__gpt-5-mini__batch1__phase3
- aime__codex__gpt-5-mini__batch1__phase4
- aime__codex__gpt-5-nano__batch1__phase2
- aime__codex__gpt-5-nano__batch1__phase3
- aime__codex__gpt-5-nano__batch1__phase4
- aime__codex__gpt-5.4__batch1__phase2
- aime__codex__gpt-5.4__batch1__phase3
- aime__codex__gpt-5.4__batch1__phase4
- aime__gemini-cli__gemini-3-flash-preview__batch1__phase2
- aime__gemini-cli__gemini-3-flash-preview__batch1__phase3
- aime__gemini-cli__gemini-3-flash-preview__batch1__phase4
- aime__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- aime__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- aime__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- aime__terminus-2__deepseek-reasoner__batch1__phase2
- aime__terminus-2__deepseek-reasoner__batch1__phase3
- aime__terminus-2__deepseek-reasoner__batch1__phase4
- aime__terminus-2__gemini-3-flash-preview__batch1__phase2
- aime__terminus-2__gemini-3-flash-preview__batch1__phase3
- aime__terminus-2__gemini-3-flash-preview__batch1__phase4
- aime__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- aime__terminus-2__gemini-3.1-pro-preview__batch1__phase3
- aime__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- aime__terminus-2__glm-5__batch1__phase2
- aime__terminus-2__glm-5__batch1__phase3
- aime__terminus-2__glm-5__batch1__phase4
- aime__terminus-2__gpt-5-mini__batch1__phase2
- aime__terminus-2__gpt-5-mini__batch1__phase3
- aime__terminus-2__gpt-5-nano__batch1__phase2
- aime__terminus-2__gpt-5-nano__batch1__phase3
- aime__terminus-2__gpt-5.4__batch1__phase2
- aime__terminus-2__gpt-5.4__batch1__phase3
- aime__terminus-2__kimi-k2.5__batch1__phase2
- aime__terminus-2__kimi-k2.5__batch1__phase3
- aime__terminus-2__mimo-v2-pro__batch1__phase2
- aime__terminus-2__mimo-v2-pro__batch1__phase3
- aime__terminus-2__minimax-m2.5__batch1__phase2
- aime__terminus-2__minimax-m2.5__batch1__phase3

### arc-agi-2 (29)
- arc-agi-2__claude-code__deepseek-chat__batch1__phase2
- arc-agi-2__claude-code__glm-5__batch1__phase2
- arc-agi-2__claude-code__glm-5__batch1__phase4
- arc-agi-2__claude-code__kimi-k2.5__batch1__phase2
- arc-agi-2__claude-code__kimi-k2.5__batch1__phase4
- arc-agi-2__claude-code__mimo-v2-pro__batch1__phase2
- arc-agi-2__claude-code__mimo-v2-pro__batch1__phase4
- arc-agi-2__claude-code__minimax-m2.5__batch1__phase2
- arc-agi-2__claude-code__minimax-m2.5__batch1__phase4
- arc-agi-2__codex__gpt-5-mini__batch1__phase2
- arc-agi-2__codex__gpt-5-mini__batch1__phase3
- arc-agi-2__codex__gpt-5-mini__batch1__phase4
- arc-agi-2__codex__gpt-5-nano__batch1__phase2
- arc-agi-2__codex__gpt-5-nano__batch1__phase3
- arc-agi-2__codex__gpt-5-nano__batch1__phase4
- arc-agi-2__codex__gpt-5.4__batch1__phase2
- arc-agi-2__gemini-cli__gemini-3-flash-preview__batch1__phase2
- arc-agi-2__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- arc-agi-2__terminus-2__deepseek-reasoner__batch1__phase2
- arc-agi-2__terminus-2__deepseek-reasoner__batch1__phase3
- arc-agi-2__terminus-2__gemini-3-flash-preview__batch1__phase2
- arc-agi-2__terminus-2__gemini-3-flash-preview__batch1__phase3
- arc-agi-2__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- arc-agi-2__terminus-2__gpt-5-mini__batch1__phase2
- arc-agi-2__terminus-2__gpt-5-nano__batch1__phase2
- arc-agi-2__terminus-2__gpt-5.4__batch1__phase2
- arc-agi-2__terminus-2__gpt-5.4__batch1__phase3
- arc-agi-2__terminus-2__kimi-k2.5__batch1__phase2
- arc-agi-2__terminus-2__minimax-m2.5__batch1__phase2

### compilebench (54)
- compilebench__claude-code__deepseek-chat__batch1__phase2
- compilebench__claude-code__deepseek-chat__batch1__phase3
- compilebench__claude-code__deepseek-chat__batch1__phase4
- compilebench__claude-code__glm-5__batch1__phase2
- compilebench__claude-code__glm-5__batch1__phase4
- compilebench__claude-code__kimi-k2.5__batch1__phase2
- compilebench__claude-code__kimi-k2.5__batch1__phase3
- compilebench__claude-code__kimi-k2.5__batch1__phase4
- compilebench__claude-code__mimo-v2-pro__batch1__phase2
- compilebench__claude-code__mimo-v2-pro__batch1__phase3
- compilebench__claude-code__mimo-v2-pro__batch1__phase4
- compilebench__claude-code__minimax-m2.5__batch1__phase2
- compilebench__claude-code__minimax-m2.5__batch1__phase3
- compilebench__claude-code__minimax-m2.5__batch1__phase4
- compilebench__codex__gpt-5-mini__batch1__phase2
- compilebench__codex__gpt-5-mini__batch1__phase3
- compilebench__codex__gpt-5-mini__batch1__phase4
- compilebench__codex__gpt-5-nano__batch1__phase2
- compilebench__codex__gpt-5-nano__batch1__phase3
- compilebench__codex__gpt-5-nano__batch1__phase4
- compilebench__codex__gpt-5.4__batch1__phase2
- compilebench__codex__gpt-5.4__batch1__phase3
- compilebench__codex__gpt-5.4__batch1__phase4
- compilebench__gemini-cli__gemini-3-flash-preview__batch1__phase2
- compilebench__gemini-cli__gemini-3-flash-preview__batch1__phase3
- compilebench__gemini-cli__gemini-3-flash-preview__batch1__phase4
- compilebench__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- compilebench__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- compilebench__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- compilebench__terminus-2__deepseek-reasoner__batch1__phase2
- compilebench__terminus-2__deepseek-reasoner__batch1__phase3
- compilebench__terminus-2__deepseek-reasoner__batch1__phase4
- compilebench__terminus-2__gemini-3-flash-preview__batch1__phase2
- compilebench__terminus-2__gemini-3-flash-preview__batch1__phase3
- compilebench__terminus-2__gemini-3-flash-preview__batch1__phase4
- compilebench__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- compilebench__terminus-2__gemini-3.1-pro-preview__batch1__phase3
- compilebench__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- compilebench__terminus-2__glm-5__batch1__phase2
- compilebench__terminus-2__glm-5__batch1__phase3
- compilebench__terminus-2__glm-5__batch1__phase4
- compilebench__terminus-2__gpt-5-mini__batch1__phase2
- compilebench__terminus-2__gpt-5-mini__batch1__phase3
- compilebench__terminus-2__gpt-5-mini__batch1__phase4
- compilebench__terminus-2__gpt-5-nano__batch1__phase2
- compilebench__terminus-2__gpt-5-nano__batch1__phase4
- compilebench__terminus-2__gpt-5.4__batch1__phase2
- compilebench__terminus-2__gpt-5.4__batch1__phase4
- compilebench__terminus-2__kimi-k2.5__batch1__phase2
- compilebench__terminus-2__kimi-k2.5__batch1__phase4
- compilebench__terminus-2__mimo-v2-pro__batch1__phase2
- compilebench__terminus-2__mimo-v2-pro__batch1__phase4
- compilebench__terminus-2__minimax-m2.5__batch1__phase2
- compilebench__terminus-2__minimax-m2.5__batch1__phase4

### gpqa-diamond (40)
- gpqa-diamond__claude-code__deepseek-chat__batch1__phase3
- gpqa-diamond__claude-code__deepseek-chat__batch1__phase4
- gpqa-diamond__claude-code__glm-5__batch1__phase3
- gpqa-diamond__claude-code__glm-5__batch1__phase4
- gpqa-diamond__claude-code__kimi-k2.5__batch1__phase3
- gpqa-diamond__claude-code__mimo-v2-pro__batch1__phase2
- gpqa-diamond__claude-code__mimo-v2-pro__batch1__phase3
- gpqa-diamond__claude-code__minimax-m2.5__batch1__phase2
- gpqa-diamond__claude-code__minimax-m2.5__batch1__phase3
- gpqa-diamond__codex__gpt-5-mini__batch1__phase2
- gpqa-diamond__codex__gpt-5-mini__batch1__phase4
- gpqa-diamond__codex__gpt-5-nano__batch1__phase2
- gpqa-diamond__codex__gpt-5-nano__batch1__phase4
- gpqa-diamond__codex__gpt-5.4__batch1__phase3
- gpqa-diamond__gemini-cli__gemini-3-flash-preview__batch1__phase2
- gpqa-diamond__gemini-cli__gemini-3-flash-preview__batch1__phase3
- gpqa-diamond__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- gpqa-diamond__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- gpqa-diamond__terminus-2__deepseek-reasoner__batch1__phase2
- gpqa-diamond__terminus-2__deepseek-reasoner__batch1__phase3
- gpqa-diamond__terminus-2__gemini-3-flash-preview__batch1__phase2
- gpqa-diamond__terminus-2__gemini-3-flash-preview__batch1__phase3
- gpqa-diamond__terminus-2__gemini-3-flash-preview__batch1__phase4
- gpqa-diamond__terminus-2__gemini-3.1-pro-preview__batch1__phase3
- gpqa-diamond__terminus-2__glm-5__batch1__phase2
- gpqa-diamond__terminus-2__gpt-5-mini__batch1__phase3
- gpqa-diamond__terminus-2__gpt-5-mini__batch1__phase4
- gpqa-diamond__terminus-2__gpt-5-nano__batch1__phase2
- gpqa-diamond__terminus-2__gpt-5-nano__batch1__phase3
- gpqa-diamond__terminus-2__gpt-5-nano__batch1__phase4
- gpqa-diamond__terminus-2__gpt-5.4__batch1__phase3
- gpqa-diamond__terminus-2__gpt-5.4__batch1__phase4
- gpqa-diamond__terminus-2__kimi-k2.5__batch1__phase2
- gpqa-diamond__terminus-2__kimi-k2.5__batch1__phase3
- gpqa-diamond__terminus-2__kimi-k2.5__batch1__phase4
- gpqa-diamond__terminus-2__mimo-v2-pro__batch1__phase2
- gpqa-diamond__terminus-2__mimo-v2-pro__batch1__phase3
- gpqa-diamond__terminus-2__mimo-v2-pro__batch1__phase4
- gpqa-diamond__terminus-2__minimax-m2.5__batch1__phase3
- gpqa-diamond__terminus-2__minimax-m2.5__batch1__phase4

### humanevalfix (43)
- humanevalfix__claude-code__deepseek-chat__batch1__phase3
- humanevalfix__claude-code__deepseek-chat__batch1__phase4
- humanevalfix__claude-code__glm-5__batch1__phase3
- humanevalfix__claude-code__glm-5__batch1__phase4
- humanevalfix__claude-code__kimi-k2.5__batch1__phase2
- humanevalfix__claude-code__kimi-k2.5__batch1__phase3
- humanevalfix__claude-code__kimi-k2.5__batch1__phase4
- humanevalfix__claude-code__mimo-v2-pro__batch1__phase2
- humanevalfix__claude-code__mimo-v2-pro__batch1__phase3
- humanevalfix__claude-code__mimo-v2-pro__batch1__phase4
- humanevalfix__claude-code__minimax-m2.5__batch1__phase2
- humanevalfix__claude-code__minimax-m2.5__batch1__phase3
- humanevalfix__codex__gpt-5-mini__batch1__phase2
- humanevalfix__codex__gpt-5-mini__batch1__phase4
- humanevalfix__codex__gpt-5-nano__batch1__phase2
- humanevalfix__codex__gpt-5-nano__batch1__phase4
- humanevalfix__codex__gpt-5.4__batch1__phase2
- humanevalfix__codex__gpt-5.4__batch1__phase4
- humanevalfix__gemini-cli__gemini-3-flash-preview__batch1__phase2
- humanevalfix__gemini-cli__gemini-3-flash-preview__batch1__phase3
- humanevalfix__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- humanevalfix__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- humanevalfix__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- humanevalfix__terminus-2__deepseek-reasoner__batch1__phase2
- humanevalfix__terminus-2__deepseek-reasoner__batch1__phase3
- humanevalfix__terminus-2__deepseek-reasoner__batch1__phase4
- humanevalfix__terminus-2__gemini-3-flash-preview__batch1__phase2
- humanevalfix__terminus-2__gemini-3-flash-preview__batch1__phase4
- humanevalfix__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- humanevalfix__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- humanevalfix__terminus-2__glm-5__batch1__phase2
- humanevalfix__terminus-2__gpt-5-mini__batch1__phase2
- humanevalfix__terminus-2__gpt-5-mini__batch1__phase4
- humanevalfix__terminus-2__gpt-5-nano__batch1__phase2
- humanevalfix__terminus-2__gpt-5-nano__batch1__phase4
- humanevalfix__terminus-2__gpt-5.4__batch1__phase2
- humanevalfix__terminus-2__gpt-5.4__batch1__phase3
- humanevalfix__terminus-2__kimi-k2.5__batch1__phase2
- humanevalfix__terminus-2__kimi-k2.5__batch1__phase4
- humanevalfix__terminus-2__mimo-v2-pro__batch1__phase2
- humanevalfix__terminus-2__mimo-v2-pro__batch1__phase4
- humanevalfix__terminus-2__minimax-m2.5__batch1__phase2
- humanevalfix__terminus-2__minimax-m2.5__batch1__phase3

### ineqmath (59)
- ineqmath__claude-code__deepseek-chat__batch1__phase2
- ineqmath__claude-code__deepseek-chat__batch1__phase3
- ineqmath__claude-code__deepseek-chat__batch1__phase4
- ineqmath__claude-code__glm-5__batch1__phase2
- ineqmath__claude-code__glm-5__batch1__phase3
- ineqmath__claude-code__glm-5__batch1__phase4
- ineqmath__claude-code__kimi-k2.5__batch1__phase2
- ineqmath__claude-code__kimi-k2.5__batch1__phase3
- ineqmath__claude-code__kimi-k2.5__batch1__phase4
- ineqmath__claude-code__mimo-v2-pro__batch1__phase2
- ineqmath__claude-code__mimo-v2-pro__batch1__phase3
- ineqmath__claude-code__mimo-v2-pro__batch1__phase4
- ineqmath__claude-code__minimax-m2.5__batch1__phase2
- ineqmath__claude-code__minimax-m2.5__batch1__phase3
- ineqmath__claude-code__minimax-m2.5__batch1__phase4
- ineqmath__codex__gpt-5-mini__batch1__phase2
- ineqmath__codex__gpt-5-mini__batch1__phase3
- ineqmath__codex__gpt-5-mini__batch1__phase4
- ineqmath__codex__gpt-5-nano__batch1__phase2
- ineqmath__codex__gpt-5-nano__batch1__phase3
- ineqmath__codex__gpt-5-nano__batch1__phase4
- ineqmath__codex__gpt-5.4__batch1__phase2
- ineqmath__codex__gpt-5.4__batch1__phase3
- ineqmath__codex__gpt-5.4__batch1__phase4
- ineqmath__gemini-cli__gemini-3-flash-preview__batch1__phase2
- ineqmath__gemini-cli__gemini-3-flash-preview__batch1__phase3
- ineqmath__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- ineqmath__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- ineqmath__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- ineqmath__terminus-2__deepseek-reasoner__batch1__phase2
- ineqmath__terminus-2__deepseek-reasoner__batch1__phase3
- ineqmath__terminus-2__deepseek-reasoner__batch1__phase4
- ineqmath__terminus-2__gemini-3-flash-preview__batch1__phase2
- ineqmath__terminus-2__gemini-3-flash-preview__batch1__phase3
- ineqmath__terminus-2__gemini-3-flash-preview__batch1__phase4
- ineqmath__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- ineqmath__terminus-2__gemini-3.1-pro-preview__batch1__phase3
- ineqmath__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- ineqmath__terminus-2__glm-5__batch1__phase2
- ineqmath__terminus-2__glm-5__batch1__phase3
- ineqmath__terminus-2__glm-5__batch1__phase4
- ineqmath__terminus-2__gpt-5-mini__batch1__phase2
- ineqmath__terminus-2__gpt-5-mini__batch1__phase3
- ineqmath__terminus-2__gpt-5-mini__batch1__phase4
- ineqmath__terminus-2__gpt-5-nano__batch1__phase2
- ineqmath__terminus-2__gpt-5-nano__batch1__phase3
- ineqmath__terminus-2__gpt-5-nano__batch1__phase4
- ineqmath__terminus-2__gpt-5.4__batch1__phase2
- ineqmath__terminus-2__gpt-5.4__batch1__phase3
- ineqmath__terminus-2__gpt-5.4__batch1__phase4
- ineqmath__terminus-2__kimi-k2.5__batch1__phase2
- ineqmath__terminus-2__kimi-k2.5__batch1__phase3
- ineqmath__terminus-2__kimi-k2.5__batch1__phase4
- ineqmath__terminus-2__mimo-v2-pro__batch1__phase2
- ineqmath__terminus-2__mimo-v2-pro__batch1__phase3
- ineqmath__terminus-2__mimo-v2-pro__batch1__phase4
- ineqmath__terminus-2__minimax-m2.5__batch1__phase2
- ineqmath__terminus-2__minimax-m2.5__batch1__phase3
- ineqmath__terminus-2__minimax-m2.5__batch1__phase4

### labbench (38)
- labbench__claude-code__deepseek-chat__batch1__phase2
- labbench__claude-code__deepseek-chat__batch1__phase4
- labbench__claude-code__glm-5__batch1__phase2
- labbench__claude-code__kimi-k2.5__batch1__phase2
- labbench__claude-code__kimi-k2.5__batch1__phase3
- labbench__claude-code__mimo-v2-pro__batch1__phase2
- labbench__claude-code__mimo-v2-pro__batch1__phase3
- labbench__claude-code__mimo-v2-pro__batch1__phase4
- labbench__claude-code__minimax-m2.5__batch1__phase2
- labbench__claude-code__minimax-m2.5__batch1__phase3
- labbench__codex__gpt-5-mini__batch1__phase2
- labbench__codex__gpt-5-mini__batch1__phase3
- labbench__codex__gpt-5-nano__batch1__phase2
- labbench__codex__gpt-5-nano__batch1__phase3
- labbench__codex__gpt-5.4__batch1__phase2
- labbench__codex__gpt-5.4__batch1__phase3
- labbench__gemini-cli__gemini-3-flash-preview__batch1__phase2
- labbench__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- labbench__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- labbench__terminus-2__deepseek-reasoner__batch1__phase2
- labbench__terminus-2__deepseek-reasoner__batch1__phase3
- labbench__terminus-2__gemini-3-flash-preview__batch1__phase2
- labbench__terminus-2__gemini-3-flash-preview__batch1__phase4
- labbench__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- labbench__terminus-2__glm-5__batch1__phase2
- labbench__terminus-2__gpt-5-mini__batch1__phase3
- labbench__terminus-2__gpt-5-mini__batch1__phase4
- labbench__terminus-2__gpt-5-nano__batch1__phase2
- labbench__terminus-2__gpt-5-nano__batch1__phase4
- labbench__terminus-2__gpt-5.4__batch1__phase2
- labbench__terminus-2__gpt-5.4__batch1__phase3
- labbench__terminus-2__gpt-5.4__batch1__phase4
- labbench__terminus-2__kimi-k2.5__batch1__phase2
- labbench__terminus-2__kimi-k2.5__batch1__phase4
- labbench__terminus-2__mimo-v2-pro__batch1__phase3
- labbench__terminus-2__mimo-v2-pro__batch1__phase4
- labbench__terminus-2__minimax-m2.5__batch1__phase2
- labbench__terminus-2__minimax-m2.5__batch1__phase4

### mmau (52)
- mmau__claude-code__deepseek-chat__batch1__phase2
- mmau__claude-code__deepseek-chat__batch1__phase3
- mmau__claude-code__deepseek-chat__batch1__phase4
- mmau__claude-code__glm-5__batch1__phase2
- mmau__claude-code__glm-5__batch1__phase4
- mmau__claude-code__kimi-k2.5__batch1__phase2
- mmau__claude-code__kimi-k2.5__batch1__phase3
- mmau__claude-code__kimi-k2.5__batch1__phase4
- mmau__claude-code__mimo-v2-pro__batch1__phase2
- mmau__claude-code__mimo-v2-pro__batch1__phase3
- mmau__claude-code__mimo-v2-pro__batch1__phase4
- mmau__claude-code__minimax-m2.5__batch1__phase2
- mmau__claude-code__minimax-m2.5__batch1__phase3
- mmau__claude-code__minimax-m2.5__batch1__phase4
- mmau__codex__gpt-5-mini__batch1__phase2
- mmau__codex__gpt-5-mini__batch1__phase4
- mmau__codex__gpt-5-nano__batch1__phase2
- mmau__codex__gpt-5-nano__batch1__phase4
- mmau__codex__gpt-5.4__batch1__phase2
- mmau__codex__gpt-5.4__batch1__phase3
- mmau__codex__gpt-5.4__batch1__phase4
- mmau__gemini-cli__gemini-3-flash-preview__batch1__phase2
- mmau__gemini-cli__gemini-3-flash-preview__batch1__phase3
- mmau__gemini-cli__gemini-3-flash-preview__batch1__phase4
- mmau__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- mmau__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- mmau__terminus-2__deepseek-reasoner__batch1__phase2
- mmau__terminus-2__deepseek-reasoner__batch1__phase4
- mmau__terminus-2__gemini-3-flash-preview__batch1__phase2
- mmau__terminus-2__gemini-3-flash-preview__batch1__phase3
- mmau__terminus-2__gemini-3-flash-preview__batch1__phase4
- mmau__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- mmau__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- mmau__terminus-2__glm-5__batch1__phase2
- mmau__terminus-2__gpt-5-mini__batch1__phase2
- mmau__terminus-2__gpt-5-mini__batch1__phase3
- mmau__terminus-2__gpt-5-mini__batch1__phase4
- mmau__terminus-2__gpt-5-nano__batch1__phase2
- mmau__terminus-2__gpt-5-nano__batch1__phase3
- mmau__terminus-2__gpt-5-nano__batch1__phase4
- mmau__terminus-2__gpt-5.4__batch1__phase2
- mmau__terminus-2__gpt-5.4__batch1__phase3
- mmau__terminus-2__gpt-5.4__batch1__phase4
- mmau__terminus-2__kimi-k2.5__batch1__phase2
- mmau__terminus-2__kimi-k2.5__batch1__phase3
- mmau__terminus-2__kimi-k2.5__batch1__phase4
- mmau__terminus-2__mimo-v2-pro__batch1__phase2
- mmau__terminus-2__mimo-v2-pro__batch1__phase3
- mmau__terminus-2__mimo-v2-pro__batch1__phase4
- mmau__terminus-2__minimax-m2.5__batch1__phase2
- mmau__terminus-2__minimax-m2.5__batch1__phase3
- mmau__terminus-2__minimax-m2.5__batch1__phase4

### qcircuitbench (45)
- qcircuitbench__claude-code__deepseek-chat__batch1__phase2
- qcircuitbench__claude-code__deepseek-chat__batch1__phase4
- qcircuitbench__claude-code__glm-5__batch1__phase2
- qcircuitbench__claude-code__kimi-k2.5__batch1__phase2
- qcircuitbench__claude-code__kimi-k2.5__batch1__phase4
- qcircuitbench__claude-code__mimo-v2-pro__batch1__phase2
- qcircuitbench__claude-code__mimo-v2-pro__batch1__phase4
- qcircuitbench__claude-code__minimax-m2.5__batch1__phase2
- qcircuitbench__claude-code__minimax-m2.5__batch1__phase4
- qcircuitbench__codex__gpt-5-mini__batch1__phase2
- qcircuitbench__codex__gpt-5-mini__batch1__phase3
- qcircuitbench__codex__gpt-5-mini__batch1__phase4
- qcircuitbench__codex__gpt-5-nano__batch1__phase2
- qcircuitbench__codex__gpt-5-nano__batch1__phase3
- qcircuitbench__codex__gpt-5-nano__batch1__phase4
- qcircuitbench__codex__gpt-5.4__batch1__phase2
- qcircuitbench__codex__gpt-5.4__batch1__phase3
- qcircuitbench__codex__gpt-5.4__batch1__phase4
- qcircuitbench__gemini-cli__gemini-3-flash-preview__batch1__phase2
- qcircuitbench__gemini-cli__gemini-3-flash-preview__batch1__phase3
- qcircuitbench__gemini-cli__gemini-3-flash-preview__batch1__phase4
- qcircuitbench__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- qcircuitbench__gemini-cli__gemini-3.1-pro-preview__batch1__phase3
- qcircuitbench__gemini-cli__gemini-3.1-pro-preview__batch1__phase4
- qcircuitbench__terminus-2__deepseek-reasoner__batch1__phase2
- qcircuitbench__terminus-2__deepseek-reasoner__batch1__phase4
- qcircuitbench__terminus-2__gemini-3-flash-preview__batch1__phase2
- qcircuitbench__terminus-2__gemini-3-flash-preview__batch1__phase3
- qcircuitbench__terminus-2__gemini-3-flash-preview__batch1__phase4
- qcircuitbench__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- qcircuitbench__terminus-2__gemini-3.1-pro-preview__batch1__phase3
- qcircuitbench__terminus-2__gemini-3.1-pro-preview__batch1__phase4
- qcircuitbench__terminus-2__glm-5__batch1__phase2
- qcircuitbench__terminus-2__gpt-5-mini__batch1__phase2
- qcircuitbench__terminus-2__gpt-5-mini__batch1__phase3
- qcircuitbench__terminus-2__gpt-5-mini__batch1__phase4
- qcircuitbench__terminus-2__gpt-5-nano__batch1__phase2
- qcircuitbench__terminus-2__gpt-5-nano__batch1__phase4
- qcircuitbench__terminus-2__gpt-5.4__batch1__phase2
- qcircuitbench__terminus-2__gpt-5.4__batch1__phase4
- qcircuitbench__terminus-2__kimi-k2.5__batch1__phase4
- qcircuitbench__terminus-2__mimo-v2-pro__batch1__phase2
- qcircuitbench__terminus-2__mimo-v2-pro__batch1__phase4
- qcircuitbench__terminus-2__minimax-m2.5__batch1__phase2
- qcircuitbench__terminus-2__minimax-m2.5__batch1__phase4

### swe-lancer (39)
- swe-lancer__claude-code__deepseek-chat__batch1__phase2
- swe-lancer__claude-code__deepseek-chat__batch1__phase3
- swe-lancer__claude-code__deepseek-chat__batch1__phase4
- swe-lancer__claude-code__glm-5__batch1__phase2
- swe-lancer__claude-code__glm-5__batch1__phase4
- swe-lancer__claude-code__kimi-k2.5__batch1__phase2
- swe-lancer__claude-code__kimi-k2.5__batch1__phase4
- swe-lancer__claude-code__mimo-v2-pro__batch1__phase2
- swe-lancer__claude-code__mimo-v2-pro__batch1__phase4
- swe-lancer__claude-code__minimax-m2.5__batch1__phase2
- swe-lancer__claude-code__minimax-m2.5__batch1__phase3
- swe-lancer__claude-code__minimax-m2.5__batch1__phase4
- swe-lancer__codex__gpt-5-mini__batch1__phase2
- swe-lancer__codex__gpt-5-mini__batch1__phase3
- swe-lancer__codex__gpt-5-mini__batch1__phase4
- swe-lancer__codex__gpt-5-nano__batch1__phase2
- swe-lancer__codex__gpt-5-nano__batch1__phase3
- swe-lancer__codex__gpt-5-nano__batch1__phase4
- swe-lancer__codex__gpt-5.4__batch1__phase2
- swe-lancer__codex__gpt-5.4__batch1__phase4
- swe-lancer__gemini-cli__gemini-3-flash-preview__batch1__phase2
- swe-lancer__gemini-cli__gemini-3-flash-preview__batch1__phase3
- swe-lancer__gemini-cli__gemini-3.1-pro-preview__batch1__phase2
- swe-lancer__terminus-2__deepseek-reasoner__batch1__phase2
- swe-lancer__terminus-2__gemini-3-flash-preview__batch1__phase2
- swe-lancer__terminus-2__gemini-3.1-pro-preview__batch1__phase2
- swe-lancer__terminus-2__glm-5__batch1__phase2
- swe-lancer__terminus-2__glm-5__batch1__phase4
- swe-lancer__terminus-2__gpt-5-mini__batch1__phase2
- swe-lancer__terminus-2__gpt-5-nano__batch1__phase2
- swe-lancer__terminus-2__gpt-5-nano__batch1__phase3
- swe-lancer__terminus-2__gpt-5.4__batch1__phase2
- swe-lancer__terminus-2__gpt-5.4__batch1__phase3
- swe-lancer__terminus-2__kimi-k2.5__batch1__phase2
- swe-lancer__terminus-2__kimi-k2.5__batch1__phase3
- swe-lancer__terminus-2__mimo-v2-pro__batch1__phase2
- swe-lancer__terminus-2__mimo-v2-pro__batch1__phase3
- swe-lancer__terminus-2__minimax-m2.5__batch1__phase2
- swe-lancer__terminus-2__minimax-m2.5__batch1__phase3

