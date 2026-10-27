# Komorebi Sufficient Resolution — Lean v0.5.0

**Komorebi P. · 13 September 2026**

Cumulative formalization of exact resolution, compression defects, linear globalization,
behavioral minimality, discrete memory, quantitative approximate sufficiency, and now
**continuous-time hidden-state elimination and exact closure**.

**369 theorem/lemma declarations in 30 proof modules. 469 explicitly named declarations.**
This block adds 97 theorem/lemma declarations and 112 named declarations in eight modules.
All 22 v0.4.0 production proof files are byte-identical. Counts include helpers and examples,
not independent discoveries. The Papers I–XII theorem census is not modified.

## Main new contract

V and H are real Banach spaces. A, B, G and D are bounded continuous linear maps.
Construct the full operator L(y,z)=(Ay+Bz,Gy+Dz) and the actual trajectory
(y(t),z(t))=exp(tL)(y0,z0). The formalization derives

    z(t) = exp(tD)z0 + integral_0^t exp((t-s)D) G y(s) ds,
    y'(t) = A y(t) + B exp(tD)z0 + integral_0^t M(t-s)y(s) ds,
    M(t) = B exp(tD)G.

No Volterra equation or desired exponential correspondence is assumed as an input.
The results quantify over all real times. Negative intervals are oriented integrals.
The full homogeneous ODE has the constructed exponential trajectory as its unique solution.

For prepared hidden state z0=0 and E(t)=C exp(tL)R,

    E(t)=exp(tA) for all t
      iff M(t)=0 for all t
      iff B D^n G=0 for all natural n
      iff E(s+t)=E(s)E(t) for all real s,t.

If d=dim H is finite, this is equivalent to B D^k G=0 for k<d and to
E^(n)(0)=A^n for n<=d+1. These are exact whole-operator moments/derivatives,
not agreement at finitely sampled times. A supplied monic annihilator of D gives
an alternative finite certificate without a finrank hypothesis.

For arbitrary bounded C,R with CR=I, the finite generator certificate is sized by
dim ker C. Orthogonality is not required. All-state closure, allowing every hidden
initial condition, is stronger: in the block system it is equivalent to B=0.

## New modules

| Module | Theorems | Content |
|---|---:|---|
| `ContinuousFlow` | 14 | Actual bounded exponential, derivatives, composition, inverse-time identities and differentiable jets. |
| `VariationOfConstants` | 6 | Backward propagator, derived forced integral formula, homogeneous and forced uniqueness. |
| `ExponentialTransfer` | 11 | All-time observed exponential equality iff every generator moment agrees; exact compression defect. |
| `ContinuousMemory` | 18 | Actual full generator and trajectories, hidden elimination, arbitrary-initialization Volterra equation. |
| `ContinuousClosure` | 19 | Memory/closure/composition equivalences, finite certificates, prepared versus all-state closure. |
| `ContinuousJets` | 9 | Mathlib iterated derivatives, first-return derivative identity, finite derivative certificates. |
| `ContinuousSplit` | 4 | Arbitrary bounded split compression with finite-dimensional ker C; all-state intertwining. |
| `ContinuousExamples` | 16 | Polynomial hidden memory and delayed return; two nonzero couplings with zero prepared feedback. |

`BLOCK_05_THEOREMS.md` maps formulas to exact declaration names.
`PROGRESS.md`, `AUDIT.json` and `CONTINUE_HERE.md` give status and continuation boundaries.

## Reproduction

    python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
    python3 scripts/validate_manifest.py verification/local-replay/computation-manifest.json --root .

The verifier rebuilds all production modules with warnings as errors, audits all named
declarations against propext/Classical.choice/Quot.sound, runs same-kernel leanchecker replay,
executes deliberately invalid controls and runs all retained Python tests. The root
`AxiomAudit.lean` is the cumulative human-readable audit inventory.

Pinned Lean/Lake: leanprover/lean4:v4.34.0-rc2.
Lean commit: 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
All nine dependency revisions are compared with lake-manifest.json.

The multi-gigabyte Linux x86_64 runtime and cached imported artifacts are not bundled.
Restoration uses the retained compact parts and LEAN_RUNTIME_METADATA.json.
The project is offline-reproducible once those dependencies are restored.
Windows/WSL is not separately exercised in this release.

## Exact finite controls

    python3 scripts/check_continuous_memory.py

The new standard-library-only test compares Taylor coefficients through degree eight in
32 rational systems with visible and hidden dimensions 0–3. Polynomial antiderivatives
are independently expanded, and mixed-time compression coefficients are compared with
hidden returns. It also tests the nilpotent delayed-return example. These controls
passed 2,127 exact assertions and rejected 15 corrupted/invalid inputs. They do not
numerically approximate an exponential or establish any universal theorem by sampling.

Earlier scripts remain available:

    python scripts/observable_model.py --input examples/observable_model_input.json --output model.json
    python scripts/approximate_certificate.py --input examples/approximate_model_input.json --output bounds.json

The Python implementations and certificate parsers are tested, not extracted from Lean
or themselves formally verified. The universal claims are the Lean declarations.

## Boundaries

This block is for bounded, time-independent real linear generators. It does not prove
unbounded-operator domain theorems, nonlinear or stochastic elimination, time-varying
memory, a new continuous-time approximation estimate, or system identification from data.
It proves the constructed full trajectory satisfies the memory equation. The converse
reconstruction of every abstract Volterra solution is not separately formalized here.
The continuous finite certificate uses derivatives at zero, not sampled-time agreement.
No positivity, arithmetic existence, Langlands correspondence, novelty, or priority claim
is inferred from the formalization.

See VERIFICATION_SUMMARY.md for actual completed runs and their trust boundary.
