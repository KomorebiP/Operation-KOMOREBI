# Independent audit: character projectors and cyclotomic resolvents

**Normalized claim.** For fixed coprime integers \(A>B\ge1\), odd primes \(p\nmid AB\), integer contact depths, and the conductor/root conventions in the two notes, the displayed projectors, order-lifting periods, compatible joint contact classes, complete-period means, Fourier resolvent, primitive valuation preservation, Hensel constructions, and fixed-filter resultant bounds are exact. The concrete proposed per-depth saving and independent-prime density multiplication are false. These identities do not supply a uniform ABC estimate.

**Primary verdict: proved as written**, for those exact local identities and the explicitly tested negative implications. No mathematical counterexample or missing load-bearing implication was found. This verdict does not certify unrestricted ABC, a universal impossibility theorem for roots-of-unity methods, or the whole upstream RR2 theorem.

## 1. Revision and provenance

This is an independent review by /root/roots_review_char_cyclo, commissioned from raw proof files without a requested outcome. No source or route-owned finite result was edited. The author froze the final cyclotomic proof and verifier before the final pass.

| Artifact | SHA-256 reviewed |
|---|---|
| routes/characters/PROOF_NOTE.md | 4d12fbbcf0b15871a550e431bdd54e7ced0073fddb0882f8fd31187e45dc3ba6 |
| routes/characters/verify.py | 590833a03ca256c49885ef419a8e7e40620686dc52fbf9aec411ccfd7d78138d |
| routes/cyclotomic/PROOF_NOTE.md, final | 45b432db3661862d8e535bedf4bc9e4220f34b3fccd132d721fcb8096bd67564 |
| routes/cyclotomic/verify.py, final | 34c38daaeeb7b084f2e776d2f9c130de4b752fad88e548baa114c58678789893 |
| abc_work/LATEST.md | c764c76cb7823213358d51165b7f865c223cfbe2f5c116e079f246ce2749eff2 |
| abc_work/routes/global/PROOF_NOTE.md | f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc |

The preliminary cyclotomic proof hash was 39458bf0ea3288e52dc3f6c2743e2c8f42875791294858bbf4010dcbe470dfc3. A separate child reviewer reconstructed its unramified-branch and resultant arguments and found them correct, while emphasizing that the finite resultant-prime set requires fixed conductor **and** fixed coefficients. The final source adds that scope explicitly, the coefficient-height bound, and the moving-conductor countercheck. I directly audited those final additions. The child review supplements the preliminary portion and is not represented as an audit of unread additions.

No applicable AGENTS.md or .mathbox ledger was found under the working project. Instructions used: mathbox:proof-audit, including its logic, characters, computation, and external-input obligations. RR2 was read to resolve notation and inherited definitions; its full restricted ABC theorem is outside this focused audit.

## 2. Claim card and dependency graph

The domains are integer \(t\) for additive divisibility projectors; positive integer exponents and \(N\) for output counts; \(e\ge1,L\ge2\); and nonempty finite prescribed prime families for the joint law. The convention \(v_p(0)=+\infty\) makes the shell formula valid at \(t=0\), while the powerful-part formula explicitly excludes \(t=0\). The prime \(2\), primes dividing \(AB\), and general multipliers \(h\) are not silently included in the odd-prime half-order formulas.

For cyclotomic expressions, \(n\ge1\), \(0\le k<n\), \(\zeta\) has primitive order \(n\), and \(\eta^n=-1\). Rational expressions are defined because \(A>B\ge1\), so \(A-\eta\zeta^jB\ne0\). At an unramified prime the valuation is normalized by \(v_{\mathfrak p}(p)=1\). A fixed filter uses \(P\in\mathbb Z[X,Y]\), homogeneous of total degree \(n-1\), with \(P(T,1)\) coprime to \(\Phi_{2n}\). Both \(n\) and coefficients must be fixed for the finite-prime-set conclusion.

The dependency graph is:

1. Finite geometric sums → additive projectors → primitive-conductor shells → truncated valuation expansion.
2. Odd-prime lifting and \(d\mid p-1\) → order \(d_e\); the unique involution modulo \(p^e\) → half-order contacts → exact counts, synchronization, and complete-period means → finite weighted birth identity.
3. Geometric expansion and Fourier orthogonality → exact resolvent → unit numerator and distinct residue roots → one deep branch and full pole depth.
4. Cyclicity of \(\mathbb F_p^\times\) and explicit simple-root digit lifting → arbitrary exact depth with order \(2n\) → primitive valuation lies in \(\Phi_{2n}(A,1)\).
5. Integral Sylvester resultant Bézout identity and \(p\)-unit \(B\) → minimum-valuation bound → canceled-prime packet divides resultant. Unit-circle roots → coefficient-height bound.

