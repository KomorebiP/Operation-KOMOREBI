# Source Map

## User-supplied IUT corpus

### IUT I

`sources/iut/IUT_I_Construction_of_Hodge_Theaters.pdf`

Themes retained in the audit:

- initial Θ-data
- Hodge theaters
- Θ-links
- Frobenius and étale pictures
- separation of arithmetic-holomorphic structures

### IUT II

`sources/iut/IUT_II_Hodge_Arakelov_Theoretic_Evaluation.pdf`

Themes retained in the audit:

- multiradiality
- coric, uniradial, and multiradial distinctions
- Kummer-theoretic theta evaluation
- conjugate synchronization
- theta and Gaussian monoids

### IUT III

`sources/iut/IUT_III_Canonical_Splittings_Log_Theta_Lattice.pdf`

Primary Block 03 landmarks:

- Proposition 3.9 and Remark 3.9.5, especially pp. 126–139
- Theorem 3.11, especially pp. 154–156
- Remark 3.11.1, especially pp. 159–163
- Corollary 3.12, pp. 173–174
- Step (xi-d), p. 183
- Step (xi-e), pp. 183–184
- Step (xi-f), p. 184
- Remarks 3.12.1–3.12.3

The detailed field-by-field mapping is in
`IUT_312_FIELD_TO_SOURCE_MAP.md`.

### IUT IV

`sources/iut/IUT_IV_Log_Volume_Computations.pdf`

Primary Block 03 landmarks:

- Theorem 1.10
- proof computations on pp. 27–29
- explicit `q^{j²}` and `j² log(q)` contributions, especially p. 28
- downstream use of IUT III Corollary 3.12

## Classification rule

Every source mapping is classified as one of:

1. **located source statement**
2. **formal interpretation**
3. **Lean-instantiated theorem**
4. **open theorem**

A page reference does not itself constitute a Lean proof. The verifier checks
the formal implementation and documentation contract, not the truth of the
source interpretation.

## External controversy references discussed in the project

These remain URL references in `external_refs/REFERENCES.md` and are not
embedded in this archive:

- Scholze–Stix, *Why abc is still a conjecture* (2018 report)
- Mochizuki's comments and responses concerning the 2018 discussions

The present formal audit is not a replacement for those documents and does not
adopt either side's conclusion by assertion.
