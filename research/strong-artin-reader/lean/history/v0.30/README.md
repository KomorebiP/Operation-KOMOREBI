# Strong Artin Lean v0.30 — Unramified Procyclic Lifting

Author: Komorebi P.

**Status:** exact Lean-checked local lifting and Frobenius-restriction theorems. No Strong Artin or automorphic-carrier result is claimed.

## Ancestry

The exact retained parent is `Strong_Artin_Lean_v0.29.0_Continuous_Local_Gauge_Obstruction_Checked.zip`, SHA-256 `e344ba51691c72eca703b1b8860f889558a1a9b8a0642d9d329cf50488172a8d`. No same-numbered sibling is silently substituted. Every retained source is authenticated in `DEPENDENCY_PROVENANCE.json`, including the unchanged v0.26 counterexample used through the parent's nested ancestry.

## Main mathematical result

Use Mathlib's actual profinite completion of the infinite cyclic group, denoted Zhat. Its topology is the profinite topology, not the discrete topology.

For every profinite group H, evaluation at the distinguished generator gives an equivalence

```
ContinuousHom(Zhat,H) ≃ H.
```

Consequently every continuous homomorphism Zhat -> K lifts across any surjective continuous homomorphism H -> K of profinite groups. Choosing a preimage of Frobenius determines the lift uniquely with that generator value. This is derived from the existing profinite-completion universal property, not asserted as an axiom.

For finite discrete rings q:A -> B with q surjective and (ker q)^2=0, unit lifting supplies the surjection A^units -> B^units. Hence every continuous representation Zhat -> B^units lifts continuously. The corresponding distinguished v0.27 continuous inhomogeneous H2 class is proved zero. The matrix specialization covers GL_n across finite commutative square-zero coefficient extensions.

No invertibility of the residual-image order is required. Unlike v0.27's averaging theorem, the lift need not preserve the original finite residual quotient or the whole representation kernel.

## Genuine unramified-condition theorem

Let G be compact and let nu:G -> Zhat be a continuous surjective homomorphism. If rho:G -> B^units is continuous and trivial on ker(nu), the factorization through nu is proved by quotient descent. The representation lifts continuously to A^units and remains trivial on ker(nu).

The local-field interpretation takes ker(nu) to be inertia. Constructing the actual quotient map of a local Galois group, including its identification with Zhat, remains external to this Lean release. The theorem is NOT a substitute definition of a local Galois group.

## Compute the prescribed-restriction obstruction

The continuous map degreeMap(d):Zhat -> Zhat sends Frobenius to Frobenius^d. Restricting a representation along it sends F to F^d. For genuine unramified extension degrees, d is positive; d=0 is allowed only as an algebraic edge case in the general theorem.

For q:A -> B with square-zero kernel K, a lift F of the residual Frobenius, and x in K, define

```
N_(F,d)(x) = sum_(j=0)^(d-1) F^j x F^(-j).
```

Lean proves the exact identities

```
((1+x)F)^d = (1+N_(F,d)(x))F^d,
(1+z)((1+x)F)^d(1+z)^(-1)
  = (1+N_(F,d)(x)+z-Ad(F^d)(z))F^d.
```

For an indexed family of prescribed Frobenius lifts V_i above the residual F^(d_i), the mismatch is

```
e_i = (V_i-F^(d_i))F^(-d_i) in K.
```

Define the actual integer-linear localization map

```
L : K × (I -> K) -> (I -> K)
L(x,z)_i = N_(F,d_i)(x) + z_i - Ad(F^(d_i))(z_i).
```

There is ONE shared global Frobenius correction x; the local conjugators z_i are independent. Lean proves simultaneous matching up to kernel conjugacy iff [e]=0 in coker L. It then proves that this vanishing is equivalent to vanishing of v0.29's constructed continuous local-gauge obstruction for the actual degree maps. It does not assume an unspecified comparison of H1 spaces.

This computes the restriction problem inside one procyclic local setting. It is not a computation of the localization map for all places of a number field.

## Positive and negative controls

The existing character C3 -> (Z/9)^units with generator 4 has no lift through C3 to (Z/27)^units. All three candidates 4,13,22 have cube 10 modulo 27.

After inflation to Zhat it DOES lift, by sending Frobenius to 4 modulo 27, now of order 9. Its actual continuous obstruction is zero, and every such lift fails to factor through the original C3 quotient.

The residual degree-three restriction is trivial. Requiring its lift to remain the trivial character is nevertheless impossible. Both the actual v0.29 local-gauge obstruction and the new explicit norm-cokernel class are proved nonzero. Thus free unramified lifting is not the same as lifting with a fixed restriction.

An independent exact modular-arithmetic script also checks all 122880 combinations of an invertible 2x2 matrix modulo 4, two square-zero kernel matrices, and degrees 0 through 4 for the conjugated power identity. This finite check corroborates, rather than replaces, the universal Lean proof.

## Main declarations

- `Procyclic.exists_lift_of_surjective`
- `Procyclic.procyclic_matrix_representation_lifts`
- `Procyclic.procyclic_continuous_obstruction_zero`
- `Procyclic.unramified_lift_preserving_inertia`
- `SquareZeroH2.Datum.simultaneous_frobenius_matching_iff_class_zero`
- `Procyclic.gauge_obstruction_zero_iff_explicit_norm_class_zero`

All are under `Komorebi.StrongArtin`.

## Verification

Pinned environment: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

```
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8
# Repeat the resume command until the verifier reports PASS.
python3 checks/exact_procyclic_checks.py
```

The verifier checks the exact parent archive, every direct dependency's ancestor bytes, sources and axiom reports, and recompiles only from fresh staged sources. Resume validates unchanged source, object and log hashes. It checks all 30 source modules and one audit module. No development object directory is in its Lean search path. The pinned Mathlib compiled cache is reused.

The first release replay completed in bounded batches. One outer call interrupted a batch before the next module's exit status was recorded; that interruption was not counted as a pass. The unchanged closure was resumed and every source plus the audit received a zero exit code.

48 new theorems, 17 definitions and 3 abbreviations in 8 modules, 696 source lines. There are 68 explicitly named new constants audited. Six local anonymous instances give discrete topologies only to finite example types. These are incremental declaration counts, including helpers and examples, not 48 new arithmetic discoveries.

The release does not package the portable Lean/Mathlib runtime or rebuild Mathlib. This is self-review plus Lean checking, not an independent kernel or a complete historical replay.
