# Primary sources and predecessor lineage

The 2020 IUT PDFs were consulted from the pre-existing B04 source directory.
The B05 portable ZIP omits the four original PDFs to avoid unintentionally
redistributing third-party copyrighted materials. Reinsert legally held copies
into `sources/iut/` if a self-contained private working copy is required.

Original source files inspected, with SHA-256 of local originals:

| Paper | File | SHA-256 |
|---|---|---|
| Mochizuki, IUT I, Construction of Hodge Theaters | `IUT_I_Construction_of_Hodge_Theaters.pdf` | `283e690f7d0695be3bfa66e8d3a947c9751e95292b67811a5cf360617af14dc0` |
| Mochizuki, IUT II, Hodge-Arakelov-Theoretic Evaluation | `IUT_II_Hodge_Arakelov_Theoretic_Evaluation.pdf` | `68f2eee6d304241a394643a9c75932d32b376df41155335824a03b063baaae0a` |
| Mochizuki, IUT III, Canonical Splittings of the Log-Theta Lattice | `IUT_III_Canonical_Splittings_Log_Theta_Lattice.pdf` | `e484619ec0d8ed2d9ad21aca1572c9dcca576c76fbb59b4e3a27f7f59feb55a0` |
| Mochizuki, IUT IV, Log-volume Computations | `IUT_IV_Log_Volume_Computations.pdf` | `9e8cd3b89406970b7eadbfd0b3ee8f3994bb8f478860f4981ded2e445c19f4e0` |

Locations used: IUT I Abstract, introduction and §6; IUT II Abstract and
introduction; IUT III Theorem 3.11, Remark 3.11.1, Remark 3.9.5(vii), Corollary
3.12 Step (xi-c)–(xi-f); IUT IV explicit theta `j²` weights. The B04
`notes/IUT_312_FIELD_TO_SOURCE_MAP.md` supplies further page mapping.

Previous packages: `Komorebi_IUT_Hodge_Reduct_B04.zip` and
`Komorebi_IUT_KTG_Block03_Checked_v0.3.0_2026-09-17.zip`. All B04 Lean modules
were preserved byte-for-byte. `ABC_Global_IUT_RR5_2026-10-25.zip` was checked
for its numerical cofinality and unit-hull lattice arguments. No IUT-original
source construction was ported as a proved Lean term in B05.
