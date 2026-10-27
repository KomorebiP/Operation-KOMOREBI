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
    inputs=["verification/replay_rank_gate_launcher.py","verification/replay_rank_gate.py","verification/replay_scoped.py",
            "verification/DEPENDENCY_PROVENANCE.json","verification/provenance_runner/run_experiment.py",
            "verification/provenance_runner/validate_manifest.py","sources/self_calibration/polyphase_gibbs_breakthrough.py"]
    versions=[{"name":"Python","version":platform.python_version()}]
    for name in ["numpy","scipy","matplotlib","sympy"]:
        versions.append({"name":name,"version":metadata.version(name)})
    contract={"claim_id":"SIGNAL_RANK_RATIO_BOUNDARY",
              "mathematics":{"assertion_tested":"Exact Hankel factorization, native largest-ratio failure, and independently supplied threshold recovery in a bounded perturbation witness",
              "coefficient_domain":"exact Fraction Gaussian-rational Q(i) factorization; float64/complex128 native heuristic and SVD",
              "conventions":"moments sum_j a_j z_j^n; n0=4; Hankel[i,j]=moment[n0+i+j]; Fourier basis unitarily diagonalizes square Hankel; threshold2",
              "inputs":inputs,"bounds":{"true_jump_order":3,"square_Hankel_shape":[4,4],"native_sequence_length":16,"native_order_bound":3,"amplitudes":[100,-99,-1],"noise_amplitude":"1/10","supplied_threshold":2},
              "non_claims":["No universal verified Python","No guarantee for source largest-ratio heuristic","No alteration of preserved source","No data-only certified threshold selector"]},
              "execution_artifacts":inputs,"software":versions,"randomness":{"used":False,"generator":"","seed":None}}
    base=ROOT/"verification/runs"/args.run_name
    if base.exists():raise FileExistsError(base)
    base.mkdir(parents=True)
    contract_path=base/"contract.json";contract_path.write_text(json.dumps(contract,indent=2)+"\n")
    output=str((base/"rank_ratio_boundary").relative_to(ROOT));result=output+"/scientific_result.json"
    command=[sys.executable,str(ROOT/"verification/provenance_runner/run_experiment.py"),"--root",str(ROOT),
             "--contract",str(contract_path),"--output",output,"--result",result,"--timeout","60",
             "--max-cpu-seconds","45","--max-memory-bytes","2147483648","--max-cores","1",
             "--max-threads","1","--max-output-bytes","1048576"]
    for item in inputs:command.extend(["--input",item])
    command.extend(["--",sys.executable,"verification/replay_rank_gate.py","--result",result])
    completed=subprocess.run(command,cwd=ROOT,env=env,check=False)
    raise SystemExit(completed.returncode)

if __name__=="__main__":main()
