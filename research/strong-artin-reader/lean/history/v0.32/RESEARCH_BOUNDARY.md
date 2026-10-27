# Research boundary — v0.32

## Closed at the stated scope

1. The geometric norm for every k-linear operator satisfies S_(p^a)(T)=(T-1)^(p^a-1)
   in characteristic p, without diagonalization or finite dimensionality.
2. For d=m*p^a, the exact polynomial factorization is
   S_d(X)=(X-1)^(p^a-1) S_m(X)^(p^a).
3. A polynomial nonzero at lambda evaluates to a unit on a nilpotent lambda-primary
   block; an exact root factorization computes both operator image and kernel.
4. With m nonzero in k and lambda nonzero, the primary resonance exponent is
   p^a-1 at lambda=1, p^a at a nontrivial m-th root, and zero otherwise.
5. These image criteria are connected to the **actual inherited square-zero
   Frobenius norm and normalized mismatch**, producing iff criteria for roots
   with prescribed residue. One local kernel conjugator can still be absorbed.
6. Arbitrary invertible residual matrices over k have a constructed linear kernel
   model in the actual matrix ring over dual numbers, without a spectral hypothesis.
7. A genuine unipotent F3 matrix example has norm image k*E_01, giving an actual
   positive prescribed root and an actual obstruction for E_00.

## Important limitations

- General mixed-degree statements apply to a supplied lambda-primary block,
  meaning T-lambda*1 is nilpotent. We do not supply an automatic decomposition
  of an arbitrary operator into primary blocks or a rational canonical form.
- The prime-power identity itself has no primary-block or diagonalization restriction.
- For a general square-zero coefficient extension, a field-linear action model
  is explicit data. It is constructed automatically here for dual-number matrices,
  not every mixed-characteristic coefficient layer.
- A nilpotent Jordan part must not be discarded. An eigenvalue-one block may
  have a nonzero prime-degree norm, as the actual matrix example demonstrates.
- This release handles a single Frobenius root/restriction. It does not classify
  the nonsemisimple simultaneous-prescription problem with one shared correction.
- No new comparison with continuous cohomology, a continuous local-gauge quotient,
  an actual local-field inertia quotient, or an arithmetic Selmer complex is claimed.
- One square-zero step is not a compatible higher coefficient-tower theorem.
- No arithmetic auxiliary descent, determinant-bearing automorphic carrier,
  ramified compatibility, or Strong Artin theorem is obtained.
- These are standard characteristic-p polynomial and nilpotent functional-calculus
  mechanisms. No historical novelty claim is made.

## Next consequential target

For several prescriptions sharing one Frobenius, use the actual localization map

    (x,(z_i)) -> (S_(d_i)(T)x + (1-T^(d_i))z_i)_i.

A single root criterion cannot silently choose a different x for each i.
Determine its image on nilpotent primary blocks, or construct automatic models
for actual mixed-characteristic layers, before attempting coefficient-tower
compatibility. Global arithmetic localization and automorphic occurrence remain
independent tasks.
