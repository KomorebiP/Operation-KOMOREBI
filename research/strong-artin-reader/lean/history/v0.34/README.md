# Strong Artin Lean v0.34 — Mixed-characteristic kernel coordinates

Author: Komorebi P.

Parent: `Strong_Artin_Lean_v0.33.0_Simultaneous_Nonsemisimple_Norm_Checked.zip`

Parent SHA-256: `88706e3980c6c8306e250df8d3ba45618a1f33e803f9984ff8a6cf7d28079e24`

## Exact change

v0.33 required an explicit field-linear coordinate model of the actual square-zero kernel outside the dual-number case. This release constructs it for every positive prime-power coefficient layer:

    Mat_n(Z/p^(r+1)) -> Mat_n(Z/p^r),  p prime, r >= 1.

The implementation first works with Z/(m*p) -> Z/m, assuming m != 0 and p divides m. Specializing m=p^r gives the displayed layer; the product m*p is definitionally the chosen ZMod modulus and equals p^(r+1) by pow_succ.

The scalar embedding is z |-> m*z from ZMod p. It is additive and identifies ZMod p with the actual reduction kernel. Its inverse is canonical integer division: for a kernel element x, the coordinate is x.val / m modulo p. Matrix coordinates are entrywise.

No coefficient-ring section, dual-number identification, semisimplicity, diagonalization, or image-order invertibility is assumed. In fact, a theorem rules out an additive retraction of this scalar embedding from the entire upper coefficient ring when p divides m.

## Exact action and norm

For every actual upper Frobenius unit F, kernel conjugation becomes

    T(X) = Fbar * X * Fbar^(-1)

on Mat_n(F_p), where Fbar is reduction modulo p. All higher coefficients of F disappear from the correction operator, but NOT from the normalized prescribed mismatch.

The actual norm has coordinates S_d(T)=1+T+...+T^(d-1). If U reduces to F^d, put

    e = theta((U-F^d)*F^(-d)).

Then a root F' with the SAME reduction modulo m and F'^d=U exists iff e belongs to range S_d(T). For d=p^a this is range (T-1)^(p^a-1), with no diagonalization hypothesis.

The initial upper Frobenius is available: the matrix reduction is proved surjective and every lower matrix unit has an upper unit lift. No representation lift is assumed in that statement.

## Simultaneous prescriptions

The inherited actual matching cokernel is used unchanged. A single x is shared by all prescribed restrictions, and local conjugators are independent units equal to 1 modulo m. The exact condition is

    e_i = S_(d_i)(T)x + (1-T^(d_i))z_i.

For d_i=p^(a_i), choose a least exponent i0. The class vanishes iff

    e_i0 in range (T-1)^(d_i0-1),
    e_i - (T-1)^(d_i-d_i0)e_i0 in range (T-1)^d_i for all i.

The all-positive-layer capstone is `primePower_layer_simultaneous_criterion`. It supplies the mixed-characteristic kernel coordinates automatically, rather than retaining them as an input.

## Genuine mixed-characteristic controls

Over Z/9 -> F3 take F=[[1,1],[0,1]]. The residual operator satisfies (Ad(Fbar)-1)^3=0 and its square sends X to X_21*E_12. Thus the prescribed cube norm image is exactly F3*E_12.

* Nonzero upper-off-diagonal normalized mismatches lift.
* A diagonal E_11 mismatch does not lift.
* [[1,1],[6,7]] is a literal order-three upper lift, although the naive F has cube [[1,3],[0,1]].
* The degree-one prescription F and degree-three prescription 1 lift separately but have no shared Frobenius, even up to independent local kernel conjugacy. The inherited matching class is proved nonzero.
* Replacing the first prescription by the order-three lift gives a shared Frobenius and zero matching class.

## Scope

This is a one-layer local square-zero result. It proves automatic coordinates at EVERY positive prime-power level; it does not prove simultaneous solvability at EVERY level. The same residual adjoint operator can coexist with a new nonzero mismatch at a later level.

No general ramified DVR coefficient model, local-field inertia dictionary, arithmetic global localization, auxiliary-prime descent, automorphic carrier, or Strong Artin result is constructed. No historical novelty is claimed for the residue-layer arithmetic or the inherited norm identities.

## Evidence and replay

See RESULT.json for the actual fresh source replay. There are 7 additive source modules, 55 theorem declarations, 24 definitions, 11 abbreviations, and 603 source lines. Counts include helpers and examples. All 90 explicitly named new constants receive axiom reports. The 37 unchanged direct dependency modules are not new.

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8

Repeat resume until PASS. PARTIAL is not PASS. The verifier checks dependency bytes against the exact parent archive and checks prior source/object/log hashes before resuming. It reuses the pinned Mathlib cache.

    python3 checks/exact_mixed_characteristic.py

The independent integer-arithmetic script records its exact enumeration and sampling scope. It supplements the uniform Lean proofs and does not replace them.
