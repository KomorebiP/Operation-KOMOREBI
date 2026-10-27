# Continue Strong Artin from v0.17

## Restore point

Use this directory as the canonical additive checkpoint above:

```text
Strong_Artin_Lean_v0.16.0_Jacobian_Chebotarev_Algebra_Checked.zip
```

Do not replace the v0.16 base archive or silently weaken any open arithmetic hypothesis.

## Strongest checked endpoint

The abstract linearized pipeline is complete under explicit arithmetic interfaces:

```text
split-prime raw one-class detection
  + transverse Selmer/Jacobian equivalence
  -> automatic equation-column representation
  -> exactly codimension-many admissible auxiliaries
  -> augmented Jacobian surjective
  -> every compatible finite-depth linearized lift exists.
```

The module-theoretic generic-support pipeline is also complete:

```text
nonzero special fibre
  + flatness/regular uniformizer
  + split generic product ring
  + transitive twist equivariance
  -> every generic branch is supported.
```

The exact local algebraic pairing is:

```text
ker(1 - Ad(A)) ≃ Dual(Matrix / range(1 - Ad(A)))
```

with pairing `trace(P * X)` and tame relation `Ad(A)P = P` at `q = 1`.

## First open technical theorem

Construct and verify the arithmetic comparison map identifying:

```text
continuous local unramified cohomology modulo coboundaries
```

with the checked Frobenius quotient, and identify normalized local Tate duality with the checked trace pairing. Fix all Frobenius, inertia, Tate-twist, and sign conventions explicitly.

A proof must not replace the arithmetic cohomology group by the matrix quotient without a comparison theorem.

## First open global theorem

Produce the residual finite-Satake descent packet in a determinant-bearing automorphic or cohomological complex. The linearized and support theorems cannot manufacture a nonzero residual automorphic module.

Candidate routes remain:

- torsion/coherent/completed cohomology occurrence;
- Smith/Tate residual descent followed by relative flat patching;
- a finite Hecke-equivariant weight shift into a realization range;
- enhanced carrier descent along the cyclic tower;
- a large separating coefficient prime.

## Verification

Run:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

A valid continuation must preserve warnings-as-errors, zero `sorry`/`admit`/custom axioms, and the exact v0.16 base hash recorded in `README.md`.
