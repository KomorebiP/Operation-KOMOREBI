# Exact finite protected repair

Run `python3 examples/protected_repair.py --demo` from the package root. It prints the three preservation problems in Section 17: a unique answer, a one-dimensional affine family, and an obstruction. Every returned certificate is checked before the command succeeds.

For a custom problem, provide JSON with keys `A`, `P`, and `x` and run `python3 examples/protected_repair.py problem.json`. Entries must be integers or exact rational strings such as `"1/2"`. Empty row families and zero-dimensional candidates are supported. Row widths must match the candidate dimension. Floats and booleans are deliberately rejected. An obstructed mathematical problem is a successfully classified input, not an execution failure. Malformed input exits with code 2.

`solve_protected(A, P, x)` solves `A y = 0` and `P y = P x` over the rational numbers. The feasible result contains one particular answer and a basis of `ker A ∩ ker P`. It does **not** claim that its particular answer minimizes a norm. The obstructed result contains row vectors satisfying `lambda A = mu P` and `lambda A x = 1`, which directly rule out an answer.

The proof of the alternative is KS57 in the monograph. KS56 is the separate nearest-answer theorem in a specified Hilbert geometry. Neither new written theorem is represented as a newly compiled Lean declaration. Finite implementation tests are in `checks/revision_exact.py`; an independent minor-based rank oracle is used for the small matrix tests.

The coefficient domain matters: this program is not an integer solver. For example, `2m = 1` is solvable over Q but not over Z. An exact rational computation also does not certify a floating-point implementation or a large-scale complexity bound.

## Approximation and obstruction models (publication 1.4.0)

Run `python3 examples/approximation_models.py --depth 16 --steps 10` for exact rational trajectory data, diagonal repair sizes, certified infinite-tail bounds, and the finite phase table. It uses only the Python standard library. The infinite nonexistence and convergence claims are proved in the monograph rather than inferred from its output. `checks/deepening_exact.py` is the separate finite regression audit.
