# Independent review of the fixed-support route

**Normalized claim.** For every finite set S of rational primes, the ordered primitive positive additive triples supported on S correspond bijectively to the positive S-unit solutions of x+y=1 and are finite with the displayed ESS count. Their bounded factorial residue chain has exactly the intended bounded source as its inverse limit. For S={2,3}, the four displayed triples up to swapping the first two coordinates exhaust the source, B(S)=9, and the residue system stabilizes at modulus 24. Finally the uniform estimate (U), with all finite S quantified, is equivalent to the usual positive primitive formulation of ABC.

**Primary verdict: proved as written, within the disclosed scope and with ESS Theorem 1.1 imported as an external theorem. Review result: pass.** No necessary correction to the frozen proof note was found. This verdict does not establish (U), ABC, any new quantitative height bound, or the proof of the external theorem itself.

## Exact reviewed inputs and provenance

- PROOF_NOTE.md: SHA-256 `b41e4ea612676dc0e85e22129f403872b4614753f6dbd8c49d3f875b8d0d979e`, 8607 bytes.
- SOURCE_RECORD.md: SHA-256 `227d2da513bd6ddddd772c1c106ec09770f46d1fd78aea8429205b8bd7a3f61e`, 2581 bytes.
- Review date: 2026-10-25 UTC.
- Reviewer: isolated delegated task `/root/rr8_fixed_support/isolated_fixed_support_review`, using the proof-audit and literature-check skills. Raw proof and source records were read; the critical implications were independently reconstructed rather than accepted from their outcome paragraphs. No sibling status, proofreading verdict, or separate review was consulted. The parent subsequently disclosed an exposition-only change to the final three-prime paragraph; the entire final proof note above was reread and its hash was checked before writing this review.
- This is an independent task-level review, not a claim of independence between model families. Mathematical agreement alone is not evidence of correctness.

The accompanying REVIEW_INPUTS.json freezes the same exact inputs and lists the external locators. The base RR7 archive identity, the full RR7 implementation and categorical conventions, historical novelty, and any ledger outside this route were not audited. No applicable AGENTS.md was present on the inspected directory ancestry. No .mathbox ledger appeared in the inspected RR8 tree.

## Claim card and dependency graph

The coefficient domain is Q for the S-units, embedded in an algebraically closed characteristic-zero field for ESS. All integer coordinates are strictly positive; triples and S-unit pairs are ordered. The source condition is support contained in S, not equal to S. The inverse system is in sets and has reduction arrows F_(N+1) -> F_N; a coherent section means an element of its inverse limit. Budgets satisfy B>=2 and factorial indices are integers N>=3. The ABC comparison uses every epsilon>0 and a constant depending on epsilon alone.

The dependencies are:

1. Unique prime factorization and primitive rational normalization -> the bijection and rank 2|S|.
2. The bijection, rank computation, nondegeneracy, and imported ESS Theorem 1.1 -> the displayed count -> finiteness -> existence of B(S).
3. Bounded coordinate uniqueness, divisibility of the additive defect by factorials, and eventual detection of every common prime -> the inverse-limit identification. The finite-level strengthening uses N!>2B and detection of every prime <=B.
4. Pairwise coprimality and allocation of only two possible primes -> a unit coordinate -> two prime-power difference equations -> the complete S={2,3} classification -> budget 9, seven ordered triples, the restricted ABC constant, and stabilization at 24.
5. The definition of B(S), radical monotonicity for contained supports, and using the actual support of a triple -> ABC iff (U). No count-to-height implication enters this equivalence.

