# Exact computational examples

These four programs accompany the monograph's examples of protected repair, regularization, approximation, and certificates. They use Python's standard library and exact rational arithmetic. Run the commands from the package root, keeping the files together in `examples/`.

| Program | Purpose | Command |
| --- | --- | --- |
| `protected_repair.py` | Solve a finite protected linear system or return an obstruction | `python3 examples/protected_repair.py --demo` |
| `budgeted_repair.py` | Compute a protected regularized correction and its budget certificate | `python3 examples/budgeted_repair.py` |
| `approximation_models.py` | Evaluate finite trajectory formulas, diagonal data, tail bounds, and a phase table | `python3 examples/approximation_models.py --depth 16 --steps 10` |
| `inexact_repair_certificate.py` | Certify a proposed correction without computing the optimizer | `python3 examples/inexact_repair_certificate.py` |

Each command writes JSON to standard output. Add `> result.json` to save a result. The supplied demonstration JSON files are reference outputs. The commands above generate fresh records.

## Protected linear repair

The program solves

$$
Ay=0,\qquad Py=Px
$$

over the rational numbers. Here `A` describes the equations to satisfy, `P` describes the information to preserve, and `x` is the original candidate.

The demonstration covers a unique answer, a one-dimensional affine family, and an obstructed problem. For a custom problem, save an object such as the following as `problem.json`:

```json
{"A": [[1, -1, 0]], "P": [[1, 0, 0], [0, 0, 1]], "x": [2, 0, 5]}
```

Then run:

```sh
python3 examples/protected_repair.py problem.json
```

A feasible result contains a particular answer and a basis for all invisible exact changes, `ker A ∩ ker P`. The chosen particular answer is obtained by elimination and need not minimize a norm. An obstructed result contains row vectors satisfying

$$
\lambda A=\mu P,\qquad \lambda Ax=1.
$$

These equations exclude a protected exact answer. The command checks each returned certificate before succeeding. An obstructed input is a successfully classified mathematical problem and exits with code 0. Invalid input exits with code 2.

Matrix entries must be integers or exact rational strings such as `"1/2"`. Floats and Boolean values are rejected. Matrix row lengths must match the candidate dimension. Empty row families and zero-dimensional candidates are supported. The coefficient field is rational: a system that has a rational solution may have no integer solution.

## Protected quadratic regularization

For fixed matrices `d` and `p`, datum `r`, and positive parameter `alpha`, the regularized solver minimizes

$$
\|da-r\|^2+\alpha\|a\|^2\quad	ext{over }a\in\ker p.
$$

The candidate is `f - a`, so the protected value `p f` is preserved. By default the datum is `r = d f`. The optional `measured_residual` field supplies a different datum for the fitting objective. The output reports both that fit residual and the candidate's actual residual under the supplied model.

Use the included problem file:

```sh
python3 examples/budgeted_repair.py --input examples/budgeted_problem.json
```

Custom inputs have keys `d`, `p`, `f`, and `alpha`, with optional `measured_residual`. The candidate dimension and number of residual coordinates must be positive. A zero-dimensional protected kernel is supported. Entries use the same integer or rational-string format as the linear solver.

The program constructs a basis of the full protected kernel and retains its Gram matrix. It returns the unique regularized correction, exact preservation and normal-equation checks, objective value, and squared norms. Its budget certificate describes optimality at the norm of the returned correction. A unit dual witness is represented by its rational numerator and squared normalization factor, avoiding rounded square roots.

The default demonstration includes a protected coordinate, a nonorthogonal kernel basis, a fully protected candidate, a dual witness, and a diagonal tail enclosure.

## Approximation models

```sh
python3 examples/approximation_models.py --depth 16 --steps 10
```

The output contains a polynomial-decay trajectory, a trajectory with alternating growth and decay, a diagonal finite-prefix model, and a two-bit phase table. `--depth` and `--steps` each accept integers from 1 through 4096 and default to 8.

The tail intervals evaluate analytic bounds proved in the monograph. Their finite evaluation does not establish an infinite convergence or nonexistence theorem by itself. The program evaluates these specific formulas and does not implement a general reconstruction method.

## Inexact correction certificates

The certificate program evaluates a proposed correction using the actual protected kernel and its inherited Euclidean metric. It provides exact primal and dual values, a normal-residual certificate, and squared bounds on the distance to the regularized optimizer.

See [INEXACT_CERTIFICATES.md](INEXACT_CERTIFICATES.md) for input fields, a complete example, and the saved-record verification workflow.

## Interpretation

These are finite exact computations tied to declared mathematical inputs. The monograph supplies the relevant general proofs, and the accompanying Lean source formalizes its stated scope. The Python programs are not certified extractions from Lean. Their executions do not establish universal implementation correctness, floating-point accuracy, or an efficiency bound for large problems.
