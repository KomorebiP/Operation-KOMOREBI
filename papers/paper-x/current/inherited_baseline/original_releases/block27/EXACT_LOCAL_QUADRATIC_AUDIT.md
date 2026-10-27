# Block 22 exact finite local quadratic audit

The bounded exact assertions passed. The v2 execution manifest validates with current input and output hashes. This report documents the implementation and its finite result; independent source review is a separate release obligation.

## Contract and scope

There are two different variables and two different roles for primes:

- At the **arithmetic prime** `p`, the variable `y` solves `y^2 = -1` modulo powers of `p`. The program exhaustively tests every residue at every depth `m >= 0` with `p^m <= 100000`, for all 15 primes `p <= 47`. Depth zero means the zero ring. Every fiber between consecutive displayed depths is constructed again by testing all digits `y + k*p^m` and compared with the independently scanned roots.
- At the **coefficient prime** `ell`, the variable `x` solves `x^2 = +1` in `Z/(ell^m)`. Independently, all candidate images of the generator of `C2` are checked for being units and satisfying all four group-law pairs. The coefficient ranges are `ell=2`, `0<=m<=8`, and `ell=3`, `0<=m<=5`.

The finite local quotient map is explicitly a **declared model** `C2 -> C2`: the zero map at arithmetic primes congruent to one modulo four, and the identity map at the other tested primes, including two. For every finite coefficient character, the program checks that its restriction is trivial exactly when this model map is zero or its generator image is one. The map itself and the restricted characters are checked against their group laws. Every high-to-low coefficient reduction, every character, every arithmetic prime, and both group elements are checked for naturality. Trivial local restriction is also checked to descend.

The model does not execute an absolute Galois group, infer its image, or identify inertia. Its arithmetic interpretation belongs to the separate mathematical and Lean arguments.

## Independent implementation paths and boundaries

`arithmetic_roots` scans the whole ring. Lift fibers use a distinct digit construction and are checked to exhaust the high roots. The arithmetic root counts are compared with the proposed prime-congruence criterion; that criterion is never used to produce the roots.

`coefficient_roots` directly evaluates the polynomial, while `unit_characters` enumerates units and tests the homomorphism law without calling the root predicate. Prime enumeration uses trial division and is checked against the explicit prime list.

The following small cases are explicit guards:

- `y^2=-1` has the root one modulo two and no root modulo four. Thus the first residue test at arithmetic prime two does not suffice for a compatible tower.
- At arithmetic primes five and three the root lists modulo the prime are respectively `[2,3]` and `[]`.
- Coefficient trivial and sign characters coincide modulo two and differ modulo four. Their model restrictions differ modulo four at arithmetic primes two, three, and seven, while both restrictions are trivial at arithmetic prime five.
- The coefficient character with generator value three modulo eight has no character lift modulo sixteen.
- At all 14 tested odd arithmetic primes, the residues one and minus one differ.

## Exact results

| Check | Count |
|---|---:|
| Arithmetic primes | 15 |
| Arithmetic levels, including depth zero | 88 |
| Arithmetic residue candidates scanned | 755,060 |
| Arithmetic roots found, including depth zero | 64 |
| Arithmetic consecutive reduction edges | 73 |
| Arithmetic root lift fibers | 52 |
| Digit candidates checked in those fibers | 998 |
| Coefficient levels | 15 |
| Coefficient residue candidates scanned | 875 |
| Root/character matches | 39 |
| Character group-law pairs for these matches | 156 |
| Local restriction cases | 585 |
| Local character group-law pairs | 2,340 |
| Coefficient reduction maps, including identities | 66 |
| Coefficient/local naturality values | 6,180 |
| Trivial-restriction descent implications | 1,830 |

The output retains every arithmetic root list and full lift fiber, every finite coefficient character and its restriction, the exact bounds, counts, and non-claims. No random sampling or floating arithmetic is used. It is deterministic under the recorded Python version.

## Reproduction and provenance

From the Block 22 project root:

```sh
python3 checks/exact_local_quadratic.py --output exact_local_quadratic.json
```

The authoritative bounded run used the computation-audit runner and produced `checks/local_quadratic_run/results.json`, byte-identical to `exact_local_quadratic.json`. Its manifest is `checks/local_quadratic_run/manifest.json`; the contract is `exact_local_quadratic_contract.json`.

- CPython standard library: `3.12.13`.
- Runtime recorded by the runner: `0.115947` seconds.
- Wall limit: 30 seconds. Per-process address-space limit: 512 MiB. Per-process CPU-time limit: 20 seconds. CPU affinity: one core. Cooperative thread cap: one.
- Exit status: zero. No missing or invalid results. The input hash did not change during the run.
- Project Git commit is unavailable; exact source and result hashes are recorded instead.
- Block 21 baseline ZIP SHA-256: `fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2`.
- Script SHA-256: `a0067c572a23785dc30ee496706b963a5127f92b50e7e67b1e974d3ccbae5bab`.
- Scientific result SHA-256: `c37ffd85faaa61bf22ecee0a75e474433ad016e0ef6c41cf516e927b1efad798`.

No implementation failure or resource truncation occurred in this run. A pass only corroborates the finite assertions in the contract. It does not prove a universal prime-splitting criterion, a p-adic lifting theorem, an infinite branch, inertia compatibility, Hodge–Tate data, Weil–Deligne attachment, or any of the five full partial arithmetic claims. The local map interpretation is supplied, not discovered by the finite computation. The full lift fibers stop at their displayed terminal depth.
