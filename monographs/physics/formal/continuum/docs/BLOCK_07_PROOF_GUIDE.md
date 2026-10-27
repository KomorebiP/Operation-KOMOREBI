# Block 07 — Positive, overlapping and moving effect atlases

Komorebi Physics Lean v0.7.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 pages, physical PDF pages 27–28 (printed 14–15). The literal targets are Chapter 5.1–5.3, equations (5.1)–(5.21). Equation (5.32)'s sharp-projector specialization is also checked. The authoritative completed audit is `verification/final/report.json`; this guide is not a substitute for it.

Files returned the page-28 image but could not supply page 27's image. The included original PDF was rendered locally, and page 27 was inspected directly. The source convention is K = dU U*, with the derivative on the first U. The original PDF hash is unchanged.

## 1. Inventory and mathematical scope

| New module | Theorems | Definitions | Structures | Role |
|---|---:|---:|---:|---|
| PositiveEffects | 25 | 5 | 1 | Genuine positive resolutions, actual Born derivatives and continuity |
| MovingEffects | 14 | 2 | 0 | Actual moving sources, differentiated completeness and unitary transport |
| EffectRefinement | 14 | 2 | 0 | Genuine coarsening, source/current matrix laws and composition |
| WeightedEffects | 9 | 2 | 0 | Column-stochastic positive postprocessing and composition |
| EffectExamples | 27 | 8 | 0 | Exact nonprojector and nonzero-source witnesses |
| **Block 07** | **89** | **19** | **1** | **109 new inventoried declarations** |

The cumulative inventory is 572 theorem declarations, 688 named declarations, and 34 mathematical modules. It contains 39 recovered Paper VII theorems and 533 full-edition declarations. The 29 previous mathematical modules are preserved byte-for-byte. These are declaration counts, including support lemmas and exact examples, not independent physical discoveries or a full-edition completion percentage.

The base space is an arbitrary complex inner-product space; finite-dimensionality and completeness are not needed for fixed effects, general moving effects or finite postprocessing. The unitary-conjugation section additionally assumes a complete complex Hilbert space so that the bounded adjoint operators exist in the chosen interface. All effect and generator operators are bounded and defined everywhere. Label types are finite.

## 2. An effect atlas is not a disguised sharp atlas

`EffectAtlas H I` has only these data and laws:

    effect : I -> (H ->L[Complex] H)
    selfAdjoint : <F_i x,y> = <x,F_i y>
    nonnegative : 0 <= Re<x,F_i x>
    sum_effect : sum_i F_i = I

There is no field for idempotence, orthogonality, commutation, probability balance or a derivative. Positivity is represented by its Hermitian quadratic-form condition. The real expectation

    effectExpectation F psi = Re<psi,F psi>

is used to define the actual Born probability p_i. Its imaginary part is proved to vanish using self-adjointness, and the real value cast to the complex numbers is proved equal to the literal complex pairing. Thus taking the real part is not concealing an unproved reality assertion.

The proofs derive

\[
p_i\ge0,\qquad \sum_i p_i=\|\psi\|^2,\qquad p_i\le\|\psi\|^2.
\]

For a normalized state, they give a nonnegative probability distribution with every p_i at most one. Reconstruction of the *effected vectors* follows from the partition of unity. Their squared norms are not claimed to be the Born probabilities or to obey a sharp-projector Parseval identity.

`ofAtlas` constructs the sharp case from the earlier checked projector atlas. Its probabilities are identified with the older packet energies, and its current equals the older projector current under skew-adjointness, checking the source's equation (5.32).

## 3. Actual fixed-effect continuity

The actual source current is defined by

\[
J_{ij}=\operatorname{Re}\langle F_i\psi,A F_j\psi\rangle
       -\operatorname{Re}\langle F_j\psi,A F_i\psi\rangle.
\]

This difference is antisymmetric for every A. With the additional skew-adjointness assumption, it equals twice the first real pairing. Summing over j uses the partition of unity in *both* terms, giving

\[
\sum_j J_{ij}=2\operatorname{Re}\langle F_i\psi,A\psi\rangle.
\]

The derivative theorem starts from the actual original vector derivative

```lean
HasDerivAt psi (A (psi t)) t
```

