# Komorebi Space Theory: infinite-depth residual reconstruction
## v0.8.0 · Komorebi P.

The finite retained-detail identity now has an infinite-depth theory. Three assertions are distinguished throughout:

\[
\boxed{\text{uniqueness from all details}\quad\neq\quad
\text{coordinatewise reconstruction}\quad\neq\quad
\text{reconstruction in the uniform norm}.}
\]

For the actual dyadic tower construction, the first two hold for every bounded residual. Uniform-norm reconstruction has separate necessary and sufficient conditions. Abstract split cascades can also carry a nonzero persistent coarse component. The statements below use the existing objects and maps, rather than replacing the tower residual by a scalar surrogate.

## 1. Split coarsening cascades and lifted remainders

Let \(\mathbb K\) be a nontrivially normed field. Let \(R_j\) be normed \(\mathbb K\)-spaces, with continuous linear maps
\[
C_j:R_j\to R_{j+1},\qquad J_j:R_{j+1}\to R_j,
\qquad C_jJ_j=I.
\]
For \(x\in R_0\), set
\[
x_0=x,\qquad x_{j+1}=C_jx_j,
\qquad h_j(x)=(I-J_jC_j)x_j,
\]
\[
L_0=I,\qquad L_{j+1}=L_jJ_j.
\]
The old finite identity is
\[
x=\sum_{j<N}L_jh_j(x)+L_Nx_N.
\]
Define continuous linear maps on the original space:
\[
\boxed{Q_Nx=L_Nx_N,\qquad S_Nx=x-Q_Nx.}
\tag{1}
\]
Thus \(Q_N\) is the **lifted** coarse remainder, not the raw coarse coordinate \(x_N\). Lean proves
\[
Q_N^2=Q_N,\qquad S_N^2=S_N,\qquad Q_NS_N=0,
\]
\[
\boxed{Q_mQ_n=Q_nQ_m=Q_n\quad(m\le n),}
\tag{2}
\]
\[
\boxed{L_nh_n(x)=Q_nx-Q_{n+1}x,\qquad
S_Nx=\sum_{n<N}L_nh_n(x).}
\tag{3}
\]
These are nested, not necessarily orthogonal, projections. No completeness is needed here.

**Lean:** `CoarseningCascade.levelMap`, `remainder`, `reconstructed`, `level_restore`, `remainder_idempotent`, `remainder_nested_left`, `remainder_nested_right`, `detailTerm_eq_remainder_sub`, `partial_eq_sum`.

## 2. What an infinite detail record may omit

Define the persistent coarse submodule
\[
\boxed{\mathcal P_\infty=\{x\in R_0:\forall N,\ Q_Nx=x\}.}
\tag{4}
\]
Lean proves
\[
\boxed{x\in\mathcal P_\infty\iff\forall n,\ h_n(x)=0,}
\tag{5}
\]
\[
\boxed{\bigl(\forall n,\ h_n(x)=h_n(y)\bigr)
\iff x-y\in\mathcal P_\infty.}
\tag{6}
\]
For (5), zero details make consecutive remainders equal by (3), and \(Q_0=I\). Conversely, a persistent input has every transported detail zero; the restoration maps are injective because coarse observation is their left inverse.

Therefore all details determine a general cascade input only modulo \(\mathcal P_\infty\). Its disappearance must be proved in a concrete model, not assumed from the word "resolution."

**Lean:** `persistent`, `persistent_iff_details_zero`, `equal_details_iff_persistent_difference`, `restore_injective`.

## 3. The exact criterion for norm reconstruction

The error identity is
\[
\boxed{\|x-S_Nx\|=\|Q_Nx\|.}
\tag{7}
\]
Consequently,
\[
\boxed{S_Nx\longrightarrow x\iff Q_Nx\longrightarrow0,}
\tag{8}
\]
where both limits are in the original norm of \(R_0\). Equivalently,
\[
\lim_{N\to\infty}\sum_{n<N}L_nh_n(x)=x
\iff \lim_{N\to\infty}L_Nx_N=0.
\]
Define the recoverable submodule
\[
\boxed{\mathcal D=\{x:Q_Nx\to0\}.}
\tag{9}
\]
Its linear-submodule structure is constructed. The formalization proves
\[
\mathcal D\cap\mathcal P_\infty=\{0\},
\]
and the detail record is injective on \(\mathcal D\).

