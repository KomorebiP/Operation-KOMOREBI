# B77.3. The remaining problem is an affine adjoint Selmer problem

B77.1 and B77.2 reduce the global second-stage problem to local matching.  This
note records the reduction precisely so that later blocks do not revert to
independent local lifts.

## Stage P

Let

    P = { p in C^1(K,k) : dp=-alpha cup beta }.

It is a nonempty affine space under `Z^1(K,k)`, using the inherited cup-zero
result.  At each place `v`, let `P_v^geom` be the set of first-stage local
cochains compatible with the actual local integral representation: toric
monodromy, fixed-prime data, endpoint normalization, and semilinear symmetry.

The first matching problem is

    find p in P with p|_v in P_v^geom for every v.           (P)

This is already an affine Selmer problem.  The existence of arbitrary local
solutions does not imply (P).

## Stage Q

Fix one global `p` satisfying (P).  If all local classes `[mu_p]_v` vanish,
B77.2 gives a global solution `q_0` of

    d_chi q_0=R_p.

Every other global solution is

    q=q_0+z,     z in Z^1(K,k(chi)).                         (1)

At each place let `Q_v^geom(p)` denote the actual allowed local affine set for
`q`, after fixing the same `p`.  Choose one local solution `q_v` in that set.
Then a global solution matching all local conditions exists exactly when

    ( q_v-q_0|_v )_v

lies in

    loc H^1(K,k(chi)) + product_v L_v,                       (2)

where `L_v` is the homogeneous tangent subspace preserving the local geometric
condition.  Equation (2) is the affine q-Selmer obstruction.

Equivalently, after quotienting by the `L_v`, the required tuple must belong to
the image of the global localization map

    H^1(K,k(chi)) -> direct-sum_v H^1(K_v,k(chi))/L_v.       (3)

This is the exact point at which Poitou-Tate duality can become useful.  The
dual Selmer group supplies linear functionals that can rule out a nonhomogeneous
local target.

## The fixed-seven condition is genuinely affine

At `v=7`, Blocks 71--74 do not merely prescribe a homogeneous subspace.  The
actual period/uniformizer comparison imposes the nonzero labelled mixed-trace
value

    Delta(tau,g)/49 = nu_7 beta(g),
    nu_7 = v_7(C) v/(2 epsilon)  mod7.                       (4)

Thus the target at seven is an affine coset depending on the actual arithmetic
coordinate `v_7(C)` and the coefficient orientation.  This is exactly the kind
of information that Block 70's homogeneous finite-sieve limitation does not
absorb by adding fresh conductor variables.

## What must be computed next

For each of the four support patterns (and its coefficient conjugate):

1. derive `P_v^geom` and `L_v` at the nine ramified toric primes;
2. derive the fixed-local conditions at 2,3,5,7,13 and any other forced place;
3. compute the global localization image or its Poitou-Tate orthogonal;
4. test whether the fixed-seven affine target lies in that image.

A zero result would eliminate all eight bounded tuples.  A nonzero affine
solution would provide an explicit finite-dimensional parameterization of the
remaining global deformation, which is also decisive progress.
