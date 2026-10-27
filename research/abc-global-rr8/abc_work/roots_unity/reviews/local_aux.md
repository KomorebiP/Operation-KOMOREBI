# Independent audit of the local and auxiliary routes

Normalized claim: the local torsion split preserves first-contact valuation; the specified roots average selects coefficient classes without reducing an invariant high-contact evaluation; the Hensel examples have arbitrary exact depth with their stated input-height cost. Separately, the integral evaluation lattice satisfies (A1), its nonzero evaluations obey (A2), and the degree-one minimum is (A3). These are operation-specific statements, not a universal impossibility theorem for roots-of-unity or auxiliary-polynomial methods, and not a proof or disproof of ABC.

**Primary verdict: proved as written, for the corrected source revisions pinned below.** The original auxiliary source contained one false ancillary sentence. That sentence is expressly failed below; the verdict does not apply to the original document without correction. No global height estimate is supplied by this audit.

## Claim cards and exact scope

1. For an odd prime $p$, $p\nmid AB$, $t=A/B\in\mathbb Z_p^\times$, and $d=\operatorname{ord}_{\mathbb F_p^\times}(t)$, the unique torsion lift $z\equiv t\pmod p$ of order $d$ satisfies
   $$v_p(t^d-1)=v_p(t-z)=v_p(t/z-1).$$
   Modulo $p^k$, all valuations are truncated at $k$. The lift has exact order $d$ because its reduction does. The conventional extension $v_p(0)=+\infty$ handles the allowed integer-ratio cases $t=\pm1$; the finite truncated formulation is unambiguous even there.
2. For positive integer $n$ and $p\mid A^n+B^n$, $d$ is even, $2n/d$ is odd, and $v_p(A^n+B^n)=v_p(A^d-B^d)+v_p(n)$. In a coefficient ring containing the lifted root and $d^{-1}$, the displayed averaging operator selects exactly the exponents congruent to $r\bmod d$. This is a polynomial identity, not an inequality on surviving evaluations.
3. For $n=2^s$, $s\ge0$, $p\equiv1\pmod{2n}$ odd, and the chosen primitive seed, every $e\ge1$ gives positive $A_e$, $B=1$, with exact output/birth valuation $e$, order $2n$, and $p^e\le A_e<3p^e$. The certified single-prime contribution satisfies $p^{e-1}<A_e\le(A_e^n+1)^{1/n}$. “Exceptional” applies for $e\ge2$; the depth-one examples are ordinary with contribution $1$.
4. For positive coprime $A,B$, $D\ge1$, $M\ge1$, use exactly the integral homogeneous evaluation $E:\mathbb Z^{D+1}\to\mathbb Z$ in the source. Then $E(L_M)=M\mathbb Z$, $L_M/L_0\cong M\mathbb Z$, and $u\in L_M\setminus L_0$ implies $H\ge M/S_D(A,B)$. For $D=1,A=2,B=1$, the minimum height is $\lceil M/3\rceil$.

The local identities need only $p\nmid AB$, rather than coprimality; their ABC interpretation and the auxiliary claim use the stated positive coprime bases. The odd-prime restriction matters: the excluded case $p=2,A=3,B=1,n=1$ would give unequal valuations $2\ne1$. The projection claim is read in the lifted $p$-adic/finite-ring setting; abstract order in an arbitrary ring would not alone prove that $1-z^\ell$ is a unit.

## Dependency graph

- $d\mid p-1$ and residue order $d$ → unit derivative $d z^{d-1}$ → unique lifts → unit quotient in $t^d-z^d$ → exact contact identity.
- $t^n=-1$ → even $d$ and $n=(d/2)j$, $j$ odd → $A^{d/2}-B^{d/2}$ a unit at $p$ → elementary exponent lifting → plus-valuation formula.
- Reduction of $z$ of order $d$ → $1-z^\ell$ a unit for $d\nmid\ell$ → geometric sum → coefficient selection → the two displayed mechanism checks.
- Simple root of $X^n+1$ → unique next digit $j_e$ → distinct chosen digit $k_e$ → exact depth $e$ and order/birth identities; representative interval → height inequality.
- Coprimality → $\gcd(A^D,B^D)=1$ → surjective $E$ → (A1); nonzero multiple of $M$ plus triangle inequality → (A2); lower bound plus explicit witness → (A3).

