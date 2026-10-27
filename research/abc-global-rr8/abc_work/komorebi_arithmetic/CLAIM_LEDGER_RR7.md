# RR7 claims and scope

Base RR6 archive SHA-256:
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.
The earlier phase ledgers remain historical inputs, not overwritten views.

| ID | Exact statement | Evidence and limit |
| --- | --- | --- |
| KS1 | For fixed B>=2, the explicit factorial-residue view space is canonically the set of positive primitive a+b=c with max coordinates<=B | Complete proof in routes/integer_space/PROOF_NOTE.md; focused context-free audit. No conductor-dependent B established. |
| KS2 | The factorial coherent family lies in lim_N union_B F_N(B), outside union_B lim_N F_N(B), with minimal level-N budget 1+sum_(k<N)k! | Complete proof and audit. Its radicals are not held fixed; no ABC violation asserted. |
| KS3 | The finite integer additive protected-correction obstruction modulo M is the class of A+B-C in Z/MZ | Complete proof and audit before positivity/budget restrictions. |
| WK1 | Normalized Teichmuller sections exist uniquely at every prime and precision; their carry classes reduce naturally and are nonzero at precision N>=2 | Proved in routes/witt_space/PROOF_NOTE.md with exact finite coefficients and edge cases. |
| WK2 | The carry quotient injects into the actual protected obstruction quotient of the declared finite additive view category | Complete diagram-level proof. No claim that the two whole quotients are equal. |
| WK3 | Retaining carry views and multiplication gives a unique normalized coherent table; the precision maps commute; separate digit rings reconstruct Z_p | Complete proof. Multiplication is Set-valued/nonlinear; no unrestricted additive-correction theorem is imported. |
| PC1 | The power presentation is a semiring isomorphism with its transported addition, and the ordinary comparison residual is D_s=c^s-a^s-b^s | Proved in FIRST_COMPARISON.md; focused audit. This elementary candidate is not identified with full IUT. |
| PC2 | Protecting the first two powered coordinates forces c_s=a^s+b^s; its stated logarithmic correction cost on (1,t,t+1) is asymptotic to (s-1)log(t+1) | Proved and audited. Rules out a free gain for this candidate and norm, not every possible comparison. |
| PC3 | Repaired radical behavior has the exact even gcd(c,c_s)=gcd(c,2) and odd gcd(c,c_s/c)=gcd(c,s) identities | Proved and audited; no useful general bound on the new radical is derived. |
| GC1 | Under the stated closed-range hypothesis on D, joint size control by (D,P) is equivalent to P being bounded below on ker D | Complete proof in global_coercivity. P is linear in this model; prime support is not declared linear. |
| GC2 | Control of one linear height functional on ker D is equivalent to bounded factorization through P(ker D) | Complete proof and focused audit; no arithmetic realization of the required functional/cost estimate established. |
| GC3 | Primitive integer raw candidates with radical 6 have unbounded log height and nonzero relative additive defect tending to zero | Complete infinite-family proof and audit. They fail exact addition and are not ABC triples. |
| GC4 | For integer defect d and c<=B, eta=abs(d)/c<1/B implies d=0 | Exact positive stopping law. B is supplied, not bounded by a conductor theorem. |
| AB1 | The explicit weak adelic contract over Q(i) admits norm-balanced locally exact families with fixed support and unbounded ambient height outside the diagonal source | Complete construction and focused review. Three coordinate product formulas only; full-field product-formula reconstruction is not refuted. |
| AB2 | The two-place marking class [(2^m,1)] in (K_v2 plus K_v3)/Delta(K) is nonzero | Actual three-view additive protected obstruction; proof in GLOBAL_MARKING_OBSTRUCTION.md. No height saving on genuine diagonal inputs. |
| ABC | All-epsilon uniform height bound for intended primitive positive integer additive triples | Open. No global exponent improved in RR7. |

These are written proofs with the stated review provenance. No new Lean
verification or finite sampling establishes the universal results. Earlier
formal receipts are not reassigned to these new diagrams. Sources and
reviewed revisions are recorded separately.