Elementary leaves are finite sums, odd-prime binomial lifting, finite-field multiplicative cyclicity, the displayed Hensel digit calculation, determinant/adjugate identities for resultants, and Eisenstein's criterion applied to the exact substituted polynomials. There is no circular dependency, numerical estimate, distribution theorem, or priority claim. Finite computations are not used to establish universal claims.

## 3. Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Additive shell sign and normalization | passed | Nonprimitive frequencies give the complete sum at \(p^{e-1}\), hence \(p^eP_{p^e}-p^{e-1}P_{p^{e-1}}\). |
| Powerful-part truncation | passed | It counts exactly \(e\in[2,L]\) with \(e\le v_p(t)\). |
| Order-lifting formula | passed | \(v_p(A^{dk}-B^{dk})=s+v_p(k)\); least admissible \(k=p^{\max(0,e-s)}\). |
| Half-order projector and conjugation | passed | Even-order \(x\) satisfies \(x^{d_e/2}=-1\); the full-character summand equals \(\chi(-x^n)\). |
| Exact count and 1093 counterexample | passed | Counting \(d_e/2+j d_e\) gives the floor; two contacts exceed \(1095/1093\). |
| Joint half-order contacts | passed | Equal 2-adic valuations are necessary and sufficient; the common odd part is an lcm. |
| Logarithmic and positive-moment means | passed | Complete-period averaging gives \(1/d_e\) at each depth, and moment coefficients telescope. |
| Finite weighted birth identity | passed | Even \(d_p\le2N\) gives first contact \(d_p/2\le N\), so all primes lie in a fixed finite product. |
| Resolvent powers and Fourier sign | passed | The surviving geometric-series indices are \(l=k+nt\), giving exactly the stated numerator. |
| Split and unramified primitive valuation | passed | Numerator is a unit; precisely one denominator is nonunit, of valuation \(e\). |
| Derivative/gcd and primitive component | passed | \(\gcd(A,F(A))=1\); residue order excludes all proper-divisor factors. |
| Prescribed exact-depth family | passed | One digit lifts and every other digit stops at the requested depth; includes \(n=1\). |
| Homogeneous resultant scaling | passed | Dehomogenized evaluations differ by powers of unit \(B\). |
| Canceled packet and coefficient budget | passed | Canceled exponent is at most \(v_p(R_P)\); resultant absolute value is at most \((\sum_k\lvert\lambda_k\rvert)^{\varphi(2n)}\). |
| Fixed versus moving conductor | passed | Final note explicitly fixes \(n,P\); \(P(T)=T-2\), \(n=2^s\ge2\) gives absolute resultant \(2^n+1\). |
| Uniform exceptional birth bound / ABC | not addressed | The notes explicitly leave this arithmetic estimate open. |

## 4. Reconstructing the character claims

For \(x=A/B\bmod p^e\), reduction modulo \(p\) forces any period to have the form \(dk\). Denominators are units and odd-prime lifting gives \(v_p(A^{dk}-B^{dk})=s+v_p(k)\). Therefore
\[
d_e=d p^{\max(0,e-s)}.
\]
If \(d\) is odd there is no contact with \(-1\). If \(d\) is even, \(x^{d_e/2}\) is the unique element of order two and hence equals \(-1\): the factors \(z-1,z+1\) have gcd dividing 2. Thus the complete contact set is \(n=d_e/2\bmod d_e\). Formula (8) inherits this even-order hypothesis. Formula (9) remains valid for odd order, where its character sum is zero, and has the correct conjugation.

The actual per-depth density is \(1/d_e\); the first \(s\) depths all have density \(1/d\). For \(A=p^L-1\), \(A+1=p^L\) and \(A-1\) a \(p\)-unit give \(d=2,s=L\). This is an arbitrary plateau in the stated domain, with changing base, rather than an ABC counterexample.

For several even periods \(q_i=2^{r_i}m_i\), \(m_i\) odd, the condition \(n=q_i/2\bmod q_i\) is precisely \(v_2(n)=r_i-1\) and \(m_i\mid n\). Unequal \(r_i\) are incompatible. If the common value is \(r\), all conditions are equivalent to
\[
n=2^{r-1}\operatorname{lcm}(m_i)\cdot\text{an odd integer}
\quad\Longleftrightarrow\quad n=D/2\pmod D.
\]
This proves density \(1/D\) with no independence assumption. In particular primitive birth contacts at prime exponent \(\ell\) can share the same order \(2\ell\) and identical projectors.

