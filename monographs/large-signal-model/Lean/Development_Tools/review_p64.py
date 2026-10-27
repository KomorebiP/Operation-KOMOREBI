from pathlib import Path
import hashlib, json

root = Path('/workspace/scratch/ea498747acd5/work/Komorebi_LSM_Lean_0.18.0')
expected = {
    'BernsteinKernel': '005b4bfb8cbbef7ad936ba60db6ef0c962dcb020388ec0941c554f620b10a5cd',
    'PositivePolynomialApproximation': 'e928c825c37a5d0f6be7bb8e423d0a1227eefc0f041fd5cace7f868776eff2a8',
}
for name, digest in expected.items():
    assert hashlib.sha256((root / 'KomorebiLSM' / (name+'.lean')).read_bytes()).hexdigest() == digest
report_path = root / 'verification/p64_positive_polynomial/REPORT.json'
report = json.loads(report_path.read_text())
assert report['passed'] and report['source_sha256'] == expected
assert len(report['axioms']) == 68
assert all(set(v) <= {'propext', 'Classical.choice', 'Quot.sound'} for v in report['axioms'].values())
checks = [
    'Literal Bernstein basis, positivity, partition of unity, and exact integrals 1/(n+1), including n=0',
    'Actual derivative ladder and degree elevation derive the beta first moments; no moment identities assumed',
    'The literal Durrmeyer kernel is nonnegative on the unit square, symmetric, and has both exact unit marginals',
    'Actual restricted Lebesgue product and withDensity joint probability law, with explicit support and integral dictionary',
    'Actual joint squared displacement equals 1/(3(n+2)); the first-square, second-square, and cross-moment computations have the correct constant',
    'Cauchy-Schwarz follows from nonnegative variance under the actual joint law, with integrability and denominator positivity justified',
    'Literal Bochner coefficient integrals define the finite approximating polynomial; actual degree at most n follows from its power expansion',
    'Closed convex cone integration derives positivity of every coefficient and every approximating branch on [0,1]',
    'Double stochasticity derives exact integrated operator equality and hence mass conservation of the constructed DensityInstrument',
    'The pointwise and integrated errors use the genuine probability-cone base norm, including its proved integral inequality',
    'The induced base-norm Lipschitz premise gives the normalized-input discrepancy; no finite true-degree hypothesis is introduced',
    'The actual arbitrary common reported-history policy record laws satisfy min(1, T*L/(2*sqrt(3(n+2)))) through the full P59 theorem',
    'Zero-L and zero-degree cases remain meaningful; normalization and nonzero displacement controls reject the stated false alternatives',
]
out = {
    'claim': 'P64 valid positive polynomial approximation',
    'verdict': 'proved as written in the registered scope',
    'provenance': 'Coordinator raw-source review of all 703 lines, separate from the author. Same model/team lineage, not external independent certification.',
    'source_hashes': {'KomorebiLSM/'+k+'.lean': v for k,v in expected.items()},
    'checks': [{'obligation': x, 'passed': True} for x in checks],
    'proof_route': 'The exact mixed and marginal moment computation replaces the equivalent conditional-beta variance computation in the prose; the actual joint law and constant coincide.',
    'scope_limit': 'Numbered proposition and its whole-law conclusion. Adjacent illustrative scalar truncation examples are not newly claimed here.',
    'execution_boundary': 'Author individual compilation, all 68 named axiom records, two module kernel replays and both semantic rejection controls were inspected in the hash-bound report. This coordinator review did not rerun those commands; fresh cumulative .18 verification is still required.',
    'author_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
}
dest = root/'verification/p64_positive_polynomial/RAW_COORDINATOR_REVIEW.json'
dest.write_text(json.dumps(out, indent=2)+'\n')
print(dest)
print(hashlib.sha256(dest.read_bytes()).hexdigest())
