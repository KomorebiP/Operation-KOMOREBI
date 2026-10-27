# Komorebi Stratified Universality Foundations v1.16.0

## Consolidated foundations edition

This directory contains the journal-facing source of **Stratified Universality
for Resolved Representations**. The proof architecture is organized around a
theorem spine rather than the chronological development sequence:

1. resolved syntax and the additive-Karoubi envelope;
2. normalized representation strata;
3. reversible overlaps and directional bridge passports;
4. finite atlas assembly, coherence, and effective descent;
5. compatible native invariants;
6. componentwise global completeness on the certified atlas;
7. finite profiled lane analysis, transport, refinement, selection, residuals,
   realization, fold loss, and certified descent;
8. holonomy-twisted transport, matrix local systems, monodromy-orbit
   coarsening, and orbital composition.

The Block 15 theorem identifies a morphism at a complete finite declared
resolution with its unique source-target lane matrix. Block 16 proves that
nontrivial address holonomy does not destroy this transport calculus. Instead,
local matrices form a matrix local system, descended morphisms are compatible
sections, and evaluation at one chart yields the loop-invariant part of one
matrix fiber. Ordinary fixed labels reappear at the monodromy-orbit
coarsening.

Residue projectors are direct additive lane realizations. The factorial
step-product is a separate exact multiplicative companion transported through
a specified multilinear multiplication map. The holonomy extension does not
identify these doctrines.

## Build

Windows PowerShell:

```powershell
& .\Build.ps1
```

Full historical recomputation:

```powershell
& .\Build.ps1 -FullRegression
```

Linux or macOS:

```bash
./Build.sh
./Build.sh --full
```

The normal build replays the recent theorem suites, runs the Block 15 and Block
16 exact verifiers, regenerates current LaTeX components, compiles the
integrated manuscript, refreshes the Block 16 publication audit, recompiles the
audit table, and builds the standalone note.

The integrated target is:

```text
Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex
```

The standalone target is:

```text
../standalone/Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex
```

## Exact validation

`verify_block15_lane_transport.py` records 197,099 exact assertions for the
finite-profile base theorem.

`verify_block16_holonomy_lane_transport.py` records 1,344,823 exact assertions
covering finite monodromy actions, orbit descent, pair-orbit intertwiner bases,
orbital structure constants, selector controls, equivariant refinement,
rational cyclotomic projectors, and theorem-source contracts.

`verify_block16_publication_audit.py` checks the complete TeX input graph,
abstract length, theorem labels, references, citations, graphics, environment
balance, theorem concordance, exact validation record, compiled PDF, metadata,
and LaTeX log. Its machine-readable result is
`results/block16_publication_audit.json`.

These computations guard against implementation, transcription, packaging,
and synchronization errors. They do not replace the symbolic proofs or
independent mathematical review.

## Claim boundary

The theorem is finite and profiled. It assumes split lane systems, invertible
chart transitions, coherent address and splitting cocycles, and preservation
of all used operations. It does not establish infinite convergence,
noninvertible or nonsplit descent, higher-stack effectivity, or a canonical
lane system independent of the initial presentation. Address and orbit counts
are not identified with dimension, rank, entropy, information, or complexity.
