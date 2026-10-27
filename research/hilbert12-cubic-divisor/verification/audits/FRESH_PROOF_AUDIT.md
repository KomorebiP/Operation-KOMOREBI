# Fresh independent mathematical audit

Audit date: 2026-10-07. This is a read-only audit of authoritative raw proofs and Lean signatures. The author’s status labels and `REVIEW.md` verdicts were not used as evidence. No raw source was edited. This is an independent agent derivation, with a separately tasked predecessor audit, rather than an independent human referee report. Agreement between agents is not itself mathematical evidence.

**Normalized target.** With the fixed lower embedding of the pure cubic field, determine the complete scalar divisor of the actual principal correction, prove its unsigned zero and pole growth, construct the stated absolute canonical product, recover the remaining cubic exponential and its normalized special cube, and assess what follows for the arithmetic equality.

**Primary verdict: incomplete, with the smallest missing implication being the exact phase assertion `Im(C_pol U_Gamma^3)=0`, once the separately named modulus, positivity and branch inputs are supplied.** The analytic divisor/reconstruction claims pass the scoped audit. The finite-theta exclusion is correct with the explicit restriction that the nonvanishing entire prefactor is one global factor outside the finite rational expression. Without that restriction, a broader reading admitting unrelated prefactors inside sums is refuted below. The analytic formula is not an arithmetic evaluation.

## 1. Objects and hypotheses reconstructed from definitions

Let `omega=exp(2*pi*i/3)`, `beta=cuberoot(7)*omega^2`, `epsilon=2-beta`, `rho=epsilon^(-1)`, `tau=(beta^2+2*beta)/15`, `t=-tau`, `s=-(beta+2)/15`, and `d=(tau+2*s+4)/7`. Write `r=cuberoot(7)`. Since `r<2`,

\[
\operatorname{Im}t=\frac{\sqrt3 r(2-r)}{30}>0,\qquad
\operatorname{Im}s=\frac{\sqrt3 r}{30}>0,\qquad
\operatorname{Im}d=\frac{\sqrt3 r^2}{210}>0.
\]

Eisenstein irreducibility of `X^3-7` implies rational independence of `1,beta,beta^2`, and hence of `1,t,s`. This is rational independence, not real linear independence in the complex plane. The full rank-three lattice image is nondiscrete; only its selected nonzero divisor support is locally finite.

For positive periods set `S5(z;a,b)=Gamma(z;a,b)^5/Gamma(5z;5a,5b)` and `F(z)=1/S5(z+t;t,s)`. This equals the negative-first-period convention retained in the raw source. Let `qt(z)=theta0(z;t)^5/theta0(5z;5t)`, `qs(z)=qt(rho*z)`, and

\[
R(z)=\frac{\prod_{k=0}^{6}F(z+kd)}{F(\beta z)}.
\]

The integer coordinate map is `lambda(a,b,c)=(a*tau+b*s+c/5)/beta`, with `H(n)=1` for `n>0` and zero otherwise, `w(c)=4` for `5|c` and `-1` otherwise, and `j=ceil((3c-2b)/7)`. Counts below include analytic multiplicities. In particular `n_D=n_++n_-=sum |m_lambda|`; it is not the signed sum.

## 2. Dependency graph and obligation matrix

The local analytic chain is: positive-period gamma product and its reciprocal continuation → base divisor and shifts → unique seventh lift with preserved fifth weight → complete correction divisor → cubic family lower bounds and cone upper bound → absolute genus-three product. Separately, the fourth logarithmic derivative of the defining gamma product → the same derivative for the canonical product → cubic exponential. Exact reflection plus normalized theta covariance gives the quadratic jet; exact period-one transition plus the canonical second jet gives the cubic jet; the based transition gives the special cube.

The arithmetic chain is separate: independently defined ray-field candidate and CM units → algebraic cube/polarization certificate; exact partial-zeta/BCG modulus input → equal moduli; positive-real-part and branch enclosures + exact polarized reality → cube equality and then unpowered equality. No edge from divisor matching or formula (17) supplies polarized reality.