and `IsSkew A`. The proof differentiates the expectation, not a norm chosen to have the desired derivative, and establishes

\[
\boxed{\frac{d}{dt}\langle\psi,F_i\psi\rangle=\sum_jJ_{ij}.}
\]

Finite subsystem boundary flux and zero total probability derivative follow. No pairwise orthogonality or effect commutation is used. No solution existence or uniqueness is proved.

Antisymmetry without skewness does **not** imply the current is the correct probability derivative. The exact identity-generator example below separates these two assertions.

## 4. The moving source is derived, including its reality and zero sum

For a family F(t) of genuine effect atlases and actual derivatives

```lean
forall i, HasDerivAt (fun s => (F s).effect i) (D i) t
```

`derivative_sum` differentiates the operator partition law to prove sum_i D_i=0. This is not an additional hypothesis. `differentiated_selfAdjoint` differentiates the actual Hermitian pairing identities to prove D_i is Hermitian. Consequently

\[
s_i=\operatorname{Re}\langle\psi,D_i\psi\rangle
\]

is equal to its literal complex expectation, and sum_i s_i=0 is derived from the proved operator sum.

The generic expectation derivative comes from the product rule for the actual operator-state application and the inner-product rule:

\[
\frac{d}{dt}\operatorname{Re}\langle\psi,F_i\psi\rangle
=\operatorname{Re}\langle\psi,D_i\psi\rangle
 +2\operatorname{Re}\langle F_i\psi,\dot\psi\rangle.
\]

Substituting the supplied original vector flow and the proved current row sum gives

\[
\boxed{\dot p_i=s_i+\sum_jJ_{ij}.}
\]

No source equation or probability balance is supplied as input. Subsystem derivatives retain their source sum plus only the boundary current. Zero total derivative follows by separately cancelling the sources and currents.

`moving_total_constant` also proves the conserved total at any two real times along a supplied all-real-time skew flow. That total theorem needs no effect derivatives because the total Born probability is already identically the state norm squared at every time.

### Actual unitary motion

`conjugate` constructs effects U F_i U*, proving positivity, Hermiticity and completeness. Positivity and Hermiticity of conjugation do not require unitarity; the constructor uses U U*=I for completeness. The derivative theorems impose the inverse identities needed for actual unitary transport.

With an actual operator-norm derivative dU at t, U(t)*U(t)=I at the base time, and U(s)U(s)*=I along the curve, the formalization derives

\[
K=\dot U U^*,\qquad K^*=-K,\qquad
\boxed{\dot F_i=[K,F_i].}
\]

The earlier inverse-derivative theorem is reused; a formal symbol for dU* is not assumed. Applying the moving-probability theorem gives the commutator source and its zero sum. These hypotheses include the manuscript's two-sided unitary family. They do not treat arbitrary invertible similarity as positivity-preserving unitary transport.

## 5. Exact coarsening is a physical construction, not only a matrix identity

For an address map f:I->J, construct

\[
G_a=\sum_{f(i)=a}F_i.
\]

The new definition proves each G_a is positive and Hermitian and that their sum is I. Every fine effect is assigned once. Empty fibers are allowed and produce the zero effect.

From these actual operators the proofs derive

\[
p_a^c=\sum_{f(i)=a}p_i,\quad
s_a^c=\sum_{f(i)=a}s_i,\quad
J_{ab}^c=\sum_{f(i)=a}\sum_{f(j)=b}J_{ij}.
\]

All three are also proved in the source's literal incidence-matrix notation:

\[
\boxed{p^c=Rp,\qquad s^c=Rs,\qquad J^c=RJR^{\mathsf T}.}
\]

The coarse effect derivative is obtained by differentiation of the finite operator sum. The actual coarse probability derivative is then derived with its source and all fine currents retained. Sequential coarsening agrees with composed addressing at the operator, probability and current levels. Coarsening also commutes with actual unitary conjugation.

Overlapping *effects* are allowed. Duplicating a fine effect in multiple coarse bins without normalized weights is not automatically a valid resolution of the identity.

### Explicit weighted strengthening

The added `postprocess` construction allows real weights R_ai satisfying

\[
R_{ai}\ge0,\qquad\sum_aR_{ai}=1\quad\text{for every fine label }i.
\]

