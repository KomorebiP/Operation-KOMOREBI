# Global rigidity to half the lattice depth

Block 53, v5.3.0. Written proofs, not a Lean certificate.
The arithmetic application is conditional on the explicit inherited inputs
in ../TARGET_CONTRACT.md. None of the arguments below proves those geometric
inputs by running a finite script.

## 1. A local character-identification lemma (B53.1)

Let R=O/(7^n), with n>=1 and O the unramified quadratic integer ring over
Z_7. Let H be a group. Suppose a,d,lambda:H -> R^* are characters satisfying

    a(g)+d(g)=lambda(g)+1,    a(g)d(g)=lambda(g)       for every g in H,
    a mod 7=lambda mod 7,       d mod 7=1.

Assume lambda(g0)-1 is a unit for some g0. Then a=lambda and d=1 on H.

Proof. At g0, the trace and determinant identities give

    (a(g0)-lambda(g0))(a(g0)-1)=0.

The second factor is a unit because of the residual orientation. Hence
 a(g0)=lambda(g0) and d(g0)=1. Subtract the trace identity at g from the
trace identity at g0*g, using multiplicativity of all three characters:

    (lambda(g0)-1)a(g)=(lambda(g0)-1)lambda(g).

Cancel the unit. The trace identity then gives d(g)=1. No diagonalization
of the representation at every g, no reducedness of R, and no freeness of
an extension module are assumed. QED.

The same proof works in a commutative local ring with the stated units.
It does NOT follow from residual trace information alone. It also fails
when the two residual characters coincide everywhere on H. An exact cyclic
counterexample modulo 49 is retained in the verifier: on a generator take
lambda=8, a=15, d=43. The trace/determinant identities hold on every power,
but a is not lambda and d is not1.

## 2. A natural-inertia divisibility lemma (B53.2)

Let O be a characteristic-zero DVR, with uniformizer7 and valuation w(7)=1.
Suppose n>=1 and

    N=[[u,b],[c,-u]],    N^2=0,
    b in 7O,           c in 7^n O.

Then

    u in 7^m O,        m=floor(n/2)+1=ceil((n+1)/2).     (1)

Proof. The upper-left entry of N^2 is u^2+bc, so u^2=-bc lies in
7^(n+1)O. If u is nonzero, 2w(u)>=n+1, giving (1); if u=0 the assertion
is immediate. QED.

More generally, b in 7^t O gives w(u)>=ceil((n+t)/2). In the application
only t>=1 is needed. This does not require beta to ramify, exact valuation
of c, an upper bound on a prime multiplicity, or a bound on the residue
cardinality. The field-coefficient valuation is the unramified one, not
the normalized valuation in a ramified coefficient extension.

The condition b in 7O is essential. At n=2 the matrix

    [[-7,1],[-49,7]]

is nilpotent but its diagonal is not divisible by 49. At n=3 the matrix

    [[-49,7],[-343,49]]

satisfies all the hypotheses and its diagonal has valuation exactly 2.
Thus replacing m by n is already false locally at n=3.

## 3. The actual global diagonal characters

Use the single natural-lattice Frobenius-at-three basis from Block51:

    rho(g)=[[a(g),b(g)],[7^n c(g),d(g)]],
    a mod 7=chi_bar, d mod 7=1, det(rho)=chi_7.

Multiplication of the matrices shows that a_n=a mod 7^n and d_n=d mod 7^n
are continuous characters. The cross terms vanish modulo 7^n. They are
units because their residual values are units, and

    a_n*d_n=chi_7 mod 7^n.

Define the actual diagonal correction

    eta_n=a_n/chi_7,            d_n=eta_n^(-1).           (2)

It has values in (1+7O)/(1+7^n O). This is one global character extracted
from the actual representation, not a collection of chosen local roots
of its characteristic polynomials.

## 4. Fixed bad places: full precision, not only residual splitting

At each place over 2,3,5,7, the inherited characteristic-zero twisted RM
representation has local subcharacter chi_7 and quotient1. Therefore its
trace is exactly chi_7+1 at every local Galois element. The determinant
is exactly chi_7. After reduction, apply B53.1:

| place | element with chi_bar !=1 | source of exact toric sequence |
|---|---|---|
| above 2 | arithmetic Frobenius, value4 mod 7 | Block47 even-C graph plus Block48 identification of nu |
| above 3 | arithmetic Frobenius, value9=2 mod 7 | Block49 split toric calculation, length7v_3(C)-3 |
| above 5 | arithmetic Frobenius, value5 mod 7 | Block49 split toric calculation, length14v_5(C)-5 |
| above 7 | an inertia element with nontrivial mod 7 cyclotomic value | Block48 analytic uniformization at all 7-power levels, nu=psi |

