# Independent mathematical review of the 48 new lessons

The displayed formulas, worked examples, generator semantics, and source/scope notes consistently use the stated sequence, OGF/EGF, phase, tap, and boundary conventions. All **48 lessons** were read, together with all three generators. **No unresolved mathematical or meaning-changing finding remains.**

Primary proof-audit verdict: **conditional on a named input**. The classical identification of the up/down EGF and the Apéry binomial recurrence remain explicitly identified source statements. This review does not supply new universal proofs of those source identities. The new channel, routing, FIR, reconstruction, lifting, and resampling identities have direct algebraic reductions. This distinction is compatible with the guide's teaching scope and its explicit nonclaims.

The six final chapter/generator files and six source/support files are SHA-256 pinned in `addition_independent_audit.json`. The final sequence chapter and generator match the author-ready hashes `e997d7c744e8f133cfd9c157bf5fc33cac9bd95160114ed74976515b4053402f` and `9381f0cd14c9ff99a66a2b63b1951e2cfed27461c87c55b7ad4a95f1e1ea0b53`.

## Contract and evidence

The computation uses exact Python integers, rational coefficients, and exact cyclotomic quotient polynomials. Core checks were constructed before reading the author implementations. Later additions were independently derived from the mathematical contracts. The independent script imports and executes no author generator.

The current bounded run covers **24 contract families** and executes **33,943 exact checks**, with the bounds stated individually in the result and contract. Check counts are implementation evidence, not universal proofs. Earlier run directories are superseded by the final `addition_independent_run_v4` record.

| Evidence | Result |
|---|---|
| `addition_independent_audit.py` | Independent standard-library computation |
| `addition_independent_contract.json` | Explicit domains, indexing, finite bounds, and nonclaims |
| `addition_independent_run_v4/results.json` | PASS for all 24 bounded contract families |
| `addition_independent_run_v4/manifest.json` | Version-2 bounded execution record |
| Manifest validator with `--root` | PASS against the current script/result hashes |
| Final author-file and source-record hashes | Recorded in the companion JSON |

The runner enforced a 45-second wall limit, 20-second CPU limit, 512 MiB address-space limit, one CPU core, one cooperative library thread, and 1 MiB combined output limit. The execution completed successfully. Python was 3.12.14; the independent script uses only the standard library and no randomness.

The command is recorded exactly in the version-2 manifest. The validation command was:

```text
python3 /root/.codex/plugins/cache/openai-curated-remote/mathbox/3.2.0/skills/computation-audit/scripts/validate_manifest.py evidence/addition_independent_run_v4/manifest.json --root <guide-root>
```

## Dependency graph and proof obligations

The sequence definitions and their native indices lead to exact numeric streams. An OGF keeps their raw coefficients; an EGF divides each value by the factorial of its original index. Euclidean division routes those coefficients to phase channels. A complete channel state reconstructs the scalar series. Finite operators then act either before routing or through the corresponding polynomial matrix after routing. The two routes agree by coefficient reindexing.

The named source leaves are kept separate: current official OEIS identification and formula statements; the cached PSC V Section 4 convolution proof; and bounded execution records. Plot coordinates and logarithmic display values are rendering choices and are not proof leaves.

| Obligation | Result and scope |
|---|---|
| Native offsets and initials | PASS, including tangent offset 1, tribonacci `0,0,1`, tetranacci `0,0,0,1`, and positive-index Möbius/totient |
| OGF/EGF distinction | PASS; phase splitting retains `(Mm+r)!`, rather than replacing it by `m!` |
| Root-of-unity selector | PASS over a characteristic-zero field containing a primitive root; the inverse of the modulus is required |
| Carry and refinement indices | PASS; full finite support and coarse delays are retained |
| FIR routing and composition | PASS by finite reindexing and convolution associativity |
| Recurrence taps versus reciprocal response | PASS; the denominator annihilator is finite, its reciprocal response is infinite in the Fibonacci example |
| Haar sign, normalization, and pairing | PASS; the paired block convention is explicit and differs from causal even-decimation alignment |
| Signed lifting reversal | PASS by reversing the triangular steps; no predictor/update inverse is required |
| Streaming and flush tails | PASS; the direct implementation retains `L−1` preceding samples and explicitly flushes `L−1` zeros |
| Rational resampling | PASS as a discrete indexing identity; no anti-aliasing performance is inferred |
| Source/proof distinction | PASS; Apéry and up/down source identities remain named classical inputs |
| Assembled page layout | Out of scope here; author/root visual QA is a separate record |

