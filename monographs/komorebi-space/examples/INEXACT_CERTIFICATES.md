# Certifying a proposed correction

`inexact_repair_certificate.py` evaluates a proposed rational correction without computing the regularized optimizer. It uses the entire protected kernel, its inherited Euclidean metric, and a positive regularization parameter.

Run commands from the package root. The default command prints four complete problem-and-certificate records:

```sh
python3 examples/inexact_repair_certificate.py
```

The examples cover a nonorthogonal kernel, a rescaled basis for the same correction, a nonzero proposal for the zero operator, and a fully protected candidate.

## Create and verify a certificate

Save the following problem as `proposal.json`:

```json
{
  "d": [[1, 0]],
  "p": [[1, -1]],
  "f": [1, 0],
  "alpha": 1,
  "correction": ["1/4", "1/4"]
}
```

Generate a record, then verify that saved record:

```sh
python3 examples/inexact_repair_certificate.py --input proposal.json > certificate.json
python3 examples/inexact_repair_certificate.py --verify certificate.json
```

Successful verification prints `"status": "PASS"` and exits with code 0. Verification expects one complete object containing `schema`, `problem`, and `certificate`. To verify an individual default demonstration, save one object from its four-element output array. A certificate whose claims differ from exact recomputation is rejected with exit code 2.

## Input fields

| Field | Meaning |
| --- | --- |
| `d` | Residual operator matrix, with at least one row |
| `p` | Protected-observable matrix, which may have no rows |
| `f` | Original candidate, with positive dimension |
| `alpha` | Strictly positive regularization parameter |
| `correction` | Proposed correction `a`, in the full kernel of `p` |
| `measured_residual` | Optional fitting datum, defaulting to `d f` |
| `basis` | Optional matrix whose columns form a basis of the full protected kernel |
| `dual_witness` | Optional residual-space witness, defaulting to the fit residual |

Entries must be integers or rational strings such as `"1/2"`. Floating-point entries, Boolean values, nonpositive parameters, malformed dimensions, and corrections that change protected data are rejected. The candidate and correction have the same dimension, and the residual datum and dual witness match the number of rows of `d`.

For an ambient dimension `n` and kernel dimension `k`, a supplied basis has `n` rows and `k` columns. The program checks independence and membership in the protected kernel. The required column count ensures that it spans the entire kernel. If the kernel is zero-dimensional, each of the `n` basis rows is empty.

## Reading the output

The candidate is `f - a`. The record includes its protected value before and after correction, its fit to the supplied datum, and its actual residual under `d`. The fit and actual residual can differ when measured data are supplied independently.

For a basis matrix `B`, let `G = BᵀB`, `S = dB`, and `a = Bc`. The coordinate normal residual is the covector

$$
q=(S^{\mathsf T}S+\alpha G)c-S^{\mathsf T}r.
$$

Its Hilbert representative and squared norm are

$$
g=BG^{-1}q,\qquad \|g\|^2=q^{\mathsf T}G^{-1}q.
$$

The output retains both the Gram-corrected norm and the raw coordinate-covector norm. Only the Gram-corrected quantity is the Hilbert certificate. The record also contains exact primal and dual objective values, the gap identity, and squared optimizer-error bounds. An arbitrary dual witness may give a valid but loose bound.

For the displayed input, the candidate is `(3/4, -1/4)`, the protected value remains `1`, and the squared normal-residual norm is `1/32`. The primal objective is `11/16`, the default dual value is `21/32`, and their gap is `1/32`. The squared correction-error bound is `1/32`, while the squared fitted-error bound is `1/128`.

Squared bounds avoid rounding square roots. They concern the exact regularized optimizer for the recorded maps, datum, and positive parameter. They do not assert that an exact unregularized realization exists or that measured data equal the actual data.

## Scope of verification

Verification recomputes every reported claim from the included problem. It checks consistency of that mathematical record. The caller must still identify the recorded operator, observable, datum, and parameter with the intended task. Replacing the problem and recomputing a valid certificate produces a valid record for that different problem.

The implementation uses exact rational arithmetic and is accompanied by finite computational evidence. It is not a universally verified Lean extraction. General mathematical guarantees and the scope of the formal development are described separately in the monograph and Lean guide.
