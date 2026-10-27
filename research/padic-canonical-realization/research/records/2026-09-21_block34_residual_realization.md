# Block 34 — Intrinsic residual modules and cross-realization minimality

## Claim card
Let R be a commutative ring, A an alphabet, and f : List A -> R an ALL-WORD
behavior. A linear realization consists of an R-module V, a seed v, digit
endomorphisms T_d, and an R-linear output lambda. Words are consumed left to
right: run(u ++ w,x) = run(w,run(u,x)). No field or freeness assumption is made.

A realization is reachable when span{run(u,v)} = V. It is observable when equality
of lambda(run(w,x)) and lambda(run(w,y)) for every w implies x=y.

## Intrinsic construction
For each prefix u, f_u(w)=f(u ++ w). Put H_f=span_R{f_u}, a submodule of the full
function module (List A -> R). Its seed is f, output is evaluation at the empty
word, and digit map is D_d(g)(w)=g(d::w). Because D_d(f_u)=f_(u++[d]), this is an
invariant submodule. It is reachable and observable directly from its definitions.

For any realization M define beta_M(x)(w)=lambda(run(w,x)). This is R-linear.
The exact identities proved in ResidualBehavior.lean are

    ker beta_M = unobservable(M),
    beta_M(reachable(M)) = H_(behavior M).

The image identity follows by mapping the spanning orbit: beta_M(run(u,v)) is
exactly f_u. No numerical rank argument, basis, or nonunit division is used.

If M is reachable, beta_M is surjective onto H_f. If it is also observable,
it is injective. The resulting R-linear equivalence preserves seed, digit maps,
and output on every state. The observable quotient of any reachable source is
therefore linearly equivalent to this same intrinsic residual module.

## Cross-realization result
For reachable M and reachable-observable N with the same f, compose beta_M with
beta_N inverse. This is a surjective simulation M -> N. Observability of N forces
uniqueness: any two simulations agree on all future observations of every source
state, hence are equal. For two reachable-observable realizations the comparison
is the unique intertwining linear isomorphism.

For an arbitrary competing realization W, first restrict W to its reachable
submodule. That reachable part surjects onto N. If W is finite,

    |N| <= |reachable(W)| <= |W|.

Thus N has minimum cardinality among ALL finite R-linear realizations of f,
not only among quotients of one fixed source. This is not minimum DFA cardinality,
minimal generator rank, a preferred basis, or literal canonical matrices.

## Finite comparison horizon
The product difference system (M,N) on V x W has output lambda_M-lambda_N.
If |V|=p^b and |W|=p^c for a prime p, its cardinality is p^(b+c).
Block33's observation theorem gives

    behavior M = behavior N
      iff they agree on all words of length strictly less than b+c.

The empty word is included. For the actual finite alphabet this is a finite test;
for an infinite generic alphabet it is only a finite-length horizon.
No polynomial-time or tight-horizon claim is made.

## Actual masks
For prime p, positive r, integer A,B, p not dividing B(0), and equal constants
modulo p^r, the canonical Mahler series is already constructed. Define f(ds)
as coefficient cartierWordValue(p,ds) of that series. Block33's actual quotient
realizes f on every word, including noncanonical digit encodings. The generic
results identify it with H_f, prove global minimum cardinality, and prove unique
machine isomorphism to every other reachable-observable realization of f.
The certificate retains the entire Block33 certificate and additionally carries
the residual equivalence, its simulation law, all-word behavior, and universal
finite-cardinality lower bound.

## Scope witnesses
The constant-one realization on ZMod5 has a singleton deterministic orbit but
minimum linear module cardinality five. Scaling its seed by 2 and output by 3
changes coordinates without changing behavior. A zero-output system on the same
module has a different behavior, so the underlying module signature alone does
not classify machines.
The ZMod4 twice-identity output example has a two-element minimal behavior module,
demonstrating that the argument is not a field-dimension argument.
A binary system outputs zero on the empty word and every word ending in 1, yet
outputs one at [0]. Agreement restricted to canonical integer encodings cannot be
silently substituted for equality of all words.

## Scientific evidence
The universal statements are proved by Lean proof terms. The finite audit checks
90 pairs of different realizations by exhaustive small state/span enumeration,
residual image comparisons, and future-observation signatures. Sixteen actual
mask cases compare finite Hankel matrices built from the independent coefficient
recurrence against the earlier module-quotient implementation. These comparisons
are not a formal executable refinement of the Python code.
