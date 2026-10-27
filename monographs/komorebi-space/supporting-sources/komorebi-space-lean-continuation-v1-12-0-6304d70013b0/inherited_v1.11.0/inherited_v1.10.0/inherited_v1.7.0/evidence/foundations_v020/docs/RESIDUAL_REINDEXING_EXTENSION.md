# Komorebi Space Theory: controlled residual reindexing
## v0.6.0 · Komorebi P.

This extension constructs a bounded change of residual coordinates for common-schedule resampling of contractive sequential Banach towers. It distinguishes preservation of exactness from detection of exactness, quantifies the dependence on the length of skipped blocks, and compares the two orders of resampling and repair.

**Scope:** fixed source and target towers, actual bonding operators, a common monotone schedule, contractive bonds, and a finite gap bound for the quantitative operator. The previous exact eventual category remains unchanged. No quotient of arbitrary nonexact premorphisms is constructed.

## 1. Towers and the actual differential

Fix a nontrivially normed field \(\mathbb K\). Let
\[
 X_{n+1}\xrightarrow{\rho^X_n}X_n,
 \qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n
\]
be the existing sequential Banach towers. Write
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),
 \qquad R=\ell^\infty_n\mathcal L(X_{n+1},Y_n),
\]
\[
 \boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\]
For the new norm estimates assume
\[
 \boxed{\|\rho^X_n\|\le1,\qquad\|\rho^Y_n\|\le1\quad(\forall n).}
\]
These hypotheses are explicit. The general uniformly bounded tower definitions from previous releases are not silently changed.

## 2. Finite-block restriction and defect

For \(i\le j\), construct
\[
 \rho^X_{i,j}:X_j\to X_i,
 \quad \rho^X_{i,i}=I,
 \quad \rho^X_{i,j+1}=\rho^X_{i,j}\rho^X_j.
\]
The analogous target maps satisfy the same equations. Lean verifies
\[
 \rho_{i,j}\rho_{j,k}=\rho_{i,k},
 \qquad\|\rho_{i,j}\|\le1.
\]
It also verifies agreement with the actual all-pairs functions used in the earlier finite-stage category.

Define the block defect
\[
 \boxed{D_{i,j}(f)=\rho^Y_{i,j}f_j-f_i\rho^X_{i,j}.}
\]
Its exact concatenation law is
\[
 \boxed{D_{i,k}(f)=\rho^Y_{i,j}D_{j,k}(f)+D_{i,j}(f)\rho^X_{j,k}.}
\]
The terms are transported into the same Hom space. Adding arbitrary untransported defects would not even be well typed for varying dimensions.

**Lean:** `BanachTower.restriction`, `restriction_trans`, `restriction_underlying`, `restriction_contractive`, `blockDefect_concat`.

## 3. Accumulation of arbitrary residuals

For any adjacent residual family \(r_n:X_{n+1}\to Y_n\), define recursively
\[
 B_{i,i}(r)=0,
\]
\[
 \boxed{B_{i,j+1}(r)=\rho^Y_{i,j}r_j+B_{i,j}(r)\rho^X_j.}
\]
This transported recursion is the formal definition of the block sum. It is linear in \(r\). For an actual candidate residual, Lean proves the telescope
\[
 \boxed{B_{i,j}(df)=D_{i,j}(f).}
\]
The local and uniform bounds are
\[
 \boxed{\|B_{i,j}(r)\|\le\sum_{k=i}^{j-1}\|r_k\|,}
\]
\[
 \boxed{\|B_{i,j}(r)\|\le(j-i)\|r\|_\infty\quad(r\in R).}
\]
These inequalities discard cancellation only when taking norms. The block sum itself retains signs, operator order, and cancellation.

**Lean:** `blockSum`, `blockSum_succ`, `blockSum_differential`, `blockSum_add`, `blockSum_smul`, `blockSum_norm`, `blockSum_uniform_bound`.

## 4. The resampled tower and candidate map

Let \(\phi:\mathbb N\to\mathbb N\) be monotone. Define
\[
 X^\phi_n=X_{\phi(n)},
 \qquad(\rho^{X^\phi})_n=\rho^X_{\phi(n),\phi(n+1)},
\]
and analogously for \(Y^\phi\).

The sampled tower is an actual `BanachTower`, with the composite bonding maps and a proved bound of one. Define the bounded candidate map
\[
 \boxed{S_\phi:E\to E_\phi,
 \qquad(S_\phi f)_n=f_{\phi(n)}.}
\]
Then
\[
 \|S_\phi f\|_\infty\le\|f\|_\infty,
 \qquad\|S_\phi\|\le1.
\]
Neither these definitions nor the preservation of exactness require cofinality or a finite gap bound. Repeated schedule indices are allowed.

