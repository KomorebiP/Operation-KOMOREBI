# Block 33: finite observation kernels and observable quotients

## Claim card
Let R be a commutative ring, V an R-module, A an alphabet, T_d linear endomorphisms,
v a seed, and lambda:V->R a linear output. Words are consumed left to right:
T_(d::w)(x)=T_w(T_d(x)). The empty word is the identity.
No field, freeness, or absence of zero divisors is assumed.

Define N as the intersection of the kernels of lambda composed with T_w over
all finite words. N is the greatest T-invariant submodule in ker(lambda).
It is not generally just ker(lambda): future digits can move a state into a
currently visible coordinate.

## Finite horizon, with indexing fixed
Let N_0=V and

    N_(n+1)=N_n intersect ker(lambda) intersect intersection_d T_d^(-1)(N_n).

Then N_n consists exactly of states killed by every observation of a word of
length < n. In particular N_0 has no tests and N_1 tests the empty word.
The first N_n factor is redundant on this descending orbit but makes the
transformer deflationary on every input submodule.

If V is finite of cardinality p^b, with p prime, every submodule has p-power
cardinality. Each strict decrease lowers that exponent at least once. If the
chain were still nonstationary after b rounds, its b+1 strict decreases would
force a negative exponent. Consequently N_b=N and all later rounds agree.
Any x not in N has a distinguishing word of length < b. Applied to x-y, this
bounds the length needed to distinguish two inequivalent source states.
The alphabet may be infinite in the theorem. Only for a finite alphabet is the
set of tested bounded words finite. The actual mask alphabet is Fin p.

## Quotient and largest allowable identification
Construct Q=V/N. Invariance lets each T_d descend through the quotient. Since
N lies in ker(lambda), lambda descends as well. Projection q preserves the seed,
transitions, complete words, and outputs. Precisely,

    q(x)=q(y) iff lambda(T_w(x))=lambda(T_w(y)) for every word w.

All distinct quotient states are distinguishable; its unobservable submodule
is zero. Linear reachability of V implies linear reachability of Q.
For every other silent invariant kernel U, U is contained in N and there is a
unique linear surjection V/U -> V/N factoring the source projection. Hence Q
has least cardinality among these silent-kernel quotients of this fixed V.
The exact cardinality identity is |Q|*|N|=|V|.

This does not prove a comparison with every different realization of the same
word behavior. That cross-realization universal property is a next obligation.
It also does not identify the linear span of an orbit with the orbit set or
claim a minimal deterministic automaton.

## Actual rational-mask integration
The source V is Block31's actual correlated ReachableMaskState. Its output is
bundled as a linear map by proving additivity and scalar compatibility of the
inherited finite coefficient formula. No supplied matrix or coefficient oracle
is introduced. The constant compatibility, unit-denominator, positive precision,
and prime hypotheses remain unchanged.
The quotient output on the digits of n equals the nth coefficient of the
already constructed canonical solution F, F(0)=1 and B F=A F(z^p).
The quotient remains linearly reachable and observable. Block32 provides a
chosen cyclic presentation and its intrinsic exponent signature. Outputs reduce
correctly across precision. State-module reduction morphisms are not constructed.

## Exact reference algorithm
In a chosen presentation V=product Z/d_i with d_i dividing m=p^r, represent an
observation lambda by a row l with d_i*l_i=0 mod m. All transition matrices obey
d_i*T_ji=0 mod d_j. Compute the row-observation module by ascending closure of
l and its precompositions with digit maps, using integer HNF and including mZ^n.
If H is a column basis for the transpose observation lattice, then

    N is represented by {x in Z^n : H^T x = 0 mod m}, modulo diag(d_i)Z^n.

A verified Smith proposal D=U H^T V gives the kernel lattice
V*diag(m/gcd(m,D_ii))Z^n. Its HNF K contains diag(d_i)Z^n. A second verified Smith
proposal for K presents Q=Z^n/KZ^n. Projection, representative choice, transitions,
and output are evaluated in mixed cyclic moduli with all source relations checked.
The representative selector is not claimed additive; the quotient projection is.
Exhaustive small-system behavioral partition refinement is independent of both
normal-form algorithms and checks the same state equivalence.

## Restriction witnesses
1. R=Z/4, V=R, T=id, v=1, lambda(x)=2x. The source is linearly reachable but
   N={0,2}; Q has two states. No field-rank argument applies.
2. R=Z/5, V=R^2, T swaps coordinates, lambda(x)=x_0. Immediate output cannot
   distinguish (0,1) from zero; one future digit does. N=0.
3. Empty alphabet still tests the empty word. With lambda=id the kernel is zero.
4. Zero output makes N=V regardless of transitions.
