# Independent audit of the v1.0 structural extensions

**Primary verdict: proved as written.** This verdict applies to the five frozen mathematical proof files pinned below, under their stated parameter domains. The separately inspected sequence API's two invalid-input defects have been repaired and their targeted regression checks pass. No remaining mathematical gap was found in this scoped audit.

Checkpoint: SF-DISCOVERY-100. Audit actor: a fresh isolated reviewer assigned the four exact statements, with no author verdict supplied. Historical priority is a separate unresolved question.

The independent derivations below were completed before reading the four v1.0 author proof files. The sequence and polyphase chapter, arithmetic inverse conditioning and character extensions, and shifted spectral appendix were then added to the review scope and read in full. The old v0.1 definitions and proofs were read to fix the objects being audited. This is an informal mathematical audit with explicit dependency and artifact checks, rather than a machine-checked proof certificate.

## Normalized claim cards

1. For every finite bank of positive weights summing to one and contractions strictly between zero and one, the unique normalized solution of
   \(F'(z)=1+\sum_jh_jF(q_jz)F(r_jz)\), \(F(0)=0\), is entire and has positive finite lower and upper type at \(\rho=\max_j\rho_j\), where \(q_j^{\rho_j}+r_j^{\rho_j}=1\):
   \(0<\liminf_{R\to\infty}R^{-\rho}\log M_F(R)\le\limsup_{R\to\infty}R^{-\rho}\log M_F(R)<\infty\).
2. For real \(a>1/2\), \(\beta>0\), and positive integer \(Q\), equality of the complex-depth arithmetic germs
   \(A_{a,\beta,Q}(s)=\sum_{n\ge2,(n,Q)=1}\mu(n)^2n^{-2a}(1-n^{-\beta})^{2s}\)
   is equivalent to equality of \(a\), \(\beta\), and \(\operatorname{rad}Q\). The logarithm in each complex power is real.
3. For a finite set of primes and real strengths \(\lambda_p\), the measure
   \(\nu_\lambda=\sum_{n\ge1}\mu(n)^2n^{-4}\prod_p(1+\lambda_p\mathbf1_{p\mid n})\delta_{(1-n^{-2})^2}\)
   is positive if and only if every strength is at least \(-1\). Every violation has an explicit finite-degree polynomial with negative squared norm.
4. For integer \(N\ge2\), the zero zeta of \(d_N(w)=\sum_{n\ge0}(-1)^nw^n/(Nn)!\), counting zeros with multiplicity and using arguments in \((-\pi,\pi]\), continues meromorphically to \(\mathbb C\). Its only pole is simple at \(1/N\), with residue \(\sin(\pi/N)/(N\pi)\); \(\mathcal Z_N(-m)=0\) for all integers \(m\ge0\), and \(\mathcal Z'_N(0)=-\log N\).
5. The factorial-normalized asymmetric coefficients are integer polynomials with the stated exponent and degree bounds; rational banks admit the stated denominator clearing. Positive parameters beyond a unit scale give zero-radius formal series, while exactly one unit scale and one strict positive contraction give an entire function of infinite order. Root-filter sections, EGF antiderivative taps, Hurwitz products, and the ordinary finite polyphase tap matrix obey the precise identities in `new_results/sequence_polyphase.md`.

The spectral scope also includes real shifts \(a\ge0\): for \(a>0\), the poles are precisely \(1/N-k\), with residues \(\sin(\pi/N)(1-1/N)_k a^k/(N\pi k!)\); nonpositive integer values vanish and the regularized product is \(N E_{N,1}(a)\). At \(a=0\), only the unshifted pole remains.

## Independent critical derivations

### A. Finite-bank lower type without a fixed-contraction loss

Positive Taylor coefficients give \(M_F(R)=F(R)\). Put \(H(t)=\log F(e^t)\), \(a_j=-\log q_j\), and \(b_j=-\log r_j\). The v0.1 upper comparison proves \(H(t)\le Ce^{\rho t}\) for sufficiently large \(t\). It also proves an order lower bound of every exponent below \(\rho\), by integrating over a fixed fraction of the radius and then letting that fraction tend to one. That argument alone does not prove positive lower type.

The crucial extra fact is log-sum-exp convexity: \(H\) is convex because it is the logarithm of a positive sum of exponentials. For large \(t\), \(H(t)\ge0\), and hence
\[
0\le H'(t)\le H(t+1)-H(t)\le C_1e^{\rho t}.
\]
Choose a maximal-order channel with positive weight \(h\) and logarithmic contractions \(a,b\). Set \(\varepsilon=e^{-\rho t}\) and integrate the defining equation over \([e^t(1-\varepsilon),e^t]\). For large \(t\), \(-\log(1-\varepsilon)\le2\varepsilon\). The derivative bound therefore implies bounded losses in each child logarithm. Consequently
\[
H(t)\ge H(t-a)+H(t-b)+(1-\rho)t+C_0
\]
with a constant independent of \(t\). Define \(G(t)=H(t)+(1-\rho)t+B\). Taking \(B\le C_0+(1-\rho)(a+b)\) gives \(G(t)\ge G(t-a)+G(t-b)\).

The old lower-order estimate ensures \(H(t)/t\to\infty\), so \(G\) is eventually positive even when \(\rho>1\). Choose a compact seed interval of length \(\max(a,b)\), above this threshold, on which \(G(t)\ge ce^{\rho t}\) for some \(c>0\). Induction over intervals of length \(\min(a,b)\), using \(e^{-\rho a}+e^{-\rho b}=1\), propagates that bound. Subtracting the linear correction proves a positive lower type. No existence of a single type limit is implied.

The upper comparison for a finite bank must use the maximum of the channel roots, rather than a weighted characteristic equation. Zero-weight taps must be removed before that maximum is taken. Strict positivity and strict contractions are substantive hypotheses of this proof.

### B. Equality identifies the arithmetic parameters

Each member is an entire positive Laplace sum with a finite mass and strictly decreasing positive frequencies
\(\lambda_n=-2\log(1-n^{-\beta})\), indexed by the increasing squarefree integers coprime to \(Q\), excluding one. Germ equality implies entire equality. Along \(s=-t\), the largest frequency dominates, with a remainder exponentially smaller than its positive leading mass. Thus the largest frequency and its weight agree. Subtracting that common atom and repeating identifies both ordered atomic spectra exactly. This is an elementary proof of Laplace uniqueness here and does not require abstract moment determinacy.

Frequency matching means that the matched support integers satisfy
\(m=n^{\beta/\beta'}\). Write \(c=\beta/\beta'>0\). The elementary squarefree coprime counting theorem gives
\(S_Q(X)=\delta_QX+O_Q(\sqrt X)\), with \(\delta_Q>0\). A support power bijection gives \(S_{Q'}(X)=S_Q(X^{1/c})\), up to the identical removal of one. Since both sides have positive linear-density asymptotics, \(c=1\). Hence \(\beta=\beta'\), and the matched integers are equal. Equality of their positive weights gives \(a=a'\). Finally, a prime belongs to the support precisely when it does not divide \(Q\), so the prime divisors, and thus radicals, agree.

No claim identifies the actual integer \(Q\) beyond its radical: higher prime powers are genuinely invisible. The squarefree density is an internally proved dependency in the baseline complex-depth route.

### C. Constructive negative form for every bad prime strength

If every strength is at least \(-1\), every atomic factor is nonnegative. If \(\lambda_p<-1\), the squarefree atom at \(n=p\) has negative mass \(w_p=p^{-4}(1+\lambda_p)\), irrespective of the other strengths. Let \(x_n=(1-n^{-2})^2\), which is strictly increasing. Put
\(g=\min(x_p-x_{p-1},x_{p+1}-x_p)>0\) and \(\eta=1-g^2\in(0,1)\). The polynomial
\[
f_K(x)=[1-(x-x_p)^2]^K
\]
takes value one at \(x_p\), while \(0\le f_K(x_n)\le\eta^K\) at every other support node. With \(C=\prod_p\max(1,|1+\lambda_p|)\), the total variation of the measure is at most \(C\,105\pi^{-4}\). Thus
\[
\int f_K^2\,d\nu_\lambda\le-|w_p|+C\,105\pi^{-4}\eta^{2K}.
\]
Any integer \(K>\log(C\,105\pi^{-4}/|w_p|)/(-2\log\eta)\) gives a strict negative form of degree \(2K\). This explicit proof works even if other primes are deleted or also have bad strengths. The bound is conservative and is not a claim of minimum witnessing degree.

### D. Spectral continuation, with the complex-zero interchange checked

The root-of-unity filter gives
\[
d_N(-t)=\frac1N\sum_{k=0}^{N-1}\exp(e^{2\pi ik/N}t^{1/N})>0\quad(t\ge0),
\]
where positivity also follows from its positive power series. The finite exponential representation proves
\(\log d_N(-t)=t^{1/N}-\log N+O(e^{-ct^{1/N}})\) and, by differentiating that representation,
\[
g_N(t):=\frac{d}{dt}\log d_N(-t)
=\frac1N t^{1/N-1}+O(t^{1/N-1}e^{-ct^{1/N}}).
\]
The differentiation of the remainder is justified by the finite explicit exponential sum, not by differentiating a bare asymptotic statement.

The seed has order at most \(1/N<1\), is one at zero, and has a genus-zero Hadamard product. Every zero stays away from the negative axis by a uniform angular margin: in a sufficiently narrow fixed sector around \(w<0\), the term \(\exp((-w)^{1/N})\) dominates all other root-of-unity terms for large modulus. The finitely many remaining zeros cannot lie on that axis because \(d_N(-t)>0\). Therefore \(|t+w_j|\ge c_0(t+|w_j|)\) uniformly in \(t>0\) and the zeros.

For \(1/N<\Re s<1\), absolute integration and summation now follow from
\(\int_0^\infty t^{-\Re s}|t+w_j|^{-1}dt\le C_s|w_j|^{-\Re s}\), together with the zero-count bound. The single-zero beta integral uses the principal argument in \((-\pi,\pi)\), which is legitimate because there are no negative-axis zeros. Consequently
\[
\mathcal Z_N(s)=\frac{\sin\pi s}{\pi}\int_0^\infty t^{-s}g_N(t)\,dt.
\]
Subtract the leading term at infinity. The resulting representation is
\[
\frac{\sin\pi s}{\pi}\left[
\int_0^1t^{-s}g_N(t)dt+
\int_1^\infty t^{-s}\bigl(g_N(t)-N^{-1}t^{1/N-1}\bigr)dt+
\frac{1/N}{s-1/N}\right].
\]
The infinity integral is entire. Taylor subtraction at zero continues the first integral, with possible simple poles only at positive integers. The sine cancels those poles. The uncancelled pole is \(1/N\), and its displayed residue is nonzero. At every nonpositive integer the bracket is regular, proving the stated zeros. Its value at zero equals
\[
\lim_{R\to\infty}\bigl[\log d_N(-R)-R^{1/N}\bigr]=-\log N,
\]
which gives \(\mathcal Z'_N(0)=-\log N\). The known \(N=2,4\) Hurwitz reductions independently agree with the special-value normalization.

## Source dependency checked independently

Hadamard factorization and zero-count bound: Noam Elkies, *Math 259: Functions of finite order: product formula and logarithmic derivative*, primary Harvard lecture notes, https://people.math.harvard.edu/~elkies/M259.02/prod.pdf, first theorem on page 1 and its proof through page 4. Checked directly on 2026-10-08 UTC. The theorem states the product with zero multiplicity, exponential polynomial degree at most the floor of the order, and \(O_\epsilon(R^{\alpha+\epsilon})\) zero count. In the present normalization the order is below one, the exponential factor is constant, and \(d_N(0)=1\) makes it one. The logarithmic derivative follows on compact sets avoiding zeros. This is a checked classical source leaf, not evidence of historical novelty.

## Dependency graph and proof-as-written review

The four principal branches are independent after their defining seeds are fixed.

- Dilation recurrence and positive coefficients -> tangent germ majorant -> entire radius bootstrap -> radial integral inequalities -> translated-radius lower comparison and logarithmic-radius upper comparison -> positive lower and finite upper type. Homogeneous positive weight polynomials -> coefficientwise diagonal majorant -> normal convergence in complex parameter domains and the quantitative simplex tap bound.
- Arithmetic positive Laplace sum and finite mass -> dominant-frequency peeling -> exact spectral atoms. Elementary squarefree coprime density -> spectral rank law -> depth exponent -> integer support -> weight exponent and radical. The same finite mass -> compact deleted-prime derivative bounds and injective Hilbert feature space. Nonprincipal character period cancellation -> squarefree count bound -> beta-integral sector bound.
- Finite prime Euler factors -> exact moments. Infinitely many surviving prime nodes -> strict Hankel positivity. Any bad prime's isolated negative atom -> isolating polynomial and rational tail envelope -> negative finite Hankel form. Positive conditional submeasures -> definite pencil -> exact degree, root locations, and collapsing margins. Monic orthogonality equations -> normalized moments -> Stieltjes germ and residues -> the full-sequence separator.
- Root-of-unity exponential packet -> negative-axis positivity, angular zero separation, and differentiated exponential asymptotic. Finite-order Hadamard factorization -> genus-zero product and zero count. Product logarithmic derivative plus branch separation and beta integral -> absolutely interchanged Mellin representation. Compatible endpoint subtractions -> continuation, pole set, trace zeros, and origin determinant. A rightward real shift preserves the branch gap and introduces the binomial asymptotic ladder.
- Factorial-normalized recurrence -> integer polynomials and homogeneous weight degree -> denominator clearing. A positive one-sided recurrence -> zero-radius obstruction above unit scale. A unit-scale linear ODE bootstrap -> entire extension at the edge; its real logarithmic derivative -> infinite order. A finite geometric root sum -> exact sections; indexed delayed coefficients -> EGF antiderivatives; Euclidean residue and carry -> the polyphase matrix.

The implications in this graph are supplied by local proofs except for the explicitly checked classical factorization, beta/reflection, gamma-ratio and even-zeta leaves. Finite computations support the implementations and examples; no universal analytic arrow is inferred from those computations.

| Obligation | Status | Decisive check |
|---|---|---|
| Positive bank type, including order below one | Passed | The author's fixed-width lower proof uses a translated radius, with no convexity assumption on the power. The seed interval, child radius lower bound, and fixed-step propagation all hold. |
| Explicit upper constants | Passed | The majorant recurrence sums to the printed \(V_N\); the seed radius is covered by \(Q^{-N}\), and \(B_+\) absorbs every channel's contraction loss. |
| Complex joint parameter dependence | Passed | A compact absolute-weight bound gives \(|c_n|\le W^nd_n(Q)\) and a convergent entire diagonal majorant on every joint compact set. |
| Quantitative tap-weight continuity | Passed | Differentiation preserves the positive coefficientwise majorant. The positive and negative parts of a normalized weight difference each have mass half its \(\ell^1\) norm, giving the stated factor \(1/4\). |
| Complete-germ arithmetic identification | Passed | Positive spectral peeling and the density-controlled rank asymptotic identify \(\beta\), then exact support labels, \(a\), and the radical. Modulus prime powers are correctly left invisible. |
| Effective count and rank envelopes | Passed | The coprime floor error is bounded by \(2^{\omega(Q)}\), and the omitted square-divisor tail by \(2\varphi(Q)\sqrt x/Q\). The two quadratic inequalities have the printed signs. |
| Peeling and true truncation intervals | Passed | Secants underestimate the largest residual frequency. Positive omitted tails give the displayed numerator/denominator interval bounds. Cancellation costs are separately identified. |
| Excluded-prime compact derivative instability | Passed | For a prime not already dividing \(Q\), the deleted shelf's exact mass is \(Z_Q(2a)/(p^{2a}+1)\), with all its frequencies at most \(\lambda_p\). |
| Hilbert feature space and character sectors | Passed | Absolute summability proves feature-map injectivity; the reproducing-kernel conjugation matches an inner product linear in the first argument. Fixed nonprincipal character sums are bounded by their modulus, giving the claimed sector exponent. |
| Exact multiprime positivity, including deletion endpoints | Passed | Every safe factor is nonnegative and infinitely many outside primes survive. At a bad strength, the prime's own node has negative mass unaffected by other strengths. |
| Explicit polynomial negative detector | Passed | \(L_p\) kills every lower integer node; its higher-node bound and \(\sum_{n>p}n^{-4}\le1/(3p^3)\) give the printed exact rational criterion and depth variant. |
| Conditional roots and margins | Passed | Both conditional moment matrices are strictly positive definite even at other deletion endpoints. The degree is exactly the Hankel order; roots are below \(-1\), with possible multiplicity. The detector produces the stated all-prime margin bound. |
| Additive versus multiplicative domains | Passed | Every prime subset is represented by a squarefree integer. The new separate PSD example has mass factors \(1,2,-1/25\); the earlier midpoint example is correctly confined to strict positive-definiteness. |
| Full polynomial-sequence separator | Passed | The final text supplies a local normalized-moment and isolated-residue argument. The mass-one zero atom fixes normalization; two changed prime atoms cannot be a one-prime deformation. |
| Mellin branch and summation interchange | Passed | The explicit dominant-term sector estimate provides a uniform angular gap. Its denominator estimate gives absolute integration of the complete zero sum in the original strip. |
| Unshifted continuation and exact abscissa | Passed | Taylor poles cancel at positive integers; the asymptotic pole at \(1/N\) has nonzero residue. Absolute convergence on the boundary would contradict that pole by dominated convergence. |
| Spectral trace zeros and origin normalization | Passed | The unsubtracted small-end integral is regular at nonpositive integers. The exponential-packet constant is \(-\log N\), giving the printed derivative. |
| Shifted spectral pole ladder and product | Passed | Rightward shifts reduce absolute argument. The two alternating signs in the residue cancel. Every secondary residue is nonzero for a positive shift, and the origin constant includes \(-\log E_{N,1}(a)\). |
| Polynomial normalization and rational clearing | Passed | Multiplying the ordinary recurrence by \((2n+1)!\) gives exactly the binomial EGF recurrence. Its weight degree is \(n\) and contraction degree at most \(n(n+1)\). |
| Analytic/formal phase boundary | Passed | Above unit scale a retained positive recurrence term forces superexponential coefficients. On the one-unit edge a linear ODE extends each disk, and the printed lower bound makes the entire order infinite. |
| Root filters, EGF taps, and finite polyphase carries | Passed | The integer residue projector, original factorials, zero-constant antiderivatives, binomial product, and nonnegative carry exponent agree with the definitions. |
| Invalid API residues and phase count | Passed after repair | The earlier fractional residue and zero-phase inputs were accepted. Both now raise `ValueError`, independently exercised after the fix; dedicated regression assertions are present. |
| Historical priority | Out of scope | Neither mathematical correctness nor failed searches establish novelty. The release explicitly leaves historical priority unresolved. |

### Checks of the author's particular proof choices

The author's fixed-width lower proof is simpler than independent derivation A. Its constants \(L=1/h\), \(C\ge qL/(1-q),rL/(1-r)\), and \(B=L+2/\min(q,r)\) make every propagated child at least two and make each translated child dominate its pure scaled translated parent. On the full seed \([2,B]\), the choice \(c_-=\log2/(B+C)^\rho\) is valid. Every later child is at most a fixed positive distance below its parent. This establishes the printed stronger bound for every \(R\ge2\), not merely an asymptotic subsequence.

The character sector proof's derivative integral is exactly bounded by
\(2a\beta^{-1}B(\gamma,2\Re s+1)+2|s|B(\gamma+1,2\Re s)\), with \(\gamma=(2a-1/2)/\beta\). The sector keeps \(|s|/\Re s\) bounded. Division by the principal diagonal is legitimate at sufficiently large radius because its uniform nonzero leading term has been proved. No growing-modulus or character-uniform-in-modulus conclusion is inferred.

For the shifted spectral proof, the normalized product is a ratio of the already convergent genus-zero products, so no exponential factor is missing. The algebraic infinity expansion has powers \(t^{1/N-k-1}\). At \(s=1/N-k\), the sign in the sine and the sign in the binomial coefficient cancel. The stated pole ladder consists entirely of nonintegers, which justifies the trace-zero argument. The determinant constant follows from the exact logarithmic asymptotic and agrees with the \(N=2\) anchor \(2\cosh\sqrt a\).

## Additional checked classical source leaves

All checked directly on 2026-10-08 UTC against official NIST DLMF version 1.2.8, release date 2026-09-15:

- https://dlmf.nist.gov/5.12, equations 5.12.1 and 5.12.3: beta integrals for arguments of positive real parts. With the project arguments \(1-s,s\), the strip is precisely \(0<\Re s<1\).
- https://dlmf.nist.gov/5.5, equation 5.5.3: gamma reflection, valid away from integer singular arguments, as required in that open Mellin strip.
- https://dlmf.nist.gov/5.11, equations 5.11.12--13: fixed-parameter gamma-ratio asymptotics in closed sectors separated from the negative axis. The project's closed right sectors satisfy these hypotheses and provide the required beta asymptotics.
- https://dlmf.nist.gov/25.6, equation 25.6.2: the even positive-integer zeta value in rational Bernoulli coordinates times a power of \(\pi\). The project ratio therefore has the stated rational \(\pi^{-2}\) coefficient field.
- https://dlmf.nist.gov/10.46, equation 10.46.3: the classical Mittag-Leffler seed with \(a=N,b=1,z=-w\), including the constant term and factorial normalization.

The other literature comparisons are attribution records rather than necessary unchecked proof arrows. No global novelty conclusion is supplied by this audit.

## Implementation findings, commands, and retained corrections

The reviewer read `family_lab.py` and the mathematical sequence chapter. The two invalid-input findings were independently reproduced before repair: `section([1,2,3],3,1.5)` returned an all-zero section, and `apply_polyphase_matrix([],[],0)` returned an empty output. After the author's repair, the same calls independently raised the intended `ValueError`. The final regression script contains `reject_fractional_residue` and `reject_zero_phase_base` and the passing evidence records 8,038 exact assertions. These repairs affected invalid inputs; the stated identities already had integer residues and a positive phase base as hypotheses.

An earlier chapter snapshot had transcribed two \((q,r)=(1,2)\) values incorrectly. The latest chapter and its correction record now agree with the API. Independently, the printed cubic polynomial gives
\(A_3(1,2)=8[48\cdot5\cdot17+80\cdot4]=35200\), and the recurrence gives \(A_4(1,2)=38041600\). Every five-term table anchor was recomputed against the API and agrees with the final text.

Read and pin commands used included `cat`, targeted `sed` and `rg`, and `sha256sum` on the proof files. Independent boundary checks imported the pinned API by `importlib.util` and exercised both bad inputs, the two-phase tap matrix, and all printed five-term coefficient anchors. The source checks used primary-page retrieval at the URLs listed above. No failed source retrieval occurred in this audit session.

The parent's separate bounded runner supplies full execution provenance for the release computations. This mathematical audit does not relabel approximate quadrature, determinant roots, or floating interval endpoints as exact arithmetic certificates.

## Final artifact pins

Paths are relative to the v1.0 release directory. Any subsequent content change invalidates that file's specific proof-as-written pin and requires comparison with this audit.

| File | SHA-256 |
|---|---|
| `new_results/dilation_type.md` | `4a438fa513b06cc729d8317c565bc2a45dc9da253964d3d9ce406a5ac6f97494` |
| `new_results/arithmetic_inverse.md` | `a8c29614a565231ac91e14c17312928ebdc40bcd5c1597e73b487f1f8b00cc81` |
| `new_results/multi_prime_sieve.md` | `5b5997c122e80bfad68cbb20698e704788e9ff6b82e72794418efde3a0df716e` |
| `new_results/spectral_continuation.md` | `d131b25e28921d79700a5b7a86e357e4f60623785c73a657664e0b7bd7c81d7b` |
| `new_results/sequence_polyphase.md` | `77186be00ffda9f1751432d869849d1388ec78a55bc5c4cbd97eeb0ebabd20c0` |
| `family_lab.py` | `7b546c1cd3159bb59634a3306c116719cd8d8d368c0046af90270c709b08cc8e` |
| `checks/family_lab_checks.py` | `d9e549133cf38cc285aa5f079c569eb381b9059c08263bee3ecb442a768cae56` |

## Remaining scope and cheapest next check

No missing implication remains in the audited v1.0 claims. A single dilation type limit, optimal signed-defect resolution degrees, broader variable-change nonreduction, residue-weighted spectral sums, and global historical priority remain outside the proved assertions. The cheapest release check is to compare these pins with the packaged files and compare the monograph's theorem statements with their source domains. Further finite computation is not needed to promote these informal proofs into their stated mathematical conclusions.
