# Exact prescribed integer step

`PolynomialPrescribedStep.lean` contains seven theorems and adds no definitions or axioms.

The construction uses the actual residual of the supplied polynomial system. For a prescribed integer parameter target `t`, divisibility gives an integer quotient `w` with `t - freePart x = q^L w`. Solved-block surjectivity solves the finite correction equation with parameter digit `w mod q`. The full integer correction is `join (integerLift q u) w`, retaining `w` exactly. The inherited polynomial Taylor theorem therefore proves the next root congruence, and the parameter part equals the requested integer target exactly.

The step is valid for every positive integer modulus, including one and composite moduli, at depth at least one. It preserves the actual solved Jacobian. The separate prime-field count theorem counts distinct actual prescribed residue lifts and yields `p^(m-e)` for every parameter digit; the dimension inequality `e ≤ m` is also proved.

Development verification used the pinned Lean 4.34.0-rc2 runtime, the existing low-memory runner, Werror, one thread, a 240-second timeout, and default kernel/resource limits. The first attempt found two definitional-unfolding mismatches for reduction/join and a deprecated `if_pos` theorem name. The second attempt, after explicitly unfolding reduction and using `ite_eq_left`, passed with no output. No mathematical assumption or target statement changed. The cumulative fresh gate remains authoritative for release provenance.
