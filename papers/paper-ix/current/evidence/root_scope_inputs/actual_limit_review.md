# Independent review of actual reinsertion and stationary convergence

**Claim and verdict: proved as written.** For a fixed admitted ordinary
terminal-161 index r, retaining the exact undepletion factor in every packet
transfers the parent Jacobi error bound to the actual Euler function at every
depth. For L_m>=9 the critical-point error is at least L_m-1 and the
critical-value error at least L_m. Actual nonvanishing is equivalent to the
existence of a depth passing the strict comparison test. The theorem does not
assert that any such depth exists for every admitted index.

This is an independent read-only review by `/root/cross_cartier_review` of
the proof, checker, and previously reviewed parent facts. No author change was
needed and no Lean compilation was run. The reviewed proof SHA256 is
`b867df68e54cceaa87ccb8966754bdbe7a101497b854213093bba86b85e26f39`.
All exact proof, implementation, dependency, author-evidence, and replay pins
are in `ACTUAL_LIMIT_REVIEW_HASHES.json`.

## Dependency and obligation checks

The exact Bernoulli identity feeds the packet normalization. The parent
Jacobi theorem supplies an all-q moment error and unit model moments. The
true carry minimum supplies integral scalar packet weights tending to zero
dyadically. The inherited actual quadratic chart supplies an integral
restricted function with an isometric half derivative and unit quadratic
term. These inputs together give the comparison; no Padé theorem, moment
positivity, height bound, or new external theorem is invoked.

| Obligation | Status | Decisive reason |
|---|---|---|
| Sign and orientation of actual/depleted factor | Passed | `D(n)=2(1-2^(2n-1))B_(2n)` gives precisely the numerator at r and denominator at r+q |
| Unit property at every packet index | Passed | r>=1 makes delta_r even, so both numerator and denominator are odd; e_(r,0)=1 |
| Actual gamma normalization | Passed | Expanding the beta ratio gives `2^(154+5q)`, the odd linear ratio, the factorial quotient, and the Bernoulli ratio |
| Uniform all-depth function comparison | Passed | Multiplication by e is unit multiplication, with no loss depending on E or q |
| Source and derivative convergence | Passed | Integral source packets and scalar valuation tending to infinity give convergence in the restricted algebra |
| Critical-center and critical-value losses | Passed | Half differentiation loses one bit; stationarity makes center displacement contribute quadratically |
| Depth threshold and unbounded precision | Passed | L_25=10 and `L_(m+1)-L_m=4+4v_2(m+1)>0` |
| Exact nonvanishing equivalence | Passed | Strict ultrametric comparison proves both directions |
| Uniform arithmetic separation | Not asserted or proved | Existence of a passing depth is precisely the remaining implication |

## Normalization reconstructed

For every ordinary n>=1,

    D(n)=(2-4^n)B_(2n)=2(1-2^(2n-1))B_(2n).

Taking the ratio at r+q and r therefore gives

    B_(2(r+q))/B_(2r)
      = [D(r+q)/D(r)] [(1-2^(2r-1))/(1-2^(2r+2q-1))].

The same formula holds with 2B in numerator and denominator. This confirms
the orientation and sign of e_(r,q). As a small direct check, r=1,q=1 gives
`D(2)/D(1)=-7/5` and `e=1/7`, hence the actual ratio `-1/5`.

Substituting
`beta_n=-4^n(2n-1)B_(2n)/(2n)!` into
`gamma_q=2^154*8^q beta_(r+q)/beta_r` produces exactly `R*d*e`.
There is no omitted common normalization unit. The q=0 coefficient remains
2^154, and the first 2m actual packets remain exactly matched.

The actual model keeps the q-dependent e factor outside the finite Jacobi
moment approximation. The theorem does not claim that multiplying by this
factor leaves the entire actual moment sequence finite-rank or governed by
the same constant-coefficient recurrence. Such a claim is unnecessary.

## Error and stationary comparison

The parent theorem gives `d^[m]-d in 2^h_m Z_2` for every q. Since e is a
unit, the same bound holds after actual reinsertion, even when h_m exceeds
2r-25. The exact e factor is never replaced by 1. Each scalar R has
nonnegative valuation, and each source packet has integral restricted
coefficients after substituting the chart. Thus every summand of the
function difference lies in `2^(h_m-178) Z_2<Z>`. Scalar growth in q makes
the sum converge, so the closed coefficientwise ideal contains the entire
difference. This proves the bound for every m>=1; negative L_m merely gives
a weaker valid bound.

For L_m>=9, both actual and model functions have the inherited chart
congruences. Ordinary differentiation in Z is bounded; dividing by 2 gives
half-derivative error in `2^(L_m-1)`. The isometry property then gives
`v_2(c_(r,m)-c_r)>=L_m-1`. Expanding the actual function at its stationary
point removes the linear term. Its integral Taylor expansion gives a
displacement error of valuation at least `2L_m-2`, which is at least L_m.
Together with direct function error, this proves the critical-value bound.
There is no missing factor from an x derivative, because both sides use
ordinary Z derivatives.

The identity `h_m=8m-4s_2(m)` and the positive increments above show that
L_m tends to infinity. At m=25 it is 10. Thus every m>=25 satisfies the
stated sufficient chart threshold. The previous cap E appeared only when
the depleted limit was compared to actual undepletion afterward. Here the
exact actual factor is already part of every model, so that cap is absent.

## Equivalence and remaining gap

Take `v_2(0)=+infinity`. If a model critical value has valuation below L_m,
its difference from the actual value has strictly higher valuation, so the
actual value has the same finite valuation. Conversely, if the actual value
has finite valuation v, choose m>=25 with L_m>v. The same comparison forces
the model valuation to equal v and pass the strict test.

This establishes the stated equivalence for each fixed admitted ordinary r.
It does not convert convergence into separation. In particular, when the
limit is zero, nonzero model values with valuations at least L_m are fully
consistent with the comparison theorem. A finite upper bound on model
critical valuations along cofinal depths would suffice, but no such bound
is proved by these estimates. That is the exact unresolved arithmetic step.

## Computation and provenance

The checker and its imported rational Bernoulli helper were inspected and
replayed into `review/actual_replay`. The result is byte-identical to the
author result. Both manifests validate against the project root.

The run checks r=1,...,6, m=1,...,4, and q=0,...,20: 504 factor-identity
checks, 504 actual model-error checks, and 24 exact first-exit valuations.
The factor identity is repeated across the four model sizes, so these are
126 distinct (r,q) identity inputs. The model errors do use all 504 distinct
(r,m,q) triples. Bernoulli numbers are generated independently by their exact
rational recurrence, and finite Jacobi entries by rational Gram--Schmidt.

These checks validate the reinsertion implementation and its finite examples;
they do not directly test the giant terminal-161 chart. The all-depth and
stationary conclusions rest on the reconstructed proof and named parent
inputs. No extra T digits or actual stationary values were computed.

Self-review: conservative proofreading covered this report. No
mathematical-token correction or unresolved local notation issue remains.
