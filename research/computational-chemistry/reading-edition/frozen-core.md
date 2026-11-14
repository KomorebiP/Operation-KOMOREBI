# The declared H10-derived frozen-core model

**Komorebi P. · Reviewed reading edition · 13 November 2026**

This calculation checks the numerical recovery method on one exactly
specified finite model derived from H10 integrals. It does not bound the
physical approximation error of the full molecule.

## Input arrays and symmetry completion

The original fixture is `h10_1.4.npz`: a linear chain of ten hydrogen atoms,
with adjacent separation 1.4 angstroms, represented in the STO-3G basis.
The retained generator uses a real restricted Hartree–Fock orbital basis.
These are properties of the finite input model, not claims of basis-set
convergence. Its full-container SHA-256
is recorded in `FIXTURE_VIEW.json`. Every finite binary64 input entry is
interpreted as an exact dyadic rational, not as an unknown exact molecular
integral.

Before evaluation, define

$$
h=\frac{h_{\mathrm{raw}}+h_{\mathrm{raw}}^{\mathsf T}}2,
\qquad
G=\frac{G_{\mathrm{raw}}+G_{\mathrm{raw}}^{\mathsf T}}2,
$$

where $G$ is the matrix indexed by unordered spatial pairs. Restore
within-pair symmetry using the zero-based packed index

$$
\operatorname{pair}(p,q)
=\frac{m(m+1)}2+n,
\qquad m=\max(p,q),\quad n=\min(p,q).
$$

Then $g_{pqrs}=G_{\operatorname{pair}(p,q),\operatorname{pair}(r,s)}$.
This is a declared symmetry-completed model. It is not silently substituted
for an earlier operator assembled with different stored-bit conventions.

## Frozen and active orbitals

Freeze spatial orbitals 0, 1 and 2 doubly occupied. Keep orbitals 3, 4
and 5 active with two alpha and one beta electrons. Keep orbitals 6, 7,
8 and 9 empty. The retained space has nine determinants, with a total of
five alpha and four beta electrons.

Relabel the active orbitals 3, 4 and 5 as 0, 1 and 2 when using the
probe matrix and determinant table. The frozen-core occupations are
implicit in those nine active coordinates.

The source fixture's ion sector has four alpha and five beta electrons.
The present calculation uses the spin-conjugate component of the declared
spin-free model. Relating it to a differently assembled numerical target
requires the basis/embedding check described in the
[full-model bridge](model-error.md).

For frozen indices $i,j\in\{0,1,2\}$ and active indices
$p,q\in\{3,4,5\}$, define the electronic core energy and effective
one-body matrix by

$$
E_{\mathrm{core}}=2\sum_i h_{ii}
+\sum_{i,j}\bigl(2g_{iijj}-g_{ijji}\bigr),
$$

$$
h^{\mathrm{eff}}_{pq}
=h_{pq}+\sum_i\bigl(2g_{pqii}-g_{piiq}\bigr).
$$

Use the restricted active $g$ and include $E_{\mathrm{core}}I_9$.
The calculation uses electronic energies throughout; no nuclear constant
is inserted into only one side of the comparison.

An explicit ladder-operator projection in the first six spatial orbitals
agrees with this formula exactly. Its 564 nonzero quartic projection terms
are included. Contributions involving the four always-empty orbitals have
zero matrix elements within the projection. This identity validates the
finite model and indexing; it is not a bound on coupling to discarded
states.

## What the arithmetic qualification measures

Construct the exact rational matrix $H_{\mathrm{red}}$. Convert it to
binary64 and perform the three products with the raw integer probes $V$.
Convert the observed binary64 products back to exact dyadics and evaluate

$$
\epsilon_{\mathrm{actual}}^2
=\|Y-H_{\mathrm{red}}V\|_F^2
$$

exactly. Round the square root outward at 80 binary places. Thus the cap
includes both Hamiltonian conversion and matrix-product rounding, rather
than being inferred from a small floating-point residual.

The source is the first active determinant, $b=e_0$, with exact norm 1
and source radius zero by definition. Set $\eta=1/100$ Hartree and

$$
E=E_{\mathrm{neutral,stored}}+\frac12\text{ Hartree}
\approx-11.868299456410346\text{ Hartree}.
$$

The stored neutral reference is approximate. Here it is a fixed evaluation
coordinate, not a certified neutral ground-state energy. The source is not
the original neutral-state annihilation source.

## Qualified output

| Quantity | Result in the checked run |
|---|---|
| Active space | Nine determinant states |
| Raw action count | Three |
| Aggregate action cap | Approximately $2.092\times10^{-15}$ Hartree |
| Positive-integral check | Exact Gram and $C$ positivity; the all-compatible margin passes |
| Response center | Approximately $-16.9789009973742-3.17602569421687i$ per Hartree |
| Response radius | Less than $9.314\times10^{-11}$ per Hartree |

The exact rational nine-state response lies inside the returned disk. The
qualification records contain the full fractions; decimals here are not
used as proof thresholds. The arithmetic radius is a complex-response
bound and also bounds the pi-scaled density error. Divide it by $\pi$
for the unscaled source-resolved density interval.

## Public input view and reproducibility

The focused replay keeps only `h1`, `eri` and `ground_energy`, the three
arrays read by this calculation. Their shapes, types and element bytes
match the corresponding original arrays. The smaller NPZ container has a
different hash, and its identity is recorded separately.

The checked replay reproduced the qualified scientific values exactly;
the reported fixture-container hash changed as intended. A new platform
or numerical-library build may change the floating products and resulting
cap. The replay measures its own cap against exact arithmetic and must
validate its own response inclusion. It should not copy a saved cap onto
different numerical outputs.

[Replay instructions](reproduce.md) distinguish the original historical
results from fresh validation records. The
[conditional full-model bound](model-error.md) lists the truncation,
source and energy-reference caps still needed for a full-H10 accuracy
claim. Reference construction and validation costs are separate from the
three-query identification count.