| ID | Claim and exact source locator | Required implication | Status |
|---|---|---|---|
| A01 | Fixed domain, v013 §1; v014 §1 | Upper-half-plane periods; injective rational coordinates | Passed by the displayed calculations and irreducibility |
| A02 | Base divisor, v013 Theorem 2.1 | Positive-period zero/pole cones, including walls `a=0,b=0`, and fifth smoothing | Passed; conventions checked against primary authors’ PDF, exact arXiv-v2 artifact authentication remains conditional |
| A03 | Complete divisor, v013 Theorem 3.1; v014 (1) | Unique lift digit and preserved fifth weight | Passed; analytic derivation plus integer Lean signatures |
| A04 | Locally finite support, v013 §2; v014 §2 | Cone support has bounded indices on every compact set | Passed; full nondiscrete lattice is not confused with support |
| A05 | Explicit cubic families, v014 (2)–(4) | Positive pivot, order, injection, disjointness, radius bound | Passed; smallest `n=1,r=4` pole case included |
| A06 | Cubic upper/lower growth, v014 (5) | Finite union of translated/dilated cone supports; extend discrete-radius lower bounds to all large radii | Passed; separate zeros and poles both have `Theta(r^3)` multiplicity counts |
| A07 | Finite affine-theta exclusion, v014 §3 | Fixed positive-definite period matrix gives order-two bound; clearing denominators; Jensen count | Passed with one global nonzero entire prefactor; broader closure under arbitrary prefactors in sums fails |
| A08 | Canonical divisor product, v014 (8)–(9) | Fourth-power absolute summability, separated positive/negative products and normal convergence | Passed; no arithmetic normalization used |
| A09 | Minimal ungrouped absolute genus, v014 §4 | Cubic lower bound implies third-power divergence and `E2` absolute failure | Passed; conditional/grouped genus-two convergence is not excluded |
| A10 | Tail bounds, v014 (10) | Multiplicity count `n_D(r)<=A*r^3` for `r>=R_*`; partial summation | Passed with constants `4A/T` and `2A|z|^4/T`; rename radius threshold to avoid overloading anchor `R0` |
| A11 | Fourth logarithmic derivative, v014 (11) | Normal differentiation of gamma products, sine partial fractions, absolutely convergent fourth-power regrouping | Passed; signs and beta/fifth scaling checked directly |
| A12 | Cubic exponential, v014 (12) | Nonzero entire ratio on simply connected C plus vanishing fourth derivative | Passed; divisor matching alone is insufficient |
| A13 | Reflection identity, v014 (13) | `F(z)F(-z)=qt(z)/qs(z)` and seventh translation pairing | Passed as meromorphic identities, including removable behavior at zero |
| A14 | Quadratic coefficient, v014 (14) | Exact theta scalar, covariance, Laurent constants and six-to-three pairing | Passed; factor `1/2` and `4*alpha2=(log T)''(0)` checked |
| A15 | Canonical second jet and cubic coefficient, v014 (15)–(16) | Absolute fourth-order cancellation and period-one double-log differentiation | Passed; no third-power conditional sum isolated |
| A16 | Special cube, v014 (17) | `exp(alpha1)` from based period-one transition; cubing removes logarithm lift | Passed; exponents `-2/3` and `-8/9` checked independently |
| A17 | Conjugation cancellation, v014 (18) | Conjugating divisor product and polynomial jets | Passed on C; torus descent and nonzero periodic relative multiplier are not supplied |
| A18 | Seven-point norm and zero anchor, v012 §2; v013 §5 | Nonempty common log chamber; connected parameter continuation; direct leading coefficient; central gamma value | Passed on reconstruction; `F(0)=epsilon^2` is unnecessary for `R(0)` anchor |
| A19 | Canonical theta normalization/covariance, v003 §§1–7 | Exact norms for degrees2 and3, fifth-torsion ordinate identity and coprime powers3 and8 | Passed on internal reconstruction; analytic addition laws remain external inputs |
| A20 | Smooth principal-norm rigidity, v012 §4 | Fourier transfer decay from `B^3=7I`, smooth mean-zero hypothesis and norm compatibility | Passed as an abstract sufficient theorem; its gamma/model application is not addressed |
| A21 | Algebraic polarized candidate, v006 §§1–3 | Independently defined candidate, actual conjugation and explicit cube certificate | Passed for the presented algebraic implication; full field/ray identification was not replayed end to end in this audit |
| A22 | Exact gamma modulus, Stark proof §§2–7 | Artin induction, cubic reciprocity, precise Kronecker/ray indexing and BCG Theorem3.2 | Conditional on coordinated exact external-source/hypothesis review; internal signs/constants reconstructed consistently |
| A23 | Positive-real-part and branch enclosure, v005 §7 and v006 §5 | Containing interval computation with analytic tail and trusted elementary interval backend | Computationally verified only to the shipped scope; new replay owned by the numerical-validation agent, not this audit |
| A24 | Original `U_Gamma=U_alg` | Exact `Im(C_pol*U_Gamma^3)=0`, with A21–A23 | Not addressed by the analytic product; smallest arithmetic gap |

