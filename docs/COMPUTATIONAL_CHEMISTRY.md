# Computational chemistry: three-query Hamiltonian recovery

**Komorebi P. · Research checkpoint · 13 November 2026**

How much of an electronic Hamiltonian can be recovered from a few of its
actions on known states? This project studies that question through exact
finite models, then asks which conclusions survive numerical error and
chemical restrictions.

For the real, spin-free **three-spatial-orbital sector with two alpha and one
beta electrons**, the answer is precise: the nine-state Hamiltonian family
has **21 independent parameters**, and **exactly three complete action
vectors** identify every member. A fixed probe design, an exact rational
decoder and rigorous error bounds accompany the proof.

> This closes a specified finite-family recovery problem. The molecular
> example certifies arithmetic in a reduced H10 model. Novelty, approximation
> error for the full molecule and a practical speed advantage remain open.

[Read the normal-form proof](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/normal-form.html)
· [Read the three-query theorem](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/three-queries.html)
· [Download the focused replay bundle](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/Stage14_Fixed_Spin_Recovery.zip)
· [Return to the Physics collection](PHYSICS_COLLECTION.md)

## What is being recovered?

There are three real orthonormal spatial orbitals. Two electrons occupy
alpha-spin orbitals and one occupies a beta-spin orbital. Choosing the alpha
pair and beta orbital gives

```math
\binom{3}{2}\binom{3}{1}=9
```

determinant states. The Hamiltonian contains a real symmetric one-electron
matrix and real two-electron integrals with the usual eightfold chemists'
symmetry. These give 27 input coefficients, but six combinations are
redundant after restriction to this sector. The resulting operator space
has dimension 21. The energy shift is included.

An **action query** supplies a known real nine-component vector and returns
the complete vector obtained by applying the unknown Hamiltonian to it.
This is a classical matrix-vector oracle model. Three such queries do not
mean three scalar expectation measurements or three quantum experiments.

The recovery identifies the sector operator. It does not uniquely identify
the original one-electron and two-electron integrals separately.

## Why three queries are enough

Two action vectors supply at most 18 scalar constraints on 21 independent
parameters. A nonzero perturbation remains invisible to them. The argument
also covers deterministic adaptive probes: an invisible perturbation
preserves the outputs, so it preserves the strategy's query path.

The constructive part uses these three fixed columns, in the determinant
order specified in the proof:

```math
V=\begin{pmatrix}
-1&0&0\\0&1&0\\0&0&1\\-1&0&0\\0&0&1\\0&-1&0\\
1&0&0\\0&1&0\\0&0&1
\end{pmatrix},\qquad V^{\mathsf T}V=3I_3.
```

Each probe has three signed unit entries and norm \(\sqrt 3\). The
27-by-21 coefficient map for the three outputs has an explicitly selected
21-by-21 minor with nonzero integer determinant. Thus the same probes work
for every member of the family. Their rank and stability claims use exact
integer and rational arithmetic, rather than a numerical rank threshold.

The [complete theorem and certificate](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/three-queries.html)
give the basis order, minor and frame bound. The lower bound applies to
the integral-symmetry family and its positive-integral relaxation. Necessity
for the smaller set of actually Coulomb-realizable molecules is unproved.

## The structure behind the count

Represent a state by a real 3-by-3 matrix: one index records the missing
alpha electron, and the other records the beta electron. In this
hole/electron representation the complete family has the unique form

```math
\Phi(X)=tX+[K,X]+\sum_{a,b=1}^{5}C_{ab}[T_a,[T_b,X]],
```

where \([A,X]=AX-XA\), \(K\) is traceless real symmetric, the five
\(T_a\) form a fixed basis of traceless symmetric 3-by-3 matrices, and
\(C\) is real symmetric 5-by-5. The parameter count is

```math
1+5+15=21.
```

A compressed Choi reshuffling separates the interaction coefficients from
the scalar and one-body terms and proves uniqueness. With unrestricted
one-electron terms, the existence of a positive integral Gram representative
is exactly the condition \(C\succeq0\). This is a useful admissibility
test. It does not prove that an arbitrary such tensor comes from actual
orbitals interacting through the Coulomb potential.

[Read the derivation, integral gauge and positivity statement](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/normal-form.html).

## Recovery with imperfect actions

Let \(Y\) be the observed 9-by-3 action cache. The decoder computes the
unique structured least-squares estimate \(\widehat H\). Suppose the
aggregate raw action error obeys \(\|Y-HV\|_F\le\epsilon\), and put
\(d=\|Y-\widehat HV\|_F\). The full linear family is consistent precisely
when \(d\le\epsilon\), and every compatible operator satisfies

```math
\|H-\widehat H\|_F\le r_H,
\qquad r_H=\sqrt{20(\epsilon^2-d^2)}.
```

This is a certified upper bound; the constant is not asserted sharp. The
raw inverse-noise constant is at most \(\sqrt{20}\). Normalizing each probe
to unit length changes that constant to \(\sqrt{60}\). The decoder keeps
these error units explicit and rejects inconsistent caches.

For a real source with \(\|b-\widehat b\|\le\delta\), define the resolvent
response at energy \(E\) and positive broadening \(\eta\) by