## Uniform reductions checked separately from finite runs

For a formal series over a commutative coefficient ring, writing each index uniquely as `n=Mm+r` proves phase reconstruction. Writing a parent index as `m=Kj+ell` proves refinement and its address permutation. Multiplication by the fine delay acts through the carry matrix; applying it `M` times gives one coarse delay times the identity.

For the root selector, the finite geometric sum is the residue indicator. This requires an invertible modulus and a primitive root. The guide chooses a characteristic-zero field and does not invoke this formula in characteristics dividing the modulus.

Fibonacci jump recurrences follow from Cayley–Hamilton for the two-by-two matrix `T^M`. Its trace is `L_M` and determinant is `(-1)^M`. This applies to every nonnegative starting offset. Canonical residue representatives impose the additional range `0<=r<M`.

For a causal finite filter, evaluating `y[Mm+r]` forces the kernel address `Mk+r−s` for input phase `s`. A wrap contributes one coarse delay. All sums are finite coefficientwise, so this derivation works for growing Fibonacci streams without an `l^p` assumption. The PSC V norm theorems are not invoked. Composition follows by the same finite double sum, or by conjugating composition through the exact routing/synthesis maps.

The Haar matrix satisfies `A^T A=I` with high channel equal to even minus odd. Its pair convention is `(x[2m],x[2m+1])`. Causal taps followed by even-index decimation instead pair `(x[2m],x[2m−1])`; the guide does not silently identify those two conventions. Lifting reversal subtracts the update, reconstructs the even channel, then adds the prediction to reconstruct the odd channel.

Streaming equality follows by induction on the retained input history. Its complete finite convolution tail is obtained by an explicit zero flush. Zero insertion places input `x[n]` at fine index `Ln`; filtering and selecting fine index `Mm` gives `y[m]=sum_n h[Mm−Ln]x[n]`. This algebraic identity supplies phase scheduling but does not specify a suitable anti-aliasing filter.

Catalan's formal quadratic solution expands to its binomial coefficients; coefficient uniqueness yields the convolution recurrence and integrality. Stirling-column EGFs are `(exp(t)−1)^k/k!`, from which the Bell and factorial-weighted Fubini EGFs follow formally. Bernoulli numbers arise from the reciprocal of `(exp(t)−1)/t`, forcing `B_1=−1/2`. The partition product counts independent multiplicities and is well-defined coefficientwise, since degree `N` uses only factors `j<=N`. Divisor identities follow from square-free inclusion-exclusion and gcd classes. Binary recurrences follow by appending a binary digit; in characteristic two, the factorization of `(1+x)^n` counts odd binomial coefficients by subsets of set bits.

The Apéry binomial recurrence is exactly identified in the pinned A005259 formula field and independently checked in the declared finite range. That match is not a newly supplied creative-telescoping proof. The pentagonal recurrence in the independent script is only an auxiliary bounded partition benchmark; it is not displayed and is not a guide dependency.

## Complete lesson coverage

Each row covers its displayed formula, worked arithmetic, reading directions, carry-forward statement, source scope, and generator/figure semantics.

