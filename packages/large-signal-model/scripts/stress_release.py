"""Reproducible finite stress sweep. Each row is a case, not a theorem."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from komorebi_pr_lasm import MultiAtlasAnalyzer, analyze_signal, PolyphaseFIR, StreamingFIR
from komorebi_arc3_offline.bayes import BayesianRegression
from komorebi_arc3_offline.lasm_benchmark import run_operator_benchmark


def run(output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261009)
    rows = []
    for seed in (0, 7, 19):
        random = np.random.default_rng(seed)
        for length in (1, 2, 3, 7, 16, 31, 64, 257, 1024):
            for modulus in (1, 2, 3, 4, 7):
                for tap_count in (1, 2, 3, 8, 15):
                    for scale in (1e-9, 1.0, 1e6):
                        x = random.normal(size=length) * scale
                        h = random.normal(size=tap_count)
                        truth = np.convolve(x, h)
                        bank = PolyphaseFIR(h, modulus)
                        full = bank.apply(x)
                        stream = StreamingFIR(h)
                        cuts = sorted(set([0, length, length//3, 2*length//3]))
                        pieces = [stream.process(x[a:b]) for a,b in zip(cuts,cuts[1:])]
                        causal = np.concatenate(pieces + [stream.flush()])
                        normalization = max(1., float(np.max(np.abs(truth))))
                        fir = float(np.max(np.abs(full - truth)) / normalization)
                        chunk = float(np.max(np.abs(causal - truth)) / normalization)
                        rows.append({"seed": seed, "length": length, "modulus": modulus,
                                     "tap_count": tap_count, "scale": scale,
                                     "fir_relative_max": fir, "stream_relative_max": chunk,
                                     "passed": bool(fir < 1e-11 and chunk < 1e-11)})
    images = []
    for index in range(160):
        shape = tuple(int(n) for n in rng.integers(1, 66, size=2))
        values = rng.normal(size=shape) if index % 2 else rng.integers(0,16,size=shape)
        analyzer = MultiAtlasAnalyzer()
        analysis = analyzer.analyze(values)
        residual = max(analysis.reconstruction_residuals().values())
        finite = bool(np.isfinite(analyzer.feature_vector(analysis)).all())
        images.append({"shape":list(shape),"max_residual":residual,"finite_features":finite,
                       "passed": bool(residual < 1e-11 and finite)})
    signals = []
    for length in range(1, 161):
        x = rng.normal(size=length)
        a = analyze_signal(x, modulus=1+length%9)
        residual = max(a.reconstruction_residuals().values())
        signals.append({"length":length,"max_residual":residual,"passed":residual<1e-11})
    # Negative control with known independent held-out input, no test-label fitting.
    x = rng.normal(size=(180, 6)); coefficient = rng.normal(size=(6, 3))
    y = x @ coefficient + rng.normal(scale=0.01, size=(180, 3))
    model = BayesianRegression(prior_precision=.1)
    intact = model.fit(x[:120], y[:120])
    shuffled = model.fit(x[:120], y[rng.permutation(120)])
    normal_error = float(np.sqrt(np.mean((intact.predict(x[120:])[0]-y[120:])**2)))
    shuffled_error = float(np.sqrt(np.mean((shuffled.predict(x[120:])[0]-y[120:])**2)))
    negative = {"control":"permuted training targets, same unseen test rows",
                "normal_rmse":normal_error,"shuffled_rmse":shuffled_error,
                "error_ratio":shuffled_error/normal_error,
                "passed":shuffled_error>10*normal_error}
    operators = []
    for seed in (0, 1, 4, 11, 23):
        path=output/f"operators_seed_{seed}";path.mkdir(exist_ok=True)
        for row in run_operator_benchmark(path,seed=seed):
            operators.append({"seed":seed, **row})
    summary = {
        "status":"PASS" if all(row['passed'] for group in (rows,images,signals) for row in group) and negative['passed'] and all(r['family_match'] and r['atlas_match'] for r in operators) else "FAIL",
        "fir_cases":len(rows),"fir_passed":sum(r['passed'] for r in rows),
        "max_fir_normalized_error":max(r['fir_relative_max'] for r in rows),
        "max_stream_normalized_error":max(r['stream_relative_max'] for r in rows),
        "image_cases":len(images),"image_passed":sum(r['passed'] for r in images),
        "max_image_residual":max(r['max_residual'] for r in images),
        "signal_cases":len(signals),"signal_passed":sum(r['passed'] for r in signals),
        "max_signal_residual":max(r['max_residual'] for r in signals),
        "negative_control":negative,
        "operator_cases":len(operators),
        "operator_family_matches":sum(r['family_match'] for r in operators),
        "operator_atlas_matches":sum(r['atlas_match'] for r in operators),
        "operator_median_rmse_ratio":float(np.median([r['state_rmse_ratio'] for r in operators])),
        "operator_identification_failures":[r for r in operators if not r['family_match'] or not r['atlas_match']],
        "scope":"finite CPU float64 controls and in-grammar synthetic identification; not an ARC or open-world score",
    }
    for name,data in (("fir_cases",rows),("image_cases",images),("signal_cases",signals),("operator_cases",operators),("summary",summary)):
        (output/f"{name}.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('results/release_stress'))
    result=run(parser.parse_args().output)
    print(json.dumps(result,indent=2,allow_nan=False))
    raise SystemExit(0 if result['status']=='PASS' else 1)
