# Certified responses from reusable Hamiltonian actions

A Hamiltonian action cache can serve a whole energy scan. The practical question is whether the resulting error bound is small enough for the response being studied. This study compares a nine-determinant occupation space with a source-adapted polynomial Krylov space on the same declared 52,920-state H10-derived finite operator. Both reuse their cache at every sampled energy. This extends the earlier recovery laboratory and the predecessor checkpoint's matrix-free response work; it does not change the three-query theorem.

## Target and conventions

The selected arrays in `inputs/h10_view.npz` preserve the original fixture bits. `inputs/INPUT_VIEW.json` binds the original container, selected container and individual arrays by SHA-256. Increasing integer determinant masks index each spin sector, with alpha determinants as rows and beta determinants as columns. The supplied ion source has sector (4,5). Transposing its CI array implements spin-block exchange into sector (5,4), with sign (-1)^(4*5)=+1.

The exact target uses h=(h_raw+h_raw^T)/2 and the analogous symmetric average of the pair-packed ERI array. Pair indices are unordered within each orbital pair. These exact dyadic coefficients define a real symmetric electronic Hamiltonian, without the nuclear constant. This symmetry-completed target need not be bit-identical to the predecessor's unsymmetrized contraction. The nine-state retained block agrees with all 81 exact entries of the sealed Stage 14 reference.

The real source b is the supplied local-removal vector, treated as exact bits. Its construction from the supplied approximate neutral state is independently checked to floating precision. That check establishes the determinant convention; it does not certify the neutral state against an exact ground state. The supplied approximate ground energy E0 defines coordinates only. Targets are E=E0+s, s=0.30,...,0.70 Hartree in steps of 0.01, with eta in {0.01,0.1,0.5} Hartree. The removal coordinate is omega=-s. The response is g(z)=b^T(zI-H)^(-1)b, z=E+i eta, and the displayed response strength is -Im(g), in inverse Hartree. Division by pi gives the source-resolved broadened density, not the total density of states.

## An error identity that permits an inexact solve

Let H be any finite real symmetric matrix, b real, eta>0, and x any complex approximate solution. Set R=(zI-H)^(-1) and r=b-(zI-H)x. Since R^T=R and Rb=x+Rr,

    g(z) - b^T x = (Rb)^T r = x^T r + r^T R r.

The spectral theorem gives ||R||_2 <= 1/eta. Complex Cauchy-Schwarz, applied to the bilinear expression through absolute values, gives

    |g(z)-b^T x| <= |x^T r| + ||r||_2^2 / eta.                 (1)

Transpose, rather than conjugate transpose, in the defect is essential. For an exact Galerkin solution in a real trial space, x^T r=0. It cannot be discarded for an arbitrary floating solve. With H=0, b=1, z=i and x=-1.1i, the response error is 0.1 while ||r||^2/eta=0.01. The finite audit checks this counterexample exactly.

## Exact retained and discarded residuals

Let J embed the nine determinant coordinates, P=JJ^T, A=J^THJ, B=(I-P)HJ, u=J^Tb and w=(I-P)b. For x=Jv,

    r_P = u-(zI-A)v,       r_Q = w+Bv,
    ||r_Q||^2 = ||w||^2 + 2 Re(v)^T B^T w + v* (B^T B) v.

Nine exact full-target columns determine A, B^TB and B^Tw. Thus every term of (1) can be computed with rational arithmetic for any observed binary64 v. The reported center may have a rounded dot product; add |u^Tv-center| to the radius. Omitting r_Q gives a separate numerical enclosure for the reduced response u^T(zI-A)^(-1)u. A small reduced radius alone says nothing about the full-target approximation.

The source norm, projection weights and discarded Gram entries are exact dyadic rationals. Square-root upper bounds are rational multiples of 10^-30, with rational exact squares retained exactly. Source capture is about 37.506% in the nine-state space. Enlarging only the active orbitals while keeping three doubly occupied core orbitals is one tested hierarchy, not a general approximation theorem. A large upper error bound fails to certify accuracy; it does not by itself prove a large actual error.

## Binary64 action enclosure

The matrix-free NumPy implementation uses E_pq=sum_spin a†_p a_q and

    H = sum_pq h_eff[pq] E_pq + (1/2) sum_pqrs g[pqrs] E_pq E_rs,
    h_eff[ps] = h[ps] - (1/2) sum_q g[pqqs].

