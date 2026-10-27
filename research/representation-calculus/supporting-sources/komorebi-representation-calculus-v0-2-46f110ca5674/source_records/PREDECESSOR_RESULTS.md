# Retained finite execution

The exact reference audit passed with **22,758 check calls**. Those are checks,
not independent discoveries. There were no mathematical test failures in this run.
The written proofs are separate and no new Lean build was run.

- Complete 64-state task: four current-output classes refine to sixteen exact
  all-word classes. With the additional coordinate-swap operation they refine
  to sixty-four. The initial-state interface explicitly allows every state.
- The search over all 64 binary linear predicates recovers precisely the zero
  predicate and the known relation a4+a6=0 mod 2. The relation itself is not an
  input to the search. This is a rediscovery of Block15, not a new theorem.
- Every lower root of all 125 scalar quadratics with coefficients -2..2 was
  audited for p=2,3,5 and r=1,2,3: 1,356 lower-root cases. Exact lift fibers
  agree with the Jacobian criterion, and obstruction classes are unchanged by
  every tested representative shift.
- Four hundred exact 2x2 matrix instances check residual composition.
- For the retained binary-two-color spectrum, 1,024 precision steps verify
  L(r)-L(r-1)=D(r). At r=64, D=17, L=717, and a full 17-coordinate free array
  uses 1,088 residue bits. This is not a minimal-DFA or general-program bound.

`COMPUTATION_MANIFEST.json` records the actual command, environment, runtime,
source hashes, outputs, limitations and declared ranges. Its validator passed.