These are statements about natural-order partial sums. They do not infer an unconditional `HasSum` statement from ordered convergence alone.

**Lean:** `partial_error`, `partial_tendsto_iff`, `ordered_reconstruction_iff`, `recoverable`, `persistent_recoverable_zero`, `details_injective_on_recoverable`.

## 4. A convergent boundary is necessarily persistent

If \(Q_Nx\to z\), continuity of \(Q_m\) and (2) give
\[
Q_mz=\lim_NQ_mQ_Nx=\lim_NQ_Nx=z.
\]
Hence
\[
\boxed{Q_Nx\to z\Longrightarrow z\in\mathcal P_\infty,
\qquad S_Nx\to x-z.}
\tag{10}
\]
Under completeness of \(R_0\), absolute summability of the transported details implies
\[
\sum_n\|L_nh_n(x)\|<\infty
\Longrightarrow
x-\sum_n L_nh_n(x)\in\mathcal P_\infty.
\tag{11}
\]
If also \(\mathcal P_\infty=0\), then
\[
\boxed{x=\sum_n L_nh_n(x).}
\tag{12}
\]
The last sum is supported by the absolute-summability theorem, not merely notation for an unproved infinite series.

**Lean:** `remainder_limit_persistent`, `reconstruction_with_boundary`, `absolutely_summable_boundary`, `tsum_reconstruction`.

## 5. A density characterization, rather than a circular hypothesis

Define the finite-core set
\[
\boxed{\mathcal F=\bigcup_{N\ge0}\ker Q_N.}
\tag{13}
\]
These are inputs eliminated by some finite coarse depth. Nesting implies they remain eliminated at every greater depth. Each finite reconstructed approximant satisfies
\[
S_Nx\in\mathcal F.
\]
It follows without a uniform operator bound that
\[
\mathcal D\subseteq\overline{\mathcal F}.
\]
Assume additionally
\[
\boxed{\sup_N\|Q_N\|\le K<\infty.}
\tag{14}
\]
Lean proves the converse, and therefore
\[
\boxed{\mathcal D=\overline{\mathcal F}.}
\tag{15}
\]
In particular,
\[
\boxed{\forall x,\ S_Nx\to x
\iff\overline{\mathcal F}=R_0}
\tag{16}
\]
under (14).

For the nontrivial implication, approximate \(x\) by \(y\in\ker Q_M\). For \(N\ge M\),
\[
\|Q_Nx\|=\|Q_N(x-y)\|\le K\|x-y\|.
\]
This proves convergence by choosing the approximation before choosing the depth. No density or uniform bound is inferred automatically from the existence of sections.

**Lean:** `finiteCore`, `finiteCore_recoverable`, `partial_mem_finiteCore`, `recoverable_mem_closure_finiteCore`, `recoverable_iff_closure_finiteCore`, `all_recoverable_iff_dense`, `ordered_reconstruction_of_dense`.

## 6. Quantitative decay must include restoration gain

Define
\[
\boxed{G_N=\prod_{j<N}\|J_j\|.}
\tag{17}
\]
The checked estimate is
\[
\boxed{\|x-S_Nx\|\le G_N\|x_N\|.}
\tag{18}
\]
Therefore
\[
G_N\|x_N\|\to0\Longrightarrow x\in\mathcal D.
\]
For nonnegative constants \(B,C,a,b\), if
\[
G_N\le Ba^N,\qquad\|x_N\|\le Cb^N,\qquad ab<1,
\]
then
\[
\boxed{\|x-S_Nx\|\le BC(ab)^N\longrightarrow0.}
\tag{19}
\]
Contractive lifts give \(G_N\le1\), in which case raw coarse decay suffices. Without that control it need not suffice.

