# Versioned claim ledger: ABC-20261025-RR2

Parent checkpoint: `ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip`,
SHA-256 `f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.
The archive and its extracted sources are preserved. No Git revision was
available. This checkpoint is identified by its archive and internal file hashes.

The target is the every-epsilon primitive integer ABC conjecture. It is open
in this work. Status words below describe only the displayed claims.

| ID | Exact result and scope | Evidence |
| --- | --- | --- |
| RR2-A1 | For delta>0, N(X,T)<=C_delta T X^delta, counting the complete radical | [Proof](routes/quadratic/PROOF.md), [review](reviews/quadratic_counterexample_review.md) |
| RR2-A2 | Fixed S and Q<=H^A, A>epsilon, quality exceptions in squarefree h in (H/2,H] have exponent (A-epsilon)/(1+epsilon)+eta; explicit example epsilon=1/10,A=1/2 gives H^(3/8) times a fixed logarithmic factor | [Proof](routes/quadratic/PROOF.md), same review |
| RR2-A3 | If prime h is coprime to Q and 1+hQ=u^k, then h<=((Q+1)^k-1)/Q | [Proof](routes/quadratic/PROOF.md), same review |
| RR2-B1 | For coprime A>B>=1, v_p(A^n+B^n)=v_p(A^d-B^d)+v_p(n) at odd output primes, d=ord_p(A/B) | [Proof](routes/global/PROOF_NOTE.md), [review](routes/global/audit/AUDIT.md) and its pinned source snapshot |
| RR2-B2 | U(A^n+B^n)=B_2 W_n G_n with G_n dividing n, B_2<=A; uniform restricted ABC under the stated small-exceptional-prime condition | Same proof, [current supplement](routes/global/audit/AUDIT_SECTION5.md) confirms unchanged preceding proof |
| RR2-B3 | Odd prime exponent ell has U(c)=U(A+B) ell^[ell divides A+B] W_prim with primitive primes >=2ell+1; binary n>=2 has U(c)=W_prim | Same proof and supplement |
| RR2-C1 | The fixed Q=243,m=10 quadratic class has infinitely many integer coprime multipliers with output radical 10 | [Proof](routes/counterexample/PROOF.md), [review](reviews/quadratic_counterexample_review.md); primality and squarefreeness not claimed |
| RR2-C2 | Every fixed prime multiplier p>=5 has infinitely many varying Q giving ordinary hits in an irreducible square-kernel branch | Same proof and review; fixed-epsilon violations not established |
| RR2-D1 | For a=1, the exact derivative Wronskian image is lcm(G(b),G(b+1)) Z; 1+48=49 has shortest height 6 degenerate and minimum nondegenerate height 8 | [Proof](routes/derivative/DERIVATIVE_ROUTE.md), [review](reviews/derivative_review.md) |
| RR2-D2 | General exact image LZ with L=gcd(cAB,bAC,aBC)/gcd(A,B,C), A=G(a), B=G(b), C=G(c); J=L/(abc/R) is integral and cJ<=RH log(c)/log(2) | [Proof](routes/derivative/GENERAL_IMAGE.md), [review](reviews/general_image_review.md) |
| RR2-E1 | Ordered primitive ABC fixed-excess exceptions at c<=X number O_(epsilon,eta)(X^(1/(1+epsilon)+eta)) | [Proof](routes/counting/PROOF.md), [review](reviews/counting_review.md) |
| RR2-ERR1 | Fixed-offset normalization requires gcd(h,Q)=1 explicitly | [Correction and counterexample](ERRATA.md), [review](reviews/quadratic_counterexample_review.md) |

Each proof is elementary except the source comparison describing Pasten's
existing results. The new elementary claims do not assume the truth of those
conjectures. The separate reviews reconstructed the mathematical implications.
Agreement between agents is not a formal proof certificate or external peer review.

Finite evidence is recorded by route in `computation_records/*.manifest.json`.
All five run statuses are completed. These checks support implementation and
the stated finite assertions. They do not prove the universal statements.

Unresolved: full ABC, eventual emptiness of its exceptional set, unrestricted
large exceptional contact estimates, and sufficiently small integral lifts.
No theorem above is recorded as solving any of these open obligations.

Correction to an inherited reporting label: the old verifier's instance counts
sum interval limits H in some fields. Those are interval extents, not actual
counts of tested prime multipliers. The base files remain unchanged.
