# Continuation — Sufficient Resolution v0.3.0

Read README.md, BLOCK_03_THEOREMS.md, PROGRESS.md, and AUDIT.json. Verify the current
source with scripts/verify.py and the exact pinned portable runtime before extension.
Do not treat copied historical evidence as a new replay.

## Production modules (dependency order)

1. ExactResolution
2. Compression
3. Globalization
4. ObstructionTransport
5. Behavioral
6. Examples
7. DiscreteMemory
8. MemoryClosure
9. FiniteMemory
10. SplitMemory
11. MemoryExamples
12. FiniteHorizon
13. BehavioralMinimality
14. FiniteObservableModel
15. FiniteCertificate
16. ObservableExamples

There are 190 explicit theorem/lemma declarations and 263 explicitly named source
declarations. The 11 v0.2.0 production proof files are unchanged. Historical ZIPs
and their evidence are retained separately. Do not add these numbers to other
project counts without qualified-name deduplication.

## Current theorem checkpoint

For known operations T_i and linear observation O on finite-dimensional X, let
N_r contain states invisible to words of length at most r and k=dim ker O.
N_(r+1)=ker O ∩ intersection_i T_i^(-1)N_r. A plateau is exact, and N_k=N, where N
is the all-future invisible subspace. Equality of observations through k decides
all-future equality. The proof allows an infinite alphabet; finite enumeration
explicitly requires a finite one.

The actual finite observation range Ran H_k is equivalent to X/N, carries checked
dynamics/readout, and is minimum-dimensional among exact linear models of the
specified behavior. The comparison comes from Ran q, unless q is surjective.

A finite certificate q=G H_r, q T_i=U_i q, Vq=O proves ker q=N without requiring
finite-dimensional X. Surjective q yields an equivalence with the canonical
minimal state, compatible with dynamics and observation.

The rational row-saturation program carries sparse generation witnesses and
checks certificate identities. It is not formally verified Python or extracted
Lean. One noncommuting rational example is fully instantiated in Lean.

## Next block

Develop quantitative approximate sufficiency. Start with the exact telescoping
formula for q T_w − U_w q from one-step intertwining defects. Add readout error,
then norm bounds with named operator-growth hypotheses and stability conditions.
Do not infer exact or uniformly controlled behavior from finite noisy samples.

Keep continuous-time memory, admissibility/positivity, nonlinear models, and
arithmetic existence separate. Preserve prior source contracts and proof boundaries.

## One-line continuation

Open this ZIP, read CONTINUE_HERE.md and PROGRESS.md, replay the pinned verifier,
then prove the quantitative approximate-sufficiency block with explicit growth
and conditioning hypotheses, preserving all existing source and claim boundaries.
