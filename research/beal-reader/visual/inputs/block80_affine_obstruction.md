# B80.5--6. Complete first-stage linear operator and the unevaluated affine class

Fix the residual alpha,beta, common frame and reference. Let J be the exact
ordinary localization image from B80.3, of size24-by-10. On the24 local character
coordinates let E have fifteen rows:

* the first six select the fixed-local coordinates in(8);
* one row per support prime is c_q*z(F_q)-b_q*z(I_q).

Define A=EJ (15-by-10). Every new b_q includes its self-conductor contribution and
the frozen inertia is converted by(16). The complete local and global matrices,
RREFs, kernels and left-null bases are supplied for each pattern.

## Exact homogeneous kernels

|Pattern|rank A|dim_k ker A|dim_k coker A|remaining ordinary-character support|
|---|---:|---:|---:|---|
|A|7|3|8|307,797,1483|
|B|7|3|8|307,797,1483|
|C|8|2|7|307,1483|
|D|7|3|8|307,797,1483|

The kernel basis in the global parameter order (a,x_q1,...,x_q9) consists exactly
of the unit vectors in the listed minus-congruence conductor coordinates. Thus
all plus-congruence inertia differences vanish AFTER imposing every toric row.
This says nothing about the absolute plus-congruence inertia of a primitive p0.

The two separate arithmetic implementations reconstruct all matrices. Nonzero
square minors and independently checked null bases give rank equality, not just
a numerical lower bound. Pattern C strictly improves Block79: its two old plus
kernel vectors on the9 inertia coordinates were

    (3,0,0,5,1,5,1,0,0), (2,0,5,5,1,0,0,0,1).

The additional toric constraints at197 and337 evaluate on them as

    [[3,1],[5,2]],             determinant=1 mod7.         (17)

They remove BOTH extra plus directions. Other old ranks are unchanged.

With the EXTRA common pointwise semilinear j/frame/reference hypothesis,
minus-congruence inert characters have coefficients in wF7. Thus, if the affine
Stage-P problem has a solution, the corresponding same-frame numbers of first-
stage choices are bounded by343,343,49,343. Without that extra condition the
bounds are49^3,49^3,49^2,49^3. These are cochain counts for the stated first-stage
conditions only, not representations, full q-deformations, or integer solutions.

## The arithmetic affine origin remains essential

By B80.1 choose a bare restricted global primitive p0. This is a choice guaranteed
to exist, not a list of values computed in this release. Define t(p0) in k^15:

* at the first six coordinates use the local ordinary character p_v^fix-p0|_v;
* at support q use

    t_q=-h_q*c_q - (c_q*p0(F_q)-b_q*p0(T_q)).             (18)

The cochains at support are local characters because alpha is locally zero there.
At fixed places their DIFFERENCE is an ordinary character. Only those character
coordinates are evaluated using the Artin symbols of(8).

There is a global p meeting all fixed trace and toric first-stage conditions iff

    A*z=t(p0) for some z in k^10.                        (19)

Choose the supplied full left-null basis N, so N*A=0 and rank N=15-rank A. Then

    BOX: Stage-P solvable iff N*t(p0)=0.                 (20)

Replacing p0 by p0+z0 shifts t by -A*z0. Thus the class of t in coker A, and its
coordinates N*t, are independent of the choice of bare primitive. No arbitrary
local solution can be substituted for the SAME global p0 in this argument.

The target vector and these seven/eight obstruction coordinates have NOT been
computed for any of the eight actual arithmetic patterns. Some coordinates may
vanish for further structural reasons, but no such evaluation is claimed here.
Their independence is linear-algebraic on the potential target space, not a claim
of independent arbitrary choices in an actual Galois representation.

## Executable evaluator

Run

    python -B work80/computations/evaluate_target.py --input target.json --output result.json

Input fields are pattern A/B/C/D, kind synthetic/supplied, nonempty provenance,
basis "a+7*b for a+b*w; w^2=5", and15 integers0..48 in target. The evaluator returns
the obstruction coordinates, a particular CHARACTER correction if the target is
in the image, and a homogeneous kernel basis. It does not construct p0, authenticate
the target's arithmetic source, or infer a Frey representation. Synthetic examples
are explicitly tagged. The program always records arithmetic_target_authenticated
as false. A synthetic zero target is not an affine arithmetic origin.

The auxiliary-q and higher integral lifting problems remain even after(20) passes.
The Stage-P localization operator alone is not a full adjoint Selmer computation.
