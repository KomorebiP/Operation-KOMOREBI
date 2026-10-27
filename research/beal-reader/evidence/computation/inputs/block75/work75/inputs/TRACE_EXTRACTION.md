# B74.2. Extracting fixed-seven valuation from a polarized trace

All arithmetic conclusions retain TARGET_CONTRACT.md. Use ONE global natural frame,
ONE embedding of G_F into G_K, and compatible Kummer roots throughout. Define

    T(g)=tr_O rho(g),
    D(tau,g)=T(tau g)-T(tau)-T(g)+2.

The elementary exact identity is

    D(tau,g)=tr((rho(tau)-I)(rho(g)-I)).                   (3)

T denotes a rank-two COEFFICIENT-RING trace. A rational rank-four trace does not
in general retain the information in(3).

## Local toric line alignment through the actual depth

Modulo7^n, the global lower-left entry is zero, so the two local diagonal entries
are characters a_n,d_n. At F, the exact toric trace and determinant give a_n+d_n=chi+1
and a_n*d_n=chi. There is an inertia element h with chi(h)-1 a unit modulo7.
The residual orientation is a_n(h)=chi(h), d_n(h)=1 mod7. Factoring the characteristic
polynomial at h and cancelling the unit a_n(h)-1 gives a_n(h)=chi(h) modulo7^n.
Subtracting trace identities at hg and g gives

    (chi(h)-1)*(a_n(g)-chi(g))=0.

Thus a_n=chi and d_n=1 on the full local group at precision7^n. This argument is
local. It does not assume global eta_n=1.

The projection of the natural chi-line modulo7^n into the local toric quotient
would be a G_F-map chi->1. The same separating element kills that map. The two
primitive rank-one summands therefore coincide. An integral local graded-basis
matrix P=[[a,b],[d,e]] can be chosen with a,e units and d in7^n O. The matched
coefficient bases on torus and period quotient use the exact valuation map7c I.

Set J=P E12 P^-1. Direct computation gives

    J=(det P)^-1*[[-ad,a^2],[-d^2,ad]],
    J11,J22 in7^n O,  J21 in7^(2n)O,
    J12 mod7 = kappa = v/(2epsilon) in F7*.

The last normalization is the inherited residual coefficient comparison. No local
sign is arbitrarily chosen to make a numerical contradiction.

## The probe eliminates ALL unit periods, not just their leading expansions

Let tau_j be B74.1's element. The actual split toric period extension, including
its unknown higher unit terms, evaluates on tau_j by its valuation matrix. That
matrix is EXACTLY7c I, c=v7(C). Therefore

    rho(tau_j)=I+7c J mod7^j.                            (4)

Unlike a truncated explicit unit formula, (4) has no bound j<=7c-1. It kills unit
classes rather than approximates them. The actual uniformization/functoriality
input remains inherited, and is not proved by the matrix tests.

## Existence of a detecting global element

Let G0=ker rhobar. There is g in G0 with beta(g)!=0. To see this, restrict alpha and
beta to G_(K(mu7)), where they are additive. Restriction does not kill a nonzero
beta, by degree-six inflation-restriction. Their joint F7-linear image is stable
under cyclotomic conjugation acting by3 on alpha and5 on beta. The projection
(T-3I)/(5-3) preserves this ACTUAL joint image and extracts(0,b). Choose b!=0.
An element realizing that vector has chi=1, alpha=0, hence belongs to G0.
This construction does not prescribe two unrelated abstract local characters.

## The depth-one formula

Choose tau=tau_3. When n=1, (4) gives

    rho(tau)=I+7nu7 E12 mod49,
    nu7=c*v/(2epsilon) mod7.

The possible diagonal first-order terms vanish because J11,J22 are divisible by7.
The unit-only auxiliary reference rho0 also evaluates to I modulo49 on tau, so
this is exactly the fixed-seven adjoint valuation defined in Block73.
For g in G0 write rho(g)=I+7A modulo49. Then A21=beta(g). Applying(3) gives

    D(tau,g) =49 nu7 beta(g) mod343.                     (5)

Consequently, for beta(g)!=0,

    BOX: nu7 = beta(g)^-1 * (D(tau,g)/49 mod7).           (6)

Only the THREE labelled traces T(tau),T(g),T(tau g) modulo343 are required once
beta(g) and the probe label are known. No full inertia comparison, complete trace
function, or conductor bound is assumed.

The division is of an O element known divisible by49, with the result read in k.
Using modulo49 traces alone loses the entire quantity. Using arbitrary three
Frobenius traces without identifying the labels tau,g,tau g is not legitimate.
The original lower-left7beta has not been discarded; it is what the probe detects.
