#!/usr/bin/env python3
"""
Batch re-import local trial results to Supabase.

Two steps:
1. Register missing tasks in the `task` table (required for foreign key)
2. Import successful trials that aren't yet in the `trial` table

Usage:
    source .env
    .venv/bin/python3 scripts/reimport_to_supabase.py
"""

import glob
import json
import os
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from harbor.models.trial.result import TrialResult
from supabase import create_client

load_dotenv()


def main():
    client = create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"]
    )

    # Step 1: Register missing tasks
    print("Step 1: Registering missing tasks...", flush=True)
    checksums_seen = set()
    tasks_inserted = tasks_skipped = task_errors = 0

    for jd in sorted(glob.glob("jobs/*")):
        if not os.path.isdir(jd):
            continue
        for t in os.listdir(jd):
            rp = os.path.join(jd, t, "result.json")
            cp = os.path.join(jd, t, "config.json")
            if not os.path.exists(rp):
                continue
            try:
                result = TrialResult.model_validate_json(Path(rp).read_text())
                if result.exception_info:
                    continue
                cs = result.task_checksum
                if cs in checksums_seen:
                    continue
                checksums_seen.add(cs)

                ex = client.table("task").select("checksum").eq("checksum", cs).execute()
                if ex.data:
                    tasks_skipped += 1
                    continue

                # Get path and git info from trial config
                task_path = "unknown"
                git_url = None
                git_commit_id = None
                if os.path.exists(cp):
                    with open(cp) as f:
                        tcfg = json.load(f)
                    task_cfg = tcfg.get("task", {})
                    task_path = task_cfg.get("path", "") or "unknown"
                    git_url = task_cfg.get("git_url")
                    git_commit_id = task_cfg.get("git_commit_id")

                task_data = {
                    "checksum": cs,
                    "name": result.task_name or t.split("__")[0],
                    "instruction": "",
                    "agent_timeout_sec": 1800,
                    "verifier_timeout_sec": 600,
                    "path": task_path,
                }
                if git_url:
                    task_data["git_url"] = git_url
                if git_commit_id:
                    task_data["git_commit_id"] = git_commit_id

                client.table("task").upsert(task_data).execute()
                tasks_inserted += 1
                if tasks_inserted % 50 == 0:
                    print(
                        f"  Tasks: inserted={tasks_inserted} skipped={tasks_skipped}",
                        flush=True,
                    )
            except Exception as e:
                task_errors += 1
                if task_errors <= 3:
                    print(f"  Task error: {e}", flush=True)

    print(
        f"Tasks: inserted={tasks_inserted} skipped={tasks_skipped} errors={task_errors}",
        flush=True,
    )

    # Step 2: Import trials
    print("Step 2: Importing trials...", flush=True)
    uploaded = already = errors = 0

    for jd in sorted(glob.glob("jobs/*")):
        if not os.path.isdir(jd):
            continue
        for tn in os.listdir(jd):
            tp = os.path.join(jd, tn)
            if not os.path.isdir(tp):
                continue
            rp = os.path.join(tp, "result.json")
            if not os.path.exists(rp):
                continue
            try:
                result = TrialResult.model_validate_json(Path(rp).read_text())
                if result.exception_info:
                    continue
                tid = str(result.id)

                ex = client.table("trial").select("id").eq("id", tid).execute()
                if ex.data:
                    already += 1
                    continue

                client.table("agent").upsert(
                    {
                        "name": result.agent_info.name,
                        "version": result.agent_info.version,
                    }
                ).execute()

                td = {
                    "id": tid,
                    "agent_name": result.agent_info.name,
                    "agent_version": result.agent_info.version,
                    "config": json.loads(
                        json.dumps(result.config.model_dump(mode="json"), default=str)
                    ),
                    "task_checksum": result.task_checksum,
                    "trial_name": result.trial_name,
                    "job_id": str(result.config.job_id),
                }
                if result.verifier_result and result.verifier_result.rewards:
                    td["reward"] = float(
                        Decimal(result.verifier_result.rewards.get("reward", 0))
                    )
                if result.started_at:
                    td["started_at"] = result.started_at.isoformat()
                if result.finished_at:
                    td["ended_at"] = result.finished_at.isoformat()

                client.table("trial").upsert(td).execute()

                if (
                    result.agent_info.model_info
                    and result.agent_info.model_info.name
                ):
                    mi = result.agent_info.model_info
                    client.table("model").upsert(
                        {"name": mi.name, "provider": mi.provider}
                    ).execute()
                    client.table("trial_model").upsert(
                        {
                            "trial_id": tid,
                            "model_name": mi.name,
                            "model_provider": mi.provider,
                        }
                    ).execute()

                uploaded += 1
                if (uploaded + already) % 200 == 0:
                    print(
                        f"  uploaded={uploaded} already={already} errors={errors}",
                        flush=True,
                    )
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Trial error: {e}", flush=True)
                time.sleep(0.5)

    print(f"DONE uploaded={uploaded} already={already} errors={errors}", flush=True)


if __name__ == "__main__":
    main()
