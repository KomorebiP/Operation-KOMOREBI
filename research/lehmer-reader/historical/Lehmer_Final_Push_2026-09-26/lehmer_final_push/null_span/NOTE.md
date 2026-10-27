# The terminal interpolation boundary

Final-push branch, 26 September 2026. Base checkpoint:
LEHMER-CONTENT-TRANSPORT-02 (archive SHA256
ce2c5dc5a0e82b788d2a5970537511d765f79891d0e1ca9682b25c9a0c4d502c).

**Outcome:** no proof of Lehmer was obtained. This branch proves an explicit
homogeneous interpolation theorem, rules out further identifications hidden
in the even symmetric coordinates, and isolates two exact failures of the
proposed interpolation-to-nullness route. It does not prove that the
all-degree universal-null span is the full content-preserving space.

The companion POLYNOMIAL_CONTENT_THEOREM.md proves a further extension:
every finite symmetric polynomial which is null on all shells is null
componentwise in homogeneous degree. Therefore content conservation applies
to all such polynomials, with no homogeneity assumption. This closes the
possible nonhomogeneous-polynomial escape from the content invariant.

## 1. Even symmetric coordinates identify exactly the J-orbits

Write s_j(v)=sum_i v_i^j. On a fixed nonempty shell V_n, put C=10n. The map

    I(v)=(s4/C^2, s3^2/C^3, s3*s5/C^4, s5^2/C^5)

identifies exactly v and J(v). This is a uniform assertion with the following
proof, not an inference from the finite checks below.

If I(v)=I(w), then s4 agrees and the two real vectors (s3(v),s5(v)) and
(s3(w),s5(w)) have the same rank-one outer product. They therefore agree up to
one common sign, including the zero case. The first five power sums of v
and either w or -w agree: s1=0, s2=C, and the other three as just shown.
Newton identities imply that the coordinate multisets agree. Each multiset
has exactly one coordinate in each residue class modulo 5. Equal multisets
therefore give v=w. Negated multisets give w_i=-v_{-i mod 5}=J(v)_i.
Conversely J preserves all four displayed invariants.

Thus any additional annihilator of universal-null evaluations is an
arithmetic/modular relation. It cannot be explained by a missed coincidence
of the even symmetric polynomial coordinates on this shell.

## 2. Explicit homogeneous interpolation

Let a shell have N distinct J-orbits represented by v_1,...,v_N. For arbitrary
rational values a_1,...,a_N, there is an even, symmetric, homogeneous
polynomial Q of degree 10(N-1) such that Q(v_i)=a_i. When N=1 this simply
means a constant polynomial.

Define, for a nonnegative integer t,

    E_t=s4*s2^3 + t*s3^2*s2^2 + t^2*s3*s5*s2 + t^3*s5^2.

This is homogeneous of degree 10. For two distinct orbits the polynomial
E_t(v_i)-E_t(v_j), as a polynomial in t, is nonzero by Section 1, so has at
most three roots. Hence some integer

    0 <= t <= 3*N*(N-1)/2

separates all N values e_i=E_t(v_i). For this t set

    L_i(v) = product_{j != i}
       [E_t(v) - e_j*(s2(v)/C)^5] / (e_i-e_j).

Every L_i is a rational homogeneous symmetric polynomial of degree
10(N-1), and L_i(v_j)=delta_ij. Taking Q=sum_i a_i L_i proves the assertion.
All degrees here are invariant degrees; D(v)Q(v) has degree ten higher.

There is no harmonicity or universal-nullness assertion in this theorem.

## 3. Why the interpolation theorem does not close the proof

Let m_i be the nonzero mass of the i-th J-orbit. It equals W(v_i) or 2W(v_i),
according as the orbit has size one or two. The interpolation theorem makes
the unrestricted map Q -> (m_i Q(v_i)) surjective onto Q^N. In particular,
every zero-total mass transfer can be interpolated by one homogeneous
polynomial which is null on this one shell.

