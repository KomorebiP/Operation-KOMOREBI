# The actual global coupling obstruction vanishes

Block 54, v5.4.0. Conditional arithmetic theorem, written proof. The classical
leaves are identified in `../source_records/SOURCE_CHECK.md`.

## B54.4. Local lifting at every place

Use the same actual eta_n=a_n/chi_7 of Block53. We claim that its restriction to
every local Galois group lifts from (O/7^n)^* to (O/7^(n+1))^*.

At a variable place of residue characteristic q!=7, eta has seven-power image,
so wild pro-q inertia is killed. Its tame inertia image has order7^k. If it
is nontrivial, B54.2 gives k+1<=h=v_7(Q-1). An integral principal-unit lift of
its generator has order7^(k+1), by the unit-order calculation, and this divides
Q-1. If the original inertia image is trivial, choose the trivial lift.
Choose any principal-unit lift of the unramified Frobenius value. The two
chosen values commute and satisfy the tame relation FTF^-1=T^Q. Hence they
define a continuous character of the local tame group at the next precision.
Equivalently use the seven-primary quotient of local reciprocity:
Z_7 (uniformizer) times Z/7^h (residue units). This argument does not require
that the chosen lift be the next actual matrix diagonal.

At the fixed places2,3,5,7, eta_n itself is trivial on the FULL local group by
Block53. Take the trivial lift. At all other finite places eta is unramified,
and any lift of its Frobenius value works. At real places its odd-order image
is trivial, and the same is true of the trivial lift. The n=1 case is already
trivial for eta. Therefore delta(eta_n) is locally zero at every place.

## B54.5. Global localization is injective for this coefficient module

Let k=F_49 with TRIVIAL G_K action. Then

    H^2(K,k) -> product_v H^2(K_v,k)

is injective. Here cohomology means continuous Galois cohomology.

Proof. Put L=K(zeta_7). Its degree over K divides6, and in this particular
case equals6. Restriction followed by corestriction multiplies cohomology by
[L:K], which is invertible on k. Thus restriction to H^2(L,k) is injective.

Since L contains mu_7, fix a primitive root to identify the trivial F_7 module
with mu_7. Choosing an F_7-basis of k identifies H^2(L,k) with two copies of
H^2(L,mu_7). The exact sequence

    1 -> mu_7 -> Lbar^* --seventh power--> Lbar^* -> 1

and Hilbert90 identify H^2(L,mu_7) with Br(L)[7]. This uses the standard
cohomological description H^2(L,Lbar^*)=Br(L). The Brauer local-global
injection implies that a class in H^2(L,k) zero at every completion is zero.
Local restriction is compatible with the global restriction K->L. Hence an
everywhere locally zero class over K restricts to zero over L and is itself
zero. QED.

The coefficient twist matters: alpha has twist chi and beta has twist chi^-1,
so their cup and the kernel of the unit lifting sequence both have trivial
action. Applying a Brauer statement directly to an unspecified twisted
coefficient module would not justify this argument.

## B54.6. Actual cup-zero and existence of a global character lift

Block50's identity, with its preserved sign convention, is

    [alpha] cup [beta] = -delta(a_n) in H^2(K,k),

where delta is the connecting map for

    0 -> k -> (O/7^(n+1))^* -> (O/7^n)^* -> 1.

The exact cyclotomic character lifts, so delta(a_n)=delta(eta_n). By B54.4 this
class is locally zero everywhere; by B54.5 it is globally zero. Consequently

    delta(a_n)=0,             [alpha] cup [beta]=0.         (C)

Exactness of continuous cohomology gives a continuous global character lift
of a_n to (O/7^(n+1))^*. This is an EXISTENCE theorem for a character, not an
explicit computation of its values or a statement about its minimal conductor.

An orthogonal local interpretation is B54.1: wherever beta ramifies at a
variable place, alpha is locally zero. The older nonzero upper-endpoint cup
obstruction cannot be realized there. The local-lifting proof also covers
variable places where beta is unramified but eta is not.

## Precisely what has changed

The old abstract nonzero-cup matrix example remains valid. It does not have
Block53's global Frobenius precision. The old global q=1504231 ray-character
family also remains a valid family of characters, but h=1 at its supporting
places and it has nontrivial inertia. B54.2 now excludes its identification
with the ACTUAL eta_n at EVERY n>=2, including bad13. Block53 had excluded
only its depth2 member and the good13 higher-depth cases.

It is still false that polarization or real multiplication alone makes every
such cup product zero. The new result uses actual natural monodromy, actual
Frobenius in the same lattice, and the globally derived diagonal precision.

## Boundaries that must not be crossed

(C) does not imply beta=0 or alpha=0. Orthogonal nonzero cohomology classes can
exist. It does not imply eta_n=1 for n>=3. It does not increase the actual stable
lattice depth: the next diagonal entry may fail multiplicativity through the
matrix cross terms, even though some other character is a lift. Nor does the
proof produce a conductor-preserving lift or a lift equal to the separately
chosen local lifts at all places. An unrestricted global lift can change its
local kernel-valued corrections and may acquire additional ramification.

In particular, one cannot reapply the natural-matrix arguments to an arbitrary
lift and iterate them to claim eta=1 or a full characteristic-zero reducibility
theorem. The complete reducible branch, CM branch, higher Hilbert levels,
full(3,5,7), and full Beal remain unresolved.