Consequently

    eta_n|G_v=1 mod 7^n          for v above 2,3,5,7.        (3)

At seven, Frobenius does NOT have cyclotomic value49 in the unit group.
The separating element is on inertia. The analytic uniformization supplies
the characteristic-zero sequence even though the Tate prime equals the
residue characteristic. We do not import a prime-to-residue-characteristic
filtration into that case.

The source comparison, exact frozen file hashes, and the passage from the
four-dimensional sequence to the RM rank-two trace are recorded in
LOCAL_INPUT_AUDIT.md. An inherited statement that beta splits locally
would by itself be insufficient to prove (3).

## 5. Variable bad places: ramification disappears through m digits

Let q divide C, with q outside{2,3,5,7}, and v lie above q. The inherited
split toric description of the natural lattice gives, for every inertia
element tau,

    rho(tau)=I+N_tau,    N_tau^2=0,    N_tau in 7 M_2(O).  (4)

This follows from the natural period content
1+v_7(v_q(C))>=1, together with the tame-character description of inertia.
The trace-zero shape holds in characteristic zero. The lower-left entry
is in 7^n O because this is the same global basis. Apply B53.2 to N_tau.
Since chi_7(tau)=1 for q!=7, equations (1)--(2) imply

    eta_n(tau)=1 mod 7^m,         m=floor(n/2)+1.          (5)

This covers every variable bad place, including those where beta is
unramified, exceptional multiplicities, and arbitrary values of
v_7(q^f-1). Neither eligibility nor an ordinary hypothesis is used.

At the other finite places outside 2,3,5,7, the representation and nu are
unramified unless the place divides C. Thus the reduction eta_m of eta_n
modulo 7^m is unramified at every finite place by (3)--(5).

## 6. The global step (B53.3)

The image of eta_m is a finite abelian7-group. At a real place the Galois
group has order2, so its image is trivial. The finite extension cut out
by eta_m is consequently abelian and unramified at ALL places of K.

For K=Q(sqrt5), the ring of integers is Z[phi], discriminant5. Minkowski's
bound for each ideal class is sqrt5/2<2, so every class has an integral
ideal of norm 1. Therefore Cl(K)=1. The Hilbert class field theorem now
forces eta_m to be trivial. This uses Cl(K), not the larger cyclotomic
field and not the ramified ray-class group supporting beta.

For an elementary cross-check of the class-number input, write any x in K
as x0+x1*phi and subtract integers from x0,x1 to leave r,s in[-1/2,1/2].
Then |Norm(r+s*phi)|=|r^2+rs-s^2|<=3/4<1. Thus Z[phi] is norm-Euclidean
and in particular a PID. The global class-field implication is still a
classical source theorem; this observation does not replace it.

We have proved, under the inherited geometric inputs,

    eta_n=1 mod 7^(floor(n/2)+1),                           (6)
    a_n=chi_7 mod 7^(floor(n/2)+1),
    d_n=1 mod 7^(floor(n/2)+1).

This holds for every n>=1. The assertion at n=1 is the existing residual
orientation; the first new precision is at n=2. No claim eta_n=1 modulo
7^n is made for n>=3.

## 7. Additive range of the surviving correction (B53.4)

Put m=floor(n/2)+1 and r=n-m>=0. Since2m>=n+1, the ideal7^m O/7^n O
has square zero. There is a unique continuous additive character

    theta_n:G_K -> O/7^r O

such that

    eta_n=1+7^m theta_n mod 7^n.                            (7)

For r=0, the target is the zero group and eta_n=1. For r>0, uniqueness
and additivity follow by dividing eta_n-1 by 7^m and using square-zero
multiplication. This character is locally zero at 2,3,5,7 and unramified
away from the variable bad places, but it need not be globally zero.

In particular eta_2=1, so the connecting obstruction delta(a_2) vanishes
because a_2 is the reduction of the actual cyclotomic lift. This does NOT
prove beta=0 or exclude n=2 when 13 divides C. At n=3 the surviving
correction is an additive F_49 character times49 modulo 343, which can
still have a nonzero next-level lifting obstruction.

The old ray construction eta_n=1+7^(n-1)t is ruled out as an actual
correction at n=2 by (6), even when 13 is bad. For n>=3 it satisfies the
precision bound; the existing good 13 exclusion remains, but bad 13 is not
eliminated by this observation.