`v003` here is `sources/continuation_chain/10/Komorebi_H12_Fifth_Isogeny_Transport_Lean_v0.4.0/prior/v03_PROOF.md`; `v005` and `v006` are the raw chain09 and chain08 proofs. This is not an exhaustive replay of every earlier arithmetic certificate or every cumulative Lean declaration.

## 3. Decisive derivations and boundary checks

### Divisor and support

The gamma argument `z+t` at `z=a*tau+b*s+c/5` has `(t,s)` coordinates `(1-a,b)`. Its positive-period gamma order is `H(b)-H(a)` even on the walls. The numerator in `F=Gamma(5(z+t))/Gamma(z+t)^5` contributes that order for all integer `c`, while the denominator contributes five times it only for `5|c`. Thus `ord F=w(c)(H(a)-H(b))`.

The inverse principal matrix makes the first lifted coordinate `(-2b+3c+k)/7`. Exactly one `0<=k<7` is integral. With `j=ceil((3c-2b)/7)` it gives `k=7j+2b-3c` and lift `(j,2j-a,20j+5b-8c)`. Its last coordinate is `2c mod5`, so its weight equals `w(c)`. Subtracting the denominator order yields the stated formula. The origin has order zero, `tau` order4, `s` order-4 and `-1` order4.

For a nonzero base coefficient, `a` and `b` have opposite weak signs in precisely the way needed for `|Im(a*tau+b*s)|=|a|Im(t)+|b|Im(s)`. A radius bound therefore bounds `a,b`, then the real part bounds `c`. This proves local finiteness and cubic upper count from selected cone support, rather than treating the entire rank-three lattice as discrete.

For the lower families, `n=1` already gives `a=-1,b=1,c=10` and `c=9,8,7,6`; every bracket is1. Multiplicities are4 for the zero and-1 for each pole. In general there are `n^3` zero points and `4n^3` pole points, yielding `4n^3` multiplicity in each sign. For `r>=2K0`, use `n=floor(r/K0)>=r/(2K0)` to obtain the all-large-radius lower bound.

### Canonical product and cubic residual

Partial summation of `n_D(r)=O(r^3)` gives `sum |m|/|lambda|^4<infinity`. Conversely, its cubic lower bound gives `sum |m|/|lambda|^3=infinity`. For any fixed nonzero `z`, `log E2(z/lambda)=-z^3/(3lambda^3)+O(|lambda|^-4)`, so ungrouped absolute genus2 fails. This statement is not about a specially ordered signed product.

