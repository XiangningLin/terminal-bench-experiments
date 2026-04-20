#!/usr/bin/env python3
"""
After running check_all_combos.py, generate YAML configs for incomplete jobs.

Finds all incomplete benchmark+agent+model+phase combos in Supabase,
then generates run configs pointing to the appropriate registry.

Usage:
    source .env
    .venv/bin/python3 scripts/generate_missing_configs.py
    .venv/bin/python3 scripts/generate_missing_configs.py --benchmark swe-lancer
    .venv/bin/python3 scripts/generate_missing_configs.py --phase phase4
    .venv/bin/python3 scripts/generate_missing_configs.py --dry-run
"""

import argparse
import glob
import json
import os
from collections import defaultdict
from pathlib import Path

import yaml
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

ALL_COMBOS = [
    ("terminus-2", "gpt-5.4", "openai/gpt-5.4"),
    ("codex", "gpt-5.4", "openai/gpt-5.4"),
    ("terminus-2", "gpt-5-mini", "openai/gpt-5-mini"),
    ("codex", "gpt-5-mini", "openai/gpt-5-mini"),
    ("terminus-2", "gpt-5-nano", "openai/gpt-5-nano"),
    ("codex", "gpt-5-nano", "openai/gpt-5-nano"),
    ("terminus-2", "claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"),
    ("claude-code", "claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"),
    ("terminus-2", "claude-sonnet-4-6", "anthropic/claude-sonnet-4-6"),
    ("claude-code", "claude-sonnet-4-6", "anthropic/claude-sonnet-4-6"),
    ("terminus-2", "claude-opus-4-6", "anthropic/claude-opus-4-6"),
    ("claude-code", "claude-opus-4-6", "anthropic/claude-opus-4-6"),
    ("terminus-2", "gemini-3.1-pro-preview", "gemini/gemini-3.1-pro-preview"),
    ("gemini-cli", "gemini-3.1-pro-preview", "gemini/gemini-3.1-pro-preview"),
    ("terminus-2", "gemini-3-flash-preview", "gemini/gemini-3-flash-preview"),
    ("gemini-cli", "gemini-3-flash-preview", "gemini/gemini-3-flash-preview"),
    ("terminus-2", "deepseek-reasoner", "deepseek/deepseek-reasoner"),
    ("claude-code", "deepseek-chat", "anthropic/deepseek-chat"),
    ("terminus-2", "kimi-k2.5", "zai/kimi-k2.5"),
    ("claude-code", "kimi-k2.5", "anthropic/kimi-k2.5"),
    ("terminus-2", "MiniMax-M2.5", "minimax/MiniMax-M2.5"),
    ("claude-code", "MiniMax-M2.5", "anthropic/MiniMax-M2.5"),
    ("terminus-2", "glm-5", "zai/glm-5"),
    ("claude-code", "glm-5", "anthropic/glm-5"),
    ("terminus-2", "mimo-v2-pro", "xiaomi/mimo-v2-pro"),
    ("claude-code", "mimo-v2-pro", "anthropic/mimo-v2-pro"),
    ("terminus-2", "qwen3-max", "openai/qwen3-max"),
    ("qwen-coder", "qwen3-max", "qwen3-max"),
]

MODEL_ALIASES = {
    "MiniMax-M2.5": "minimax-m2.5",
}

BENCHMARKS = {
    "aime": {"phase3": 5, "phase4": 54},
    "arc-agi-2": {"phase3": 45, "phase4": 450},
    "compilebench": {"phase3": 1, "phase4": 13},
    "gpqa-diamond": {"phase2": 10, "phase3": 90, "phase4": 890},
    "humanevalfix": {"phase3": 75},
    "ineqmath": {"phase2": 1, "phase3": 9, "phase4": 90},
    "labbench": {"phase2": 10, "phase3": 90, "phase4": 810},
    "mmau": {"phase2": 10, "phase3": 90, "phase4": 900},
    "qcircuitbench": {"phase2": 1, "phase4": 25},
    "swe-lancer": {"phase2": 2, "phase3": 18, "phase4": 180},
}

AGENT_CONFIGS = {
    "terminus-2": lambda model_name, model_short: {"name": "terminus-2", "model_name": model_name},
    "codex": lambda model_name, model_short: {"name": "codex", "model_name": model_name},
    "gemini-cli": lambda model_name, model_short: {"name": "gemini-cli", "model_name": model_name},
    "claude-code": lambda model_name, model_short: {"name": "claude-code", "model_name": model_name, "kwargs": {"version": "2.1.81"}},
    "qwen-coder": lambda model_name, model_short: {
        "name": "qwen-coder",
        "model_name": "qwen3-max",
        "kwargs": {"version": "0.14.5"},
        "env": {
            "OPENAI_API_KEY": os.environ.get("QWEN_API_KEY", "PLACEHOLDER"),
            "OPENAI_BASE_URL": "http://pp-api-ec82a10d0c5d226c.elb.us-west-2.amazonaws.com:3000/v1",
        },
    },
}

