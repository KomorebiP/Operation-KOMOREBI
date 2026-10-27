# Certifying a proposed correction

`inexact_repair_certificate.py` verifies a proposed rational correction without calling an exact optimizer. It keeps the actual protected kernel, its inherited Euclidean metric, and the positive regularization parameter explicit.

```sh
python3 examples/inexact_repair_certificate.py
python3 examples/inexact_repair_certificate.py --input problem.json
python3 examples/inexact_repair_certificate.py --verify certificate.json
```

Run the default command to see four complete input/output examples. Copy a `problem` record as the input format. Integers and rational strings are accepted. Floating-point entries, Boolean values, nonpositive parameters, malformed dimensions, and corrections outside the declared kernel are rejected.

Optional input fields include an independent measured residual, a full independent kernel basis, and an arbitrary dual witness. A supplied basis must span the entire protected kernel. The program checks independence, rank, and membership rather than assuming them.

The returned `certificate` includes the protected values before and after correction, measured fit, actual candidate residual, normal covector, Gram-corrected normal residual and its squared norm, primal and dual objectives, exact gap identity, and squared optimizer-error bounds. Verification mode recomputes the record from the included problem and rejects altered claims.

The normal-residual norm is not the Euclidean length of an arbitrary coordinate covector. With a basis matrix B and Gram matrix G, it is squared as q^T G^-1 q. The implementation reports squared error bounds to avoid rounding square roots. An arbitrary dual witness can give a valid but loose certificate.

All guarantees concern the declared regularized optimization problem. They do not certify that measured data equal actual data, or that an exact unregularized realization exists. The program is exact tested rational software, not a universally verified Lean extraction.

The independent suite `checks/inexact_certificates_exact.py` uses determinant-based full ambient constrained systems as its optimizer oracle. That oracle is outside the certificate program and supplies independent comparison evidence for the finite regression cases.

Verification establishes mathematical consistency with the included problem, not the authenticity of that problem. A caller must also match the recorded operator, observable, data and parameter to the task being certified. Changing the problem and recomputing a valid certificate creates a different valid problem instance, not an authenticated result for the original task.
