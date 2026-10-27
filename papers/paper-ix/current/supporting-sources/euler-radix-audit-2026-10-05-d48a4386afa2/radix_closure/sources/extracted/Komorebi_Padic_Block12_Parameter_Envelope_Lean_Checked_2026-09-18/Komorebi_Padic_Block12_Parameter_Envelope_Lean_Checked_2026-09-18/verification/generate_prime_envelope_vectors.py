#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

root=Path(__file__).resolve().parents[1]
cases=[]
# Positive-base representative cases: 12 * 50 = 600.
for p in range(1,13):
    for B in range(0,50):
        d=max(B-1,0)//p
        s=max(B-1,0)%p
        prop=(
            f"radixRepresentativeBudget {p} {B} + "
            f"radixRepresentativeBudgetPrimeEnvelopeGap {p} {B} = "
            f"radixRepresentativeBudgetPrimeEnvelope {p} {B} ∧ "
            f"radixRepresentativeBudget {p} {B} ≤ "
            f"radixRepresentativeBudgetPrimeEnvelope {p} {B} ∧ "
            f"(radixRepresentativeBudget {p} {B} = "
            f"radixRepresentativeBudgetPrimeEnvelope {p} {B} ↔ "
            f"lastRadixBlockQuotient {p} {B} = 0 ∨ "
            f"lastRadixBlockRemainder {p} {B} + 1 = {p}) ∧ "
            f"radixRepresentativeBudgetPrimeEnvelope {p} {B} ≤ {B} * {B}"
        )
        cases.append((f"representative_p{p}_B{B}",prop))
# Totalized zero-base envelope-square cases: 200.
for B in range(0,200):
    prop=f"radixRepresentativeBudgetPrimeEnvelope 0 {B} ≤ {B} * {B}"
    cases.append((f"zero_base_B{B}",prop))
# End-to-end small compiler cases: 6 * 20 * 3 = 360.
for p in (2,3,5,7,11,13):
    for r in range(1,21):
        for h in range(0,3):
            prop=(
                f"maximumLayerCompilerClosedBudgetBound {p} {r} {h} + "
                f"maximumLayerCompilerPrimeEnvelopeGap {p} {r} {h} = "
                f"maximumLayerCompilerPrimeEnvelopeBound {p} {r} {h} ∧ "
                f"maximumLayerCompilerTotalTests {p} {r} {h} ≤ "
                f"maximumLayerCompilerPrimeEnvelopeBound {p} {r} {h} ∧ "
                f"maximumLayerCompilerPrimeEnvelopeBound {p} {r} {h} ≤ "
                f"maximumLayerCompilerTestBound {p} {r} {h}"
            )
            cases.append((f"compiler_p{p}_r{r}_h{h}",prop))

file_count=8
chunks=[[] for _ in range(file_count)]
for i,item in enumerate(cases): chunks[i%file_count].append(item)
for i,chunk in enumerate(chunks,1):
    path=root/'verification'/f'LeanPrimeEnvelopeVector_{i:02d}.lean'
    lines=['import KomorebiPadic','','namespace KomorebiPadic','']
    for label,prop in chunk:
        lines.append(f'/-- {label} -/')
        lines.append(f'example : {prop} := by native_decide')
        lines.append('')
    lines.append('end KomorebiPadic')
    lines.append('')
    path.write_text('\n'.join(lines),encoding='utf-8')
print(f'files={file_count} examples={len(cases)}')
