# Source record: level lowering for the (3,5,7) route

Date checked: 2026-09-19. Scope: exact theorem extraction, notation
translation and hypothesis verification. This is not a novelty search.

The mathematical result and application proof are in
`../notes/level_lowering.md`. The independent cyclotomic-restriction and
Fontaine–Laffaille reviews are in
`../notes/level_restricted_irred_review.md`. Bibliographic metadata and
hashes are in `level_sources.json`.

| Primary source and exact version | What was checked |
|---|---|
| [Pacetti–Villagra Torcomian, arXiv:2512.17845v1](https://arxiv.org/pdf/2512.17845v1), 19 December 2025 | Theorem 7.8, its proof and its cited dependencies; plus-motive normalization; the conductor range at three and five. Seven is not excluded by Theorem 7.8, but its abbreviated proof omits the cyclotomic-restriction check required by the cited lifting theorem. |
| [Golfieri Madriaga–Pacetti, arXiv:2412.08804v2](https://arxiv.org/pdf/2412.08804v2), 17 December 2025 | Theorem 4.2 removes variable primes including two; Theorem 4.3 gives residual finite flatness. Theorem 6.2 is the plus-motive modularity result after interchanging the cubic and quintic variables and inverting the parameter. Its condition concerns an equation coefficient, which equals one here. |
| [Billerey–Chen–Dieulefait–Freitas, arXiv:2205.15861v5](https://arxiv.org/pdf/2205.15861v5), arXiv date 16 April 2025, internal manuscript date 17 April 2025 | Theorem 2.8 gives the cyclotomic determinant for polarized real \(\mathrm{GL}_2\)-type abelian varieties. Lemma 6.9 and the proof of Theorem 8.3 supply the additional irreducibility after cyclotomic extension from semistable local inertia. The longer manuscript expressly warns that its numbering differs from the published shorter paper. |
| [Breuil–Diamond, arXiv:1208.5367v3](https://arxiv.org/pdf/1208.5367v3), 4 September 2013 | Theorem 3.2.2, printed pp.36–37. It needs residual modularity, cyclotomic-restricted irreducibility, a suitable determinant lift, and compatible local lifts with parallel weights \((0,1)\). It produces a modular lift with the selected Weil–Deligne types. Its extra small-image restriction is for residual characteristic five, not seven. |
| [Fontaine–Laffaille, published scan](https://www.imo.universite-paris-saclay.fr/~fontaine/laffaille.pdf), Ann. Sci. ENS 15 (1982), 547–608; [journal record](https://www.numdam.org/item/ASENS_1982_4_15_4_547_0/) | §§9.10–9.12 identify finite-flat models with the relevant torsion filtered modules. Theorem 5.3 and Remark 6.13(b) justify the determinant weights. §§7.12–7.15 and Theorem 8.4 realize lifted strongly divisible modules integrally and crystallinely. The audit applies the theory with parameter \(E=\mathbf Q_7\), preserving a commuting unramified coefficient action. |

## Corrections and application boundaries

PV v1 cites GP Theorem 6.3 for both modularity assertions in its Theorem
2.4. In the checked GP v2, Theorem 6.2 is the relevant plus assertion;
Theorem 6.3 is a minus assertion with a larger exponent restriction.
Using the latter literally would not justify the required modularity.
The corrected plus result applies here.

The quadratic coefficient field is inert at seven. Replacing its residue
field by \(\mathbf F_7\) would erase a real hypothesis check; the proof
uses the two \(\mathbf F_{49}\)-coefficient components explicitly.
The modular target's own coefficient field and its primes above seven
remain unconstrained by this alone.

The proof retains the original local types at three and five. It does
not rely on interpreting an unspecified level-lowering citation as a
theorem that the minimal residual conductor is automatically attained.
It also separates finite flatness from the existence of a crystalline
parallel-weight-two lift and verifies the latter independently.

PV's exact modulo-25 conductor branch computation was read, but its
Magma computation was not replayed. The theorem proved by this audit
needs only its stated local conductor range \(\{2,3\}\). This source
dependence is distinct from the new seven-specific compatibility checks.

## Acquisition and reproducibility boundary

The project-local cache was queried first by exact identifier
`arxiv:2512.17845v1`; no cache was present. Four public arXiv PDFs were
downloaded to temporary files and extracted with `pdftotext -layout`.
The BCDF request used the unversioned endpoint, whose downloaded first
page identifies v5; the recorded digest pins those bytes. Fontaine–
Laffaille's primary PDF was inspected through the web reader and then
downloaded and extracted; its digest is also recorded. Full source PDFs are not included in the
deliverable. The saved JSON records retain the hashes and extraction
status rather than implying that a hash certifies a theorem.

Searches included the exact PV identifier, the names/titles of its BD and
BCDF references, GP's identifier, and the original Fontaine–Laffaille
paper. Search snippets and secondary hits were discovery aids only.
All load-bearing extracted statements were checked in primary text.
The published BCDF DOI endpoint was unavailable; the exact long-version
theorems above were read instead and cited with their own numbering.

No global nonexistence claim follows from this source audit. The output
is a valid modular attachment theorem conditional only on the original
residual absolute irreducibility, together with its established
\(14\nmid C\) application.
