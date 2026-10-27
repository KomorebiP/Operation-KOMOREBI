#!/usr/bin/env python3
"""Bounded launcher for the distinct repaired-copy negative controls."""
import argparse
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run-name",required=True)
    parser.add_argument("--dependency-dir",type=Path)
    args=parser.parse_args()
    if Path(args.run_name).is_absolute() or ".." in Path(args.run_name).parts:
        raise ValueError("invalid run name")
    env=os.environ.copy()
    if args.dependency_dir:
        sys.path.insert(0,str(args.dependency_dir.resolve()))
        env["PYTHONPATH"]=str(args.dependency_dir.resolve())+os.pathsep+env.get("PYTHONPATH","")
    inputs=["verification/replay_rank_controls.py","verification/replay_corrections.py","verification/replay_scoped.py",
            "verification/DEPENDENCY_PROVENANCE.json","verification/provenance_runner/run_experiment.py",
            "verification/provenance_runner/validate_manifest.py","sources/unknown_edge/universal_unknown_edge_recovery.py",
            "execution/unknown_edge/universal_unknown_edge_recovery.py","execution/unknown_edge/REPAIR_PROVENANCE.json"]
    versions=[{"name":"Python","version":platform.python_version()}]
    for name in ["numpy","scipy","matplotlib","sympy"]:
        versions.append({"name":name,"version":metadata.version(name)})
    contract={"claim_id":"SIGNAL_RANK_AWARE_EXECUTION_COPY",
              "mathematics":{"assertion_tested":"Reproduce original false compact-SVD/QR generic certificates, check repaired rank-aware controls and retained documented finite example",
              "coefficient_domain":"exact integer kernel witness evaluated in float64; numerical projectors/SVD with explicit tolerances",
              "conventions":"coefficient-side injectivity requires column rank; projector onto numerical range(B), not all QR columns",
              "inputs":inputs,"bounds":{"wide_support_shape":[2,3],"dependent_background_shape":[3,2],"zero_background_shapes":[[3,0],[3,2]],"documented_dictionary_shape":[24,8],"sparsity":2},
              "non_claims":["No universal verified Python","No exact-arithmetic rank certification","No alteration of preserved source","No zero-edge API wrapper"]},
              "execution_artifacts":inputs,"software":versions,"randomness":{"used":False,"generator":"","seed":None}}
    base=ROOT/"verification/runs"/args.run_name
    if base.exists():raise FileExistsError(base)
    base.mkdir(parents=True)
    contract_path=base/"contract.json";contract_path.write_text(json.dumps(contract,indent=2)+"\n")
    output=str((base/"rank_aware_execution_copy").relative_to(ROOT));result=output+"/scientific_result.json"
    command=[sys.executable,str(ROOT/"verification/provenance_runner/run_experiment.py"),"--root",str(ROOT),
             "--contract",str(contract_path),"--output",output,"--result",result,"--timeout","60",
             "--max-cpu-seconds","45","--max-memory-bytes","2147483648","--max-cores","1",
             "--max-threads","1","--max-output-bytes","1048576"]
    for item in inputs:command.extend(["--input",item])
    command.extend(["--",sys.executable,"verification/replay_corrections.py","--result",result])
    completed=subprocess.run(command,cwd=ROOT,env=env,check=False)
    raise SystemExit(completed.returncode)

if __name__=="__main__":main()
