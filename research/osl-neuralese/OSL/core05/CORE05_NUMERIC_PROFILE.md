# OSL-Core 0.5 Numerical Profile

Status: finite executable profile for the Core 0.5 numerical/operator fragment

## 1. Scope

This profile defines the implemented behavior of:

- `space`;
- `vector`;
- `operator`;
- `apply`;
- `transport`;
- `check_projector`;
- `check_intertwiner`.

It also defines the corresponding native receipts and the independent numeric
verifier's comparison boundary. It is a finite floating-point profile, not an
exact real or complex algebra.

## 2. Numeric representation

Source arrays and matrices contain real numeric literals. Boolean values are
not treated as numbers. Parsed vector and matrix entries must be finite.
Malformed, ragged, nonnumeric, NaN, and infinite input is rejected before it
can enter semantic state.

The runtime converts accepted vector and matrix literals with
`numpy.asarray(..., dtype=float)`. In the supported environment this is NumPy
binary64 floating-point storage. Receipt-facing values are emitted as ordinary
JSON arrays of Python floats. Canonical JSON rejects NaN and infinity.

The profile does not promise bit-identical output across every processor,
NumPy build, BLAS/LAPACK implementation, or compiler configuration. Python,
NumPy, the floating-point environment, and numerical libraries remain part of
the trusted computing base.

## 3. Spaces

```text
space NAME dim N
```

`N` must be a positive integer. A committed declaration creates:

```json
{"name":"NAME","dim":N}
```

in the `spaces` table and emits `space_declare` with that exact object. Space
names are unique.

## 4. Vectors

```text
vector X in H values [x1, ..., xn]
```

The value must be a one-dimensional finite numeric array whose length equals
`dim(H)`. Vector names are unique. A committed vector has canonical form:

```json
{"name":"X","space":"H","value":[...]}
```

and is emitted by `vector_declare`.

Conversion errors, wrong rank, wrong length, nonnumeric elements, and
nonfinite values are auditable rejection causes rather than uncaught NumPy
exceptions.

## 5. Operators

```text
operator A : H -> K kind KIND matrix M
```

The only allowed kinds are:

- `linear`;
- `projector`;
- `transport`;
- `external`.

If `dim(H) = n` and `dim(K) = m`, `M` must be a finite rectangular matrix with
shape `(m, n)`. A committed operator has canonical form:

```json
{
  "name":"A",
  "source":"H",
  "target":"K",
  "kind":"linear",
  "matrix":[...]
}
```

and is emitted by the `operator` receipt.

The `external` kind is still a modeled matrix operator in this finite runtime.
It does not by itself invoke an external system.

## 6. Projector declarations

An operator declared with kind `projector` must be a square endomorphism:

```text
source space == target space
matrix rows == matrix columns == declared space dimension
```

The declaration computes `P @ P` and requires:

```text
numpy.allclose(P @ P, P, atol=1e-9, rtol=0.0)
```

The declaration rejects a nonfinite intermediate product or a failed
idempotence comparison. This is a binary64 tolerance check, not a proof that
an exact mathematical matrix is idempotent.

## 7. Operator application

```text
apply Y = A(X)
```

The vector space of `X` must equal the source space of `A`. The runtime
computes:

```text
y = A.matrix @ X.value
```

The result must be finite. A successful application creates vector `Y` in the
target space of `A` and emits:

```text
operator_apply(target, operator, vector, result)
```

where `result` is the complete canonical result vector. The target vector name
must be new.

## 8. Similarity transport

```text
transport A via T as B
```

The transported operator `A` must be an endomorphism. `T` must act on the same
space as an endomorphism. NumPy must be able to invert `T`. The result is:

```text
B.matrix = T.matrix @ A.matrix @ inv(T.matrix)
```

The resulting matrix must be finite. `B` inherits the source, target, and kind
of `A`. Its name must not overwrite an existing operator. The `transport`
receipt binds the source operator name, transport name, and complete canonical
result.

Invertibility here means that `numpy.linalg.inv` succeeds in the declared
environment. The profile does not supply an exact symbolic condition-number
or rational-invertibility certificate.

## 9. Projector checks

```text
check_projector P tolerance EPS
```

`P` must be a square endomorphism. `EPS` defaults to `1e-9` and must be finite
and nonnegative. The runtime computes the matrix/Frobenius norm:

```text
r = numpy.linalg.norm(P.matrix @ P.matrix - P.matrix)
```

The check passes exactly when `r` is finite and `r <= EPS`. A successful
`projector_check` receipt records `operator`, `residual`, and `tolerance`.

## 10. Intertwiner checks

```text
check_intertwiner T between A and B tolerance EPS
```

The spaces must satisfy:

```text
A.source == A.target == T.source
B.source == B.target == T.target
```

`EPS` defaults to `1e-9` and must be finite and nonnegative. The runtime
computes:

```text
r = numpy.linalg.norm(T.matrix @ A.matrix - B.matrix @ T.matrix)
```

The check passes exactly when `r` is finite and `r <= EPS`. A successful
`intertwiner_check` receipt records the three operator names, residual, and
tolerance.

## 11. Failure normalization

Core 0.5 normalizes the following into auditable parse, static, or statement
rejection as appropriate:

- malformed or nonfinite scalar literals;
- nonnumeric, nonfinite, ragged, or incorrectly ranked arrays;
- vector and matrix dimension mismatch;
- unknown operator kind;
- dimension-incompatible projector;
- duplicate transport result;
- singular transport matrix;
- negative or nonfinite check tolerance;
- nonfinite application, transport, or residual output.

No successful receipt is emitted for a numerical operation whose defining
predicate fails. If failure occurs inside a transaction, component state is
restored according to the transaction lifecycle while audit evidence remains
append-only.

## 12. Independent verification boundary

`reference/osl_semantic_numeric.py` independently parses the bounded numeric
source fragment, verifies exact tracked receipt schemas and statement effect
spans, recomputes state transitions and selected rejection causes, handles
numeric rollback, and compares reconstructed `spaces`, `vectors`, and
`operators` with terminal and final-state projections.

It does not import or invoke `OSLRuntime` or the primary parser. It does use
NumPy, as does the reference runtime. Therefore it supplies independent control
flow and source/receipt reconstruction, not numerical-library diversity or a
formal proof of floating-point behavior.

The complete cross-domain transaction projection digest remains outside this
component's independent scope. General assertion truth, including every
possible `vector ... approx ...` assertion, is also outside the universal
claim.

## 13. Observed evidence

The numeric component is included in the 75/75 focused Core 0.5 gate and the
66/66 packaged corpus aggregate. The full release suite passes 168/168 tests.
These are finite observed results and do not imply correctness for every
matrix, dimension, tolerance, platform, or syntactically valid program.
