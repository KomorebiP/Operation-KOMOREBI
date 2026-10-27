# A protected arithmetic realization tower inside Komorebi Space

Checkpoint RR7. Base RR6 archive SHA-256:
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.

This note constructs finite view systems, their protected obstruction class,
and a coherent local arithmetic tower. It does not infer a global height
bound from local reconstruction. No historical novelty is claimed for the
underlying Teichmuller, cyclic-extension, or inverse-limit arithmetic.

## 1. Rings, coefficient groups and every precision map

Fix a prime p, including p=2. Write k=F_p and R_N=Z/p^N Z for N>=1,
with R_0 the zero ring. Let t_0:k->R_0 denote the unique zero map,
used only for the zero tails below. Put K_N=R_(N-1). There are maps

    rho_N : R_(N+1) -> R_N,
    r_N   : R_N -> k,
    i_N   : K_N -> R_N,       i_N(z)=p z.

The last map is an injective homomorphism of additive groups whose image
is ker(r_N). Division by p below always means its inverse on that image;
it is not division by a unit of R_N. At N=1 its domain is the zero group.
The reductions on K_(N+1)->K_N and R_(N+1)->R_N make the i_N square commute.

For x in k, choose an integer representative x_tilde and define

    t_N(x)=x_tilde^(p^(N-1)) mod p^N.                       (1)

Here t_1 is the identity map of k. The following elementary congruence
proves all precision assertions we use: if u=v mod p^r, r>=1, then
u^p=v^p mod p^(r+1). Indeed the first binomial term has a factor
p^(r+1), the intermediate terms have at least that factor, and the last
has p^(rp), with rp>=r+1. Iterating gives congruence modulo p^(r+j)
after the p^j-th powers are taken.

Consequently (1) is independent of the integer representative, is
multiplicative, reduces to x modulo p, and satisfies

    t_N(x)^p=t_N(x),
    rho_N(t_(N+1)(x))=t_N(x),
    t_N(0)=0,                 t_N(1)=1.                    (2)

For the fixed-point and reduction statements, apply the congruence to
x_tilde^p=x_tilde mod p. For multiplicativity, representatives of xy and
the product of representatives agree modulo p, and their p^(N-1)-th
powers therefore agree modulo p^N. This also covers p=2 without dividing
by p-1 or assuming an odd prime.

## 2. Uniqueness of the protected multiplicative section

**Lemma 1.** The only multiplicative section u:k->R_N satisfying
u(0)=0 and u(1)=1 is t_N.

For x!=0, u(x) is a unit and u(x)^(p-1)=1. The same is true of t_N(x).
Their quotient w is congruent to 1 modulo p and has w^(p-1)=1. If
w=1 modulo p^r with 1<=r<N, write w=1+p^r z. The binomial expansion
modulo p^(r+1) gives w^(p-1)=1+(p-1)p^r z. Because p-1 is a unit
modulo p, z=0 modulo p. Induction gives w=1 modulo p^N. The zero value
is already protected. When p=2, the exponent p-1 is 1 and the unit
assertion is immediate. This proves uniqueness. Existence was proved
in (2).

This is a statement about the fixed finite ring and the fixed residue
section. It does not say that every change of arithmetic realization is
a section correction of this form.

## 3. The carry, its reductions and its protected correction group

Define C_N:k times k -> K_N by

    i_N(C_N(x,y))=t_N(x)+t_N(y)-t_N(x+y).                   (3)

The right side lies in ker(r_N), so C_N is uniquely defined. In the
argument x+y is the addition in k. It is normalized and symmetric, and
the additive cancellation identity gives

    C_N(x,y)+C_N(x+y,z)=C_N(y,z)+C_N(x,y+z).               (4)

To prove (4), apply injective i_N and substitute (3). Both sides become
t_N(x)+t_N(y)+t_N(z)-t_N(x+y+z). This proves the cocycle equation in its
correct coefficient group K_N, not merely after multiplication by p.

Reduction of (3), followed by the commuting i_N square and injectivity,
gives precision naturality:

    C_(N+1)(x,y) mod p^(N-1) = C_N(x,y).                  (5)

Let B_N be the additive group of maps b:k->K_N with b(0)=b(1)=0.
These conditions protect the zero and the unit. Its additive defect is

    (d b)(x,y)=b(x)+b(y)-b(x+y).

Every lift u of the identity residue map with u(0)=0,u(1)=1 is uniquely
u=t_N+i_N b, b in B_N. Its carry is exactly

    C_u=C_N+d b.                                          (6)

