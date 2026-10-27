from __future__ import annotations

from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

from pathlib import Path

from block23.external.audit import run_causal_audit, summarize_causal_audit
from block23.external.fake_runtime import FakeLatentAdapter
from block23.external.prontoqa import donor_pairs, semantic_twin
from block23.external.protocol import PilotTask
from block23.receipts import digest, write_json

ROOT=Path(__file__).resolve().parent

def make_tasks(n:int=72)->list[PilotTask]:
    tasks=[]
    for i in range(n):
        answer="True" if i%2==0 else "False"
        depth=3+(i%3)
        family=f"shape-{i%18}"
        steps=tuple(f"anonymous rule {j} in {family}" for j in range(depth))
        tasks.append(PilotTask(f"fixture-{i:03d}",f"fixture question {i}",answer,steps,family,{"proof_depth":depth}))
    return tasks

def main()->dict:
    tasks=make_tasks()
    twins={t.task_id:semantic_twin(t,4000+i) for i,t in enumerate(tasks)}
    donors=donor_pairs(tasks)
    records=run_causal_audit(FakeLatentAdapter(),tasks,donors=donors,twins=twins)
    result={
        "schema":"sric.block23.external-adapter-fixture.v1",
        "claim_boundary":"Protocol and intervention plumbing only; not evidence about any third-party checkpoint.",
        "summary":summarize_causal_audit(records),
        "records":records,
    }
    result["fixture_receipt"]=digest(result)
    write_json(ROOT/"results"/"external_adapter_fixture.json",result)
    print(f"BLOCK23_EXTERNAL_FIXTURE_TASKS={len(records)}")
    print(f"BLOCK23_EXTERNAL_FIXTURE_RECEIPT={result['fixture_receipt']}")
    return result

if __name__=="__main__":main()