**Lean:** `liftGain`, `restore_gain_bound`, `reconstruction_error_bound`, `recoverable_of_weighted_coarse_decay`, `recoverable_of_geometric_bounds`, `recoverable_of_coarse_decay`.

## 7. The actual dyadic residual hierarchy has no persistent component

Now specialize to the existing `DyadicResidual.System`, with its actual sequential Banach towers, contractive bonds, supplied bounded target sections, transported coarsener, and parity lift:
\[
(Cr)_n=\rho^Y_{2n}r_{2n+1}+r_{2n}\rho^X_{2n+1},
\]
\[
(Jc)_{2n}=0,\qquad(Jc)_{2n+1}=s_{2n}c_n.
\]
All coarsening levels are the previously constructed actual dyadic systems. They are not arbitrary copies of a scalar example.

Lean proves
\[
\boxed{\mathcal P_\infty=0}
\tag{20}
\]
for every such system, without a convergence hypothesis.

The proof uses strong induction on the coordinate index, uniformly over the scale. Zero hidden detail reveals every even coordinate directly. An odd coordinate reduces to a coordinate at the next scale with index \(\lfloor k/2\rfloor<k\). Every fixed coordinate is therefore forced to zero.

Consequences:
\[
\boxed{\forall j,\ h_j(r)=h_j(s)\Longrightarrow r=s,}
\tag{21}
\]
\[
\boxed{\operatorname{Exact}(f)
\iff\forall j,\ h_j(df)=0.}
\tag{22}
\]
Here \(d\) and `Exact` are the existing compatibility differential and predicate. This does not define exactness in a new way.

**Lean:** `DyadicResidual.System.all_details_zero_implies_zero`, `persistent_residual_eq_bot`, `infinite_details_injective`, `exactness_iff_all_details`.

## 8. Every coordinate is reconstructed at finite depth

There is a stronger actual-dyadic support statement:
\[
\boxed{k+1<2^N\Longrightarrow (Q_Nr)_k=0.}
\tag{23}
\]
Thus
\[
\boxed{k+1<2^N\Longrightarrow (S_Nr)_k=r_k.}
\tag{24}
\]
In particular, for every bounded residual \(r\) and every fixed coordinate \(k\),
\[
\boxed{(S_Nr)_k\longrightarrow r_k.}
\tag{25}
\]
The equality is eventually exact, not just an approximation. Convergence here is in the operator norm at the fixed coordinate. No uniform bound over all \(k\) follows from this statement.

The finite threshold is strict. For the identity-tower pair sum, a remainder can be nonzero at the last coordinate \(k=2^N-1\) of a block.

**Lean:** `finite_details_zero_coordinate`, `remainder_coordinate_zero`, `reconstruction_coordinate`, `coordinatewise_reconstruction`. Typed wrappers `residualLevel`, `reconstructedResidual`, and `residualRemainder` expose the actual dependent operator types.

## 9. Sufficient norm-reconstruction conditions on the actual towers

The original residual space is complete by the existing bounded-product and continuous-linear-map instances. Since (20) was proved, absolute summability is sufficient:
\[
\boxed{\sum_j\|L_jh_j(r)\|<\infty
\Longrightarrow r=\sum_jL_jh_j(r).}
\tag{26}
\]
Any norm-convergent sequence \(Q_Nr\) must converge to zero. This does not prove that it converges.

If the supplied target-section bound is at most one, that bound remains at most one under every actual dyadic section composition. Thus all cascade lifts are contractive and
\[
\boxed{\|r-S_Nr\|\le\|r_N\|.}
\tag{27}
\]
Consequently \(\|r_N\|\to0\) gives norm reconstruction in this case.

**Lean:** `cascade_zero_complete`, `absolute_residual_reconstruction`, `convergent_remainder_zero`, `stage_section_bound_le_one`, `cascade_lifts_contractive`, `residual_error_le_coarse`, `residual_reconstruction_of_coarse_decay`.

The theorem does not assert that all bounded residuals satisfy these analytic hypotheses. Nor does it identify arbitrary sequences of detail values with the image of the full detail map.

## 10. A fully specified recovery domain: bounded sequences

