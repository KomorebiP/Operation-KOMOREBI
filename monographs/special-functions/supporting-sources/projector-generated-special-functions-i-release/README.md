# Projector-Generated Special Functions I

**Author:** Komorebi P.

This release contains a complete LaTeX paper and one Python asset generator for a special-function theory built from projector and polyphase operations.

## Main outputs

- `Projector_Generated_Special_Functions_I.pdf`
- `Projector_Generated_Special_Functions_I.tex`
- `projector_generated_special_functions.py`
- `figures/` with 26 vector-PDF and 26 PNG figures
- `tables/` and `generated_tables/`
- `results/` with numerical and verification ledgers
- `tests/test_special_functions.py`

## Rebuild

From the extracted source directory:

```powershell
python build_all.py
```

The build is offline. It regenerates every figure and table, runs the tests, and compiles the manuscript three times.

## Mathematical scope

The paper proves:

- exact polyphase reconstruction of analytic germs
- the carry-shift representation of multiplication
- the packet Euler operator and Weyl commutator
- the differential-lift theorem
- Bernoulli-Hurwitz packet reconstruction and refinement
- the differential ladder and translation law
- cyclotomic Bernoulli-Lerch details, inverse synthesis, and Parseval
- the Bernoulli-Euler two-channel identity
- a parity law for third-root cyclotomic norms
- generalized reciprocal L-function transfer identities
- the Mellin and Poissonization formulas
- the diagonal packet-energy asymptotic
- the long-time diagonal power identity
- the coherence reformulation of the Baez-Duarte criterion

The paper does not claim that all generated functions are historically new. It does not prove the Riemann hypothesis. The Mobius packet coherence inequality is an open theorem target equivalent to the known Baez-Duarte criterion after the proved energy asymptotic.
