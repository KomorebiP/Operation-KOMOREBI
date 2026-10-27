# From a proposed correction to a checked certificate

This example connects the monograph's chapter **“Certifying an inexact protected correction”** to one executable certificate and the general Lean theorems behind its bounds. Python 3 and its standard library are sufficient. Run the commands from the publication package root.

Take the Euclidean spaces $E=\mathbb R^2$ and $Y=\mathbb R$, with

$$
d(x,y)=x,\qquad p(x,y)=x-y,\qquad f=(1,0),\qquad r=df=1,\qquad \alpha=1.
$$

Allowed corrections lie in the full protected kernel $H=\ker p=\{(t,t):t\in\mathbb R\}$. Write $T=d|_H$. The proposed correction is $a=(1/4,1/4)$, so the repaired candidate is $f-a=(3/4,-1/4)$ and its protected value remains $1$. The objective is

$$
J_1(t,t)=(t-1)^2+2t^2.
$$

Its unique minimizer is $a_1=(1/3,1/3)$. The certificate evaluates the proposal without computing this minimizer.

## Generate and verify the record

Save the following as `proposal.json`:

```json
{
  "d": [[1, 0]],
  "p": [[1, -1]],
  "f": [1, 0],
  "alpha": 1,
  "correction": ["1/4", "1/4"]
}
```

Then run:

```sh
python3 examples/inexact_repair_certificate.py --input proposal.json > certificate.json
python3 examples/inexact_repair_certificate.py --verify certificate.json
```

The second command exits with code `0` and prints:

```json
{
  "status": "PASS",
  "scope": "Exact finite certificate recomputation"
}
```

The generated record contains `schema`, `problem`, and `certificate`. Within `certificate`, the following values are exact rational strings or arrays of them:

| Field | Expected value |
| --- | --- |
| `candidate` | `["3/4", "-1/4"]` |
| `protected_before`, `protected_after` | `["1"]` in each field |
| `fit_residual`, `actual_candidate_residual` | `["3/4"]` in each field |
| `normal_residual` | `["-1/8", "-1/8"]` |
| `normal_residual_norm_squared` | `"1/32"` |
| `objective` | `"11/16"` |
| `dual_value` | `"21/32"` |
| `duality_gap` | `"1/32"` |
| `duality_gap_identity_residual` | `"0"` |
| `correction_error_norm_squared_upper` | `"1/32"` |
| `fitted_error_norm_squared_upper` | `"1/128"` |

For this input, fitting and actual residuals coincide because the datum is $r=df$. The input format also permits a separate measured datum, for which that equality need not hold.

## Why these numbers certify the proposal

The adjoint must use the inherited metric on $H$. In the kernel basis $B=(1,1)^{\mathsf T}$, the Gram matrix is $G=[2]$. The coordinate normal residual is $q=-1/4$, giving

$$
g=BG^{-1}q=(-1/8,-1/8),\qquad
\|g\|^2=q^{\mathsf T}G^{-1}q=1/32.
$$

The raw coordinate square is $q^2=1/16$. The program reports that separately as `coordinate_covector_norm_squared_not_a_Hilbert_certificate`.

Theorem WR13 bounds the squared correction error by $\|g\|^2/\alpha^2=1/32$ and the squared fitted error by $\|g\|^2/(4\alpha)=1/128$. The actual squared errors in this example are $1/72$ and $1/144$. These bounds concern the optimizer at the recorded positive parameter.

For the default dual witness $z=r-Ta=3/4$, Theorem WR14 gives

$$
J_1(a)-\mathcal D_1(z)=\frac{11}{16}-\frac{21}{32}=\frac1{32}.
$$

The actual objective excess is $J_1(a)-J_1(a_1)=1/48$. The duality gap bounds this excess and can be larger.

## Follow the general proof in Lean

All names below begin with `KomorebiSpace.`. Their source files are in `lean/KomorebiSpace/` and are imported by `KomorebiSpaceCombined`.

| Mathematical step | Lean declaration |
| --- | --- |
| An allowed proposal preserves the protected value | `ProtectedRegularizedRepair.proposal_preserves` |
| WR13: correction and fitted error bounds | `RegularizedHilbertRepair.correction_error_bound`, `RegularizedHilbertRepair.fitted_error_squared` |
| WR14: exact gap and the residual witness | `RegularizationCertificates.primal_dual_gap`, `RegularizationCertificates.residual_witness_gap` |
| A duality gap controls correction error | `RegularizationCertificates.gap_controls_correction` |
| WR15: full-kernel coordinates retain the inherited Hilbert metric | `CoordinateCovector.protected_coordinate_certificate` |

The certificate bounds assume real Hilbert spaces, a continuous linear restricted map, a proposal in the actual protected kernel, and $\alpha>0$. A dual witness may be arbitrary. The coordinate theorem uses a basis of the entire kernel and orthonormal ambient and residual coordinates. The finite Euclidean problem above meets these hypotheses. See the Lean guide's chapters **“Regularized repair and certificates”** and **“Coordinates without an orthonormal kernel basis”** for the interfaces, and `lean/USAGE.md` for the pinned environment and build instructions.

## What acceptance and rejection mean

The displayed inexact correction is accepted: passing does not mean it is the optimizer. Changing its `correction` to `["1/4", "0"]` is rejected with exit code `2` because it changes protected data. Altering `certificate.objective` in the saved record to `"0"` is also rejected with exit code `2`, because the claim disagrees with exact recomputation.

Verification recomputes the claims for the problem included in the record. A different valid problem with a consistently recomputed certificate is a different valid record. The caller must identify the recorded problem with the intended task. These exact finite Python computations are not a certified extraction from Lean and do not establish universal implementation correctness. The general proofs reside in the monograph and Lean development.

See [INEXACT_CERTIFICATES.md](INEXACT_CERTIFICATES.md) for the full input contract and additional examples.