As a separate model, take \(R_j=\ell^\infty(\mathbb N,\mathbb R)\) at every scale and
\[
(Cx)_k=x_{k+1},\qquad Jx=(0,x_0,x_1,\ldots).
\]
Then \(CJ=I\), and Lean proves
\[
(Q_Nx)_k=\begin{cases}0&k<N,\\x_k&k\ge N.\end{cases}
\tag{28}
\]
The exact characterization is
\[
\boxed{x\in\mathcal D\iff x_k\to0.}
\tag{29}
\]
Thus \(\mathcal D=c_0\) inside the bounded-sequence space, in the ordinary meaning of sequences tending to zero. This is a theorem relating the actual remainder to coordinate decay, not the definition of recoverability.

Here
\[
\|Q_N\|\le1,\qquad\mathcal P_\infty=0,
\]
but for \(\mathbf1=(1,1,\ldots)\),
\[
\boxed{\|Q_N\mathbf1\|=1\quad\text{for all }N.}
\tag{30}
\]
Therefore uniform boundedness plus a trivial persistent submodule does not imply norm reconstruction for every input. Density is a separate obligation.

For \(x_k=q^k\), \(0\le q<1\), the package constructs the actual bounded sequence and proves
\[
\boxed{\|x-S_Nx\|=q^N.}
\tag{31}
\]
This provides an all-depth positive reconstruction example with an exact error rate.

**Lean:** `SequenceCascade.recoverable_iff_vanishes`, `persistent_eq_bot`, `ones_remainder_norm`, `stability_and_separation_not_enough`, `geometric_recoverable`, `geometric_reconstruction_error`.

## 11. A coarse-decay counterexample with a persistent boundary

Take \(R_j=\mathbb R\), \(C_j=\tfrac12I\), \(J_j=2I\). Then
\[
C_jJ_j=I,\qquad x_N=2^{-N}x,\qquad L_N=2^NI,
\]
so
\[
\boxed{x_N\to0,\qquad Q_Nx=x,\qquad h_j(x)=0.}
\tag{32}
\]
For \(x=1\), raw coarse data tend to zero and the transported details are absolutely summable because they are all zero, yet reconstruction from those details gives zero, not one. The entire input is persistent coarse information.

This is a counterexample in the explicitly constructed scalar split cascade, not a claim that the actual dyadic hierarchy has a nonzero persistent subspace. The latter is ruled out by (20).

**Lean:** `CascadeBoundaryExamples.coarse_tends_zero`, `remainder_identity`, `every_detail_zero`, `coarse_decay_and_summability_not_enough`.

## 12. Verification and boundaries

The release adds six proof modules: `CascadeProjections`, `CascadeLimits`, `CascadeDensity`, `SequenceCascade`, `CascadeBoundaryExamples`, and `DyadicInfiniteReconstruction`. They add 97 named theorems and 23 indexed non-theorem declarations. The cumulative project has 56 modules, 656 named theorems, and 271 indexed constructions. Counts include auxiliary declarations, not discoveries.

The complete clean build and complete theorem and construction axiom audits passed. Original v0.7 proof modules remain byte-identical. The delivery receipt separately records fresh-extraction replay and source/compiled hash comparisons.

The independent exact-rational computation covers 36 variable-dimension finite cascades, 48 dyadic configurations, and 230 sequence/scalar cases, with 8,778 explicit assertions. Three deliberately false variants are rejected. It compares recursive dyadic remainders with independent block-sum formulas, checks nested projections, reconstruction and gain bounds, and tests the strict finite-coordinate threshold. Finite checks do not establish infinite convergence; the universal statements above have Lean proof terms.

Not proved: universal sup-norm recovery of all dyadic bounded residuals, unconditional summability without an absolute-summability hypothesis, uniform norm bounds on every hierarchy, orthogonality, a basis/Riesz-basis theorem, surjectivity onto arbitrary infinite detail sequences, arbitrary-block lossless coordinates, grouping-independent conditioning, full pro-category comparison, stacks, higher obstruction theory, unrestricted arithmetic correspondence, data compression or computational complexity. No novelty claim is made relative to the literature.