| Sequence lesson | Reviewed contract | Result |
|---|---|---|
| S01 | Fibonacci/Lucas seeds and common-index defect | PASS |
| S02 | Tribonacci/tetranacci initials and recurrence start | PASS |
| S03 | Jacobsthal growing and alternating modes | PASS |
| S04 | Integer Pell update and common-index norm | PASS |
| S05 | Central-binomial/Catalan normalization | PASS |
| S06 | Catalan convolution and OGF quadratic | PASS |
| S07 | Stirling row sum and Bell EGF | PASS |
| S08 | Factorial weights and Fubini EGF | PASS |
| S09 | Derangement signs, initial values, recurrence `n>=2` | PASS |
| S10 | Positive up/down coefficients and tangent reindexing | PASS; source identity retained |
| S11 | Reduced Bernoulli coordinates and `B1=−1/2` | PASS |
| S12 | Formal partition product and finite truncation | PASS |
| S13 | Apéry polynomial recurrence and worked value | PASS; named source recurrence retained |
| S14 | Divisor convolution and native positive indices | PASS |
| S15 | Binary weight, parity, and Gould outputs | PASS |
| S16 | Polynomial prefix sums and backward differences | PASS |

| Polyphase lesson | Reviewed contract | Result |
|---|---|---|
| P01 | Three concrete Fibonacci coefficient streams | PASS |
| P02 | Complete interleaving and reconstruction | PASS |
| P03 | Two-channel resolvent and shared denominator | PASS |
| P04 | General stride recurrence; starting offset versus residue | PASS |
| P05 | Exact characteristic-zero root selector | PASS |
| P06 | Even/odd refinement into six channels | PASS |
| P07 | Two refinement orders and address permutation | PASS |
| P08 | Three carries and full boundary support | PASS |
| P09 | Polynomial product cross terms and carries | PASS |
| P10 | Original-index EGF factorial normalization | PASS |
| P11 | Secant/tangent parity and native tangent index | PASS |
| P12 | Thue–Morse affine complement | PASS |
| P13 | Binary weight affine increment | PASS |
| P14 | Haar normalization, signs, and energy | PASS |
| P15 | Explicit discarded-channel noninjectivity witness | PASS |
| P16 | Complete finite operation square and final coefficient | PASS |

| Tap lesson | Reviewed contract | Result |
|---|---|---|
| T01 | Causal delayed contributions | PASS |
| T02 | Applied FIR on Fibonacci values | PASS |
| T03 | Three-tap two-phase matrix | PASS |
| T04 | Indexed coefficient nodes and tap weights | PASS |
| T05 | General finite FIR routing and four-phase matrix | PASS |
| T06 | Signed FIR composition and matrix multiplication | PASS |
| T07 | Finite differences and boundary residuals | PASS |
| T08 | Fibonacci denominator taps and initial impulse | PASS |
| T09 | Phase-specific numerator residuals | PASS |
| T10 | Finite numerator kernels versus infinite reciprocal | PASS |
| T11 | Exact gain/zero and bounded frequency illustration | PASS |
| T12 | Symmetric delay, amplitude sign, and undefined zero phase | PASS |
| T13 | Fixed Haar pair convention and exact inverse | PASS |
| T14 | Signed predict/update lifting reversal | PASS |
| T15 | Rate `3/2`, phase schedule, and finite tail | PASS |
| T16 | Chunk state and explicitly flushed tail | PASS |

## Resolved findings and proofreading

| Finding | Final resolution |
|---|---|
| T04 mixed indexed delays with OGF-delay arrow labels | Arrow labels are now weights `1,2,1`; node subscripts carry the shifts |
| T06 used a comma in a matrix product | Explicit multiplication dot |
| P04 table included `M=1,r=1` under an implicit residue interpretation | Starting offset is explicit; canonical residue range is separate; P05 domains are explicit |
| S09 recurrence lacked its starting range | `n>=2` is stated beside the recurrence |
| S16 backward differences lacked a starting convention | `n>=1` is explicit with zero-index boundary values |
| S13 directions referred to a table | Directions identify the prefix annotation |

The repaired source text and generator labels were re-read. The reviewer made no edits to author files and no mathematical-token changes in the manuscript. Routine prose alignment was handled by the author. No objective mathematical or meaning-changing issue remains.

## Limits and remaining source boundary

This review supplies no new Lean certificate, novelty result, universal proof from computation counts, generic finite stationary filter for arbitrary OEIS sequences, or analytic convergence/performance guarantee. Native sequence identification, source formula statements, universal algebraic reductions, bounded execution, and page QA remain separate evidence classes. The source proof boundary is explicit; there is no remaining blocking correction within the 48-lesson audit scope.