Each E_pq is the sum of two signed partial permutations, so ||E_pq||<=2. Stacking m=n^2 such maps has norm at most L=2n. All bounds below are per unit input norm. Let gamma_j=ju/(1-ju), u=2^-53, F_h and F_G be Frobenius upper bounds for the converted h_eff and G coefficient arrays, and delta_h, delta_G their exact coefficient-conversion error bounds. The code implements the following conservative recurrences:

    eT = L gamma_2,                 T = L(1+gamma_2),
    eW = delta_G L + F_G eT + gamma_(2m) F_G T,
    W  = (1+gamma_(2m)) F_G T,
    eS = L eW + gamma_(2m+2) L W,
    S  = (1+gamma_(2m+2)) L W,
    eA = delta_h L + F_h eT + gamma_(2m) F_h T,
    A  = (1+gamma_(2m)) F_h T,
    xi = eA + eS/2 + gamma_2 (A+S/2).

Here T denotes the norm bound for the stack E_pq v, W the G contraction, S the final E accumulation, and A the one-body contraction. Frobenius norms bound each coefficient contraction, and the same L controls the absolute signed-permutation accumulation. Coefficient conversion errors are computed exactly before outward square roots. The resulting full-target action bound is about 3.202e-11 times the input norm.

These inequalities assume the usual correctly rounded binary64 multiply/add or fused multiply-add dot-product model. This is an explicit arithmetic assumption about the NumPy/BLAS implementation, not a formal verification of the processor or library. Coefficient and input magnitude guards, together with dyadic denominator-exponent guards, exclude overflow and subnormal underflow for the bounded workload. Nonzero intermediates lie on the corresponding dyadic lattice; rounded additions and products cannot introduce a finer lattice. The small-model audit compares the action to an independent exact fermion-ladder construction, including dense observed trial columns. Nine full-target determinant columns are also compared coordinate by coordinate with exact sparse columns.

An independent operator-norm bound is N max_p sum_q |h_pq| + C(N,2) max_(p,r) sum_(q,s) |g_pqrs|. The ordered-pair two-electron operator is real symmetric, so its maximum absolute row sum bounds its spectral norm. Restriction to the antisymmetric N-electron space does not increase the first-quantized sum bound. For this target the result is below 74.766 Hartree.

## Response enclosure from observed caches

Let Q contain the observed real trial columns and Y their cached actions, with ||HQ_j-Y_j||<=xi_j. The projected solve produces any observed complex coefficient vector a; no exact orthogonality or exact solve is required. The implementation forms x_hat=fl(Qa), y_hat=fl(Ya), r_hat=fl(b-z_float x_hat+y_hat), c=fl(b^T x_hat), and d=fl(x_hat^T r_hat).

Let eX and eY bound the two matrix-vector rounding errors. Componentwise dot-product bounds followed by Frobenius norms give

    eX = gamma_(2k) ||Q||_F (||Re a||+||Im a||),
    eY = gamma_(2k) ||Y||_F (||Re a||+||Im a||).

The exact action discrepancy is bounded by

    ||H x_hat-y_hat|| <= ||H|| eX + sum_j xi_j |a_j| + eY.

Add the complex multiplication, residual additions and exact-target versus z_float discrepancy to obtain e_r >= ||r-r_hat|| for r=b-(zI-H)x_hat. `float_certificate.py` records each term; its conservative complex product and addition factors are 2 gamma_3 and 2 gamma_2 respectively. Norms are enclosed using the observed sum of squares divided by 1-gamma_(2d+2), then an outward rational square root. Actual denominator exponents and magnitudes guard all these norm and dot operations.

Dot rounding is bounded by e_d=4 gamma_(8D)||x_hat||||r_hat|| and e_c=2 gamma_(2D)||b||||x_hat||, where D is the target dimension. Applying (1) and triangle inequalities gives the reported rational upper radius

    |g(z)-c| <= |d| + e_d + ||x_hat|| e_r
                + (||r_hat||+e_r)^2 / eta + e_c.               (2)