That condition is much weaker than being null on every shell. The bounded
check constructs the interpolated correction which kills all but the first
orbit at n=7. It has degree 20 and is exactly null at n=7, leaving -16744 in
the first orbit. But its weighted sum at shell 1 is

    -449 / 42371287350,

which is nonzero. The analogous degree-150 interpolant at 31 fails already
at shell 1 as well. Thus the natural interpolation construction does not
produce universal-null corrections, even in these small examples where
different, genuinely universal-null corrections are already known to exist.

Nor can one simply harmonicize the interpolation polynomial while keeping
its values. The Vandermonde D is harmonic of degree 10 on the rank-four
hyperplane. Therefore

    Laplacian(s2*D) = (2*4+4*10)*D = 48*D.

The top-degree harmonic component of s2*D is zero. A nonzero constant value
on a fixed sphere has disappeared under this operation. More generally,
the harmonic projection of s2^k*D into degree 10+2k is zero for every k>0.
Consequently interpolation followed by top-degree harmonic projection has
no value-preservation principle. Restoring this lost information is a real
missing step, not a normalization issue.

I also examined the high-degree dimension approach: harmonic polynomial
dimension grows quadratically, while the number of modular coefficient
constraints grows linearly. Those dimensions do not prove that the kernel
evaluates onto any prescribed finite zero-total space. The needed statement
is independence between the shell evaluation rows and the modular rows.
No uniform independence theorem was established here. The finite ranks in
the parent checkpoint cannot supply it.

## 4. Even maximal null-span completeness would retain the prime problem

Let the J-orbits be partitioned by exact content g. Write T_g for the mass
of each content class, and H_content for the vectors whose sum in each
class is zero. The parent content-conservation theorem proves that every
permitted universal homogeneous null transfer belongs to H_content.

Suppose, optimistically, that the all-degree null transfers span exactly
H_content. Then a correction with every orbit mass strictly positive exists
if and only if T_g>0 for every nonempty content class. The negative version
holds with T_g<0. Necessity follows by summing within a class. For sufficiency,
distribute T_g equally over its finitely many orbits; the difference from the
original mass vector lies in H_content and is therefore available by the
assumed completeness.

For the weaker certificate with all masses nonnegative and at least one
strictly positive, the necessary and sufficient condition is all T_g>=0 and
sum_g T_g>0. Again there is a corresponding nonpositive statement.

At a prime shell there is one content class, with mass tau(p). Thus the
existence of a strict common-sign certificate, under even this strongest
completeness hypothesis, is equivalent to tau(p)!=0. A concrete, independently
verified sign certificate could still prove nonvanishing; completeness
alone does not establish that such a certificate has a nonzero sign.

Equivalently, under fullness every conserved linear functional at a prime
is proportional to the total mass. A purported new linear invariant
distinguishing zero would then just restate the original total. This is a
boundary on this method, not a no-go theorem for Lehmer or for nonlinear
arithmetic arguments.

## 5. Exact audit and scope

The official bounded run is in computations/run001. It checked invariant
separation on all 128 shells through 128 (5,847 packets and 2,964 J-orbits),
with an independent direct q-product check of their total masses. It verified
all Kronecker interpolation evaluations at n=7 and n=31, their exact
zero-sum corrections at the target shell, and their explicit nonzero failure
at shell 1. The finite assertion passed; its version-2 manifest passed the
input/output hash validator. The written proofs in Sections 1, 2, and 4 are
independent of this bounded computation. No external theorem beyond the
parent packet setup and elementary polynomial facts is needed for them.

The parent paper supplies the harmonic Vandermonde fact used in Section 3;
the displayed Laplacian identity also follows directly from Euler's identity
for a homogeneous harmonic polynomial in four variables.

No Lean verification or priority claim is made. The precise unresolved
arithmetic requirement remains an independent mechanism forcing the
primitive prime-shell mass tau(p) away from zero.
