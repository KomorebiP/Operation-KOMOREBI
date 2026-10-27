# Independent audit of radical-supported precision

**Normalized claim.** For supported modulus M=product p^k_p, an integer defect d=a+b-c that is zero modulo M is either zero or has |d|>=M. For every N>=4 there are positive pairwise-coprime triples (4^u,9^v,25^w), with u,v,w>=N, radical exactly 30, c>a+b, and d=0 modulo 30^N; their c values are unbounded at each fixed N. On unrestricted corrections in M Z^3, the minimum sup norm needed to kill d=Mt is M ceil(|t|/3).

**Primary verdict: proved as written**, for the corrected current revision identified below. This verdict covers the stated stopping certificate, explicit finite-precision obstruction, and unrestricted repair formula. It supplies no ABC estimate, bound for exact S-unit solutions, compatible nonvanishing inverse-limit tower, or obstruction to source-dependent precision selected using an independently known height.

## Revision and provenance

- Current raw proof: `routes/radical_precision/PROOF_NOTE.md`.
- Current SHA-256: `2dbf5a7caab60a7bc22d12a15778d140c745ae4a696e4f10328a5edd4a5ba0f2`.
- Initially reviewed SHA-256: `e7b9472eff5565403593b12567e0725a3065b8eaba5621aca0a73add2fa444fc`; its preserved bytes are `routes/radical_precision/snapshots/PROOF_NOTE.pre-positivity-fix.md`.
- Review type: independent isolated reviewer `/root/rr8_precision_review`, tasked with the raw proof and no desired verdict. The critical arithmetic was reconstructed directly. Authorial evidence/status assertions were not used as evidence.
- The applicable `mathbox:proof-audit` skill and its general-logic checklist were read. No applicable ancestor `AGENTS.md` or `.mathbox` ledger was found in the inspected project paths.

The initial revision had a real local hypothesis error. The consequence “If c>=max(a,b)>0, then |d|<=c” was false for the theorem's stated arbitrary integer triples. For S={2,3,5}, k_p=1, M=30, the triple (-30,1,1) satisfies that displayed condition, c<M, and d=-30=0 modulo M, but d is nonzero and |d|>c. The author changed this one condition to “If 0<a,b<=c”. A direct byte diff verifies that this is the only change to the proof note. The corrected consequence follows from 0<a+b<=2c, hence -c<d<=c. The original unrestricted subsidiary assertion does not receive a pass.

## Dependency graph

1. Integer divisibility d in M Z -> either d=0 or |d|>=M -> weighted stopping certificate and its height corollaries.
2. Elementary valuation formula for (1+p^s q)^k-1 -> exact cyclic orders -> the three local exponent residues.
3. Local exponent residues plus elementary CRT compatibility -> exponents u,v,w in the stated classes -> congruence modulo each of 2^N,3^N,5^N -> congruence modulo 30^N.
4. Disjoint prime supports -> pairwise coprimality and radical 30. Increasing w in its fixed class -> c>a+b, d<0, and unbounded c.
5. Triangle inequality for k_1+k_2-k_3 and an explicit three-part distribution of |t| -> exact unrestricted repair norm -> logarithmic asymptotic along the fixed-u,v family.

All leaves in this review are directly checked elementary arithmetic. The CRT existence needed here follows from Bezout inversion for coprime moduli, and compatibility modulo the gcd for the two v conditions; no unverified source-dependent theorem or computation is used.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| General certificate and exact strict threshold | Passed | e^h eta=|d| and e^L=M; nonzero multiples of M have magnitude at least M. |
| Positivity consequence and supplied height bound | Passed after the recorded local correction | 0<a,b<=c implies -c<d<=c. If c<=B and eta<M/B, then |d|=c eta<M. |
| Unit valuation formula, including p=2 | Passed | Prime-to-p exponents preserve valuation; a p-th power raises it exactly once under the stated s restrictions. |
| Cyclic subgroups and all local targets | Passed | The computed order equals the size of the specified subgroup; 25 and -9 belong to the required subgroups. |
| CRT compatibility, minimum N, and arbitrarily large exponents | Passed | Only v has a common modulus factor, namely 2, and ell_2 is odd for N>=4. |
| Three local congruences and their exact periods | Passed | Orders and vanishing terms are checked independently below. |
| Strict sign, support, positivity, and coprimality | Passed | Choose positive representatives >=N and then enlarge w; the three prime supports are {2}, {3}, {5}. |
| Uniform/nonuniform fixed finite supported precision | Passed | Use N>=4 and at least all prescribed depths, then reduce the congruences. |
| Inverse-limit and archimedean scope | Passed | Own-prime valuations tend to infinity as N increases; the theorem makes no stronger tower or small-relative-defect assertion. |
| Exact unrestricted repair cost, including t=0 and either sign | Passed | Triangle bound is sharp by distributing |t| across three entries with the required signs. |
| Logarithmic repair asymptotic | Passed | With M,a,b fixed, cost=(c-a-b)/3+O(M)=c/3+O(1). |
| Ordinary every-epsilon ABC bound | Out of scope / not established | The construction consists entirely of nonadditive raw triples. |