Thus the protected carry class [C_N] in

    Map(k times k,K_N) / d(B_N)                            (7)

is independent of the lift, using these exact protected data. Equation
(4) also permits restriction to cocycles, but (7) is enough for the
protected realization criterion below. No identification of (7) with
every other obstruction quotient is assumed.

The cycle functional L_N(C)=sum_(j=0)^(p-1) C(1,j) satisfies

    L_N(C_N)=1 in K_N,            L_N(d b)=p b(1)=0.       (8)

The first identity follows by applying i_N: all t_N(j) terms telescope,
leaving p t_N(1)=p. The second is the same telescope on b. Therefore
[C_N]!=0 for N>=2. At N=1, K_1=0 and this class is zero, as it must be.

Even if only b(0)=0 is protected and b(1) is free, L_N(d b)=p b(1)
is zero modulo p. Hence the class remains nonzero for N>=2 in that
larger correction problem. No additive section of r_N can exist. This
also follows because a lift of 1 modulo p has additive order p^N, while
the generator of k has additive order p.

## 4. An actual finite Komorebi view diagram

We now encode the preceding obstruction in the view-system construction
of Komorebi Space, not just in terminology.

Form the free category on the following finite directed graph. It has
objects l_x and v_x for each x in k, and w_(x,y) for each ordered pair.
The arrows and contravariant fiber maps are:

| Arrow in the view category | Fibers and restriction |
| --- | --- |
| l_x -> v_x | R_N -> k, the residue map r_N |
| v_x -> w_(x,y), role 1 | R_N squared -> R_N, (a,b) maps to a |
| v_y -> w_(x,y), role 2 | R_N squared -> R_N, (a,b) maps to b |
| v_(x+y) -> w_(x,y), role 3 | R_N squared -> R_N, (a,b) maps to a+b |

The fibers at l_x, v_x and w_(x,y) are respectively k, R_N and
R_N squared. Maps on composite arrows are the composites of the listed
restrictions. If some variable labels coincide, the roles are distinct
parallel arrows. They must not be collapsed into one arrow. This is a
finite category: nonidentity paths have length at most two. All listed
maps are additive, so it is also an additive view system.

Prescribe a partial section on the full subcategory with objects all
l_x together with v_0 and v_1. Give l_x the value x, v_0 value 0, and
v_1 value 1. The only nonidentity arrows inside this partial domain are
the two corresponding residue arrows, and these values are compatible.

**Theorem 2.** Extensions of this partial section are exactly additive
sections u:k->R_N with u(0)=0,u(1)=1. The relation-coordinate values are
forced to be (u(x),u(y)). Consequently the extension fiber is empty
for N>=2, and is a singleton at N=1.

Indeed the first two role equations force the pair coordinates; the
third then says u(x+y)=u(x)+u(y). The residue equations give r_N u=id,
and the protected vertices give the two specified values. Conversely
such a u gives every coordinate and satisfies every generating arrow,
hence every composite arrow. The asserted emptiness follows from (8),
and the N=1 section is the identity of k.

Here is the precise quotient-valued obstruction. For an arrow f:v->w,
its residual lies in F_N(v), the target of the contravariant restriction
f^*. Put E_N=product_v F_N(v) and
Rdef_N=product_(f:v->w) F_N(v), over all arrows of the finite category.
Define the compatibility differential

    (D_N z)_f=f^*(z_target)-z_source.

Let P_N be restriction to the protected objects above. The Komorebi
protected obstruction quotient is

    Q_N=Rdef_N / D_N(ker P_N).                              (9)

Take the raw lift e_N whose variable coordinates are t_N(x), whose pair
coordinates are (t_N(x),t_N(y)), and whose residue coordinates are x.
Its only nonzero generating-arrow defects occur at role 3 and equal
i_N C_N. Every composite residue-arrow defect is zero.

For an arbitrary cochain C:k squared->K_N, let j_N(C) in Rdef_N have
role-3 defects i_N C and zero at all other arrows, including composites.
Then

    j_N(C) in D_N(ker P_N)   iff   C in d(B_N).            (10)

For the forward implication, choose h in ker P_N with D_N h=j_N(C).
Its residue-arrow component is zero, so r_N(h_vx)-h_lx=0. Protection
gives h_lx=0, hence h_vx=i_N b(x) for unique b; protection at v_0,v_1
forces b(0)=b(1)=0.
Zero role-1 and role-2 defects force the relation correction to be
(i_N b(x),i_N b(y)). Its role-3 defect is i_N(d b)(x,y), and injectivity
proves C=d b. For the reverse implication choose exactly those correction
coordinates, with zero residue coordinates. All generating and composite
defects have the specified values. This proves (10).

