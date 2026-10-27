# The ABC Three-Channel Signal

## Companion verification release

This release audits the recent chain connecting the COS method, a three-channel arithmetic signal, an exact circulant perfect-reconstruction block, Eisenstein factorization, the Frey invariants, and a rational 3-isogeny.

The main finite-dimensional identities are proved in the paper and checked by exact symbolic and integer computation. The release does **not** claim a proof of the `abc` conjecture.

## Main outputs

- `ABC_Three_Channel_Companion_Verification.pdf`
- `ABC_Three_Channel_Companion_Verification.tex`
- `verify_three_channel_companion.py`
- `independent_verify.py`
- `make_figures.py`
- `tables/` with worked examples, 250 random audits, and 400 representation-count checks
- `results/verification_results.json`
- `results/independent_verification.json`
- eight vector figures with matching PNG copies

## Reproduction

```bash
python verify_three_channel_companion.py
python make_figures.py
pdflatex -interaction=nonstopmode -halt-on-error ABC_Three_Channel_Companion_Verification.tex
pdflatex -interaction=nonstopmode -halt-on-error ABC_Three_Channel_Companion_Verification.tex
pdflatex -interaction=nonstopmode -halt-on-error ABC_Three_Channel_Companion_Verification.tex
python independent_verify.py
```

## Claim boundary

The four supplied COS and spectral sources support the transform, filtering, periodogram, and analytic-recursion principles. They do not state the arithmetic theorems proved in the companion.

The factor `1/(q-1)` in a proposed transformed Ramanujan filter is not treated as canonical without a specified averaging measure. The double-atlas expansion-rigidity theorem remains open.
