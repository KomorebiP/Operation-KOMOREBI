#!/usr/bin/env python3
"""Join measured producer costs to actual final-source Lean compilation receipts."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
r=json.loads((root/'FINAL_VERIFICATION_RECEIPT.json').read_text());bench=json.loads((root/'computations/release-final/benchmark/benchmark.json').read_text())
compiled={a['module']:a for a in r['successful_final_modules']}
rows=[];entries=[]
for c in bench['cases']:
    for x in c['results']:
        a=compiled[x['module']];assert a['source_sha256_after']==x['source_sha256']
        y=dict(case=c['name'],mode=x['mode'],iterations=x['iterations'],producer_seconds=x['median_seconds']['total'],iteration_seconds=x['median_seconds']['iteration'],certificate_seconds=x['median_seconds']['certificate'],output_seconds=x['median_seconds']['output'],export_seconds=x['export_seconds'],lean_check_seconds=a['elapsed_seconds'],receipt_path=a['receipt_path'],module=x['module'],source_sha256=x['source_sha256'])
        y['producer_export_check_seconds']=y['producer_seconds']+y['export_seconds']+y['lean_check_seconds'];entries.append(y)
    ca,pr,fu=c['results'];rows.append('| '+c['name']+' | '+str(ca['iterations'])+' / '+str(fu['iterations'])+' | '+f"{1000*ca['median_seconds']['total']:.2f}"+' | '+f"{1000*pr['median_seconds']['total']:.2f}"+' | '+f"{1000*fu['median_seconds']['total']:.2f}"+' | '+f"{pr['median_seconds']['iteration']/ca['median_seconds']['iteration']:.2f}"+'× |')
(root/'results/FULL_COST_BENCHMARK.json').write_text(json.dumps(dict(status='PASS',entries=entries,common_clean_build_seconds=r['accumulated_final_compile_process_seconds'],interpretation='Producer values are medians of five runs. Export and per-instance Lean compilation each have one measurement; their sum is an accounting estimate, not a statistically sampled end-to-end distribution.'),indent=2)+'\n')
lines=['# Bounded performance and verification cost','',
'The cache reduces work compared with recomputing every output packet. In this',
'seven-case test it does not establish an overall advantage over an efficient full',
'Richardson baseline. This is a negative result for a broad speedup claim, not a',
'failure of the certified mathematical algorithm.','',
'All modes use exact Fraction arithmetic, the same zero-skipping matrix backend,',
'exact-score stopping at epsilon^2/4, common requested epsilon/delta, a final',
'rounded certificate, and parameter output. Cached and recomputed selective runs',
'return identical candidates. The full baseline maintains its complete residual',
'by recurrence and does not waste time computing packet scores or scanning labels.','',
'One warmup precedes five repetitions, with rotating method order. Dimensions are',
'at most eight. Cases include concentrated residuals, dense residuals, a singular',
'rotated prior, rectangular observations and sigma=1/10. These are controlled',
'reference measurements, not benchmarks against optimized BLAS, GPU or GP packages.','',
'Producer time includes setup, iteration, final certificate calculation and output',
'evaluation. Times in the next table are milliseconds and exclude export/Lean.','',
'| Case | Cached / full updates | Cached ms | Recomputed ms | Full ms | Iteration speed ratio, recomputed/cached |',
'|---|---:|---:|---:|---:|---:|']+rows+['','## Export and Lean checking','',
'Every method/case also exported an explicit final-candidate certificate. All 21',
'exports compiled in separate pinned Lean processes during the clean build. The',
'posterior tolerance is therefore checked for every benchmark output gain. These',
'static certificates do not certify the Python timing trace or numeric output arrays;',
'array arithmetic is timed here, tested independently, and covered by the universal',
'output theorem and two separately checked full-program examples.','',
'| Case / mode | Producer ms | Export ms | Lean check seconds | Combined seconds |',
'|---|---:|---:|---:|---:|']
for y in entries:lines.append(f"| {y['case']} / {y['mode']} | {1000*y['producer_seconds']:.2f} | {1000*y['export_seconds']:.2f} | {y['lean_check_seconds']:.3f} | {y['producer_export_check_seconds']:.3f} |")
lines += ['',
'Per-instance checks include a fresh Lean process, import, elaboration and kernel',
'checking with common dependencies already compiled. The one-time clean dependency',
'build is recorded separately in FINAL_VERIFICATION_RECEIPT.json. A single check',
'measurement per export is insufficient to rank small differences reliably. The',
'combined column is median producer time plus one export/check measurement.','',
'## What changed and what did not','',
'Cached execution forms the full residual once at initialization, refreshes one',
'packet energy per update, and updates total energy by a difference. Selection still',
'scans stored scalar energies. The final rounded evaluator and independent exported',
'candidate checker still examine the complete model/residual obligations. The cache',
'adds storage proportional to the number of represented packet matrices.','',
'The counters in the raw report cover iterative scalar matrix kernels and selection.',
'They exclude preprocessing, final verification arithmetic, output arithmetic,',
'integer bit growth and allocation cost. No formal bit-complexity theorem is claimed.','',
'## Decision','',
'The exact cached branch is suitable for the declared checked reference release.',
'These measurements do not justify making a new rounded selective solver a release',
'gate, nor presenting the method as a fast practical alternative to established GP',
'solvers. Further performance work should first address final certification and',
'certificate-checking cost, then test substantially larger structured problems.',
'The general rounded-cache proof remains open; its naive center-only variant has',
'a checked counterexample.','']
(root/'BENCHMARK_REPORT.md').write_text('\n'.join(lines));print('Joined',len(entries),'checked benchmark outputs.')