Thus j_N induces an injection of (7) into (9), and the actual Komorebi
obstruction class of e_N is the image of [C_N]. Its nonvanishing in (8)
is therefore a genuine protected obstruction in this declared diagram.
No assertion that the entire quotient (9) equals (7) is needed or made.

## 5. Retaining the carry gives an exact arithmetic realization

The empty additive-section problem does not mean that local arithmetic
cannot be realized. It means that the specified zero-carry reconstruction
cannot preserve its protected data. We now enlarge the declared views by
retaining the required carry as data.

Use carry objects c_(x,y) with fiber K_N and relation objects w_(x,y)
with fiber R_N squared times K_N. Their restrictions are

    role 1: (a,b,c) -> a,
    role 2: (a,b,c) -> b,
    role 3: (a,b,c) -> a+b-i_N(c),
    carry role: (a,b,c) -> c.

The first three arrows have source respectively v_x,v_y,v_(x+y), and
the carry-role arrow has source c_(x,y). Keep the same residue arrows
and protected partial section. The graph is again finite and acyclic,
so these maps define a view functor. Coherent extensions are now exactly
the residue sections u with normalized endpoints, equipped with their
unique carries C_u satisfying (3) with t_N replaced by u.

For every ordered pair add a multiplication relation object m_(x,y)
with fiber R_N squared and restrictions a, b and ab to v_x,v_y,v_(xy).
Multiplication is not additive on the pair fiber. The enlarged object is
a Set-valued view system, not an additive view system to which the
quotient construction (9) can simply be reapplied.

**Theorem 3.** The enlarged carry-and-multiplication diagram has one
protected coherent realization: u=t_N and C=C_N, with the pair and
multiplication coordinates forced by u.

Coherence at multiplication objects is exactly multiplicativity of u.
Lemma 1 forces u=t_N. Coherence at the carry objects then forces C=C_N.
Conversely, (2)-(3) construct all coordinates and verify every generating
arrow, hence a realization. This proves existence as well as uniqueness.

Arbitrary additive section corrections need not preserve multiplication.
Explicitly u=t_N+i_N b is multiplicative exactly when, for every x,y,

    b(xy)=t_(N-1)(x)b(y)+t_(N-1)(y)b(x)+p b(x)b(y)
                                                               in K_N. (11)

To derive (11), expand u(x)u(y)=u(xy) in R_N, use multiplicativity of
t_N, and divide the resulting kernel equality by injective i_N.
The coefficient reductions are t_(N-1) by (2), including the zero-ring
interpretation when N=1. For normalized sections this condition forces
b=0 by Lemma 1. In general (11) is a nonlinear constraint, not a linear
subgroup assertion. The protected additive correction quotient and the
mixed multiplication diagram have therefore been kept distinct.

## 6. Naturality of the complete finite realization

Use one fixed view graph at every N. Reduce R_(N+1) coordinates to R_N,
K_(N+1) coordinates to K_N, and leave the k coordinates unchanged. These
maps commute with all residue, addition, carry, multiplication and pair
restrictions. In the carry restriction this is precisely the commuting
i_N square; for multiplication it is the ring-homomorphism property
of reduction. They preserve the protected endpoints and partial seed.

Thus they are actual natural transformations of the declared view
functors, and induce maps on their protected coherent realizations.
Their compositions are the usual precision reductions, so the positive
realizations of Theorem 3 form an inverse system. Its unique compatible
family is exactly the t_N,C_N system by (2) and (5).

The coefficient reductions also commute with d on the cochain groups,
inducing maps between (7). The classes [C_N] form a coherent obstruction
family. The N=1 class is zero, but every N>=2 class remains nonzero;
vanishing at the first residue view does not imply liftability to the
next precision.

The obstruction quotients (9) themselves also reduce naturally. For the
additive diagrams, reduction on all raw fiber and arrow products commutes
with D_N and with restriction P_N. Hence D_(N+1)(ker P_(N+1)) maps into
D_N(ker P_N), inducing Q_(N+1)->Q_N. The commuting i_N square gives
compatibility with j_N, so the injected classes [D_N e_N] are coherent
in this actual Komorebi quotient tower as well. This uses only maps
already declared in the finite diagrams.

