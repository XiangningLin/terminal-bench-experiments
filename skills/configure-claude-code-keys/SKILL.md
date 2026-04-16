---
name: configure-claude-code-keys
description: Replace ANTHROPIC_AUTH_TOKEN_PLACEHOLDER in experiment configs with real API keys for third-party models (deepseek, kimi, mimo, minimax, glm) when running Claude Code as the agent.
---

# Configure Claude Code Third-Party Model Keys

When Claude Code is used as the agent to run non-Anthropic models (deepseek, mimo, glm, minimax, kimi), the experiment config files contain a placeholder `ANTHROPIC_AUTH_TOKEN_PLACEHOLDER` that must be replaced with the actual API key for the corresponding model provider.

## Background

Claude Code natively uses `ANTHROPIC_API_KEY` for Anthropic models (claude-sonnet, claude-opus, claude-haiku). For third-party models, it routes requests through a compatible API endpoint using:

- `ANTHROPIC_BASE_URL` — the provider's Anthropic-compatible endpoint
- `ANTHROPIC_AUTH_TOKEN` — the provider's API key (this is the placeholder that needs replacing)
- `ANTHROPIC_MODEL` — the model name
- `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL` — all set to the same model

## Config Example (Before)

```yaml
agents:
- name: claude-code
  model_name: anthropic/deepseek-chat
  kwargs:
    version: 2.1.81
  env:
    ANTHROPIC_AUTH_TOKEN: ANTHROPIC_AUTH_TOKEN_PLACEHOLDER   # <-- needs replacing
    ANTHROPIC_BASE_URL: https://api.deepseek.com/anthropic
    ANTHROPIC_MODEL: deepseek-chat
    ANTHROPIC_DEFAULT_SONNET_MODEL: deepseek-chat
    ANTHROPIC_DEFAULT_OPUS_MODEL: deepseek-chat
    ANTHROPIC_DEFAULT_HAIKU_MODEL: deepseek-chat
    CLAUDE_CODE_SUBAGENT_MODEL: deepseek-chat
    API_TIMEOUT_MS: '600000'
```

## Provider → Base URL → API Key Mapping

| Model | Base URL | .env Variable |
|-------|----------|---------------|
| deepseek-chat | `https://api.deepseek.com/anthropic` | `DEEPSEEK_API_KEY` |
| kimi-k2.5 | `https://api.moonshot.ai/anthropic` | `KIMI_API_KEY` |
| mimo-v2-pro | `https://api.xiaomimimo.com/anthropic` | `XIAOMI_MIMO_API_KEY` |
| MiniMax-M2.5 | `https://api.minimaxi.com/anthropic` | `MINIMAX_API_KEY` |
| glm-5 | `https://api.z.ai/api/anthropic` | `ZAI_API_KEY` |

## How To Replace

### Quick: One-liner per model

```bash
source .env

# deepseek
sed -i '' "s/ANTHROPIC_AUTH_TOKEN_PLACEHOLDER/$DEEPSEEK_API_KEY/g" \
  outputs/adapter_experiments/batch1/contributors/Xiangning/**/*deepseek*.yaml

# kimi
sed -i '' "s/ANTHROPIC_AUTH_TOKEN_PLACEHOLDER/$KIMI_API_KEY/g" \
  outputs/adapter_experiments/batch1/contributors/Xiangning/**/*kimi*.yaml

# mimo
sed -i '' "s/ANTHROPIC_AUTH_TOKEN_PLACEHOLDER/$XIAOMI_MIMO_API_KEY/g" \
  outputs/adapter_experiments/batch1/contributors/Xiangning/**/*mimo*.yaml

# minimax
sed -i '' "s/ANTHROPIC_AUTH_TOKEN_PLACEHOLDER/$MINIMAX_API_KEY/g" \
  outputs/adapter_experiments/batch1/contributors/Xiangning/**/*minimax*.yaml

# glm (skip if key is unavailable)
sed -i '' "s/ANTHROPIC_AUTH_TOKEN_PLACEHOLDER/$ZAI_API_KEY/g" \
  outputs/adapter_experiments/batch1/contributors/Xiangning/**/*glm*.yaml
```

### Automated: Python script (recommended)

```python
import os, glob

key_map = {
    'deepseek':    os.environ['DEEPSEEK_API_KEY'],
    'moonshot':    os.environ['KIMI_API_KEY'],
    'xiaomimimo':  os.environ['XIAOMI_MIMO_API_KEY'],
    'minimaxi':   os.environ['MINIMAX_API_KEY'],
    'api.z.ai':   os.environ.get('ZAI_API_KEY', ''),
}

files = glob.glob('outputs/**/Xiangning/**/*.yaml', recursive=True)

for f in files:
    with open(f) as fh:
        content = fh.read()
    if 'ANTHROPIC_AUTH_TOKEN_PLACEHOLDER' not in content:
        continue

    for keyword, key in key_map.items():
        if keyword in content and key:
            content = content.replace('ANTHROPIC_AUTH_TOKEN_PLACEHOLDER', key)
            break

    with open(f, 'w') as fh:
        fh.write(content)
```

Run with:

```bash
source .env
python3 scripts/replace_keys.py   # or inline the script above
```

### Verify

```bash
# Should return nothing if all placeholders are replaced
grep -rl "ANTHROPIC_AUTH_TOKEN_PLACEHOLDER" outputs/adapter_experiments/batch1/contributors/Xiangning/
```

## Notes

- Anthropic native models (claude-sonnet, claude-opus, claude-haiku) do NOT need this — they use `ANTHROPIC_API_KEY` from the environment directly.
- Do NOT commit real API keys to git. The replacement should happen locally before running jobs.
- GLM key (`ZAI_API_KEY`) may be unavailable — skip glm-5 jobs if so.
- The `ANTHROPIC_BASE_URL` and other env vars in the config are already correct — only `ANTHROPIC_AUTH_TOKEN` needs replacing.
