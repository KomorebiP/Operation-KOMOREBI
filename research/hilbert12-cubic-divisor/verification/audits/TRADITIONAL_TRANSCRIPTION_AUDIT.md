# Independent traditional transcription check

Normalized claim: the rendered `principal.tex` and `reconstruction.tex` preserve the definitions, signs, ranges, formulas and proof steps of the retained v0.13 and v0.14 sources. This is a source-transcription audit, not a replacement audit of every external analytic theorem.

Final primary verdict: **proved as written**, for the scoped source-preserving transcription claim. The current sections preserve the retained mathematical formulas and proof route, with the required period-matrix hypothesis and the canceled-singularity continuation stated explicitly. This does not assert a newly independent proof of all external analytic inputs.

The initial review required a restriction in the finite-theta theorem wording: “positive-definite period matrices” must mean symmetric Riemann period matrices with positive-definite imaginary parts. The proof already used `Y = Im Ω > 0`; the raw source explicitly states this condition. No sign, index, scalar-normalization or displayed-formula transcription error was found.

## Exact initial revision

| Artifact | SHA-256 |
|---|---|
| `traditional/sections/principal.tex` | `841c3d0021dfc42dfd81206e1cc1f2fdf1fb4a70800f7d8cc65f81bf8a6e8f41` |
| `traditional/sections/reconstruction.tex` | `92e295263aca0f509f894eb00b141f34cf1cb1d5a07520650c8241cac72990da` |
| `sources/v014/PROOF.md` | `0a2c32818790213efc30dd566ed124841bf647357764e6424b4149083e7712d1` |
| `sources/continuation_chain/01/Komorebi_H12_Principal_Divisor_Transport_Lean_v0.13.0/PROOF.md` | `7b8b42ea194af5d14a9386f915819a3990724b4a26a56d89dc40c798b5c6f0b4` |

## Obligations checked independently

| Obligation | Result |
|---|---|
| Fixed periods, negative-period continuation represented by `F = S₅(z+t;t,s)⁻¹` | Passed; matches v0.13. |
| `βτ`, `βs`, `βδ`, seven-product ranges `k=0,…,6` | Passed. |
| Base divisor `w(c)[H(a)−H(b)]`, strict positivity of `H`, smoothing weights | Passed, including `a=0`, `b=0`. |
| `N₅`, inverse, quotient generator `(1,2,20)/7`, ceiling pivot and unique residue digit | Passed. The generator uses basis `(τ,s,1/5)`. |
| Integral lift `(p,2p−a,20p+5b−8c)` and equality of weights | Passed; direct matrix substitution and residue comparison. |
| Complete signed bracket and all three rays | Passed, including both signs of the nonzero `ns` ray. |
| Transition ranges `1,…,15`, `0,…,6`, `0,…,3`, `1,…,8` and reciprocals | Passed against raw v0.13 equations (12)–(15). |
| Period-one triple shift, digit carry, zero anchor and central argument | Passed. Eta factors cancel as in source; the anchor keeps three reciprocal theta values. |
| `n³` distinct order-four zeros, `4n³` distinct simple poles, each multiplicity `4n³` | Passed, including the worked `n=1` digit/lift table. |
| Upper cubic bound, unsigned versus signed counts, finite-theta grammar | Passed after the imaginary-part hypothesis clarification. The single global unit is outside finite polynomial sums. |
| Actual support `m≠0`, zero excluded, genus-three jets and ungrouped absolute minimality | Passed. Signed regroupings are explicitly outside the minimality statement. |
| Analytic tail constants `4A/T`, `2A|z|⁴/T`, `T≥R_*`, `|z|≤T/2` | Passed; independently reconstructed partial summation and local power-series estimate. |
| Fourth logarithmic derivative coefficient `−6`, argument scaling and absolutely convergent fourth powers | Passed as meromorphic identities. See the local-domain clarification below. |
| Reflection ranges and pairing of six `L_t` values; `α₂` factor `1/2` | Passed. The paired sum is `2Σ L_t(u_j)` and `(log T)″(0)=4α₂`. |
| Combined `B_D(1)` summand, cancellation through degree three, `α₃` sign/range | Passed; the combined remainder is `O(|λ|⁻⁴)` and the formula is `−[β²Σ₁¹⁵L_t(rs)+B_D(1)]/6`. |
| Exponential of `α₁`, special cube exponents `−2/3`, `−8/9` | Passed. No principal logarithm is substituted. |
| Regularized conjugation and open periodic/arithmetic comparison | Passed. Ordinary analytic statements and the open equality are not represented as Lean proofs. |

