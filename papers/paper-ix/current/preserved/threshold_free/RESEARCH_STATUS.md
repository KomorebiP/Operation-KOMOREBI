# Program checkpoint

Goal: remove the \(\min(k,n)\) threshold from the actual Nishibuchi reciprocal coefficients and push the resulting theorem to defensible stronger statements.

## Claim map

| Claim | Evidence type | Status and boundary |
|---|---|---|
| All-row \(2^k\) higher differences for \(N=4\) | Algebraic reciprocal induction; independent audit | Closed, including \(k>n\) |
| All dyadic section sizes and mixed-step precision | Same induction plus exact source kernels | Closed for every \(N=2^a\), every allowed address |
| Sign-twisted prime-power theorem | General-prime induction; separate audit | Closed; raw odd-prime ordinary difference statement is false |
| Least periods and isometry for all four \(N=4\) addresses | Universal Newton bound plus exhaustive low-order certificate | Closed, from row zero |
| Same first-distance law at \(N=2,8\) and all-rank lower-half family | Complete low certificates and symbolic binomial proof | Closed in stated scope |
| Universal larger upper-half exact distance law | Exact rational counterexamples | Refuted; the lower divisibility theorem survives |
| Factorial gain with surplus \((0,0,3,1)\) for normalized \(N=4\) coefficients | Divided-power proof plus tangent/cotangent transfer | Closed; independently audited |
| Exact homogeneous higher differences at addresses 0 and 1 | Divided-power unit parity; finite operator expansion | Closed; independently audited |
| Mixed-step leading parity at addresses 0 and 1 | Classification of every possible leading expansion term | Closed; cancellations prevent an unrestricted equality formula |
| Address-two paired filtration and exact power-of-two orders | Bernoulli central-factorial lemma and divided-power filtration/parity | Closed; independently audited |
| Exact Taylor radii at addresses 0, 1, 2 | Coefficient bounds and unbounded exact-degree subsequences | Closed; independently audited |
| Exact valuations at every order for addresses 2 and 3 | Bounded patterns and counterchecks only | Open beyond the exact family stated in README |
| Separate Euler-tail simplicity/nonvanishing problem | Earlier project state, not tested here | Open; no implication claimed |
| New Lean formalization | No compilation in this checkpoint | Not performed |

## Routes and evidence

The generic reciprocal induction changes the source character \(+1\) to \(-1\). The dyadic character conversion is integral and proves the original goal. An independent umbral expansion gives the same all-row conclusion.

A factorial version of the generic induction was not assumed. The negative-character inverse already fails that stronger property in the actual address-zero example. The separate divided-power transformation supplies the needed positive-character cancellations. The failed shortcut and its exact witnesses remain in combinatorial/FACTORIAL_SHARPENING_BOUNDARY.md.

The stronger \(N=4\) route has four links: ordinary Euler divided-power moments to address zero; a tangent-factor transfer to address one; an elementary Bernoulli central-factorial construction for address two; a cotangent-factor transfer to address three. Exact unit parity closes addresses zero and one. A finer paired filtration and elementary Bernoulli parity identify unbounded sharp address-two orders and its exact Taylor radius.

The first-difference sharpness proof uses only finitely many low coefficients because the global theorem rigorously covers every omitted order. This is a finite exact proof certificate attached to a universal estimate, not an inference from successful row testing.

Computations through row 512 were executed before the factorial proof closed. Supplemental runs through row 96 test the sharper conclusions. Their executed code revisions and contracts are retained with independent manifest validation. Failed exact extensions remain visible as exact counterexamples.

## Scope of this closeout

The original threshold-free target is discharged. This checkpoint preserves the strengthened proved conclusions and their exact boundaries. The next unresolved mathematical task would be a full exact valuation law for the remaining address-two orders or address three; that task must account for mixed-step and base-row cancellations. It is not needed for the closed congruence theorem.

Final proof and audit revisions are pinned in CHECKPOINT_MANIFEST.json. Computation manifests separately pin executed code and input contracts.