Since every \(d_e\mid d_L\), the complete-period mean is
\[
\sum_{e=2}^{L}\frac1{d_e}
=\frac1d\left(s-1+\sum_{j=1}^{L-s}p^{-j}\right)
\qquad(L\ge\max(2,s)).
\]
Its limit is \((s-1+1/(p-1))/d\). As written this is a limit of complete-period means of truncated functions. It also equals the natural Cesàro mean of the untruncated local powerful-part valuation; multiplying by log p gives the logarithmic mean: on the contact class the valuation is \(s+v_p(n)\), and counting extra depths yields a geometric sum with \(O(\log N)\) total rounding error before division by \(N\). This does not justify exchanging an infinite moving-prime sum with an average.

For \(M=\min((v_p(A^n+B^n)-1)_+,L-1)\),
\[
p^{\sigma M}
=1+\sum_{e=2}^{L}
\left(p^{\sigma(e-1)}-p^{\sigma(e-2)}\right)1_{p^e\mid A^n+B^n}.
\]
Averaging proves the stated truncated moment formula for every real \(\sigma>0\). The plateau terms telescope exactly. A truncated Fourier expansion has principal coefficient equal to its mean, so nonprincipal cancellation does not remove its positive birth contribution.

For formula (18), even \(d_p\le2N\) is equivalent to first contact \(d_p/2\le N\). Every contributing prime divides \(\prod_{n\le N}(A^n+B^n)\); thus its prime sum is finite and the stated double counting is exact.

## 5. Reconstructing the cyclotomic claims

With \(t=\eta B\), expand each \((A-t\zeta^j)^{-1}\). The weight \(\zeta^{-kj}\) keeps precisely the powers \(l=k\bmod n\), giving
\[
\frac nA\left(\frac tA\right)^k\frac1{1-(t/A)^n}
=\frac{nA^{n-1-k}t^k}{A^n+B^n}.
\]
The powers are nonnegative for \(0\le k<n\), the plus sign follows from \(\eta^n=-1\), and \(\eta=1\) gives the minus variant. The endpoint \(n=1\) is exactly \(1/(A+B)\).

At a split prime \(p\nmid nAB\), every numerator is a unit, so each individual mode has valuation \(-e\). Separability gives distinct reductions of the \(n\) roots of \(X^n+1\); exactly one equals \(A/B\). All other denominator factors are units. Their product is \(A^n+B^n\), so the one nonunit branch has valuation \(e\). The same proof works at the stated unramified prime with \(v_{\mathfrak p}(p)=1\). This separates branches without bounding depth.

The Hensel construction is exact. Cyclicity gives residue order \(2n\) because \(2n\mid p-1\). The derivative is a unit. Exactly one digit lifts a root from depth \(j\) to \(j+1\); any other digit after depth \(e\) gives valuation exactly \(e\). Adding a multiple of \(p^{e+1}\) enforces \(A\ge2\) without changing the valuation. Any proper-divisor cyclotomic factor would force smaller residue order, so all this output valuation lies in \(\Phi_{2n}(A,1)\). The example \(A=7,n=2,p=5\) also directly refutes the claimed disappearance of square contact under a unit derivative/discriminant.

The fixed-filter normalization \(\eta^{-k}\) removes the root-of-unity numerator exactly. Let \(Q(T)=P(T,1)\), \(H=\Phi_{2n}\), and \(m=\deg H\). The integral Sylvester adjugate gives \(R_P=UH+VQ\). At \(A/B\), all coefficients and powers of \(B\) are \(p\)-integral, and
\[
H(A/B)=B^{-m}H(A,B),\qquad
Q(A/B)=B^{-(n-1)}P(A,B).
\]
Both factors are units, even if the actual degree of \(Q\) is smaller. Thus
\[
\min\{v_p(H(A,B)),v_p(P(A,B))\}\le v_p(R_P).
\]
A primitive order-\(2n\) prime has \(2n\mid p-1\), so \(p\nmid nAB\), and its entire output valuation lies in \(H(A,B)\).

“Denominator depth canceled” means \(\min(e,v_p(P(A,B)))\), with \(v_p(0)=+\infty\). The bound does not cap numerator valuation beyond the canceled pole. Multiplying the primewise inequalities proves that the canceled primitive-prime packet divides \(\lvert R_P\rvert\). Since \(H\) is monic with unit-circle roots,
\[
|R_P|=\prod_{H(z)=0}|Q(z)|
\le\left(\sum_k|\lambda_k|\right)^m.
\]
There is no omitted denominator or leading-coefficient factor.

