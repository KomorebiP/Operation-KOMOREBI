# Strong Artin Lean v0.33 — Simultaneous Nonsemisimple Norm

Author: Komorebi P.

Parent: `Strong_Artin_Lean_v0.32.0_Nonsemisimple_Frobenius_Norm_Checked.zip`

Parent SHA-256: `636a99685b1da21d8f4a1ec9c046293194e8a7d3563474bb73487cccf43f88e7`

This is a local square-zero representation-lifting checkpoint. It does not prove Strong Artin, a global localization theorem, automorphic occurrence, or a higher coefficient-tower theorem.

## Main change

The preceding checkpoint classified **single** prescribed Frobenius powers. This checkpoint classifies simultaneous prescribed powers with **one shared** Frobenius correction and independent local conjugators. The constructed mismatch is the actual one in the inherited square-zero kernel. Vanishing is checked against the inherited norm-localization cokernel and continuous local-gauge obstruction, not an unidentified comparison datum.

Write S_d(T)=1+T+...+T^(d-1). The exact localization problem is

    e_i = S_(d_i)(T)x + (1-T^(d_i))z_i.

The same x must work for every i. Each z_i is one kernel element, hence one constant kernel conjugator for the corresponding local group.

## Prime-power degrees: arbitrary T

Let k be a field of prime characteristic p. Put N=T-1 and d_i=p^(a_i). Choose a pivot i0 with least d_i. The family is solvable iff

    e_i0 belongs to range N^(d_i0-1),
    e_i - N^(d_i-d_i0)e_i0 belongs to range N^(d_i) for every i.

No diagonalization, nilpotence, finite-dimensionality, or finiteness of the index family is assumed. A least exponent exists for every nonempty family; the empty family is treated separately as vacuous.

The operator theorem is `SimultaneousNorm.primePower_localization_iff_pivot`.
The actual class theorem is `FrobeniusLinearCoordinates.primePower_matchingClass_zero_iff_pivot`.

## Mixed degrees on a supplied nilpotent primary block

For d_i=m_i*p^(a_i) with m_i nonzero in k:

* If T=lambda+N, N nilpotent, and lambda is nonzero and not 1, simultaneous matching is equivalent to individual norm-image membership. The local conjugators absorb all cross-prescription constraints. The image is range N^e_i with the exact v0.32 resonance exponent.
* If T=1+N with N nilpotent, let U_i=S_(m_i)(T)^(p^(a_i)). This is an actual invertible operator. Normalize f_i=U_i^(-1)e_i. The prime-power pivot criterion applies exactly to f_i, with d_i replaced by its p-power part.

The inverse U_i^(-1) is not replaced by its constant term. This is exact nilpotent functional calculus, not a truncated heuristic.

## Mechanism

The identity S_d(T)(1-T)=1-T^d rewrites localization as S_d(T)(x+(1-T)z_i). At prime-power degree S_d(T)=N^(d-1). Absorbing a sign into z_i reduces the system to

    e_i=N^(r_i)(x+N z_i), r_i=d_i-1.

For r_i0<=r_i, subtracting N^(r_i-r_i0)e_i0 cancels the shared x and leaves N^(r_i+1)(z_i-z_i0). Conversely, lift e_i0 through N^(r_i0), and use the quotient differences to choose all z_i. This proves both directions.

A checked nested-filtration consequence says that matching each prescription with the pivot is sufficient for the whole family. This is NOT a general pairwise-gluing theorem for unrelated local groups.

## Actual matrix example

Over F3[epsilon]/epsilon^2 take F=[[1,1],[0,1]], and T=Ad(F) on the matrix kernel. The inherited computation is

    (T-1)^3=0,  (T-1)^2 X = X_21 E_12.

For degrees 1 and 3, the new full criterion is

    e_3=(e_1)_21 E_12.

The pair (e_1,e_3)=(0,E_12) has individual roots but no common Frobenius, even allowing independent kernel conjugators. The pair (E_21,E_12) has a common lift. These claims are proved on actual prescribed units and the actual matching cokernel class.

## Evidence

See RESULT.json for the fresh source replay status and exact commands. Six additive modules contain 38 theorem declarations and 9 definitions (573 lines). Counts include helpers and examples, not 38 new arithmetic results. The complete direct closure has 38 unchanged dependency modules plus six new modules; AxiomAudit checks all 47 explicitly named new constants. Dependency sources are checked byte-for-byte against the parent or its embedded v0.31 archive.

The pin is Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Warnings are errors. No sorry/admit/custom axiom/custom opaque/native_decide/unsafe is allowed in active project source.

This reuses the pinned Mathlib object cache. It is not an independent-kernel check, an independent specialist referee report, or a complete historical branch replay. Underlying polynomial identities and linear algebra are standard; novelty is not claimed.

## Replay

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8

Repeat the resume command until RESULT.json reports PASS. A PARTIAL result is not a complete pass. The verifier checks previous object hashes before resuming.

    python3 checks/exact_simultaneous_checks.py

The finite test is independent exact modular arithmetic. It corroborates the uniform Lean proof; it does not replace it.
