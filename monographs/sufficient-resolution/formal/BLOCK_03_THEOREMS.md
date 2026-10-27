# Block 03 — Finite observable-state construction and minimality

**Komorebi P. | Sufficient Resolution v0.3.0 | 13 September 2026**

This block adds **65 theorem declarations in five proof modules**. The cumulative
source contains **190 theorem/lemma declarations in 16 modules**, and **263 explicitly
named declarations**. Counts include supporting lemmas and exact examples.
They are not independent novelty counts and do not update the twelve-paper census.

## 1. Exact finite observation horizon

Let X be a finite-dimensional vector space over a field K, let T_i be a specified
family of endomorphisms, and O:X→Y a specified linear observation. Words are
chronological: T_(i::w)=T_w T_i. Define

\[
N_r=\{x:O T_w x=0\text{ for every word }|w|\le r\},\qquad
N=\bigcap_w\ker(OT_w),\qquad k=\dim_K\ker O.
\]

The first new module proves

\[
N_0=\ker O,\qquad
N_{r+1}=\ker O\cap\bigcap_i T_i^{-1}N_r,
\qquad N_{r+1}\subseteq N_r.
\]

One plateau certifies the exact all-future invisible subspace:

\[
N_{r+1}=N_r\Longrightarrow N_r=N.
\]

A rank plateau is equivalent to a subspace plateau because this is a nested,
finite-dimensional family. The dimension-budget proof gives the a priori bound

\[
\boxed{N_k=N.}
\]

Consequently, for all states x,y,

\[
\boxed{
[OT_wx=OT_wy\text{ for every }|w|\le k]
\iff
[OT_wx=OT_wy\text{ for every finite word }w].
}
\]

Distinct behavioral states have a distinguishing word of length at most k.
The bound includes the empty word, k=0, zero-dimensional X, and zero observation.
It does not require the operations to commute. The alphabet can be infinite in
this theorem; the bounded family is a finite enumeration only for a finite alphabet.

**Lean:** `FiniteHorizon.visibleKernel_succ`,
`visibleKernel_eq_invisible_of_plateau`, `visibleKernel_eq_invisible_of_eq_finrank`,
`visibleKernel_finrank_budget`, `visibleKernel_stabilizes`,
`same_future_iff_bounded`, `exists_bounded_distinguishing_word`.

## 2. Minimal dimension, not only kernel inclusion

The canonical state space X/N is observable: its own all-future invisible subspace
is zero. For any exact linear model q:X→Z with

\[
qT_i=U_iq,\qquad Vq=O,
\]

the existing quotient comparison is now proved surjective. It induces a unique
surjection from the actual image of q to X/N. Surjectivity of q onto all of Z is
**not** assumed.

\[
\boxed{\dim(X/N)\le\dim(\operatorname{Ran}q)\le\dim Z.}
\]

The last comparison assumes finite-dimensional Z. Also

\[
\dim(X/N)=\dim X-\dim N,
\]

and the exact competitor image attains the minimum precisely when

\[
\boxed{\ker q=N.}
\]

An explicit linear equivalence from such a minimal image to X/N is constructed.
This is minimality among exact linear models related to the original state by q,
for all original states and all specified future operation sequences. It is not
an unrestricted claim about nonlinear encodings or state inferred from sampled data.

**Lean:** `BehavioralMinimality.quotient_is_observable`,
`modelQuotientComparison_surjective`, `imageComparison`, `imageComparison_unique`,
`finrank_state_le_image`, `finrank_state_le_model`, `image_dimension_minimal_iff`,
`minimalImageEquiv`.

## 3. A finite-coordinate realization, with its dynamics

For a finite alphabet, `wordsUpTo` recursively enumerates exactly the words of
length at most r. Lean proves the enumeration membership specification. Define

\[
H_kx=(OT_wx)_{|w|\le k}.
\]

The finite-coordinate state space is **Ran H_k**, not the entire product of
arbitrary observation tables. Only realizable tables are included.

\[
\ker H_k=N,\qquad X/N\cong\operatorname{Ran}H_k.
\]

The formalization constructs dynamics and readout on this range and proves