**Lean:** `resample`, `sampleCLM`, `sampleCLM_apply`, `sampleCLM_bound`, `sampleCLM_opNorm`, `sample_exact`.

## 5. A bounded residual map and a commuting square

Suppose additionally
\[
 \boxed{\phi(n+1)-\phi(n)\le M\quad(\forall n),\qquad M\in\mathbb N.}
\]
Define
\[
 \boxed{C_\phi:R\to R_\phi,
 \qquad(C_\phi r)_n=B_{\phi(n),\phi(n+1)}(r).}
\]
This is constructed as a continuous linear map, with
\[
 \boxed{\|C_\phi r\|_\infty\le M\|r\|_\infty,
 \qquad\|C_\phi\|\le M.}
\]
The central identity is
\[
 \boxed{d_\phi S_\phi=C_\phi d.}
\]
Therefore
\[
 \boxed{\|d_\phi S_\phi f\|_\infty\le M\|df\|_\infty.}
\]
This is controlled reindexing, not invariance of the number \(\|df\|\). Notice that \(C_\phi\) is a transported accumulation, not the componentwise sample \(r\mapsto(r_{\phi(n)})\).

**Lean:** `residualSampleCLM`, `residualSampleCLM_opNorm`, `resampling_chain`, `sampled_residual_bound`.

## 6. Two different convergence statements

### 6.1 Sequences in the candidate Banach space

For fixed \(\phi,M\),
\[
 df^{(k)}\longrightarrow0\text{ in }R
 \quad\Longrightarrow\quad
 d_\phi S_\phi f^{(k)}\longrightarrow0\text{ in }R_\phi.
\]
This follows from continuity of the constructed \(C_\phi\).

**Lean:** `sampled_residual_tendsto_zero`.

### 6.2 A single candidate at increasing resolution

Assume also that \(\phi\) is unbounded. If
\[
 \|r_n\|\longrightarrow0,
\]
then the local sum bound and the bounded gaps imply
\[
 \boxed{\|B_{\phi(n),\phi(n+1)}(r)\|\longrightarrow0.}
\]
In particular,
\[
 \| (df)_n\|\longrightarrow0
 \quad\Longrightarrow\quad
 \|(d_\phi S_\phi f)_n\|\longrightarrow0.
\]
The two results have different quantifiers. Neither asserts a converse.

**Lean:** `blockSum_local_bound`, `blockSum_cofinal_vanish`, `sampled_levelwise_residual_vanish`.

## 7. Abstract presentation change and repair mismatch

Let \(d:E\to R\), \(D:F\to T\) be continuous linear maps. A bounded defect map consists of
\[
 S:E\to F,\qquad C:R\to T,\qquad DS=Cd.
\]
It induces a bounded map \(\ker d\to\ker D\) and composes with other such maps.

Let \(A:R\to E\) and \(B:T\to F\) be chosen bounded sections,
\[
 dA=I,\qquad DB=I,
\]
with projectors \(P_A=I-Ad\), \(P_B=I-BD\). Define
\[
 \boxed{H=SA-BC.}
\]
Then Lean proves
\[
 \boxed{DH=0,\qquad P_BS-SP_A=Hd.}
\]
Thus the discrepancy is exact-valued and vanishes on exact inputs. The estimates are
\[
 \|(P_BS-SP_A)f\|\le\|H\|\,\|df\|,
\]
\[
 \|H\|\le\|S\|\|A\|+\|B\|\|C\|.
\]
Since \(d\) has a section, it is surjective. Consequently
\[
 \boxed{P_BS=SP_A\quad\Longleftrightarrow\quad SA=BC.}
\]
Repair is natural precisely when the selected sections are compatible with the presentation change. Exactness of the repaired outputs alone does not give this equality.

**Lean:** `SplitDefect.DefectMap`, `coreMap`, `comp`, `mismatch`, `mismatch_exact`, `repair_change`, `repair_change_bound`, `repair_natural_iff`.

## 8. Triangular coordinates and composition

Using the already checked section charts
\[
 \Psi_A:E\simeq_L\ker d\times R,
 \qquad\Psi_B:F\simeq_L\ker D\times T,
\]
the presentation change has the exact form
\[
 \boxed{\Psi_BS\Psi_A^{-1}(e,r)=(S_0e+Hr,Cr),}
\]
where \(S_0\) is the restriction of \(S\) to the exact kernel.

