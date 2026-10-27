# Formalization boundary

**Actually compiled:** 50 theorem constants across six Lean modules, plus the all-theorem axiom audit.

**Not a formal proof of:** any elliptic-gamma algebraicity statement, the Stark modulus note, the analytic theta multiplication theorem, the full meromorphic/divisor dictionary, or the outstanding comparison with U_alg.

The Lean files expose the exact algebraic core and conditional bridge. The ordinary proof identifies its inputs with analytic quantities. No unproved analytic input is declared as a project axiom.

`H12NormAlgebra.pointwise_phase_comparison` has two explicit hypotheses identifying the same field element with epsilon^6/u^3 and epsilon^6/v^3. It proves only the implication to u^3=v^3. The arithmetic equality required in the research problem is not supplied.

`H12OrbitObstruction` uses finitely supported integer functions and genuine finite-support pushforwards. It proves conservation of orbit charges and the no-boundary consequences. It does not postulate an abstract obstruction with the desired conclusion already included.

`H12NormSemigroup.all_residue_products` is a complete finite theorem for ten residue classes. `norm_matrix_multiplicative` lifts it to arbitrary natural indices using the proved modular multiplication law. This is not a bounded claim advertised as an unbounded one.

`H12Audit.lean` prints the axiom dependencies of every exported theorem. The runner requires coverage of all 50 and rejects any dependency outside propext, Classical.choice, Quot.sound. It separately compiles a false arithmetic statement and requires its rejection.
