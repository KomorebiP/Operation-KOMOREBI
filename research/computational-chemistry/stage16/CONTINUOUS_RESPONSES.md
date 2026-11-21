# Response certificates across continuous energy intervals

An energy scan needs a bound between its sampled energies as well as at them. The Stage 15 response disks can be extended over whole energy cells without another Hamiltonian action. The extension uses the imaginary response at the endpoints to control the curvature of the resolvent response.

For the existing H10-derived finite target, the 128-action scan at broadening 0.1 Hartree gives a continuous radius below 0.007565 per Hartree over the whole interval. The full and nine-state imaginary responses differ by more than 0.02365 per Hartree at every energy in that interval. These are conditional finite-model certificates: the endpoint disks retain their stated binary64 arithmetic assumptions, and the supplied approximate neutral source and reference remain fixed inputs.

## The interpolation theorem

Let H be a finite Hermitian matrix, b a fixed complex vector, eta>0, and

    R(E) = ((E+i eta)I-H)^(-1),     g(E) = b* R(E) b,
    S(E) = -Im g(E).

Here * denotes conjugate transpose. Fix real a<c, put h=c-a and E=a+t h for 0<=t<=1. Suppose endpoint disks are known:

    |g(a)-c0| <= r0,      |g(c)-c1| <= r1.

The centers c0,c1 are complex and the radii r0,r1 are nonnegative. Define nonnegative upper bounds

    U0 = -Im(c0)+r0,       U1 = -Im(c1)+r1.

If either upper bound is negative, the purported endpoint certificate contradicts S>=0. Then for every t in [0,1],

    |g(a+t h)-[(1-t)c0+t c1]|
      <= (1-t)r0+t r1 + t(1-t) C,
    C = (h^2/eta^2) sqrt(U0 U1).                              (1)

Any rational upper enclosure of C can replace C. In particular, a radius valid uniformly throughout the cell is

    R_cell = max(r0,r1) + C/4.                                (2)

No requirement h<eta is needed. A coarse cell can yield a large bound, particularly at small broadening.

## Proof

All three resolvents are functions of the same Hermitian matrix and commute. Multiplication by their commuting inverse factors gives the exact operator identity

    R(a+t h)-[(1-t)R(a)+t R(c)]
      = -t(1-t) h^2 R(a) R(a+t h) R(c).                        (3)

The sign in (3) follows from (E-a)(E-c)=-t(1-t)h^2. The endpoint cases t=0 and t=1 give zero on both sides.

In a unitary eigenbasis of H, write lambda_j for the real eigenvalues and w_j>=0 for the squared source components. Then

    S(E) = eta sum_j w_j / ((E-lambda_j)^2+eta^2),
    ||R(E)b||^2 = S(E)/eta,       ||R(E)|| <= 1/eta.

The same source norm identity holds for R(E)*b. Cauchy-Schwarz therefore gives

    |b* R(a) R(E) R(c) b|
      <= ||R(a)*b|| ||R(E)|| ||R(c)b||
      <= sqrt(S(a)S(c))/eta^2
      <= sqrt(U0 U1)/eta^2.

Apply this inequality to (3), then add the endpoint-center errors by the triangle inequality. This proves (1). The inequalities (1-t)r0+t r1<=max(r0,r1) and t(1-t)<=1/4 prove (2). The zero-source case is included: g and S vanish identically.

Hermiticity is essential. A finite exact counterexample uses H=[[0,100],[0,0]], b=(1,1), eta=1, a=0, c=1/100 and t=1/2. Its endpoint strengths are positive, yet the Hermitian bound (1) fails. A non-Hermitian effective Hamiltonian requires a different resolvent estimate.

## A continuous comparison of two models

Apply (1) separately to the full and reduced models. Their sources and dimensions may differ, but each model must keep its own fixed operator and source across the cell. Let D_i=-Im(c_full,i)+Im(c_reduced,i) and q_i=r_full,i+r_reduced,i. If C_full and C_reduced are the two interpolation coefficients, then throughout the cell

    min(D0-q0,D1-q1) - (C_full+C_reduced)/4
      <= S_full(E)-S_reduced(E)
      <= max(D0+q0,D1+q1) + (C_full+C_reduced)/4.                (4)

A strictly positive lower endpoint in (4), or strictly negative upper endpoint, proves disagreement at every energy in that cell. The minimum absolute separation over a tiled interval is a lower bound for the whole interval. This is stronger than observing disjoint disks at isolated samples.

`interval_certificate.py` evaluates (1), (2) and (4) with Fraction arithmetic. Square roots are enclosed upward by rational multiples of 10^-30, with exact rational squares retained exactly. Public display data can be rounded outward again; short decimal labels and plots are approximate.

## Results from the existing endpoint data

The unchanged Stage 15 public fixture supplies 21 Krylov curves: seven action budgets at three broadenings. Each has 40 energy cells. Propagating those endpoint disks gives 840 continuous-cell certificates and requires zero new Hamiltonian actions.

