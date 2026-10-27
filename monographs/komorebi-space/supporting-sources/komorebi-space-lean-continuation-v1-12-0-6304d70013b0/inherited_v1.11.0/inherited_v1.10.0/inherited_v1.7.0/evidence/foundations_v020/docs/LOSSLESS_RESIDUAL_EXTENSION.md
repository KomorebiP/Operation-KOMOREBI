# Komorebi Space Theory: lossless dyadic residual detail
## v0.7.0 · Komorebi P.

This extension characterizes the information erased by the actual dyadic residual coarsener and constructs bounded coordinates retaining it. It then iterates the construction through every finite number of coarsening levels. The splitting of a bounded surjection is established mathematics. The content here is its explicit realization for the existing, transported tower residual, the independent detail channels, the exactness criterion, and the connected finite-depth hierarchy.

## 1. Fixed towers and scope

Let \(\mathbb K\) be a nontrivially normed field. Retain the sequential Banach towers
\[
 X_{n+1}\xrightarrow{\rho^X_n}X_n,
 \qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n,
\]
and their bounded transport and residual spaces
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),\qquad
 R=\ell^\infty_n\mathcal L(X_{n+1},Y_n).
\]
The actual compatibility differential is unchanged:
\[
 \boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\]
Assume contractive bonding maps and specified uniformly bounded target sections:
\[
 \|\rho^X_n\|\le1,\quad \|\rho^Y_n\|\le1,\qquad
 s_n:Y_n\to Y_{n+1},\quad\rho^Y_ns_n=I,\quad\|s_n\|\le S.
\]
All maps in these equations are continuous linear. The sections are supplied input. The existence of bounded sections for arbitrary bonding maps is not asserted.

The schedule is specifically \(\phi(n)=2n\). Write
\[
 R'=\ell^\infty_n\mathcal L(X_{2n+2},Y_{2n}).
\]
The v0.6 coarsening operator, specialized to this schedule, is
\[
 \boxed{(Cr)_n=\rho^Y_{2n}r_{2n+1}+r_{2n}\rho^X_{2n+1}.}
 \tag{1}
\]
It has \(\|C\|\le2\). It is a transported pair sum, not a componentwise sample. Source and target maps can have varying dimensions.

**Lean:** `DyadicResidual.coarsen`, `coarsen_pair`. These use the actual `BanachTower.residualSampleCLM` from v0.6.

## 2. A constructed section of coarsening

