# Block 51 proof guide

The source target is the centered approximation argument in sections 3 and 4 of
*The Dirac Group and Its Generator*. The proof works on the inherited complete
coefficient Hilbert space and the actual torus Fourier equivalence.

## Construction and proof order

1. `Relativistic3DCenteredConvergence` transports the arbitrary real-momentum
   Clifford square into the Hilbert spinor representation. Its exact norm
   identity controls both individual symbols and their differences.
2. `boundedModewiseOperator` lifts any uniformly bounded family of mode maps
   to a continuous linear operator on the full coefficient space. The sine
   bound gives the centered norm estimate `sqrt(m²+3h⁻²)` for `h ≠ 0`.
   Summing modal symmetry proves self-adjointness.
3. The sine quotient is expressed using the continuous sinc function. This
   supplies a genuine two-sided modal limit. Centered modal norms are bounded
   by continuum modal norms, so errors are dominated by twice the continuum
   output. Its square sum is finite on the maximal domain. The checked
   coefficient dominated-convergence lemma yields the complete graph limit.
4. `Relativistic3DCenteredResolvent` constructs modal inverses for every nonreal
   parameter, using self-adjoint real spectrum and the imaginary-part norm
   lower bound. The uniform `1/abs(z.im)` estimate lifts the inverses to the
   coefficient space. The identity `H R_z f = f + z R_z f` proves range
   membership in the unbounded domain, and both inverse laws are supplied.
5. Applying the resolvent identity to `g = R_z f` reduces the resolvent error
   to the already proved graph error at this actual domain vector. The bound
   proves strong resolvent convergence for every square-summable input and
   every nonreal parameter. No convergence in operator norm is asserted.
6. `Relativistic3DCenteredRates` uses the global sine error with coefficient
   `1/6`. The third-order condition is a `Summable` proposition. It implies
   first-order domain membership and bounds the summed squared modal errors.
   This proves the full generator estimate under precisely the stated extra
   regularity.
7. `Relativistic3DModalPerturbation` differentiates the interpolation
   `U_A(t-s) U_B(s) ψ`. The two matrices need not commute. Unitarity and the
   real mean-value estimate give the perturbation bound with `abs(t)` for
   positive and negative times. Applying the exact Clifford difference norm
   and the third-order moment yields the full propagator rate.
8. The inherited Fourier equivalence transports graph limits, actual
   resolvents, inverse laws, and rates to physical torus fields. The compact
   time bounds are pointwise uniform on `[-T,T]` with the explicit `T ≥ 0`.

## Zero spacing and domain boundaries

The bounded global centered operator has auxiliary value zero at `h = 0`.
Its mode evaluation and inverse identities require `h ≠ 0`, and graph
convergence uses a punctured neighborhood. The filled modal propagator and
resolvent take continuum values at zero and are not identified as the
evolution or inverse of that auxiliary zero operator there.

The global third-order moment is not a finite-grid approximation. No rate is
claimed for arbitrary square-summable data without its summability hypothesis.
Strong resolvent convergence, in contrast, does hold for every such input.
The rate keeps the stated coefficient `1/6`; its optimality is not separately
proved.

## Verification and sensitivity

The fresh gate compiles the exact local import closure into empty local object
storage, audits all compiled constants owned by the five root modules, replays
each root with `leanchecker`, and runs positive, elaboration-rejection and
axiom-policy controls. Named source declarations and generated environment
constants are counted separately. External compiled dependencies and the Lean
kernel are reused under their recorded pins.

Positive controls exercise negative mass, negative spacing and time, physical
transport, arbitrary nonreal parameters, and concrete modes. Rejection controls
remove or alter spacing/domain/moment witnesses, signs, constants and filter
types. The custom-axiom control compiles in isolation before the recursive
axiom audit rejects it. Missing imports, timeouts and resource errors are not
accepted as intended rejections.

The complete result is in the [gate receipt](../verification/block51/current/receipt.json)
and [scoped inventory](../declaration_inventory.json). The [progress ledger](../PROGRESS_LEDGER_v0.51.0.md)
preserves failed development and infrastructure attempts separately from the
accepted run.

## Remaining programs

The abstract unbounded spectral-functional-calculus API linkage remains open.
Finite-grid sampling, interpolation and aliasing require separate maps and
estimates. Background or dynamical gauge coupling and cosmological matching,
state preparation, capture and abundance are not consequences of this block.
The full historical physics aggregate has not received a new complete audit.