At eta=0.1, the 128-action curve has maximum continuous radius below 0.007565 per Hartree. Equation (4) gives a whole-interval discrepancy greater than 0.02365 per Hartree. At eta=0.5, the 32-action curve has maximum continuous radius below 0.00009506 per Hartree and discrepancy greater than 0.4450 per Hartree. The interval is E0+[0.30,0.70] Hartree, equivalently removal coordinate omega in [-0.70,-0.30] Hartree.

The endpoint radius below 4e-9 at eta=0.1 remains an endpoint result. It is not relabeled as a continuous radius. The additional interpolation term accounts for the space between samples.

## The narrower broadening

The successful bounded run constructs 512 polynomial Krylov actions at eta=0.01. In the same blocked implementation, the 256-column prefix has maximum radius about 0.4992 per Hartree at the original 41 energy samples. The 512-column prefix reduces that maximum below 1.74e-6 per Hartree.

The continuous radius on the initial mesh is still about 2.444 per Hartree. Adaptive energy refinement changes the node counts from 41 to 81, 148 and finally 166. On the final 165 cells the maximum continuous radius is below 0.09735 per Hartree, meeting the declared absolute budget of 0.1 per Hartree. The 125 additional energy evaluations use the existing cache and require zero new Hamiltonian actions. This tolerance is an illustrative finite-model response budget, not a universal chemical-accuracy criterion.

Preparing the cache metadata once makes that refinement a separate postprocessing task. The recorded run took about 293.9 seconds, of which about 7.3 seconds evaluated the additional energy nodes. These measurements describe this Windows NumPy run and implementation; they do not establish superiority over an optimized solver.

## Prepared caches and bounded action buffers

`cached_response.py` retains the Stage 15 endpoint error formula while preparing Q^TQ, the projected operator, and the norm/error metadata once. A source-independent claim is not made: the Krylov basis is built from the fixed supplied source. Refining the energy grid evaluates the same prepared cache and performs no additional Hamiltonian actions.

The initial 512-column run failed when NumPy could not allocate a 40.4 MiB contraction buffer. File-backed basis storage alone did not remove that buffer requirement. The revised action uses determinant blocks of at most 4096 entries. Its two principal contraction buffers each contain at most 100*4096 binary64 values for the ten-orbital target. Basis and image arrays use column-major file-backed storage, reopened read-only after construction. Their hashes are observed before and after evaluation. Large intermediate arrays are not retained as published evidence; the input arrays, source code, output disks and execution manifests permit a fresh calculation.

The blocked action applies the same spin-free expression as Stage 15. Each E_pq is a sum of two signed partial permutations. Constructing its stack component uses at most two signed source terms. Each G contraction still has length n^2, and the one-body contraction has the same length. The final output component receives at most two additions per orbital pair, independent of determinant-block order, because each spin map is injective and the source blocks are disjoint.

Consequently the Stage 15 gamma-count normwise action cap remains valid under the same binary64 primitive-operation model. Concatenating the contraction-block error matrices gives the same Frobenius bound; no missing factor proportional to the number of blocks is introduced. The summation order can change observed rounding and timing. This phase does not claim bit-identical actions or a speed advantage over the previous implementation.

Independent exact fermion-ladder columns test the blocked action on small models and nine full-target determinant columns. Exact rational response references test both copied and read-only mapped caches. These finite checks support the implementation; the analytic arguments establish the general interval implication and explain reuse of the arithmetic cap.

## Replay and scope

From the extracted package root, the identity verifier requires only Python:

```text
python -B research/computational-chemistry/stage16/verify_stage16.py
```

For fresh calculations, the recorded environment used Python 3.12.14, NumPy 2.3.5 and SymPy 1.14.0. Request one thread with OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and MKL_NUM_THREADS=1, then choose fresh output directories:

```text
python -B research/computational-chemistry/stage16/audit_interval.py --output fresh-interval-audit
python -B research/computational-chemistry/stage16/audit_interval_data.py --output fresh-existing-intervals
python -B research/computational-chemistry/stage16/continuous_study.py --order 512 --max-nodes 2049 --tolerance 1/10 --output fresh-narrow-scan
```

The large calculation uses about 434 MB of temporary file-backed basis/image storage, plus bounded working buffers. The recorded provenance runner imposed a 900-second wall-clock cap on that calculation and conventional one-thread environment settings. It imposed no Windows OS memory cap. Manual commands above do not themselves impose the runner's time limit. The identity verifier checks saved bytes and source ancestry; it does not rerun the large calculation or prove the analytic statements.

The active execution manifests under `verification/chemistry-stage16` identify the exact code and data revisions. Failed attempts are retained with input snapshots and are excluded from active mathematical evidence. A memory-allocation failure is a resource outcome, not evidence against convergence or the interpolation theorem.

The same finite target, source ordering, exact symmetry completion, electronic energy convention and approximate reference coordinate from Stage 15 are retained. Physical source error, ground-reference accuracy, basis error and experimental prediction remain separate obligations. This work makes no novelty claim or comparison with an optimized rational or block solver. The proof review is project self-review, without independent expert or proof-assistant verification.