## Findings and scope

1. Required hypothesis clarification in the finite-theta theorem: write “symmetric period matrices with positive-definite imaginary parts `Im Ωℓ`.” This is uniquely forced by the raw definition and by the displayed proof.
2. A useful local-domain clarification for the fourth-log proof is to derive initially away from the union of the individual gamma-factor divisors, then cancel coefficients and extend meromorphically to `C \ D`. A canceled constituent singularity can lie outside the final support `D`. This is the already-stated meromorphic interpretation, not a new proof route or a change to the formula.

No author files were edited by this reviewer. The seven-point multiplication identity's full appendix and the external theta/Jensen/gamma source authentication are not newly audited here; they remain dependencies covered by the separate proof/literature audit. No finite diagnostic is used as a universal complex-analytic proof, interval certificate, or proof of `UΓ=Ualg`.

## Final changed-lines recheck

The author confirmed the mathematical sources frozen. The revised finite-theta theorem now says “symmetric period matrices ... with positive-definite imaginary parts.” The fourth-log proof now derives off the union of constituent gamma-factor divisors and extends by meromorphic continuation after cancellation to `C \ D`. Both corrections were re-read independently in context and pass. Added Jensen/sine citation commands do not change the formulas. The updated local distinction between the integer step function and the CM Green quantity also changes no formula. Both named section contents were re-inspected.

| Final artifact | SHA-256 |
|---|---|
| `traditional/sections/principal.tex` | `6120cd959632d8df067709c8b12e97d1c5b36be2edbfe29039ddf1a1bcf8bbb2` |
| `traditional/sections/reconstruction.tex` | `7d8796105f5c625f1935507730a9d83356c8225980f9bd1fa0990bd90ec9e14d` |

Both raw source hashes remain unchanged. No unresolved formula/proof-step transcription defect remains in these two scoped sections. Subsequent figure-only insertions are allowed within the author's publication work but would change the TeX hash; they require a recorded diff establishing that the audited mathematics is unchanged. This report does not silently extend to future revised mathematical text.

## Final figure-insertion preservation check

The final publication inserts the cover, fourth-log ambiguity and special-cube figures, and adjusts the existing family figure caption/size. Removing only those inserted figure blocks and paragraph-spacing commands in memory, and restoring the earlier family figure block, reconstructs **both exact previously audited TeX hashes**. This independently verifies that the mathematical text outside those publication blocks is unchanged. The added captions were checked against the already audited source formulas: the seven-label action is multiplication by four; the `n=2` family has eight order-four zeros and 32 simple poles; divisor matching alone produces a holomorphic unit; and the cube coefficients are `0,−2/3,−8/9` without an arithmetic evaluation claim.

The final principal figure was placed after the complete paragraph. The preservation evidence is `TRADITIONAL_FIGURE_INSERTION_PRESERVATION.json`. Final pinned publication source hashes:

- `principal.tex`: `058b9221ba7c66df361e903f4b0eb9616389faf949129b8a8ae59c45713032f9`.
- `reconstruction.tex`: `76ac15a1fdf6792e01bba369a96e99bc012cb0c28f5224752c1b4daefe0c1af6`.

The scoped mathematical transcription verdict remains passed. Traditional PDF native-page coverage is supplied by the separate publication review; this reviewer does not claim to have inspected all of those pages.

Coverage: both named TeX sections read completely, raw v0.13 read through its divisor, transitions, anchor and conjugation arguments, raw v0.14 read completely; relevant v0.12 definitions and four-line norm source checked separately. These are independent source/formula checks rather than acceptance of an author's QA verdict.
