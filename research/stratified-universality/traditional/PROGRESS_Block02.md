# Komorebi Stratified Universality - Block 02 Progress Note

**Version:** 1.2.0 Block 02  
**Date:** 29 August 2026  
**Manuscript:** *Stratified Universality for Resolved Representations: Finite Profiled Atlases, Descent, and the C-Finite Three-Chart Theorem*

## Block objective

Block 01 established the common resolved foundation and the additive-Karoubi envelope. Block 02 develops the next required layer: the concrete stratum atlas, the distinction between reversible and directional bridges, explicit information-loss profiles, overlap coherence, and the obstruction objects that measure failure of global compatibility.

## Material added

### 1. Profiled stratum passports

A stratum is now recorded by

\[
\mathbf S_\alpha=
(\mathcal C_\alpha,\Pi_\alpha,\mathcal M_\alpha,
 \mathcal N_\alpha,\operatorname{Sem}_\alpha,\mathcal I_\alpha).
\]

The record separates the ambient category, admissible models, verified preservation profile, native semantics, normalized subcategory, and invariant target. The manuscript also defines normalization witnesses and completeness only relative to a declared normalized classification domain.

An eight-stratum registry now covers:

- finite linear and C-finite systems
- holonomic systems
- digital systems
- algebraic branches
- nonlinear and rooted-tree systems
- product and multiplicative systems
- local, Mahler, and polyphase systems
- Galois and Tannakian systems

Each row names exact existing slices and the boundary that remains open.

### 2. Representation groupoids and directed transformations

Coordinate equivalence is formalized through action groupoids

\[
[\operatorname{Rep}_{\mathbf d}(\mathbb K)/G_{\mathbf d}],
\qquad
G_{\mathbf d}=\prod_X GL_{d_X}.
\]

Gauge symmetry, intrinsic automorphisms, and reconstructed Tannakian symmetry are kept distinct. Noninvertible quotient, truncation, completion, specialization, annihilator, and compression maps live in a separate directed transformation category.

### 3. Bridge passports and information loss

Every certified bridge now carries a passport recording:

- exact domain and codomain subcategories
- bridge class
- preserved and reflected structures
- semantic comparison
- normalization compatibility
- residual and certificate transport
- information-loss profile

The bridge taxonomy distinguishes equivalences, fully faithful inclusions, conservative forgetful functors, information-losing maps, constructors, completions, partially defined bridges, and absent uncertified bridges.

Object collapse, morphism collapse, and essential-image loss are defined separately. A composition theorem proves that collapse can only increase under further directional composition, while conservativity, classification-faithfulness, and equivalence compose under their stated hypotheses.

### 4. Overlap categories and higher coherence

Reversible overlaps now require explicit equivalences and semantic comparison isomorphisms. A bridge-law certificate has six gates:

1. semantic commutation
2. packet analysis and synthesis
3. refinement and coarsening
4. named residuals
5. proof or computation certificates
6. normalization and invariant comparison

Triple-overlap comparison cells are introduced, and the quadruple-overlap coherence defect

\[
\Omega_{\alpha\beta\gamma\delta}
\]

is defined as the ratio of the two composites from a three-bridge chain to the direct overlap bridge. Vanishing is exactly the pseudofunctor coherence condition.

### 5. Reversible cores inside directional bridges

For a split bridge

\[
X\xrightarrow{A}Y\xrightarrow{L}X,
\qquad LA=I,
\]

Block 02 proves that \(E=AL\) is idempotent, that

\[
Y\cong\operatorname{im}E\oplus\operatorname{im}(1-E),
\]

and that \(A:X\to\operatorname{im}E\) is an isomorphism. The ambient packet chart remains directional, while its consistent core is reversible and the complementary component is retained as a named residual.

### 6. Four typed obstruction theories

The manuscript now separates four noninterchangeable obstruction roles.

#### Finite holonomy

A spanning-tree gauge reduces gluing to fundamental holonomies \(H_e\). The maximal path-flat core is

\[
C_o=\bigcap_{e\notin S}\ker(H_e-I)
    =\ker\Delta_S,
\]

with

\[
\dim C_o=\dim F_o-\operatorname{rank}\Delta_S.
\]

The full fibers possess one global frame exactly when all fundamental holonomies are the identity.

#### Relative cokernel obstruction

For a declared correction map \(D:U\to V\) and defect \(r\in V\), the obstruction is

\[
\operatorname{Ob}_D(r)=[r]\in\operatorname{coker}D.
\]

Vanishing is equivalent to the existence of an allowed correction. Naturality, packet decomposition, coarse loss, and the mapping-cone extension are included, while the dependence on the declared correction map remains explicit.

#### Brauer obstruction

Linear semilinear cocycles descend effectively by Hilbert 90. Projective descent instead carries the connecting class

\[
\delta(\alpha)\in H^2(G,L^\times)=\operatorname{Br}(L/K).
\]

Its vanishing is exactly the lifting condition from projective to linear descent. Tannakian reconstruction is kept behind the additional requirement of a faithful exact tensor fiber functor.

#### Higher coherence obstruction

The natural automorphism \(\Omega_{\alpha\beta\gamma\delta}\) detects incompatibility among pairwise comparison conventions on quadruple overlaps. It is not identified with holonomy, a cokernel class, or a Brauer class without an explicit typed comparison map.

## New figures

- `stratum_passport`
- `bridge_passport_and_loss`
- `flat_core_holonomy`
- `obstruction_comparison`

## Validation

- 67 letter-size pages
- complete LaTeX build with `latexmk`
- no overfull or underfull boxes in the final log
- no unresolved references or undefined control sequences
- all fonts embedded
- all 67 pages rendered and visually inspected
- source package prepared for a clean extraction rebuild

## Exact boundary after Block 02

Block 02 supplies the vocabulary and finite theorem layer needed to state a concrete atlas correctly. It does **not** yet assert that the entire heterogeneous atlas is a pseudofunctor or an effective stack. Missing bridges remain missing, and a pairwise bridge is not promoted to an equivalence without inverse or recognition evidence.

The next progressive block should deepen the finite assembly layer: freeze the first explicit finite atlas, verify each bridge-law passport, prove the nonempty triple-overlap coherence equations, and establish effective descent for both objects and morphisms in that selected atlas.