They are column-normalized, not merely row-normalized. Binary entries are unnecessary. The actual effects G_a=sum_i R_ai F_i are proved positive, Hermitian and complete. Their probabilities, sources and currents have the same weighted formulas, with RJR^T proved as an actual matrix product. Differentiating moving fine effects under fixed weights gives the actual weighted coarse balance.

Positive column-normalized matrices are proved closed under multiplication, and the sequentially constructed operators equal the construction from the product weights. The weights are fixed in time; a time-dependent postprocessing would contribute additional weight derivatives and is not covered by this statement. Signed or unnormalized weights are not promoted to physical effects.

## 6. Exact nonprojector witness

Let

\[
F_0=\operatorname{diag}(3/4,1/4),\quad
F_1=\operatorname{diag}(1/4,3/4),\quad
\psi=(3/5,4/5),\quad
A=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

The effects are constructed by nonnegative normalized postprocessing of the existing coordinate atlas, not introduced with assumed positivity. Lean proves norm(psi)=1 and

\[
p_0=43/100,\quad p_1=57/100,\quad
\|F_0\psi\|^2=97/400.
\]

Hence the Born probability and squared effected-vector norm differ. It additionally proves

\[
F_0^2\ne F_0,\qquad
F_0F_1=(3/16)I\ne0,
\]

and the exact currents

\[
\boxed{J_{01}=-12/25,\qquad J_{10}=12/25.}
\]

The affine vector curve psi_loc(t)=psi+t A psi has the required original vector derivative at zero. The general positive-effect theorem yields the actual p_0 derivative -12/25 there. This curve is a local derivative witness, not a global normalized solution. These diagonal witness effects commute; the general results impose no commutation assumption.

## 7. A globally positive moving atlas with nonzero source

On the one-dimensional complex space, define

\[
F_0(t)=\frac{1+\sin t}{2}I,\qquad
F_1(t)=\frac{1-\sin t}{2}I.
\]

The family is proved positive and complete for **every real time**, using the bounds on sine. Its operator derivatives at zero are derived from the actual sine derivatives. With the constant normalized state psi=1 and A=0, the theorem gives

\[
J_{ij}=0,\qquad
s_0=+1/2,\quad s_1=-1/2,\qquad
\boxed{p_0'(0)=1/2.}
\]

Thus omitting the source gives a false derivative even for a globally positive effect family and an exactly constant state. This scalar motion is a general moving atlas, not asserted to arise by unitary conjugation.

A separate fixed-atlas example with A=I has all effect currents zero while p_0'(0)=1. It shows why skewness cannot be removed from the continuity identification. Positive duplicated identities fail completeness, and the negative effect -I has expectation -1 on the state 1.

## 8. Verification and explicit boundaries

The verifier deletes all local compiled outputs, recompiles 34 mathematical modules and the aggregate with one worker and warnings as errors, and audits all 688 inventoried declarations, including every new proof-bearing constructor. It checks 50 intentionally invalid controls, including nine new variants. Each control needs its own intended diagnostic in a mapped source range. A batch nonzero exit, import failure or timeout is insufficient.

All 29 prior mathematical files are checked against `reference/block06_preservation.json`, with earlier preservation checks retained. The 483-theorem baseline was freshly verified before the extension. The final completed production report and fresh-extraction report determine the release's actual verification status.

Lean is 4.34.0-rc2 and Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine pinned dependency revisions and clean tracked trees are checked. The existing imported dependency cache is reused, not rebuilt wholesale. Permitted axiom dependencies are only propext, Classical.choice and Quot.sound. No admitted active proofs, custom axioms, native evaluation or disabled kernel checks are used.

The new work does not construct ODE solutions, prove unbounded-operator/domain results, countable-atlas limits or infinite-dimensional trace-class theorems. It does not establish universal channel factorization, a Naimark dilation for arbitrary effects, time-dependent stochastic-weight dynamics, or measurement-update instruments. The earlier positivity-preservation, entropy-boundary, continuum, gravitational, cosmological and empirical boundaries remain unchanged.

**Next literal target:** Chapter 5.4, (5.22)–(5.31), the actual Parseval analysis/synthesis maps, channel-to-channel operator reconstruction, and direct-sum dilation. Equation (5.32) is already checked here as a sharp-case consistency bridge.