For each sine factor, the fourth logarithmic derivative is `-6 sum_(n in Z)(w-n)^(-4)`. The positive-period products can be differentiated normally away from their divisors. Their cone supports have cubic count, making the resummed fourth-power series locally absolutely convergent. In a scaled factor, the chain-rule fourth power cancels the fourth power in the scaled denominator, so the fifth-scale and beta-scale contributions have exactly the multiplicities of the transported divisor. This proves the sign and normalization in (11).

After identical divisors are canceled, `R/(R0*W_D)` is a nonzero entire function equal to1 at0. It has a global logarithm whose fourth derivative is zero. The removed canonical jets at0 then identify its polynomial coefficients with the actual logarithmic jets of `R`.

### Reflection and reconstruction

Put `w=z+kd`. Combining reflection with `7d=tau+2s+4` gives `F(w)F(-w+7d)=1/qt(w-s)` for `1<=k<=6`. Hence (13) has the displayed reciprocal translated factors. With `L_s(z)=rho^2 L_t(rho*z)`, the constant term of its second log derivative is

\[
4\alpha_2=2(1-\beta^2)(1-\rho^2)S_t-\sum_{k=1}^6L_t(kd-s).
\]

The six translated arguments are, by evenness and periods1,t, two copies of the three `u_j=(t+d)/2+jd`. This yields (14).

For the canonical second jet at1, the combination `-1/(lambda-1)^2+1/lambda^2+2/lambda^3` is `O(|lambda|^-4)`. The first term must be retained together with the other two; the separately written third-power series need not converge absolutely. Differentiating `log(R(z+1)/R(z))` twice gives `6alpha3+B_D(1)`, and the normalized theta transition gives `-beta^2 sum L_t(r*s)`. This proves (16).

Finally `exp(alpha1)=K(0)exp(-alpha2-alpha3)/W_D(1)`. Cubing at1/3 gives exactly

\[
R(1/3)^3=R_0^3K(0)\frac{W_D(1/3)^3}{W_D(1)}
\exp\!\left(-\frac23\alpha_2-\frac89\alpha_3\right).
\]

`1/3` is outside the divisor lattice because `beta/3=-5s-2/3` would require nonintegral `c=-10/3`; `1` and0 have order0. Thus these evaluations have no omitted exceptional factor.

## 4. Decisive restrictions and counterexamples

1. **Finite-theta grammar.** A safe class is `exp(h(z))*P(z)/Q(z)`, with one entire `h` and nonzero entire `P,Q` obtained by finite algebraic operations from fixed-period affine theta restrictions, finite derivatives and polynomials. They obey an order-two bound, so Jensen bounds their divisor counts by `O(r^2)`. If unrelated nonvanishing prefactors may occur inside sums, `1+exp(z^3)` belongs to that broader class using constant nonzero theta restrictions. Its zeros satisfy `z^3=(2k+1)*pi*i`, and their count is `Theta(r^3)`. The unrestricted class claim is therefore false. The traditional edition was notified and explicitly restricts the global prefactor.
2. **Divisor matching is insufficient for a polynomial residual.** Multiplying `R0*W_D` by `exp(z^4)` preserves its divisor and anchor but has a nonzero fourth logarithmic derivative. The additional gamma fourth-derivative identity is essential.
3. **Raw principal norm is not scalar.** The raw product has order4 at `tau` while `F(beta*tau)` has order0. A constant phase cannot repair this. This is a genuine divisor obstruction, not a numerical disagreement.
4. **Regularity on C is not descent.** The entire phase factor in (18) need not have the three periods needed for a scalar on the real torus. The existence of that entire factor supplies neither the relative periodic multiplier nor the principal-norm coboundary hypothesis.
5. **A small residual is not equality.** For any small real `theta`, replacing the unknown ratio by `exp(i*theta)` preserves its modulus and can pass an arbitrarily tight finite proximity test. Equal modulus and a tiny imaginary enclosure cannot prove exact polarized reality.

## 5. External sources, computation scope and provenance