All leaves other than ESS are elementary internal arguments or definitions/conventions. There is no circular dependency on ABC in the finiteness, reconstruction, or two-prime classification.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Primitive triple -> S-unit pair | passed | Dividing by c creates no prime outside S; positivity and sum one persist. |
| S-unit pair -> primitive supported triple, uniquely | passed | Clearing denominators and dividing the common gcd gives gcd(a,b)=1. At a prime outside S all three integral valuations agree; primitivity makes them zero. Primitive integral representatives on the same positive rational ray are unique. |
| Rank and ESS applicability | passed | The two copies of the free group on S have rank 2|S|. Coefficients are nonzero. Each singleton subsum is nonzero; the full sum is 1. |
| Count and fixed-S finiteness | passed | Substituting n=2 and r=2|S| yields exp(12^6(2|S|+1)). The bound is for ordered pairs and the bijection preserves order. |
| Transition maps of the bounded chain | passed | The same bounded lifts witness support, additive congruence, and the gcd condition after reducing the factorial modulus. |
| Coherent sections -> intended bounded source | passed | At sufficiently high levels the bounded coordinate lifts are unique. Coherence makes them constant. A fixed integer defect divisible by all large factorials is zero, and any common prime is eventually detected. |
| Every intended bounded source point gives a section | passed | Exact addition and gcd(a,b)=1 imply every residue observer; positivity gives a,b<c<=B. |
| Finite level N>=B+1 | passed | For B>=2 the stated bound gives N!>2B. The defect lies between 2-B and 2B-1, so congruence forces zero. A common prime is <=B<N and divides N!. |
| Complete two-prime classification | passed | Pairwise coprimality forces an entry to be 1. The remaining two nonunit entries have singleton, disjoint prime supports; both possible differences of prime powers are solved by the displayed factorizations. |
| Seven ordered triples and restricted ABC constant | passed | (1,1,2) contributes once and the other three contribute twice. Radicals are 2 and 6, and c<=9. |
| Stabilization at N=4 | passed | With B=9, every defect has absolute value <24. Any common prime of supported lifts is 2 or 3 and is detected modulo 24. All levels N>=4 therefore identify with the same seven source triples under reduction. |
| Uniform support estimate iff ABC | passed | ABC gives log B(S)<=(1+epsilon)log R(S)+C_epsilon, including the fallback B(S)=1. Conversely take the actual support S, so R(S)=rad(abc), and use c<=B(S). |
| Empty support and empty source | passed | U_empty={1} has no sum-one pair, T_empty is empty, B(empty)=R(empty)=1; the contribution to the supremum is zero. |
| Height bound inferred from cardinality alone | passed as a limitation | The note explicitly refrains from this invalid inference. The singleton example addresses cardinality alone and is not offered as an arithmetic counterexample. |

## Independent reconstruction of the delicate steps

For inverse normalization, let d be a common positive denominator of x and y, and set a=dx, b=dy, c=d. Dividing by gcd(a,b,c) preserves a+b=c. Since gcd(a,b,c)=gcd(a,b) when c=a+b, the normalized triple is primitive. The valuation argument in the note then rules out every prime outside S. Conversely a primitive triple is the unique primitive integral representative of its pair of rational ratios. There is no lost scaling parameter or sign choice because all entries are positive.

For the inverse limit, choose a level K with K!>B. If a coherent element at level M>=K has a bounded lift z_M, its reduction at K has the same bounded lift, because each coordinate difference is smaller than K!. Thus every z_M is the same integer triple z_K. This supplies the stabilization of lifts used in Proposition 2 without assuming that the lower-level witnesses are unique. Eventual factorial divisibility proves exact addition and primitivity. Conversely exact primitive triples provide all levels, so no merely local solution is being added.

For the two-prime proof, gcd(a,b)=1 and a+b=c imply gcd(a,c)=gcd(b,c)=1. Three nonunit coordinates would require three distinct supporting primes, so with only 2 and 3 one additive summand is 1. In 2^m-3^n=1, reduction modulo 3 forces m even. The positive odd factors 2^k-1 and 2^k+1 differ by 2 and are coprime; as their product is a power of 3, the smaller factor is 1. In 3^n-2^m=1, m=1 is handled separately; otherwise n is even, and the factors 3^k-1 and 3^k+1 are powers of 2 with gcd 2. They must therefore be 2 and 4. These arguments cover all positive exponents, rather than a tested range.

At modulus 24 the bounded defect is in [-7,17]. Divisibility by 24 forces it to vanish. A supported common divisor can have only primes 2 or 3, so gcd(A,B',24)=1 forces gcd(A,B')=1. This stronger support-specific argument justifies N=4 even though the general sufficient threshold N>=B+1 would be N>=10. The note uses the stronger argument explicitly.

