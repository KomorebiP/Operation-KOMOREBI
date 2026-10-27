#!/usr/bin/env python3
"""Scoped follow-up retaining a reproduced stress-case identification failure.

The first replay incorrectly asserted every stress case recovers its jump
count. Its failed record and original driver remain untouched. This follow-up
uses the archived benchmark's distinction between controlled and stress cases.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from replay_scoped import Checks, clean, load, SUITES


def complex_scoped(c):
    m = load("signal_complex_scoped", "sources/complex_benchmark/complex_signal_image_benchmark.py")
    import numpy as np
    rows, _ = m.run_complex_1d_cases()
    limitations = []
    for row in rows:
        name = row["case"]
        c.check(f"complex finite synthesis metrics {name}",
                all(math.isfinite(float(row[key])) for key in ("raw_rmse", "resolved_rmse", "resolved_boundary_rmse")),
                {key: row[key] for key in ("raw_rmse", "resolved_rmse", "recovered_order", "true_order")})
        if row["scope"] == "controlled":
            c.check(f"controlled complex recovered order {name}", row["true_order"] == row["recovered_order"])
            c.check(f"controlled complex location {name}", row["location_error"] < 1e-6, row["location_error"])
            c.check(f"controlled complex native synthesis improvement {name}", row["resolved_rmse"] < row["raw_rmse"])
        elif row["true_order"] != row["recovered_order"]:
            limitations.append({"case": name, "true_order": row["true_order"], "recovered_order": row["recovered_order"],
                                "location_error": row["location_error"], "jump_error": row["jump_error"],
                                "interpretation": "stress-case jump identification failed despite finite reconstructed output"})
    burst = next(row for row in rows if row["case"] == "bursts_6_jump")
    c.check("archived burst misidentification reproduced", burst["true_order"] == 6 and burst["recovered_order"] == 9,
            {"true": burst["true_order"], "recovered": burst["recovered_order"]})
    c.check("burst location comparison correctly reports invalid order", math.isinf(burst["location_error"]))
    shape, smooth_order = (32, 32), 3
    dictionary = m.build_geometry_dictionary(shape, smooth_order)
    index = dictionary.names.index("rect_c16_16_s16_24")
    smooth = m.smooth_background_2d(shape, seed=20261006, order=smooth_order)
    truth = smooth + 0.7*dictionary.masks[index]
    selected, alpha, reconstruction, history = m.omp_unknown_order(dictionary, truth, smooth_order,
                                                    max_atoms=2, improvement_tolerance=0.01)
    c.check("small in-dictionary raster support", selected == [index], selected)
    c.check("small in-dictionary raster coefficient", abs(alpha[index]-0.7) < 1e-9)
    c.check("small in-dictionary raster synthesis", np.max(np.abs(reconstruction-truth)) < 1e-9)
    rng = np.random.default_rng(20261006)
    x, y = rng.normal(size=shape), rng.normal(size=shape)
    px, py = m.dct_lowpass(x, smooth_order), m.dct_lowpass(y, smooth_order)
    c.check("finite DCT projector idempotence", np.max(np.abs(m.dct_lowpass(px, smooth_order)-px)) < 1e-11)
    c.check("finite DCT projector self-adjointness", abs(np.sum(px*y)-np.sum(x*py)) < 1e-10)
    c.check("finite DCT complement orthogonality", abs(np.sum(px*(x-px))) < 1e-10)
    return {"complex_1d_cases": rows, "observed_identification_failures": limitations,
            "controlled_case_count": 3, "stress_case_count": 3,
            "small_raster": {"shape": shape, "candidate_atoms": len(dictionary.names), "selected": selected,
                             "true_index": index, "max_error": float(np.max(np.abs(reconstruction-truth)))},
            "scope": "controlled recovery tests passed; burst stress identification failed; complete finite raster supplied to geometric control",
            "large_out_of_model_and_natural_image_benchmarks": "archived only; not freshly replayed"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=SUITES, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    checks = Checks()
    try:
        details = complex_scoped(checks) if args.suite == "complex_benchmark" else SUITES[args.suite](checks)
        record = {"status": "PASS", "suite": args.suite, "fresh_explicit_check_count": len(checks.rows),
                  "checks": checks.rows, "scientific_details": details,
                  "interpretation": "bounded computation evidence; a successful scoped replay can include reproduced negative recovery outcomes"}
    except Exception as error:
        record = {"status": "FAIL", "suite": args.suite, "fresh_explicit_check_count": len(checks.rows),
                  "checks": checks.rows, "failure": {"type": type(error).__name__, "message": str(error)}}
        args.result.write_text(json.dumps(clean(record), indent=2, allow_nan=False)+"\n")
        raise
    args.result.write_text(json.dumps(clean(record), indent=2, allow_nan=False)+"\n")
    print(json.dumps({"suite": args.suite, "status": record["status"], "fresh_explicit_check_count": len(checks.rows)}))


if __name__ == "__main__":
    main()