```math
g=b^{\mathsf T}\bigl((E+i\eta)I-H\bigr)^{-1}b.
```

The recovered center \(\widehat g\) obeys

```math
|g-\widehat g|\le
\frac{\|\widehat b\|^2r_H}{\eta^2}
+\frac{\delta(2\|\widehat b\|+\delta)}{\eta}.
```

Rational inputs give exact rational decoding and response centers; square
roots are enclosed outward by rational bounds. These certificates are
conditional on valid action and source error caps. The molecular example
below measures its action cap independently.

## Information beyond total spin

An exact example separates two operators that have the same three-probe
cache, preserve the same total-spin operator and share the spectral interval
\([-1,1]\). One belongs to the positive-integral family; the other lies
outside the integral-symmetry family.

Their pi-scaled local density of states differs by about **0.06140**. At the
stated nonzero action and source error caps, the structured response radius
is below **0.001336**, excluding the outside-family response. This proves a
strict information gain from integral structure even after spin conservation
is supplied to the comparison class. It does not establish a runtime
advantage over a method targeted at one observable.

[Inspect the exact operators, fractions and error comparison](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/spin-comparison.html).

## A reduced model from the H10 integrals

The arithmetic test starts from the stored H10 integral fixture. Spatial
orbitals 0, 1 and 2 are frozen doubly occupied, orbitals 3, 4 and 5 are
active, and orbitals 6 through 9 are empty. The active sector has two alpha
and one beta electrons. Symmetry completion of the stored integrals is
defined explicitly before evaluation.

The frozen-core formula agrees exactly with an embedded ladder-operator
projection. Three binary64 actions are then compared against rational
reference actions, including the error from converting the Hamiltonian to
binary64.

| Quantity | Checked result |
|---|---|
| Active determinant space | 9 states |
| Aggregate action-error cap | Approximately \(2.092\times10^{-15}\) |
| Broadening | \(0.01\) Hartree |
| Source | First active determinant, exact norm 1 |
| Response center | Approximately \(-16.9789009973742-3.17602569421687i\) |
| Certified response radius | Less than \(9.314\times10^{-11}\) |
| Integral admissibility | Exact positivity and a positive margin for every compatible operator |

The disk contains the exact rational response of this declared nine-state
model. Its small radius bounds **arithmetic error**, not the error from
freezing orbitals, choosing a finite basis or approximating the original
neutral state. The source is an exact Slater determinant, rather than the
original neutral-state annihilation source. The evaluation energy uses the
stored approximate neutral reference as a fixed coordinate.

[Read the model contract](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/frozen-core.html)
· [Inspect the saved qualification](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/chemistry_stage14/molecular-audit-001/qualification.json)
· [Inspect the rational response certificate](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/chemistry_stage14/molecular-audit-001/molecular_certificate.json).

## Evidence and replay

The exact audit passed **82 named checks, covering 260 aggregated cases**.
It compares all 27 integral generators with a separate full-Fock
Jordan–Wigner construction, checks the normal-form identities and integral
gauge, certifies the probe rank and frame bound, and exercises decoding,
noise, inconsistency and positivity cases. The molecular audit checks the
finite projection and exact reference inclusion separately.

The proofs received a same-author adversarial self-review. A second matrix
implementation is a computational cross-check, not independent expert
review or proof-assistant verification.

- [Read the proof self-review](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/review.html).
- [Read the exact audit results](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/chemistry_stage14/exact-audit-001/checks.json).
- [Download the focused replay bundle](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/Stage14_Fixed_Spin_Recovery.zip): proofs, Python code, probes, saved certificates and the required input arrays.
- [Follow the replay instructions](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/reproduce.html).
- [Inspect the export manifest](https://KomorebiP.github.io/Operation-KOMOREBI/assets/chemistry/stage14/export.json) for file hashes and input-view provenance.

The small replay input retains exactly the shapes, types and element bytes
of the original fixture's `h1`, `eri` and `ground_energy` arrays. Unused
state vectors are omitted. Its NPZ container hash therefore differs from
the full original fixture; this is recorded explicitly. Replaying it gives
the same Hamiltonian, action-error cap and response. Original host-specific
runtime logs and the full earlier research history are outside this focused
export.

## What remains open

The original 52,920-state H10 ion response has not received a physical
approximation-error certificate from this result. Larger sectors need new
dimension and query arguments. Optimal conditioning, actual Coulomb
realizability, discarded-space coupling, source leakage and a fair runtime
comparison with certified Krylov methods remain research tasks.

The previous ten-query theorem concerns a different, twenty-state arbitrary
two-body operator class. Three versus ten queries is not a speed comparison
on the same input.

General recovery from matrix-vector products and least-squares inversion
are established methods; see Halikias and Townsend's
[*Structured matrix recovery from matrix-vector products*](https://arxiv.org/html/2212.09841v2).
The exact normal form, explicit probe certificate and response-separation
construction are candidate contributions. **Originality, priority and
publication significance remain unestablished.** The
[bounded source comparison](https://KomorebiP.github.io/Operation-KOMOREBI/read/computational-chemistry/literature.html)
records what was inspected and what is still missing.