# Special kwargs for certain combos
SPECIAL_KWARGS = {
    ("terminus-2", "qwen3-max"): {
        "kwargs": {
            "api_base": "http://pp-api-ec82a10d0c5d226c.elb.us-west-2.amazonaws.com:3000/v1",
            "llm_kwargs": {"api_key": os.environ.get("QWEN_API_KEY_TERMINUS", "PLACEHOLDER")},
        }
    },
}


def check_job(client, job_name, expected_tasks, min_trials=3):
    try:
        jobs = client.table("job").select("id").eq("job_name", job_name).execute()
    except:
        return 0, "QUERY_FAIL"
    if not jobs.data:
        return 0, "NO_JOB"

    task_ok = defaultdict(int)
    for job in jobs.data:
        try:
            trials = (
                client.table("trial")
                .select("task_checksum,reward")
                .eq("job_id", job["id"])
                .not_.is_("reward", "null")
                .execute()
            )
            for t in trials.data:
                tc = t.get("task_checksum", "")
                if tc:
                    task_ok[tc] += 1
        except:
            pass

    tasks_done = sum(1 for c in task_ok.values() if c >= min_trials)
    if tasks_done >= expected_tasks and expected_tasks > 0:
        return tasks_done, "DONE"
    elif tasks_done > 0:
        return tasks_done, "PARTIAL"
    else:
        return 0, "NEED"


def generate_config(bench, agent, model_short, model_name, phase, out_dir, config_base):
    """Generate a YAML config for a missing job."""
    model_in_name = MODEL_ALIASES.get(model_short, model_short)
    job_name = f"{bench}__{agent}__{model_in_name}__batch1__{phase}"

    # Find registry
    reg_path = f"{config_base}/{phase}/registries/{bench}.json"
    if not os.path.exists(reg_path):
        return None

    # Build agent config
    agent_cfg = AGENT_CONFIGS.get(agent, lambda m, s: {"name": agent, "model_name": m})(
        model_name, model_short
    )

    # Apply special kwargs
    if (agent, model_short) in SPECIAL_KWARGS:
        special = SPECIAL_KWARGS[(agent, model_short)]
        agent_cfg.update(special)

    cfg = {
        "jobs_dir": "jobs",
        "n_attempts": 5,
        "timeout_multiplier": 1.0,
        "orchestrator": {
            "type": "local",
            "n_concurrent_trials": 32,
            "quiet": False,
            "retry": {
                "max_retries": 3,
                "exclude_exceptions": [
                    "BadRequestError",
                    "RateLimitError",
                    "AgentTimeoutError",
                    "VerifierTimeoutError",
                    "RewardFileNotFoundError",
                ],
                "wait_multiplier": 1.0,
                "min_wait_sec": 1.0,
                "max_wait_sec": 60.0,
            },
        },
        "environment": {"type": "daytona", "force_build": False, "delete": True},
        "job_name": job_name,
        "agents": [agent_cfg],
        "datasets": [
            {
                "registry": {"name": "local", "path": reg_path},
                "name": f"adapter-experiments-batch1-{phase}",
                "version": "1.0",
            }
        ],
    }

    out_path = f"{out_dir}/{job_name}.yaml"
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", help="Filter by benchmark")
    parser.add_argument("--phase", help="Filter by phase")
    parser.add_argument("--min-trials", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be generated")
    parser.add_argument("--skip-glm", action="store_true", default=True)
    parser.add_argument(
        "--config-base",
        default="outputs/adapter_experiments/batch1/contributors/Xiangning",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/adapter_experiments/batch1/contributors/Xiangning/generated",
    )
    args = parser.parse_args()

    client = create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"]
    )

    incomplete = []
    checked = 0

    for bench, phases in sorted(BENCHMARKS.items()):
        if args.benchmark and bench != args.benchmark:
            continue
        for phase, expected in sorted(phases.items()):
            if args.phase and phase != args.phase:
                continue
            for agent, model_short, model_name in ALL_COMBOS:
                if args.skip_glm and "glm" in model_short:
                    continue

                model_in_name = MODEL_ALIASES.get(model_short, model_short)
                job_name = f"{bench}__{agent}__{model_in_name}__batch1__{phase}"

                tasks_done, status = check_job(client, job_name, expected, args.min_trials)

                if status != "DONE":
                    incomplete.append((bench, agent, model_short, model_name, phase, tasks_done, expected, status))

                checked += 1
                if checked % 50 == 0:
                    print(f"  Checked {checked}...", flush=True)

    print(f"\nChecked {checked} combos. Incomplete: {len(incomplete)}")
    print()

    if args.dry_run:
        print("=== Would generate configs for: ===")
        for bench, agent, model_short, model_name, phase, td, exp, status in incomplete:
            print(f"  {status:8s} {bench}__{agent}__{model_short}__{phase} ({td}/{exp})")
        return

    # Generate configs
    generated = 0
    for bench, agent, model_short, model_name, phase, td, exp, status in incomplete:
        out_path = generate_config(
            bench, agent, model_short, model_name, phase, args.output_dir, args.config_base
        )
        if out_path:
            generated += 1
            print(f"  Generated: {out_path}")

    print(f"\nGenerated {generated} configs in {args.output_dir}/")
    print(f"\nRun with:")
    print(f"  .venv/bin/python3 -u scripts/run_job.py -c {args.output_dir}/<job_name>.yaml")


if __name__ == "__main__":
    main()
