# Continuation — Sufficient Resolution v0.5.0

Read README.md, BLOCK_05_THEOREMS.md, PROGRESS.md, AUDIT.json and
VERIFICATION_SUMMARY.md completely. Replay scripts/verify.py with the pinned
portable runtime before changing proof status. Preserve predecessor production
files. Historical logs and sampled tests are not fresh universal verification.

## Checkpoint

369 theorem/lemma declarations, 30 production modules and 469 explicitly named
declarations. Block 05 adds 97 theorems in eight modules. All 22 v0.4.0 production
sources are byte-identical. Counts belong only to this standalone program.

The exact resolution/globalization, discrete memory, finite observable model,
minimum-dimension and quantitative discrete approximation layers are preserved.

The new continuous branch defines bounded real maps A,B,G,D on Banach spaces and
L(y,z)=(Ay+Bz,Gy+Dz). Actual trajectories exp(tL)(y0,z0) yield the derived equation

    y'(t)=Ay(t)+B exp(tD)z0+integral_0^t [B exp((t-s)D)G]y(s) ds.

The proof uses differentiated backward propagation and the fundamental theorem
of calculus. It does not assume a memory equation or a black-box Duhamel formula.

The analytic transfer theorem proves that bounded observations of exponentials
agree for every real time iff their observations of every generator power agree.
This connects the unchanged discrete closure theorem to continuous prepared closure:

    E(t)=exp(tA) for all t
      iff M(t)=0 for all t
      iff B D^n G=0 for all n
      iff E(s+t)=E(s)E(t) for all real s,t.

With d=dim H finite, moments k<d suffice. Actual Mathlib iterated derivatives
E^(n)(0)=A^n through n=d+1 form an equivalent certificate. These are exact
whole-operator derivatives, not samples at selected times. A monic annihilator
of D supplies an alternative finite certificate.

For arbitrary bounded C,R with CR=I, finite generator tests are sized by
actual dim ker C and do not require orthogonality. All-state intertwining is
equivalent to qL=Aq. In the block case closure for every hidden initial condition
is equivalent to B=0. Prepared closure with z0=0 is strictly weaker.

The explicit nilpotent example has M(t)=tI and its first visible error in the
third derivative. A second example has B,G nonzero and M identically zero, yet
arbitrary hidden initialization is observable.

## New module order

ContinuousFlow, VariationOfConstants, ExponentialTransfer, ContinuousMemory,
ContinuousClosure, ContinuousJets, ContinuousSplit, ContinuousExamples.
The cumulative dependency order is MODULES in scripts/verify.py.

## Next block

Derive continuous approximate-intertwining/Duhamel identity from the actual flows:

    E(t)=q exp(tL)-exp(tA)q,
    delta=qL-Aq,
    E(t)=integral_0^t exp((t-s)A) delta exp(sL) ds.

Then prove norm bounds using explicit bounds on both flows, including distinct
and equal growth rates and arbitrary initialization. Prefer bounded real Banach
operators first. Preserve t>=0 restrictions on estimates, in contrast to oriented
all-real-time exact identities. Do not assume the desired integral identity.

## Boundaries to retain

No unbounded generator/domain, nonlinear, time-varying or stochastic-noise theorem.
No automatic positive/stochastic/integral realization. No system identification
from samples. No approximate minimal-dimension theorem. The classical real Banach
formalization does not automatically endow every older quotient with a norm.
The full trajectory satisfies the memory equation, but reconstruction of every
abstract Volterra solution is not separately formalized here. No arithmetic
existence or Langlands correspondence is claimed.

## Reproduction

    python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
    python3 scripts/validate_manifest.py verification/local-replay/computation-manifest.json --root .
    python3 scripts/check_continuous_memory.py

Linux x86_64 Lean 4.34.0-rc2 and the pinned Mathlib cache are required. The runtime
is not duplicated in the source archive. Imported artifacts are reused, while
project modules are rebuilt and replayed using the same Lean kernel.

## One-line continuation prompt

Open this ZIP, read CONTINUE_HERE.md, PROGRESS.md and AUDIT.json, replay the pinned
verifier, then derive and prove the continuous-time approximate-intertwining
Duhamel identity and explicit norm bounds, preserving all existing proof sources,
initialization distinctions and proof boundaries.
