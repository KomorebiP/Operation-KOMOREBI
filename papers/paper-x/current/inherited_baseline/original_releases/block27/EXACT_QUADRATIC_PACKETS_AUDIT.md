# Block 21 exact quadratic-packet computation

Verdict: the implementation and finite assertions passed in the stated ranges.
This record is supporting computation, not a universal Lean proof or an
arithmetic packet-identification theorem. Independent external review and
replay, when performed, should be recorded separately.

## Contract and provenance

The authoritative contract is `exact_quadratic_packets_contract.json`. The
standalone implementation is `checks/exact_quadratic_packets.py`; it imports
only the CPython standard library. No predecessor experiment is rerun. There
is no randomness or floating-point arithmetic.

The runner's version 2 evidence record is
`checks/quadratic_run/manifest.json`, with stdout, stderr, and the scientific
result in the same directory. It records the actual interpreter, command,
runtime, resource limits, unchanged source hashes, and output hashes. The
manifest validator passed with the project root supplied. The root-level
`exact_quadratic_packets.json` is a byte-identical copy of the scientific result.
No git revision is available for this extracted project; the runner records
that limitation explicitly.

Regeneration command, from the project root:

```text
python3 checks/exact_quadratic_packets.py --output exact_quadratic_packets.json
```

The recorded bounded run used a 120-second wall limit, 110-second CPU limit,
1 GiB address-space limit, and one CPU. The declared thread limit is a
cooperative environment setting. The script does not create subprocesses.

## Exact objects and exhaustive ranges

For each pair `(p,M) = (2,12), (3,7), (5,5)`, every residue modulo `p^m`
is tested for every `0 <= m <= M`. Modulus one is included as the zero ring.
The cyclic group `C2` is encoded by `{0,1}` with addition modulo two. Every
possible unit generator image is separately tested against all four group-law
pairs, without calling the root predicate. The resulting characters agree
exactly with the solutions of `x^2 = 1` in each tested ring.

The quotient `R[X]/(X^2-1)` is represented by coefficient pairs `(a,b)` in
the basis `(1,X)`, with product

```text
(a,b)*(c,d) = (ac+bd, ad+bc).
```

Evaluation at each retained root is checked for zero, one, generator,
addition, and multiplication. For moduli at most 16, every ordered pair of
quotient elements is checked. For larger moduli, every ordered pair from the
25 probes with both integer coefficients in `[-2,2]` is checked. The latter
is deliberately a bounded probe family, not a full quotient multiplication
table.

For every high/low depth pair and every root at the high depth, reduction
naturality is checked on both group elements and all 25 coefficient probes.
Every candidate next-level lift is enumerated independently of the next-level
root table. Direct terminal-level projections are compared with a separate
backward-pruning computation of the finite stable cores.

Nonreduced comparison rings are `F2[epsilon]/epsilon^r` for `r=2,3,4`, encoded
by binary coefficient vectors. Every element is tested for the root and
character conditions. All ordered pairs of quotient elements are checked
under evaluation. Every root, coefficient pair, and length-reducing quotient
map is checked for naturality, including augmentation to `F2`.

## Results

| Finite assertion | Count |
|---|---:|
| Prime-power levels | 27 |
| Prime-power residue candidates | 15,377 |
| Retained roots, paired with independently enumerated characters | 70 |
| Group-law pairs for retained characters | 280 |
| Prime-power quotient evaluation pairs | 324,843 |
| Next-level lift candidates | 164 |
| Accepted reduction edges | 67 |
| Character naturality values | 922 |
| Ring-point naturality values | 11,525 |
| Complete branches through the three terminal depths | 8 |
| Nonreduced ring elements | 28 |
| Nonreduced retained roots and characters | 8 |
| Nonreduced quotient evaluation pairs | 270,848 |
| Nonreduced naturality values | 4,544 |

Counts are the specified test tuples. They should not be added together as a
count of distinct mathematical objects or Lean declarations.

The dyadic forest has four coherent branches through depth 12. Projecting
these branches to any earlier depth leaves exactly the residues of `+1` and
`-1`, with collisions at depths zero and one. This is a finite stable-core
statement. The two extra terminal roots are still valid endpoints of finite
branches; the run does not call those endpoints infinite branches.

At every tested dyadic source depth from 3 through 11, the two roots other
than `+1` and `-1` have no root lift at the next precision. At odd primes, each
tested positive-depth root has exactly one next-level root lift. These
observations suggest the familiar structural distinction but are reported
only for the complete declared ranges.

## Boundary controls and interpretation

* `3^2 = 1 mod 8`, but its only residue lifts modulo 16 are 3 and 11, whose
  squares are both 9. Thus this admissible finite point has no next-level lift.
* The values `+1` and `-1` coincide modulo 2 but are 1 and 3 modulo 4. A
  residual label alone cannot distinguish the two selected packets.
* In the nonreduced characteristic-two rings, `+1 = -1`, yet there are other
  roots of one. For example, `1+epsilon` is another root when `epsilon^2=0`.
  Consequently, the general ring-point/character correspondence must not
  silently incorporate a domain hypothesis or classify every root as a sign.

No mathematical counterexample to the intended correspondence was found, and
no implementation or execution failure occurred in the recorded run. The
boundary examples refute stronger automatic-lifting and arbitrary-ring
classification statements, not the correspondence itself.

The script does not instantiate the absolute Galois group, prove continuity,
or execute Hodge--Tate or Weil--Deligne comparisons. Those statements require
the accompanying formal arithmetic construction. Extending these finite
forests to arbitrary depth or classifying infinite branches requires a
separate proof. Raising the computational bounds alone would not provide it.
