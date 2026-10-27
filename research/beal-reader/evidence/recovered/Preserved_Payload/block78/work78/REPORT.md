# Beal research, Block 78
## Finite-local flexibility and the ramification-restricted Selmer boundary

Release 7.8.0, 21 September 2026.

The Block77 affine Selmer problem has been sharpened substantially. At every
actual depth-one beta-supporting toric place, the first-stage p condition reduces
to one invariant affine linear equation. More importantly, Neukirch's exact
localization criterion shows that the unrestricted finite localization maps for
both tangent modules k and k(chi) are surjective. Therefore finitely many local
cohomological conditions, including the fixed-seven mixed-trace target when
viewed up to strict local equivalence, do not by themselves give a global Selmer
obstruction.

No one of the eight bounded depth-one patterns is eliminated. The true remaining
problem is ramification-restricted and geometric: the global correction must be
the SAME actual Frey deformation, with any new ramification compatible with the
Diophantine bad primes, endpoint lattices and higher integral lifting.

## 1. Exact first-stage toric condition

At a beta-ramified variable place let T be a pro-seven tame generator and F an
arithmetic Frobenius. Put

    h=(Q-1)/7 mod7,
    c=beta(T) !=0,
    b=beta(F).

The actual first-order toric matrices have normal form

    M=c[[theta,-theta^2],[1,-theta]],

    A=[[theta*b, theta*h-theta^2*b],
       [b,       h-theta*b]].

Relative to the Block73 upper-triangular reference, the first-stage cochain has

    p(T)=theta*c,
    p(F)=theta*b-h.

Eliminating theta gives

    c p(F)-b p(T)=-h c.                                    (1)

This is invariant under F -> T^m F. Conversely every pair satisfying (1)
produces such a first-order toric packet. Thus P_v^geom is a nonempty affine
hyperplane at this precision.

The two independent implementations verify all806736 packets overF49 and the
one-order-later tame relation [A,M]=hM. See notes/TORIC_P_AFFINE.md.

## 2. The finite localization maps are surjective

The external input is Neukirch's Korollar6.4, in the exact formulation reproduced
as Theorem2.1 of Danny Neftin, *Tamely ramified subfields of division algebras*,
J. Algebra378 (2013),184-195.

For a finite module A, write A'=Hom(A,mu_n), let G' be the group of the field cut
out by A', and use the criterion H1(G',A')=0.

For A=k with trivial action,

    A' ~= k(chi),
    G'=Gal(K(mu7)/K)=C6.

Since6 is invertible on the seven-primary module,

    H1(C6,k(chi))=0.

For A=k(chi), the source chi action cancels the target mu7 action in the dual, so
A' is trivial and G'=1. Hence H1(G',A')=0 again.

Therefore for EVERY finite set S,

    H1(K,k) -> product_(v in S) H1(K_v,k)

and

    H1(K,k(chi)) -> product_(v in S) H1(K_v,k(chi))

are surjective. Neftin's Corollary2.3 also permits the correction to be held
fixed at any additional finite disjoint set T.

This is a theorem about finite prescribed local behavior. It does NOT keep the
class unramified at every other place. See notes/FINITE_LOCAL_FLEXIBILITY.md.

## 3. Consequence for the Block77 affine Selmer stages

Fix one global p0 with

    dp0=-alpha cup beta.

For any finite family of desired local first-stage solutions p_v, the differences
p_v-p0|v are k-valued local cocycles. Because k is trivial, there are no local
coboundaries. Surjectivity supplies ONE global z matching all of them exactly.
Thus p=p0+z realizes all chosen finite local p conditions simultaneously.

For the q-stage, once Block77's local H2 classes vanish everywhere, choose one
global q0. Any finite collection of local q solutions differs from q0 by local
k(chi)-cocycles. The second surjectivity theorem produces one global H1 class
matching those local STRICT-EQUIVALENCE classes.

A local coboundary is the first-order change induced by strict upper conjugation
I+7yE12. Hence trace conditions and the labelled mixed-trace target, which are
strict-conjugacy invariant, cannot yield an unrestricted finite-local H1
obstruction once they are individually locally attainable.

This closes the proposed pure finite-place affine Selmer route. It does NOT
construct the actual Frey representation. See notes/AFFINE_SELMER_COLLAPSE.md.

## 4. Where an actual obstruction can still live

The unrestricted localization theorem can introduce new ramification away from
the finitely prescribed places. That is precisely the information the actual
Frey representation cannot forget.

The correct remaining object is therefore a ramification-restricted geometric
Selmer problem. A closure must control at least one of:

- the full set where p and q are permitted to ramify;
- the requirement that any new ramification correspond to an actual divisor of
  the Diophantine data and satisfy its toric/period geometry;
- conditions in the one global integral frame that are not invariant under
  independent local strict conjugacy;
- the mod343 tame-lifting equations, which can reject trace-invisible mod49
  corrections.

For a justified finite Sigma one would compute

    H1(G_(K,Sigma),A) -> direct-sum_(v in Sigma) H1(K_v,A)/L_v,

and its Poitou-Tate dual Selmer cokernel. The current bounded beta patterns do
NOT bound all possible bad divisors of C where beta is unramified, so that Sigma
has not yet been justified globally.

See notes/RAMIFICATION_RESTRICTED_BOUNDARY.md.

## 5. Verification and nonclaims

The primary implementation uses the w^2=5 model of F49. The separate checker
uses t^2=t+1 and converts only the final commutative packet invariants to the
w-basis. Neither imports arithmetic from the other.

| Check | Exact coverage |
|---|---:|
| Base local data (h,c,b) | 16,464 |
| First-order toric packets | 806,736 in each implementation |
| Algebraic formula checks | 7,260,624 primary checks |
| Dual-module action checks | 588 in each implementation |
| Wrong-sign negative controls | 691,488 failures |

Both implementations agree on the order-independent canonical aggregate of all
packets. The finite computations audit B78.1 and the module-action translation;
they do not prove Neukirch's theorem.

No Frobenius point counts, Lean compilation, or independent mathematical review
was performed. No one of the eight Block70 patterns is eliminated.

## Remaining obligation

The next target is to classify **geometrically admissible auxiliary ramification**
for p and q at beta-unramified bad primes. Once that is known, compute the truly
ramification-restricted Selmer localization or a support-uniform integral
relation. Pure finite local H1 matching is no longer a plausible source of the
missing contradiction.