For every bounded coarse residual \(c\in R'\), define
\[
 \boxed{(Jc)_{2n}=0,\qquad(Jc)_{2n+1}=s_{2n}c_n.}
 \tag{2}
\]
Parity interleaving is formalized for dependent bounded families. Even and odd coordinates need not have the same types. The interleaving and its inverse preserve the maximum norm.

Using (1),
\[
 (CJc)_n=\rho^Y_{2n}s_{2n}c_n+0=c_n.
\]
Hence
\[
 \boxed{CJ=I_{R'},\qquad\|Jc\|\le S\|c\|,\qquad\|J\|\le S.}
 \tag{3}
\]
This construction needs no propagation gap \(SB_X<1\). It is a section of **coarsening \(C\)**, not a section of the compatibility differential \(d\). It therefore does not contradict the earlier identity-tower obstruction to \(d\) having a right inverse on all bounded residuals.

**Lean:** `BoundedParity.split`, `split_norm`; `DyadicResidual.lift`, `lift_even`, `lift_odd`, `lift_bound`, `lift_opNorm`, `coarsen_lift`, `sectionC`.

## 3. Hidden residual and kernel characterization

Define
\[
 \boxed{H=I_R-JC.}
 \tag{4}
\]
The formalization proves
\[
 CH=0,\qquad H^2=H,\qquad r=Hr+JCr.
 \tag{5}
\]
Its coordinates are
\[
 (Hr)_{2n}=r_{2n},\qquad
 (Hr)_{2n+1}=r_{2n+1}-s_{2n}(Cr)_n.
\]
The complete kernel criterion is
\[
 \boxed{Cr=0\iff
  \forall n,\ \rho^Y_{2n}r_{2n+1}=-r_{2n}\rho^X_{2n+1}.}
 \tag{6}
\]
The continuous linear coordinate equivalence is
\[
 \boxed{
 R\simeq_L\ker C\times R',\qquad
 r\longmapsto(Hr,Cr),\qquad
 (h,c)\longmapsto h+Jc.
 }
 \tag{7}
\]
Here \(\simeq_L\) means a linear bijection continuous in both directions, not an isometry. The kernel of \(C\) is fixed by the tower data. The section \(J\), projection \(H\), and chosen coordinates may depend on the target splitting.

The checked quantitative bounds are
\[
 \boxed{\|Hr\|\le(1+2S)\|r\|,\qquad
 \|r\|\le\|Hr\|+S\|Cr\|.}
 \tag{8}
\]
These are sufficient bounds; no sharpness is asserted.

**Lean:** `hidden`, `hidden_coarsen`, `hidden_idempotent`, `reconstruction`, `kernel_iff`, `coordinates`, `hidden_bound`, `reconstruction_bound` in `DyadicResidual`.

## 4. The two independent hidden channels

The kernel condition (6) contains both transported cancellation and target-kernel information. Define
\[
 a_n=r_{2n},\qquad
 \boxed{\nu_n=r_{2n+1}-s_{2n}\rho^Y_{2n}r_{2n+1}.}
 \tag{9}
\]
Then
\[
 \rho^Y_{2n}\nu_n=0.
\]
With \(c=Cr\), exact reconstruction is
\[
 \boxed{
 r_{2n}=a_n,\qquad
 r_{2n+1}=\nu_n+s_{2n}
   \bigl(c_n-a_n\rho^X_{2n+1}\bigr).
 }
 \tag{10}
\]
For a hidden residual, \(c=0\), so the odd edge is
\[
 r_{2n+1}=\nu_n-s_{2n}a_n\rho^X_{2n+1}.
\]
Thus the kernel is not represented by adjacent scalar cancellation alone. The term \(\nu_n\) can be nonzero while both the even edge and the coarse residual vanish.

Define the normed submodule
\[
 V=\left\{\nu\in\ell^\infty_n\mathcal L(X_{2n+2},Y_{2n+1}):
       \rho^Y_{2n}\nu_n=0\text{ for all }n\right\}
\]
and
\[
 R_{\mathrm{even}}=\ell^\infty_n\mathcal L(X_{2n+1},Y_{2n}).
\]
Every independent bounded triple \((a,\nu,c)\in R_{\mathrm{even}}\times V\times R'\) has a unique bounded synthesis by (10). The package constructs the continuous linear equivalence
\[
 \boxed{
 R\simeq_L(R_{\mathrm{even}}\times V)\times R',
 \qquad r\longmapsto((a,\nu),c).
 }
 \tag{11}
\]
The forward and inverse bounds, with product maximum norms, are
\[
 \|\Phi r\|\le\max(1+S,2)\|r\|,
 \qquad
 \|\Phi^{-1}z\|\le(1+3S)\|z\|.
 \tag{12}
\]
The inverse is a formal mathematical construction. There is no algorithmic complexity or data-compression claim.

**Lean:** `innovation`, `innovation_down`, `reconstruct_odd`, `channels_injective`, `synthesize`, `synthesize_odd`, `unique_synthesis`, `verticalSpace`, `channelsLinear`, `channels_bound`, `channels_inverse_bound`, `channels`.

## 5. Fine exactness is recoverable from retained data

Let \(S_\phi\) sample candidate transports and \(d_\phi\) be the actual sampled differential. The existing identity is
\[
 d_\phi S_\phi=Cd.
\]
Combining it with (5) gives
\[
 \boxed{
 df=0\iff
 d_\phi S_\phi f=0\quad\text{and}\quad Hdf=0.
 }
 \tag{13}
\]
The theorem is stated in Lean using the actual `BanachTower.Exact` predicates. It is not a replacement of fine exactness by a new definition of exactness.

Merely retaining coarse residuals remains insufficient. Equation (13) succeeds because the previously discarded data are retained, not because cancellation has ceased to occur.

**Lean:** `DyadicResidual.exactness_detected`.

## 6. Two checked witnesses

### 6.1 All-level alternating candidate

On the existing real identity towers, retain the candidate
\[
 f_{2n}=I,\qquad f_{2n+1}=2I.
\]
Its residual satisfies
\[
 r_{2n}=I,\qquad r_{2n+1}=-I,\qquad\|r\|=1.
\]
For the identity target splitting, Lean proves
\[
 \boxed{Cr=0,\qquad Hr=r,\qquad\|Hr\|=1,\qquad\nu_n=0.}
 \tag{14}
\]
The nonzero incompatibility is fully visible in the retained detail despite zero coarse residual.

**Lean:** `DyadicDetailExamples.alternating_coarse_zero`, `alternating_hidden_full`, `alternating_hidden_norm`, `alternating_vertical_zero`, `alternating_detected`.

### 6.2 A separate finite target-kernel block

Let
\[
 q(x,y)=x,\qquad s(x)=(x,0),\qquad b(x)=(0,x).
\]
Lean proves
\[
 qs=I,\qquad qb=0,\qquad b\ne0,\qquad b-sqb=b.
\]
This is explicitly a finite block witness, not an additional constructed infinite tower. It shows why deleting the target-kernel channel from (10) would be unsound in general.

**Lean:** `DyadicDetailExamples.BlockKernelWitness.down_up`, `down_vertical`, `vertical_nonzero`, `vertical_is_its_innovation`, `coarse_even_insufficient`.

## 7. Finite multiscale reconstruction

For normed spaces \(R_j\), suppose coarsenings and selected sections satisfy
\[
 C_j:R_j\to R_{j+1},\qquad J_j:R_{j+1}\to R_j,
 \qquad C_jJ_j=I.
\]
Starting from \(r_0=r\), define
\[
 r_{j+1}=C_jr_j,\qquad h_j=(I-J_jC_j)r_j,
\]
\[
 L_0=I,\qquad L_{j+1}=L_jJ_j.
\]
Then, for every finite \(N\in\mathbb N\), including \(N=0\),
\[
 \boxed{r=\sum_{j=0}^{N-1}L_jh_j+L_Nr_N.}
 \tag{15}
\]
Equality of all details below level \(N\) and the final coarse datum is equivalent to equality of the original data. In particular,
\[
 \boxed{r=0\iff (h_j=0\text{ for every }j<N)\text{ and }r_N=0.}
 \tag{16}
\]
These are proved by a finite transported telescoping identity. Completeness or convergence is not needed.

**Lean:** `CoarseningCascade`, `one_layer`, `reconstruction`, `equal_iff`, `zero_iff`.

### Instantiation on the actual towers

After pairing, the target sections are constructed by composition:
\[
 s^{\mathrm{coarse}}_n=s_{2n+1}s_{2n},\qquad
 \|s^{\mathrm{coarse}}_n\|\le S^2.
\]
The corresponding coarse bonding maps remain contractive. This constructs an actual next system and, by recursion, all finite levels. The resulting cascade uses the actual transported residual coarsening at each stage.

For every candidate and every finite \(N\), Lean proves fine exactness iff all retained residual details below \(N\) and the final coarse residual vanish.

**Lean:** `DyadicResidual.sampledSplitting`, `System.next`, `System.stage`, `System.cascade`, `System.residual_reconstruction`, `System.exactness_iff_hierarchy`.

The final term \(L_Nr_N\) is retained. No claim is made that it tends to zero as \(N\to\infty\). Section bounds can grow under repeated composition, so finite-level existence does not imply a uniform infinite-depth bound.

## 8. Verification and limits

Six new modules contain 79 named theorem declarations and 45 indexed non-theorem declarations. The cumulative project contains 50 proof modules, 559 named theorems and 248 indexed non-theorems. Counts include auxiliary declarations, not mathematical discoveries. All 44 prior proof modules are unchanged.

`checks/computation/dyadic_details_exact.py` is a second implementation over exact rational matrices. It checks 216 variable-dimension pair configurations and 24 finite cascade configurations, with 4,260 explicit positive assertions and three false-claim rejection controls. Its norm is the exact induced infinity norm, computed by absolute row sums. The all-level and universally quantified results come from Lean proof terms, not extrapolation from these tests.

This release does not prove arbitrary bounded target splittings, general unbounded/independent schedules, noncontractive norm estimates, an invariant-independent repair doctrine, a nonexact eventual quotient, the full pro-category comparison, higher obstruction theory, or unrestricted descent. It does not establish infinite-depth convergence, orthogonality, optimal compression, optimal conditioning, or novelty relative to the literature.

The next extension is to retain analogous detail for variable-length blocks and compare the resulting coordinate systems under changes of grouping. The present theorem concerns actual repeated dyadic grouping with explicitly selected sections.