## 7. All local elements, not only the section table

There are two different objects above: the uniquely reconstructed table
t_N,C_N and the many elements of R_N. To reconstruct the latter, let
D_N=k^N with truncation of the final digit. Define

    Psi_N(d_0,...,d_(N-1))
       =sum_(j=0)^(N-1) p^j t_N(d_j) in R_N.              (12)

**Theorem 4.** Psi_N is a bijection. It commutes with precision reduction
and digit truncation. Transporting the ring operations through these
bijections makes the digit tower a tower of rings and gives an explicit
ring isomorphism

    lim_N D_N  ~=  lim_N R_N = Z_p.                        (13)

For bijectivity, the first digit of x is r_N(x). Subtract its t_N lift
and divide by p through i_N to obtain a unique element of R_(N-1).
Induction determines all remaining digits. This also constructs a
preimage of every x. The N=1 base case is the identity of k. Reduction
of (12) deletes the last term and reduces all preceding t_N values
according to (2), proving the naturality square.

Define addition and multiplication on D_N as the pullbacks of those of
R_N through Psi_N. These are explicit finite operations because both
Psi_N and its inverse were constructed. The commuting square makes
truncation a ring homomorphism. Passing to coherent families gives
mutually inverse maps component by component, proving (13). This does
not invoke an unknown global point or a terminal fiber containing the
desired ABC solution.

The carry table supplies an explicit addition recursion. If
X=t_N(x_0)+p X' and Y=t_N(y_0)+p Y', then

    X+Y=t_N(x_0+y_0)+p[X'+Y'+C_N(x_0,y_0)].               (14)

The bracket belongs to R_(N-1), where its digits are recovered by the
preceding induction. Multiplication similarly has the recursion

    XY=t_N(x_0 y_0)
       +p[t_(N-1)(x_0)Y'+t_(N-1)(y_0)X'+pX'Y'].         (15)

The expansion and (2) prove (15). Formulas (14)-(15) include p=2 and
N=1, with the indicated zero tail when N=1. The result is the local
Teichmuller digit ring over F_p; it does not claim a construction of the
general Witt functor for arbitrary perfect residue rings.

Taking limits in (3) and (8) gives a multiplicative section t:k->Z_p
with an exact Z_p-valued carry C and sum_j C(1,j)=1. No additive
section k->Z_p exists. For example multiplication by p on lim R_N
is injective: pz=0 implies the level N+1 component is divisible by p^N,
so the level N component is zero for every N. An additive lift of 1
would be nonzero but killed by p, a contradiction.

## 8. What was achieved, and the first global obligation

This is an explicit independent local reconstruction within Komorebi Space:
the categories, fibers, protected seed, obstruction injection, carry
coordinates and precision maps are specified before any solvability claim.
The reconstruction retains the nonzero carry instead of falsely setting
it to zero. Multiplication-preserving changes obey their own constraint.

The next arithmetic task is not to prove local coherence again. It is
to couple these local reconstructions to an archimedean realization and
to the intended diagonal integer/rational source, with quantitative cost.
For primitive positive a+b=c the still unproved global target is

    log c <= (1+epsilon) log rad(abc)+C_epsilon

for every epsilon>0 with C_epsilon uniform in the triple. Neither (13)
nor the existence of a coherent product over primes supplies this bound.
Finite residue or carry precision is not itself a real height estimate.
In particular the compactness obstruction in the predecessor note remains
applicable to continuous real-valued height on a purely profinite carrier.

No fresh Lean compilation or finite mathematical experiment was run for
this note. Its universal statements have the elementary proofs above.
Earlier Block03 compilation receipts are source history, not verification
of the new incidence diagrams or the general theorems written here.

## Sources and attribution

The current Library file Realization_Calculus_Volume_I_Komorebi_Space.pdf
was read at Library id libfile_bd054a01919c8191b1bb6d1a9a4965d6, pages
8-16, covering definitions of view systems, coherent sections, protected
extension and its additive obstruction. The source identity and read
metadata are recorded in INPUTS.json; no fresh verification of the
volume's earlier Lean development is asserted.

The predecessor RESEARCH_NOTE.md in the Block03 arithmetic archive was
read in full. Its Teichmuller carry formula, nonsplitting boundary and
stated restart problem are the starting point. The new contribution in
this checkpoint is the complete typed incidence realization, obstruction
injection and coherent digit reconstruction in that declared system.
No historical priority over classical local arithmetic is claimed.