All leaves are elementary internal arguments or conventions. The 1093 divisibility is a checked illustration, not a premise of the lattice theorem. No unchecked external result or circular dependency is needed.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Torsion lift and truncated identities | Passed | Unit derivative and quotient; complete small finite-ring checks include $d=1$. |
| Plus-valuation identity | Passed | Half-order condition and elementary lifting; checks include $n=1$ and $p\mid n$. |
| Projection normalization and coefficient identity | Passed | $p\nmid d$ and exact geometric sums; actual monomial averages checked. |
| Exact-depth construction and size | Passed | Distinct next digit; $0\le x_e<p^e$. |
| CRT and height interpretation | Passed | Prescribed depths are lower bounds; representative lies in $[M,2M)$. |
| Small-$n$ and ABC interpretation | Passed | $W_1=p^{e-1}$, $c=p^e$; no bound for $\operatorname{rad}(A)$ supplied. |
| Auxiliary image, quotient, rank, height | Passed | Surjectivity, independent relation vectors, triangle inequality. |
| Degree-one minimum, including $M=1$ | Passed | $M\le3H$ and witness $(M-2H,H)$. |
| Original “need not form an integral basis” sentence | **Failed** | The vectors always form an integral basis under coprimality. |
| Corrected sentence and downstream effect | Passed | It states only properties used; no subsequent implication relied on the false aside. |
| Finite verifier contracts | Passed in stated ranges | Reruns redirected; independent bounded checks below. |
| Uniform global height estimate, universal obstruction, ABC | Not addressed | No such conclusion is established or claimed by these proofs. |

## Critical derivations and the failed original aside

Since $t\equiv z\bmod p$, the quotient in
$$t^d-z^d=(t-z)\sum_{i=0}^{d-1}t^{d-1-i}z^i$$
is congruent to the unit $d z^{d-1}$. Multiplication by it, or by $z$, preserves valuation, also after truncation. For the exponent-lifting step, an odd exponent multiplier prime to $p$ gives a unit quotient in $X^j+Y^j$. Multiplying the exponent by $p$ raises $v_p(X+Y)$ exactly once by binomial expansion. Iteration gives the precise $v_p(j)=v_p(n)$ term.

For the construction, the Taylor coefficient of $f(x_e+k p^e)/p^e$ modulo $p$ is $f(x_e)/p^e+k f'(x_e)$. Its unique zero digit is $j_e$. The chosen $k_e\in\{1,2\}$ differs from $j_e$ modulo every odd $p$, giving exact valuation $e$, not just a lower bound. Also $A_e^n-1\equiv-2\bmod p$ is a unit, proving the birth valuation. These examples do not demonstrate a height saving: their certified repeated mass is less than $\log A_e\le(\log c_e)/n$. They do not establish that every representative must be this large.

The CRT passage is valid for prescribed compatible root contacts: it gives valuation at least $e_i$ at each selected prime and a representative $M\le A<2M$. It does not assert exact valuation at every prime. Small canonical representatives and their simultaneous arithmetic constraints remain uncontrolled. At $n=1,A=p^e-1$, the exact $W_1=p^{e-1}$ has logarithmic ratio $(e-1)/e$ to $c=p^e$. This refutes an output-only uniform sublinear bound down to $n=1$, without supplying an ABC counterexample.

For (A1), choose an integral $w$ with $E(w)=1$. Multiples of $Mw$ realize all of $M\mathbb Z$; the reverse inclusion is the definition of $L_M$. The restricted map has kernel exactly $L_0$. Its rank is $D$, while the first $D$ columns of the displayed relation matrix have determinant $(-A)^D\ne0$, proving independence. For (A2), a nonzero integer evaluation divisible by $M$ has magnitude at least $M$, while the triangle inequality gives magnitude at most $H S_D$. For (A3), $H=\lceil M/3\rceil$ and $(u_0,u_1)=(M-2H,H)$ attain evaluation $M$ with both coordinates bounded by $H$.

The original auxiliary source, lines 38–39, said: “They need not form an integral basis of $L_0$.” This is false under the stated coprimality. Set $q_j=-A e_j+B e_{j+1}$. For $u\in L_0$, reduce the evaluation equation modulo $B$: $\gcd(A,B)=1$ implies $B\mid u_D$. Subtract $(u_D/B)q_{D-1}$, eliminating the last coordinate. Divide the remaining degree-$D$ evaluation equation by $B$ and induct. The degree-one case is immediate, including $B=1$. Thus every $u$ is an integral combination of the independent $q_j$: they always form an integral basis. This refutes the original aside, rather than repairing a missing main proof step. The parent deleted that claim and substituted only the properties actually used; all of (A1)–(A3) are unchanged.

At $M=1093^2=1,194,649$, (A3) gives $398,217$, whereas $(-2,1)$ has height $2$ and evaluation zero. No nonzero lattice vector has height $1$: its evaluation magnitude is at most $3<M$, and $u_0+2u_1=0$ has no such nonzero vector. Thus the shortest nonzero coefficient vectors really do vanish in this example. Direct modular checks confirm order $364$ and $v_{1093}(2^{182}+1)=2$; neither is needed for the lattice theorem.

