# Block 51 contract

## Mathematical target

Restrict which eligible variable primes can ramify in the actual opposite
residual extension, using the natural integral monodromy and the actual
length n of the stable-lattice segment. Do not replace the natural
lattice by its semisimplification, discard the higher diagonal obstruction,
or assume that all prime multiplicities in C are ordinary.

## Proven conclusion and hypotheses

For a characteristic-zero DVR O, a nonzero integral nilpotent N with
N^2=0, FN=QN, NF=N, F in GL_2(O), Q a unit distinct from 1, put
 t=min valuation(N_ij), h=valuation(Q-1).
If valuation(N_21)=n>=1 and F_21 is divisible by pi^n, then
 n=t+2s for some integer 0<=s<=h.
The theorem is proved uniformly in the written proof.

For the inherited reducible Frey branch over Q(sqrt(5)), the variable
natural periods give t=1+v_7(v_q(C)). The actual n is finite and canonical
up to the fixed orientation. The opposite class must ramify at an
eligible prime satisfying this equality. The source-dependent arithmetic
inputs are enumerated separately; this contract does not re-prove them.

## Exact computational surrogate

Use standard-library integer and Fraction arithmetic only. Quadratic
field elements are ordered rational pairs a+b*sqrt(5), with reduction at
the inert prime seven into F_49. Check the explicit polynomial/matrix
identities, selected sharp examples, independently conjugated integral
bases, power-residue examples, and the finite support selector.

Declared ranges:
- integer sharpness: t=1..6, h=1..4, every s=0..h, monodromy units 1,2,6;
- independent quadratic basis audit: 8640 generated cases, admitting only
  those satisfying the theorem's stated depth/stability hypotheses;
- targeted quadratic sharpness: t=1,2,3, h=1..4, every s=0..h, angle units
  1,sqrt(5),1+sqrt(5), monodromy units 1,sqrt(5);
- selector: multiplicities 1..200, depths 1..24, cardinalities
  29,169,197,1373,14407;
- exact node identities at both quadratic roots and power-residue data
  only at the explicitly specified prime 1504231.

All ordering is deterministic. No random seed is used. Each process has
a 120-second wall timeout in the portable runner. No OS memory or CPU
quota is imposed by that runner. A timeout is inconclusive, never a
mathematical contradiction or successful verification. The inputs and
outputs are hashed, and processes run in isolated temporary copies.

## Interpretation

A pass establishes the implemented finite assertions and matching replay
outputs. The written proofs, not the count of successful cases, establish
the universal local theorem. Failed invariants are implementation or
claim errors requiring investigation. Exclusion by the stated hypotheses
is not a counterexample. The deliberately false t+h bound and malformed
matrix/input controls must be rejected.

No computation here establishes absence of integer solutions, a uniform
bound on n, global geometric realization of sharpness examples, source
theorems, novelty, or a Lean proof. No floating-point tolerance is used
for any mathematical conclusion; elapsed runtime is ordinary timing data.