For a second defect map \((S_2,C_2)\) and a third section, the mismatches satisfy
\[
 \boxed{H_{21}=S_2H_1+H_2C_1.}
\]
This is a proved composition law, not an assumption of path independence.

**Lean:** `DefectMap.chart_formula`, `DefectMap.mismatch_comp`.

## 9. Application to actual tower sampling

Instantiate \((S,C,D)=(S_\phi,C_\phi,d_\phi)\). Given sections \(A\) and \(B\) of the actual fine and sampled differentials,
\[
 \boxed{P_BS_\phi f-S_\phi P_Af=(S_\phi A-BC_\phi)df,}
\]
\[
 \boxed{\|P_BS_\phi f-S_\phi P_Af\|
 \le(\|A\|+M\|B\|)\|df\|.}
\]
If a sequence of fine residuals tends to zero, this discrepancy tends to zero. Equality at every finite stage still requires the section-compatibility condition.

The sections in this comparison are explicit inputs. Previous releases construct sections under their own split/gap assumptions. This release does not assert section existence for every contractive resampled tower or identify independently chosen repair procedures.

**Lean:** `samplingDefectMap`, `samplingMismatch`, `sampling_repair_formula`, `samplingMismatch_opNorm`, `sampling_repair_bound`, `sampling_repair_natural_iff`, `sampling_repair_discrepancy_tendsto_zero`.

## 10. Exactness can be hidden by coarsening

On constant real towers with identity bonding maps take
\[
 f_{2n}=I,\qquad f_{2n+1}=2I.
\]
This is a bounded nonzero candidate with
\[
 (df)_{2n}=I,\qquad(df)_{2n+1}=-I,
 \qquad\|df\|_\infty=1.
\]
For the cofinal schedule \(\phi(n)=2n\),
\[
 S_\phi f=(I,I,I,\ldots),\qquad d_\phi S_\phi f=0.
\]
Lean proves all these statements for the full infinite families. It follows that \(C_\phi\) is not injective and
\[
 \boxed{\nexists c>0\;\forall f:
 c\|df\|\le\|d_\phi S_\phi f\|.}
\]
The failure already occurs on residuals of actual bounded candidates, not just on arbitrary residual families.

This does not contradict exact-class invariance from v0.5.0. A nonexact fine candidate was not a morphism in its exact transport category. Coarsening removed the constraints that detected its incompatibility.

**Lean:** `ResidualAliasing.fine_residual_norm`, `sampled_residual_zero`, `coarsening_hides_nonzero_residual`, `coarsen_not_injective`, `no_positive_reverse_bound`.

## 11. The dependence on gap length is sharp

On the same identity real towers, sample every \(M\) levels:
\[
 \phi_M(n)=Mn.
\]
The bounded unit residual \(r_n=I\) satisfies
\[
 \|r\|_\infty=1,\qquad (C_{\phi_M}r)_n=MI.
\]
Therefore Lean proves, for every natural \(M\),
\[
 \boxed{\|C_{\phi_M}\|=M.}
\]
For \(M>0\) this schedule is cofinal. The \(M=0\) case is the constant schedule and the zero block map.

This sharpness statement is about the map on **all bounded residual families**. The unit residual is not asserted to have a bounded primitive; the earlier identity-tower obstruction rules out such a primitive.

**Lean:** `stride_cofinal`, `blockSum_unit`, `coarsen_unit_norm`, `coarsen_opNorm`.

## 12. Verification and remaining boundary

Six modules add 84 named theorem declarations, including auxiliary lemmas. The cumulative project has 44 proof modules, 480 named theorems, and 203 indexed non-theorem declarations. All 38 previous proof modules are unchanged.

The exact rational audit separately tests 120 variable-dimension candidate configurations, 24 section/cochain-map configurations, and 32 sharp-gain values. It compares a recurrence implementation against independently formed products and transported finite sums. These finite tests do not prove infinite convergence or universal statements.

Not established: unrestricted source/output reindexing of nonexact premorphisms; a residual-valued localization; a full comparison with `Pro(C)`; unrestricted weighted/noncontractive estimates; automatic compatibility or existence of fine/coarse sections; stack descent; higher obstruction theory; an unrestricted arithmetic correspondence; a novelty claim.

The next precise issue is to characterize the information in \(\ker C_\phi\), or retain suitable within-block data, so that coarsening does not hide relevant incompatibility. That is a research target, not an additional theorem in this release.