For (U), the empty support shows the supremum, when finite, is nonnegative. For nonempty T_S the maximum defining B(S) is attained, and applying ABC to that point bounds it using rad(abc)<=R(S). When T_S is empty, log B(S)=0 and the same nonnegative ABC constant suffices. In the reverse direction every primitive positive additive triple has a finite actual support set. This proves the precise uniform equivalence without an extra assumption of exact support for every T_S.

## Exact external-source check

The primary author-hosted 33-page preprint was opened directly at [the Leiden PDF](https://pub.math.leidenuniv.nl/~evertsejh/00-equation.pdf) on 2026-10-25. Its title and authors match the record. The rank definition, equation (1.1), nondegeneracy definition and Theorem 1.1 on PDF pages 1-2 were read in extracted text and visually checked in page screenshots. The theorem applies to finite-rank subgroups of the n-fold multiplicative group over an algebraically closed characteristic-zero field and bounds the number of nondegenerate solutions by exp((6n)^(3n)(r+1)). Its definition checks every nonempty subsum; in the present application the full sum is 1, so the note's reference to proper subsums makes no difference. The rank definition includes finitely generated groups. This verifies the required theorem extraction and application; the full proof of the paper was not reread.

The author's [institutional publications page](https://pub.math.leidenuniv.nl/~evertsejh/publications.shtml), item [55], authenticates the preprint listing. The [publisher page](https://annals.math.princeton.edu/2002/155-3/p04) independently confirms authors, title, volume 155 (2002), pages 807-836 and DOI 10.2307/3062133. The author's page itself gives a different provisional page range, so publisher metadata is the publication authority used here. The exact preprint has no visible opening-page version date. It is pinned by URL, retrieval date, page count and read theorem location, not equated with an unexamined final or arXiv PDF. No source PDF bytes were retained or hashed. The source record accurately discloses these boundaries. No novelty search was performed.

Web provenance available to the coordinator: exact preprint `turn108view0`; screenshots `turn109view1` and `turn109view2`; publisher metadata `turn109view0`; author item [55] `turn112view0`. The coordinator should open the primary source itself before using an inline source reference in its own answer.

## Checks, limits, and remaining obligation

Commands used read the two raw files, inspected instruction-file ancestry and the RR8 file inventory, and computed SHA-256 with sha256sum and Python hashlib. Both final input hashes were rechecked immediately before producing these artifacts. No numerical enumeration was used as evidence, no Lean command was run, and no formalization or compilation is claimed.

No remaining gap was found in the scoped assertions. The strongest safe conclusion is the frozen note's finite-support theorem application, bounded-source reconstruction, complete elementary {2,3} sector, and equivalence reduction. The substantive unsolved continuation is exactly (U), a uniform radical-height estimate as S varies. Further cardinality checks cannot settle that remaining estimate. The cheapest next check of this review is to recompute the two input hashes; mathematical continuation requires a new growth argument, outside this audit.


## Separate supplemental review: effective global budget and finite diagram

**Normalized supplemental claim.** Import Stewart-Yu Theorem 1, choose a positive integer K0 at least its effective absolute constant K, and form B=4^(K0 q L^3), where q and L are the least positive integers with q^3>=Q and 2^L>=Q. This bounds c for every intended primitive positive additive triple of radical at most Q. The proposed two-object contravariant Set diagram with its bounded raw integer domain and protected zero defect has exactly the intended source of radical at most T as its protected coherent extensions.

**Separate primary verdict: proved as written, importing Stewart-Yu Theorem 1. Supplemental review result: pass.** No necessary correction was found. This is an integration of an existing effective bound, with K0 left unspecified numerically; it does not establish a stronger arithmetic exponent or the ABC conjecture.

The exact additional input is EFFECTIVE_GLOBAL_BUDGET.md, SHA-256 `6a81ec0349917220fee13635a698dbeb93d632112360afbc3229b5428208e655`. This supplemental scope was delegated after the main review was written. The companion was read in full; the final hash was checked before this addendum. The main proof and source hashes remain those frozen above. No other input content or author review was used.

### Source authentication, extraction, and application

The [13-page published institutional PDF](https://uwaterloo.ca/pure-mathematics/sites/default/files/uploads/documents/s0012-7094-01-10815-6.pdf) was opened directly on 2026-10-25. Pages 1-2 were read as text and visually inspected. They identify C. L. Stewart and Kunrui Yu, *On the abc conjecture, II*, Duke Mathematical Journal 108 (2001), 169-181. Printed page 170, Theorem 1, states the existence of an effectively computable positive absolute constant with z<exp(K G^(1/3)(log G)^3) for positive x+y=z and gcd(x,y,z)=1, where page 169 defines G as the product of distinct primes dividing xyz. Taking logarithms gives exactly the imported inequality. Unlike the preceding bound (4), Theorem 1 has no z>2 hypothesis; the minimal triple (1,1,2) is included. The full proof and its linear-form estimates were not reaudited. No numerical K or source byte hash was recovered. Source extraction and the project translation are verified; numerical instantiation remains unperformed.

The exact source read is the published PDF at that URL, not an unexamined alternate version. Web provenance is `turn117view0`, with first-page and theorem-page screenshots `turn118view0` and `turn118view1`.

### Supplemental dependency graph and obligations

The external Stewart-Yu bound, the equality G=rad(abc), and monotonicity of u^(1/3)(log u)^3 for u>=2 imply the support or radical-threshold bound. The integer ceiling inequalities and log 4>1 imply c<B. The finite raw domain supplies a bound on the *integer* defect; the zero residue then supplies exact addition. This is the only arithmetic bridge needed for soundness of the diagram. Completeness uses the imported height bound. Thus the finite diagram does not derive a height bound from a residue or from finiteness alone.

| Obligation | Result | Check |
|---|---|---|
| Translation of primitivity | passed | Under a+b=c, gcd(a,b,c)=gcd(a,b); the raw domain need only impose the joint gcd until the zero defect is enforced. |
| Small radicals and empty supports | passed | Every intended triple has radical >=2. Q=max(2,R(S)) handles empty support harmlessly; such a support has no triples. T is explicitly >=2. |
| Integer budget conversion | passed | R<=Q, Q^(1/3)<=q, log Q<=L log 2<L, and K<=K0 give log c<K Q^(1/3)(log Q)^3<=K0 q L^3. The exponent A is positive, so A<A log 4=log B. |
| Effective integer choices | passed | An effectively computable positive real constant admits an effectively obtainable positive integer upper bound. After choosing K0 the least q and L and the powers defining B and M use integer arithmetic alone. The note does not claim an evaluated K0. |
| Finite raw domain | passed | Positivity and a,b<=c<=B make the domain finite. The radical and gcd restrictions are explicitly retained nonlinear conditions, not consequences of the residue map. |
| Category and variance | passed | The base arrow d->r gives the contravariant restriction F(r)->F(d), exactly the stated defect function. Identities and that single arrow define a valid Set-valued functor. |
| Defect bound and exactness | passed | For 1<=a,b<=c, 2-c<=a+b-c<=c; hence the absolute defect is <=c<=B<M=2B. A multiple of M in that interval is zero. |
| Protected coherent extensions | passed | With d fixed at 0, a coherent extension is precisely a raw point whose defect residue is 0. Its raw point determines its whole extension. The exact-addition condition then turns the joint gcd into intended primitivity. |
| Completeness of the diagram | passed | Every intended triple of radical <=T satisfies c<B by Stewart-Yu, and exact addition implies a,b<c, so it lies in F(r) and has zero defect. |
| Modulus structure | passed | A is a positive integer, B=4^A=2^(2A), and M=2B=2^(2A+1), so the asserted power-of-two property holds. |
| Factorial-chain corollary | passed | The supplied budget is >=2, so Proposition 2 applies; its stabilization threshold is explicit relative to the specified K0. |
| Asymptotic comparison and limits | passed | The logarithm of this budget grows on the order of Q^(1/3)(log Q)^3 for fixed K0, far above the ABC logarithmic target. No new exponent follows. |

The elementary checks were symbolic and direct. No enumeration, floating-point approximation, Lean run, or other load-bearing computation was performed. A numerical executable budget is not supplied without an instantiated K0; the companion expressly keeps that boundary. The strongest safe result is the stated formula and finite source realization relative to the external effective constant, together with the existence of an effectively computable integer choice. There is no remaining mathematical gap in this supplemental scope. Recovering a numerical K0 would be the next task only if a fully instantiated numerical budget is required.