The raw analytic sources inspected were v014 `PROOF.md`, all three v014 Lean files, v013 `PROOF.md` and divisor/carry formal sources, v012 `PROOF.md`, the retained v003 normalization proof, v005 phase-regulator proof, v006 polarized comparison proof, and `sources/stark_modulus/PROOF.md`. No source `REVIEW.md` verdict was adopted.

The proof-audit skill and its general-logic, representation/symmetry, computation and external-source obligation checklists were read. No applicable `AGENTS.md` or `.mathbox` ledger was found. Source hashes were read using `sha256sum`; theorem and section locators were searched with `rg`. Raw computational scripts were not rerun in place because they overwrite authoritative evidence. The independent predecessor subaudit recomputed 343 Fraction-coordinate triples; those bounded checks supplement its universal derivation. The v014 Lean files contain exactly11 growth and14 inherited coefficient declarations; their mathematical signatures were audited here, while fresh compilation/axiom logs are owned by the Lean-companion agent.

Root coordinates external-source verification. DLMF21.2.1–2 supplies the fixed positive-definite theta series/Gaussian bound and DLMF1.10(ix)–(x) the normal-product background. The exact arXiv2311.04110v2 HTML/PDF could not be retrieved in this environment. The primary authors’44-page PDF at `https://webusers.imj-prg.fr/~pierre.charollois/BCG_cubic.pdf` has the matching positive-period product and adjacent reciprocal negative-period/difference conventions on page2. This checks those conventions; it does not authenticate the exact arXiv-v2 artifact. The precise BCG modulus and ray-indexing input remains a separately coordinated source leaf. No secondary snippet is being treated as proof.

| Raw file | SHA-256 |
|---|---|
| `sources/v014/PROOF.md` | `0a2c32818790213efc30dd566ed124841bf647357764e6424b4149083e7712d1` |
| `sources/v014/formalization/H12PrincipalDivisor.lean` | `91ec2e80c8ce48793b0f491bb0b4fffb5f43ac7400db2aa4a3d0df0fa9cf8f00` |
| `sources/v014/formalization/H12CubicDivisorGrowth.lean` | `f3620660ee3e4a8532d65170dde94ce0164c5112e9db5587fb0d25f16b7998b8` |
| `sources/continuation_chain/01/.../PROOF.md` | `7b8b42ea194af5d14a9386f915819a3990724b4a26a56d89dc40c798b5c6f0b4` |
| `sources/continuation_chain/02/.../PROOF.md` | `ee2b142c1795ab30a45e50c8645918b1cb775d44cc7847cdace344cc8d93228d` |
| `sources/stark_modulus/PROOF.md` | `2f5558f5a19572b5569c1d8af6eca559358a3813ffc45eeabb76d1754d669db1` |

## 6. Smallest remaining arithmetic implication and strongest safe statement

Set `C_pol=epsilon*a1*a2^3/omega` and `R_plus=|epsilon|^4|a1|^6|a2|^4`. The algebraic candidate certificate gives `C_pol*U_alg^3=R_plus>0`. If the exact modulus input is accepted, then `|C_pol*U_Gamma^3|=R_plus`. The positive real-part enclosure excludes the negative real value, and the branch bound `|U_Gamma/U_alg-1|<1/2` excludes the two nontrivial cube roots. Therefore the one exact assertion `Im(C_pol*U_Gamma^3)=0` suffices. It is not established by the material audited here.

The analytic correction is characterized by its complete divisor, theta transitions and normalized zero value, and now has a gamma-free, absolute genus-three formula for its cube at1/3. This is a strong analytic representation. It neither proves algebraicity of `U_Gamma` nor gives a class-field evaluation of the regularized infinite product. A proposed arithmetic comparison must still prove the special phase identity directly, or construct the actual periodic nonzero relative multiplier with the precise based identification and smooth principal-norm relation. The cheapest publication check is to keep those hypotheses visible and to use the restricted finite-theta class throughout; no new research route is asserted by this audit.