## Independent reconstruction of the arithmetic

For g=1+p^s q with p not dividing q, a prime-to-p exponent k gives (g^k-1)/(g-1)=1+g+...+g^(k-1)=k modulo p. For a p-th power, the first binomial term has valuation s+1. Every later term has strictly larger valuation for odd p with s>=1; when p=2 the final term has valuation 2s>s+1 exactly under s>=2. Iteration gives v_p(g^k-1)=s+v_p(k). Modulo p^N this makes the order p^(N-s), and the powers exhaust the p^(N-s) elements congruent to 1 modulo p^s.

Consequently ord_(2^N)(9)=2^(N-3), ord_(3^N)(4)=3^(N-1), and ord_(5^N)(16)=5^(N-1). The targets in (6) belong to those groups: 25=1 modulo 8 and modulo 3, while -9=1 modulo 5. Thus ell_2, ell_3, r_5 exist. Reducing the first target equality modulo 16 gives 9^ell_2=9, so ell_2 is odd. This explicitly checks the minimum N=4, where its modulus is 2.

For u, the moduli 3^(N-1) and 2*5^(N-1) have gcd 1. For v, the moduli 2^(N-3) and 2*5^(N-1) have gcd 2 and the residues agree modulo 2. Equivalently, v=1+2*5^(N-1)t reduces the remaining condition to

    5^(N-1)t=(ell_2-1)/2 modulo 2^(N-4),

which has a solution because the coefficient is odd; at N=4 the remaining modulus is 1. Positive shifts in the resulting classes ensure u,v>=N. The w class is nonempty and unbounded.

The additional orders actually needed for w are ord_(2^N)(25)=2^(N-3), from v_2(24)=3, and ord_(3^N)(25)=3^(N-1), from v_3(24)=1. Hence w=1 modulo 2^(N-3)*3^(N-1) gives 25^w=25 at both primes. With u,v>=N, 4^u vanishes modulo 2^N and 9^v vanishes modulo 3^N. These establish the first two local equations.

At 5, 25^w vanishes because w>=N, and u=2r_5 modulo 2*5^(N-1) gives 4^u=16^r_5=-9. Moreover ord_(5^N)(9)=2*5^(N-1): the order is even modulo 5, while its square 81 has order 5^(N-1) by v_5(80)=1. Thus v=1 modulo 2*5^(N-1) gives 9^v=9. The defect vanishes modulo 5^N. Pairwise-coprime prime-power moduli then give exactly the asserted modulus 30^N.

After fixing u,v, increasing w in its class leaves all three local equations valid and eventually gives c>a+b. Hence d<0 explicitly, independently of any exponential Diophantine non-equality theorem. The coordinate supports remain disjoint and unchanged. This proves radical 30, pairwise coprimality, and arbitrarily large heights for every fixed N. It also suffices for the claimed impossibility of a finite universal F(R,N), since its value at R=30 would already have to bound this unbounded set.

Finally, h=M(k_1,k_2,k_3) kills d=Mt precisely when k_1+k_2-k_3=-t. If max|k_i|<=q, then |t|<=3q, so q>=ceil(|t|/3). Conversely split |t| as three nonnegative integers each at most this ceiling, take k_1,k_2 with sign -sign(t), and take k_3 with the opposite sign. This attains the lower bound. For t=0 take h=0. With a,b,M fixed and c increasing, the ceiling changes the cost from (c-a-b)/3 by a bounded amount, proving the stated logarithmic ratio tends to 1. The minimization is only over unrestricted residue-preserving integer corrections; positivity, support, and primitivity are correctly excluded from its guarantees.

## Source and computation checks; remaining gap

The current proof and preserved original were read directly, SHA-256 hashes were recomputed, and their exact text diff was inspected. Filesystem checks found no project ledger requiring reconciliation. No numerical sampling, finite search, formal verification, or external theorem lookup was performed or needed; none contributes evidence to this verdict.

There is no remaining gap in the corrected scoped claims. The strongest safe conclusion is the stated finite-precision obstruction at fixed radical 30 together with its exact ordinary correction cost and the weighted stopping certificate. The missing conductor-to-height estimate for exact additive sources remains wholly open in this note. No further computation is indicated for these elementary claims; any later extension must be audited at its own stated quantifiers and domain.
