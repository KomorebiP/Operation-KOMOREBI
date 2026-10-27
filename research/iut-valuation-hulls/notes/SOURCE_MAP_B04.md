# Sources, anchors and boundaries

## Primary IUT volumes (copies retained from checked Block 03 predecessor)

1. `sources/iut/IUT_I_Construction_of_Hodge_Theaters.pdf` (Shinichi Mochizuki, May 2020). Abstract (PDF p. 1); Introduction §I1, particularly the explanation of Hodge theaters and theta links (PDF pp. 7, 11–13); original Definition 6.13. In the present model this motivates **distinguishing prime-strip-style information from ring data**. We do not implement Definition 6.13.
2. `sources/iut/IUT_II_Hodge_Arakelov_Theoretic_Evaluation.pdf` (December 2020). Abstract and Introduction, especially multiradiality and coricity (PDF pp. 1–4). Our `FactorsThrough` theorem is an elementary *analogue* of an observational descent condition; it is not the source's definition of multiradiality.
3. `sources/iut/IUT_III_Canonical_Splittings_Log_Theta_Lattice.pdf` (May 2020). Theorem 3.11, Remark 3.11.1, proof of Corollary 3.12 Steps (xi-d)–(xi-f). **Source-level witness preservation remains unproved in the Komorebi model.** See the inherited `notes/IUT_312_FIELD_TO_SOURCE_MAP.md`, `notes/IUT_312_OPEN_OBLIGATIONS.md` and `KTG/IUT312WitnessObligation.lean`.
4. `sources/iut/IUT_IV_Log_Volume_Computations.pdf` (May 2020). Weight and normalization consequences. The new B04 toy proof does not contain the source's determinant/procession normalization.

## Internal, separately preserved research

- `Komorebi_IUT_KTG_Block03_Checked_v0.3.0_2026-09-17.zip`: authoritative, fully replayed formal predecessor. The 22 preserved Lean sources have not been edited; `KTG.lean` gained imports for the two new files.
- `ABC_Global_IUT_RR5_2026-10-25.zip`: later independent IUT III numerical-realization audit, including the open source witness and quantitative error budget. Inspected but not copied into this package. Its established claims do not fill the IUT III witness gap.
- `Realization_Calculus_Volume_I_Komorebi_Space.pdf`: the Komorebi realization construction, semantic comparison, transport, obstruction, and realization-of-observation distinctions.
- `Realization_Calculus_Volume_II_Realization_Boundaries.pdf`: reconstruction limitations. These volumes were inspected from the user's Library and are not re-packaged here.

## Truth boundary

The model proves a *negative implication under precisely specified, insufficient data*. It is not a model of the full IUT hypotheses. Establishing a genuine theta-link theorem would require actual Frobenioid/prime-strip data, arithmetic structural identification, and a proof that all relevant measured invariants survive the permissible indeterminacies.
