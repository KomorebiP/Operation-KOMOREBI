#!/usr/bin/env python3
"""Independent counterexample controls for the separate rank-aware copy."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from replay_scoped import Checks, clean, load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    c = Checks()
    try:
        import numpy as np
        original = load("signal_original_dictionary", "sources/unknown_edge/universal_unknown_edge_recovery.py")
        patched = load("signal_repaired_dictionary", "execution/unknown_edge/universal_unknown_edge_recovery.py")
        wide = np.array([[1., 0., 1.], [0., 1., 1.]])
        null_vector = np.array([-1., -1., 1.])
        c.check("exact integer underdetermined kernel witness", np.array_equal(wide@null_vector, np.zeros(2)))
        old_gamma = original.restricted_separation_constant(wide, 3)
        new_gamma = patched.restricted_separation_constant(wide, 3)
        c.check("old compact-SVD false certificate reproduced", old_gamma > 0, old_gamma)
        c.check("rank-aware wide-support zero separation", new_gamma == 0)
        c.check("full-row-rank wide control", np.linalg.matrix_rank(wide) == 2)
        tall = np.array([[1., 2.], [2., -1.], [1., 1.]])
        c.check("positive full-column control unchanged", abs(original.restricted_separation_constant(tall, 2)
                -patched.restricted_separation_constant(tall, 2)) < 1e-12)
        B = np.column_stack([np.ones(3), 2*np.ones(3)])
        D = np.eye(3)
        original_problem = original.DictionaryProblem(B, D)
        corrected_problem = patched.DictionaryProblem(B, D)
        P = corrected_problem.projector
        expected = np.ones((3,3))/3
        c.check("old dependent-background overprojection reproduced", np.linalg.norm(original_problem.projector-expected) > 0.5)
        c.check("corrected dependent-background range projector", np.max(np.abs(P-expected)) < 1e-12)
        c.check("corrected projector symmetry", np.max(np.abs(P-P.T)) < 1e-12)
        c.check("corrected projector idempotence", np.max(np.abs(P@P-P)) < 1e-12)
        c.check("corrected projector retains background", np.max(np.abs(P@B-B)) < 1e-12)
        c.check("corrected projector preserves independent complement", np.max(np.abs(P@np.array([1.,-1.,0.]))) < 1e-12)
        zero = patched.DictionaryProblem(np.zeros((3,0)), D)
        c.check("empty background projects to zero", np.array_equal(zero.projector, np.zeros((3,3))))
        null = patched.DictionaryProblem(np.zeros((3,2)), D)
        c.check("zero rank background projects to zero", np.array_equal(null.projector, np.zeros((3,3))))
        old_example = original.build_dictionary_example()
        new_example = patched.build_dictionary_example()
        c.check("documented dictionary support retained", new_example[3]["support"] == old_example[3]["support"] == (1,5))
        c.check("documented dictionary synthesis retained", np.max(np.abs(new_example[3]["reconstruction"]-new_example[1])) < 1e-10)
        c.check("documented restricted separation retained", abs(new_example[-1]-old_example[-1]) < 1e-12)
        record = {"status":"PASS", "suite":"rank_aware_execution_copy", "fresh_explicit_check_count":len(c.rows),
                  "checks":c.rows, "details":{"old_wide_gamma":old_gamma, "corrected_wide_gamma":new_gamma,
                  "corrected_projector":P, "documented_gamma":new_example[-1]},
                  "interpretation":"finite regression controls of a minimally repaired numerical execution copy; preserved source remains unchanged"}
    except Exception as error:
        record={"status":"FAIL", "checks":c.rows, "failure":{"type":type(error).__name__,"message":str(error)}}
        args.result.write_text(json.dumps(clean(record),indent=2,allow_nan=False)+"\n")
        raise
    args.result.write_text(json.dumps(clean(record),indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":record["status"],"checks":len(c.rows)}))

if __name__ == "__main__":
    main()