## Computation contract and reproducibility

Run from the workspace root:

    python3 abc_work/roots_unity/reviews/local_aux_checks/check_local_aux.py

This checker executes the two unmodified author verifier sources with Path.write_text intercepted. Their only permitted writes are redirected to this review's local_aux_checks/padic_rerun.json and auxiliary_rerun.json. Author proofs, verifiers, and result artifacts had unchanged hashes during this run. Later parent reruns may alter result runtime fields; the fixed source pins below and captured review outputs are the audited objects.

Both stated contracts passed: 48 local examples at the four stated pairs and depths 1–12; 100 degree-one minima; 186 relation-vector/rank cases. The auxiliary enumeration covers every integer pair of height strictly below $H$ and supplies a witness at $H$. The local verifier computes the actual averaging formula for its two-term polynomial; it does not merely return the expected coefficient. Its legacy result does not hash the local proof, but this audit does. The auxiliary captured result binds its corrected proof and verifier.

Additional exact checks recorded in local_aux_checks/summary.json passed:

- 15,788 torsion identities, every unit modulo $p^k$ for $p\in\{3,5,7,11,13,17,19\}$, $1\le k\le3$, with lifts found by exhaustive digit search;
- 26,960 actual monomial projections, every root seed, $k=1,2$, all $0\le r<d$, $0\le m\le2d+1$;
- 10,394 qualifying plus-valuation cases at those primes, $2\le A\le30$, $1\le B<A$, $p\nmid AB$, $1\le n\le30$;
- direct next-digit searches for the smallest omitted boundary $n=1,p=3$ and for $n=2,p=5$, depths 1–5;
- 48 exact small-$n$ cases, all minima for $1\le M\le200$, and 378 maximal-minor checks for coprime $1\le A,B\le10$, $1\le D\le6$, including $A=B=1$ and reversed base order;
- order and exact valuation for the 1093 illustration.

The checks establish only these finite assertions. The uniform elementary statements rely on the derivations, not finite evidence.

## Remaining gap and strongest safe conclusion

No implication gap remains in the corrected local or lattice claims. The open arithmetic obligation is a uniform comparison between repeated first-contact mass, rational input height and radical, and output height, with moving primes and orders. An auxiliary construction must additionally prove that a controlled integral evaluation lies outside $L_0$. The necessary lower bound $H\ge M/S_D$ neither constructs an optimal auxiliary value nor prohibits more structured constructions.

The cheapest next check of a proposed continuation is to define its actual admissible auxiliary space and constraints, compute its intersection with the exact evaluation kernel, and state its nonvanishing certificate before claiming a height contradiction. This audit authorizes no change to the ABC target or open-route status.

## Provenance and revisions

Independent delegated audit by /root/roots_review_local_aux, reconstructed from the raw files; not external peer review or a formal certificate. The reviewer initially received the original sources without a suggested verdict and reported the false basis aside before the parent's local deletion. This reviewer modified no author source. No .mathbox ledger was present in the inspected tree; no AGENTS.md was found under /workspace.

| Artifact | SHA-256 audited |
|---|---|
| routes/padic/PROOF.md | 2b4e0fab980fa49f795cc5953fb2ac748909b8f5a1fc860a6802667582a1cff8 |
| routes/padic/verify.py | db973c95706fb29140357b33c51b9d06ce81b0828bfc15d32547511b509ec0e7 |
| Corrected routes/auxiliary/PROOF.md | 995d04be7d8ba1a0bef46ed3ef4a42bb3696f1bd1612840116ce5d208832f441 |
| routes/auxiliary/verify.py | 56d991cad52addc676529c57becb051e73c7b58417eea16228a6ec7c1834d39c |
| Original auxiliary proof, reviews/snapshots/auxiliary_before_review.md | 659af38f61b281656207c55a86c529b4176d69f5f960cf7e4266c5ef563340b4 |
| abc_work/LATEST.md | c764c76cb7823213358d51165b7f865c223cfbe2f5c116e079f246ce2749eff2 |
| abc_work/routes/global/PROOF_NOTE.md | f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc |
| Independent reviews/local_aux_checks/check_local_aux.py | 8a9ea792f015beacc876de0683454221eb8e0fc801304ce7367e1999a4fc4a8c |
| Independent reviews/local_aux_checks/summary.json | 59f2827448eff90ae98b890a8082f0eea34e01f3a069ad0f30d60d9faedbba09 |

The captured summary separately records the author-result hashes at the exact audit run.