\[
\widetilde T_w H_kx=H_kT_wx,\qquad
\widetilde O\widetilde T_wH_kx=OT_wx
\]

for every finite word, of unbounded length. This constructed model has the minimum
exact dimension proved in Section 2. The coordinate index set is finite even if Y
is infinite-dimensional; the realizable range is finite-dimensional because X is.

The abstract range/equivalence construction uses classical linear algebra. It is
not a compiled Lean Gaussian-elimination algorithm.

**Lean:** `FiniteObservableModel.mem_wordsUpTo`, `ker_complete_observation`,
`observableEquiv`, `coordinateDynamics`, `coordinateObservation`,
`coordinate_all_future_fidelity`, `coordinate_dimension_le_exact_model`.

## 4. Finite certificates for a proposed minimal model

A `FiniteCertificate.Certificate T O q r` contains actual maps witnessing

\[
q=G H_r,\qquad qT_i=U_iq,\qquad Vq=O.
\]

These finite identities imply

\[
\boxed{\ker q=N.}
\]

The two directions have different roles. Generation from original observations
means q cannot retain a distinction invisible to all observations. Exact output
and intertwining mean q cannot discard a distinction visible in any future.
This kernel theorem does **not** require finite-dimensional X, or an a priori
lower bound on r. If the certificate exists at an earlier depth, it already proves
minimality. A finite alphabet makes the intertwining obligations finite in number.

If q is surjective, an actual equivalence Z≃X/N is constructed and proved to
intertwine every operation and preserve the observation. Without surjectivity,
minimality applies to Ran q, not necessarily to unused coordinates in Z.

**Lean:** `FiniteCertificate.certificate_kernel_eq`, `certificate_same_future_iff`,
`certificate_all_future_fidelity`, `certificateEquiv`, `certificateEquiv_dynamics`,
`certificateEquiv_observation`, `certificate_image_dimension`.

## 5. Noncommuting exact example

Over the rationals, take X=Q³, O(x,y,h)=x, and

\[
T_A(x,y,h)=(y,0,h),\qquad T_B(x,y,h)=(0,x,h).
\]

Lean proves T_A T_B≠T_B T_A. The candidate q(x,y,h)=(x,y) has a depth-one finite
certificate: its coordinates are O(x,y,h) and O(T_A(x,y,h)).

The formalization proves that the smallest exact model has dimension 2, the hidden
coordinate h is irrelevant for every future word, and the current observation
alone misses a distinction that a one-step observation detects.

**Lean:** `ObservableExamples.exactCertificate`, `smallest_dimension`,
`operations_do_not_commute`, `hidden_coordinate_irrelevant`,
`one_step_detects_distinction`.

## 6. Runnable rational implementation

`python scripts/observable_model.py --input examples/observable_model_input.json --output model.json`

The implementation performs row-space saturation rather than enumerating all
words. It propagates sparse generation witnesses, constructs a full-row-rank
compression C, a lift R with CR=I, reduced operations U_i and readout V, and checks

\[
CT_i=U_iC,\quad VC=O,\quad CR=I,
\]

plus the exact sparse finite-observation generation equations. Strict refinement
rounds are bounded by dim X−rank O. Detecting the final plateau can require one
additional closure check. The implementation uses rational arithmetic only and
rejects floating input and specified resource-limit violations.

The generic certificate contract is Lean-proved. The concrete example above is
also instantiated in Lean. The Python minimizer and its parser are **not themselves
formally verified**; certificates for arbitrary JSON inputs are validated by exact
Python arithmetic, not automatically turned into Lean proofs.

The test suite compares against explicit all-word observation tables with a separate
forward-elimination rank routine, checks complete word-map fidelity, round trips
JSON certificates, and rejects deliberately corrupted certificates. Universal
claims come from Lean, not the finite tests.

## Remaining boundaries

No learned-operator guarantee, noisy-data sufficiency, stability estimate,
continuous-time memory, nonlinear minimality, positivity-constrained realization,
integral-lattice model, categorical descent, or arithmetic/Langlands existence
result follows from this block. Generic linear minimality does not ensure a
minimal positive or stochastic realization. No literature novelty is claimed.