The Eisenstein arguments have the stated hypotheses: for powers of two, shift \(T^n+1\) by 1; for odd prime \(\ell\), use \(\Phi_{2\ell}(-T)=\Phi_\ell(T)\) and then shift by 1. The degree restrictions correctly distinguish coprime filters from scalar multiples of \(H\).

The moving-conductor countercheck is correctly typed: \(Q(T)=T-2\) corresponds to \(P(X,Y)=XY^{n-2}-2Y^{n-1}\) in the allowed homogeneous space for \(n\ge2\). For \(n=2^s,s\ge1\),
\[
|\operatorname{Res}(T^n+1,T-2)|=2^n+1,\qquad P(2,1)=0.
\]
Its coefficient norm is 3. Thus fixed small coefficients do not keep the resultant-prime set fixed when \(n\) varies. The logarithm of the bound \(3^n\) is linear in \(n\), not a sublinear budget for fixed base \(A=2\).

## 6. Computation audit

The author verifiers were copied into reviews/characters_cyclotomic_checks/characters and /cyclotomic with frozen proof notes. Pre-review outputs are preserved as source_verification.json; reruns write only review copies. Both reruns passed. Commands from the project root:

~~~bash
cd abc_work/roots_unity/reviews/characters_cyclotomic_checks/characters
python3 verify.py
cd ../cyclotomic
python3 verify.py
cd ..
python3 independent_checks.py
~~~

Character coverage is exactly the recorded finite grid: 30,100 conductor checks, 19,804 shell residues, 351 order cases, 135,394 contact checks, 117 means, 36 joint parameter cases / 5,232 integer checks, and 32 plateau constructions. Its Ramanujan helper uses an integer Möbius formula rather than algebraic root sums. Its mean grid only uses \(L=\max(2,s)\). Those are consistency checks with the written proof, not independent proofs of universal identities.

The final cyclotomic verifier passed 50 prescribed-depth cases (five pairs, depths 1–10), 211 cleared Fourier modes, 5,880 fixed-filter cases / 8,880 resultant contacts, 87 component deletions, and seven moving-conductor checks \(n=2,4,\ldots,128\). Its Fourier examples use \(B=1,n>1\). Its Hensel checks establish valuations and order without separately evaluating every cyclotomic factor. These coverage limits do not affect the universal arguments above.

The separate independent_checks.py imports no route helper. It uses integer reduction modulo cyclotomic polynomials for actual root sums, formal cleared resolvent polynomials with independent \(A,t\), rational means, and independently constructed Sylvester determinants. It passed:

| Supplement | Exact finite scope/count |
|---|---|
| Root sums in \(\mathbb Z[X]/\Phi_q\) | All residues, \(1\le q\le40\), 820 |
| Formal resolvent, every mode | \(1\le n\le9\), 45 |
| Local period means | Coprime \(2\le A\le8\), \(1\le B<A\), \(p=3,5,7\), even order, three consecutive allowed \(L\), 81 |
| Positive truncated moments | Same grid, \(\sigma=1,2\), 162 |
| Resultant coefficient bounds | \(1\le n\le8\), recorded deterministic patterns, 39 nonzero resultants |
| Homogeneous primitive contacts, including \(B>1\) | \(2\le A\le8\), all coprime \(B<A\), 1,081 |
| Moving-conductor resultant | \(n=2,4,8,16\), 4 |

These checks address signs, endpoints, homogeneous scaling, and mean tails beyond the author grid. They establish no distribution theorem, asymptotic bound, or ABC result. Exact script hash and outputs are in characters_cyclotomic_checks/independent_results.json. Source hashes, not route output bytes or timestamps, pin the mathematical revision.

## 7. Exact remaining obligation

No gap remains in the audited local formulas. The unresolved global implication is a uniform bound on exceptional birth mass
\[
\log W_n=\sum_{p\ \mathrm{odd},\ p\mid A^n+B^n}(s_p-1)\log p
\]
at the moving-prime/height scale needed for ABC, or a proved transfer of that cost into another radical budget. The inherited ordinary odd-prime lifting part divides \(n\); these calculations leave exceptional birth weight visible. Coprime filters move canceled weight into an explicit resultant ledger. The present facts do not prove \(\log W_n=o(n\log A)\) uniformly in the intended family.

The strongest safe conclusion is that individual Fourier modes preserve primitive poles, coprime fixed filters can cancel only resultant-supported depth, and exponent-space birth contacts can synchronize strongly. Any next arithmetic claim needs a quantified height estimate for a specified simultaneous-contact or resultant packet; another orthogonality identity does not supply that estimate. General primitive triples also require coverage beyond the growing-exponent common-power family, including unrestricted multipliers or input exponent vectors. ABC remains unresolved.
