# Block 33 — Observable quotients of the correlated reachable machine

## Status and roadmap

The Block 33 target is proved under its stated fixed-system contract. The source
has 1,054 declared theorems in 87 production modules, adding 67 theorems to the
987 declarations in Block 32. All inherited mathematical modules are unchanged;
the root gains one import. This is Goal I / Phase E. The separate cross-realization
minimality and canonical-behavior theorem remains a Block 34 obligation.

## What is identified

For a commutative ring R, an R-module V, linear digit maps T_d, and linear output
lambda, define

    N = {x : for every finite word w, lambda(T_w(x)) = 0}.

Words are executed left to right. The empty word is included. Lean proves that N
is the greatest transition-invariant submodule contained in ker(lambda).
Merely quotienting by the immediate output kernel is generally invalid.

The quotient Q=V/N inherits the initial state, digit maps and output. Its
projection q satisfies

    q(x)=q(y) iff every future word gives equal outputs on x and y.

All quotient states are therefore distinguished by some future word unless they
are equal. The quotient's own unobservable submodule is zero. If V is linearly
reachable from its seed, so is Q. Reachability means span, not the actual orbit set.

For any other silent invariant kernel U of the SAME source V, there is a unique
linear surjection V/U -> V/N factoring the source projection. This proves minimum
cardinality among these quotients, not yet among all different realizations.
The exact cardinality identity is |Q|*|N|=|V|. It allows nonfree modules and zero
divisors in R. A normalized output on the seed also makes the quotient output
surjective onto R.

## Finite observation horizon

Define N_0=V and

    N_(n+1)=N_n intersect ker(lambda) intersect intersection_d T_d^(-1)(N_n).

Lean proves that N_n is exactly the set killed by all words of length < n.
Thus N_0 performs no observations and N_1 tests the empty word.
If V is finite with |V|=p^b and p prime, every strict inclusion decreases the
p-cardinality exponent by at least one. Consequently N_b=N and the chain is fixed.
An observable difference has a distinguishing word of length strictly less than b.
The theorem allows an infinite alphabet; the bounded-word set is itself finite
only for a finite alphabet. The mask application uses Fin p.

For the actual source, b=log_p|ReachableMaskState|. This is a cardinality exponent,
not a dimension over a field, and is not asserted to be the sharpest horizon.

## Actual mask integration

The source V is Block 31's actual correlated reachable submodule. The existing
finite coefficient output is proved additive and scalar-compatible and bundled
as a linear map. The transition rules are unchanged. No independently assumed
matrix or supplied-series oracle is introduced.

Under p prime, r>0, p not dividing B(0), and A(0)=B(0) in ZMod(p^r), the quotient
machine outputs coefficient n of the constructed canonical F for every natural n,
where F(0)=1 and B(z)F(z)=A(z)F(z^p). Digits are least-significant first, including
the empty word at n=0. Word output and projected initial states are also proved.

The actual quotient is both linearly reachable and observable. Block 32 gives it
a chosen cyclic presentation and an intrinsic exponent signature. Its outputs
remain compatible under positive precision reduction. No state-module reduction
morphism or common cross-precision coordinate system is claimed.

ObservableCanonicalMaskCertificate retains the full Block 32 certificate and adds
the greatest silent kernel, exact finite closure, reachability, observability,
canonical coefficient output, and cardinality identity.

## Finite exact examples

The following examples use A=1. An exponent e means p^e module elements.

| p | r | B | Reachable exponent | Observable exponent | Observable factor exponents | Closure rounds |
|--:|--:|---|--:|--:|---|--:|
| 2 | 4 | 1+4z | 8 | 4 | 4 | 1 |
| 2 | 8 | 1-z | 52 | 30 | 2,5,7,8,8 | 4 |
| 2 | 8 | 1+16z | 16 | 8 | 8 | 1 |
| 3 | 6 | 1+81z | 9 | 6 | 6 | 1 |

For B=1-z at p=2,r=8, this removes a silent submodule of 2^22 elements and reduces
the permitted linear state count from 2^52 to 2^30. The displayed quotient has
cyclic factors Z/4, Z/32, Z/128, Z/256, Z/256. Its exponent sum is 30.

Twenty-five of the 49 actual mask cases have a strict reduction. The numbers are
finite exact Python results, not separate concrete kernel reductions of Lean's
noncomputable mask presentation. Complete lattice and Smith certificates for the
four displayed cases are retained in results/audit_observable.json. No execution
speed, memory reduction, or minimum DFA follows just from these cardinalities.

## Restriction witnesses

Over Z/4, take V=R, seed 1, T=id and lambda(x)=2x. The source is linearly reachable,
but N={0,2} and the observable quotient has two elements. These are production
Lean theorems. A field-rank argument would not justify this torsion quotient.

Over Z/5, let T swap two coordinates and lambda return the first coordinate.
The vector (0,1) has immediate output zero, but one digit gives output one. Here
N=0, so the immediate kernel cannot be used as the quotient kernel.

With an empty alphabet, the empty-word observation is still tested. With lambda=id,
N=0. With output identically zero, N=V for every transition family.

## Fresh verification

The exact-pinned predecessor archive and retained-evidence verifier passed before
extension. The predecessor root was freshly rebuilt. The authoritative Block 33
run subsequently deleted only its project-local .lake/build and rebuilt all 87
modules with warning-as-error. The clean build completed 2,613 Lake jobs.

All 13 final phases passed with identical before/after execution-input hashes.
All 1,054 declared axiom closures were inspected. An environment-driven inventory
checked 2,394 project-owned theorem constants including generated support constants;
that is audit coverage, not additional discoveries. Eighteen source theorems are
axiom-free. The only observed axioms are propext, Quot.sound and Classical.choice.
There are 87 .olean and 87 .ilean project artifacts.

Twenty new concrete Lean examples, eight universal applications, and 51 immediate
predecessor examples passed. Four deliberately invalid controls were rejected for
the expected contradiction or placeholder diagnostic, and a positive control
passed. The final example module passed leanchecker replay through Lean's own
kernel, not an independent implementation.

The fresh integer audit passed 21,442 assertions: 251 small generic systems and
49 actual-mask cases. Independent exhaustive behavioral partitions validate the
small-system equivalence relation without HNF or Smith normal forms. Actual-mask
checks include 809 full matrix columns against polynomial routing and 1,568
coefficient comparisons each against the direct recurrence and predecessor.
Historical numerical suites are preserved, not relabeled as freshly rerun.

## Provenance and limits

The toolchain is Lean4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d,
and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Cached dependency revisions
were checked but the dependencies were not independently rebuilt. Stable4.34.0
compatibility and independent human/kernel review remain unperformed.

The exact Python reference uses integer HNF and checked Smith proposals. It is
not formally proved equivalent as executable code to the Lean construction.
The noncomputable interfaces remain. No minimum DFA, cross-realization uniqueness,
canonical literal matrices, analytic convergence, or time/bit/memory guarantee is
claimed. See PROOF_BOUNDARY.md and DEVELOPMENT_FAILURES.md.