Every displayed decimal is approximate; the downloadable certificate retains the rational radius. The arithmetic assumptions apply to (2). The exact-column certificate in the preceding section instead evaluates its residual terms with rational arithmetic.

## Matched workloads and interpretation

The occupation space uses nine full-target actions on determinant unit vectors. Polynomial Krylov uses b as its starting vector and two full reorthogonalization passes per new vector. Tested prefix sizes are 3, 9, 16, 32, 64, 128 and 256. Both retain Q and Y and reuse them over all 123 energy/broadening pairs, with zero new H actions per energy. Timings separate shared coefficient setup, H actions, orthogonalization and postprocessing. The latter includes the projected solve and certificate calculation. This implementation is a NumPy polynomial Krylov comparison, not an optimized rational, block or PySCF benchmark.

At eta=0.1 Hartree, the 128-action cache gives a maximum response radius below 4e-9 over the 41 sampled energies. Eta=0.01 remains harder: even 256 actions leave some broad enclosures. Increased prefix size can increase the rounding floor; no monotonic accuracy claim is made. These are pointwise certificates at the sampled energies. Lines between centers in the plot are visual interpolation.

One can also certify a discrepancy between the declared full and reduced responses. If their centers and radii are c_f,R_f and c_r,R_r, respectively, then

    |Im(g_f)-Im(g_r)| >= max(0, |Im(c_f)-Im(c_r)|-R_f-R_r).

A positive lower bound proves disagreement for those fixed finite-model responses at that sample. At eta=0.1, the 128-action result gives positive lower bounds at all 41 samples, reaching more than 2.65 inverse Hartree at one sample. It does not measure an experimental error. The public data generator evaluates this inequality exactly with Fraction arithmetic.

Three actions in the original theorem recover the declared nine-state family. The nine full-target columns used here contain additional information about coupling to omitted determinants. Recovering that information is not covered by the three reduced queries. Neither action counts nor this single-machine timing sample establish a universal speed advantage.

## Replay and evidence

Run from the repository root with Python 3.12.14, NumPy 2.3.5 and SymPy 1.14.0:

```text
python -B research/computational-chemistry/stage15/audit_reduction.py --output fresh-reduction
python -B research/computational-chemistry/stage15/audit_fp.py --output fresh-kernel
python -B research/computational-chemistry/stage15/response_study.py --maximum-order 256 --output fresh-responses
```

Set OPENBLAS_NUM_THREADS, OMP_NUM_THREADS and MKL_NUM_THREADS to 1 for the recorded timing convention. The three v2 execution manifests under `verification/chemistry-stage15` pin all listed code and input artifacts before and after execution, record finite ranges, actual software versions and output hashes, and enforce a 600-second per-run timeout. Thread counts are requested through conventional environment variables. Array sizes are fixed; Windows OS memory limits were not imposed. The full dense 52,920-square matrix is never formed. Finite checks support the implementation; they do not prove the general inequalities. `SELF_REVIEW.json` records the author's analytic audit and remaining scope obligations, without implying independent review or proof-assistant verification.

## Sources and existing methods

The determinant convention is checked against [PySCF v2.15.0 cistring.py, make_strings](https://github.com/pyscf/pyscf/blob/v2.15.0/pyscf/fci/cistring.py#L25-L65) and the supplied fixture generator. Its ascending orbital-list example gives increasing integer masks. The annihilation reconstruction supplies a separate numerical convention check.

Lanczos response approximation and error bounds have an established literature. [Chen, Greenbaum, Musco and Musco, Error bounds for Lanczos-based matrix function approximation, arXiv v2, 18 May 2022](https://arxiv.org/abs/2106.09806v2), [published DOI 10.1137/21M1427784](https://doi.org/10.1137/21M1427784), discusses Hermitian matrix functions, quadratic forms and finite-precision extensions. This is contextual attribution based on the authenticated abstract, not a claim that its theorem is identical to (2). Equations (1) and (2) are derived above from finite real symmetry and the stated arithmetic model. No novelty claim is made. The predecessor checkpoint already discussed quadratic Galerkin residual identities and reusable Krylov responses.

Physical obligations remain separate: certify the neutral source/reference if required, assess basis-set and Hamiltonian-model errors, compare against an optimized solver on meaningful workloads, and validate any eventual chemical interpretation against a specified physical target.
