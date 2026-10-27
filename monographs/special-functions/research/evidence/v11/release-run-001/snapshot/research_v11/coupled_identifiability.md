# When the pair reduces, and when its parameters are intrinsic

Checkpoint: SF-DISCOVERY-110. Base: SF-DISCOVERY-100, source archive SHA-256
`ca4debff6f9653b784b849ccc7519fcf2493a7a24e814658a950a936e8513f21`.

Throughout, \(q,r,a,b\in(0,1)\). Let the normalized coupled solution be

\[
U'=1+U(qz)V(rz),\qquad V'=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

Write \(U(z)=z+u_1z^3+u_2z^5+u_3z^7+\cdots\) and
\(V(z)=z+v_1z^3+v_2z^5+v_3z^7+\cdots\). Put \(p=qr\), \(k=ab\).
Coefficient matching gives

\[
u_1=\frac p3,\qquad v_1=\frac k3,
\]
\[
u_2=\frac p{15}(p q^2+k r^2),\qquad
v_2=\frac k{15}(p a^2+k b^2),
\]
\[
u_3=\frac p7(q^4u_2+p^2u_1v_1+r^4v_2),\qquad
v_3=\frac k7(a^4u_2+k^2u_1v_1+b^4v_2).
\]

Define the fifth-order separation quantity

\[
\boxed{D=k^2u_2-p^2v_2
=\frac{pk ar}{15}(q^2-b^2)(qb-ar).}
\]

This factorization will distinguish equality of normalized functions up to
amplitude and argument rescaling from a change of coordinates in their defining
functional differential operator. These are different equivalence relations.

## 1. Exact classification of component rescaling

**Theorem.** The following statements are equivalent:

1. There are nonzero complex constants \(A,B\) such that \(V(z)=A U(Bz)\)
   for every complex \(z\).
2. \(D=0\).
3. \(q=b\) or \(qb=ar\).

If these conditions hold, put \(s=\sqrt{k/p}>0\), and let \(T_{x,y}\) denote
the normalized scalar solution \(T'=1+T(xz)T(yz)\), \(T(0)=0\). Then

\[
\boxed{
U(z)=\sqrt{s}\,T_{q,sr}(z/\sqrt{s}),\qquad
V(z)=s^{-1/2}T_{q,sr}(\sqrt{s}\,z).
}
\]

The effective scales belong to \((0,1)\): if \(q=b\), then \(sr=\sqrt{ar}\),
and if \(qb=ar\), then \(s=b/r\) and \(sr=b\).

**Proof.** Normalization gives \(AB=1\). Comparing cubic coefficients gives
\(B^2=k/p\), and comparing fifth coefficients gives \(v_2=(k/p)^2u_2\).
Thus component rescaling implies \(D=0\), even when complex rescalings are
allowed. The displayed factorization, strict positivity, and \(q,b>0\) show
that \(D=0\) is equivalent to \(q=b\) or \(qb=ar\).

For the converse define the displayed pair using \(T=T_{q,sr}\). Direct
differentiation gives

\[
U'(z)=1+T(qz/\sqrt{s})T(r\sqrt{s}\,z)
=1+U(qz)V(rz).
\]

The second equation reduces to equality of the unordered pairs of arguments

\[
\{q\sqrt{s},\;s^{3/2}r\}
=\{a/\sqrt{s},\;b\sqrt{s}\}.
\]

When \(qb=ar\), one has \(a=sq\) and \(b=sr\), giving equality in the
displayed order. When \(q=b\), one has \(a=s^2r\), giving equality after
interchanging the factors. The pair also has the required initial values and
derivatives. Uniqueness of the formal coefficient recursion identifies it
with the coupled solution. Finally, \(V(z)=s^{-1}U(sz)\), proving rescaling.

The positive parameter domain therefore contains two explicit reduction
surfaces. Outside them the two component functions cannot be obtained from
one another by amplitude and argument rescaling. This statement does not
exclude every representation using previously known functions.

## 2. Seven derivatives recover all four ordered scales away from reduction

**Theorem.** If \(D\ne0\), the six coefficients
\((u_1,v_1,u_2,v_2,u_3,v_3)\) uniquely determine the ordered tuple
\((q,r,a,b)\) within \((0,1)^4\). Consequently, equality of the two labeled
normalized germs implies equality of these parameters in this regime.

**Proof.** First recover \(p=3u_1\), \(k=3v_1\). If \(x=q^2\), then
\(r^2=p^2/x\), and the equation for \(u_2\) gives

\[
p x^2-\frac{15u_2}{p}x+kp^2=0.
\]

This leaves at most two positive candidates. If there are two distinct
positive roots \(x,x'\), their product is \(xx'=kp\). The corresponding
seventh-coefficient values differ by

\[
u_3(x)-u_3(x')
=\frac p7(x^2-x'^2)
\left(u_2-\frac{p^2}{k^2}v_2\right)
=\frac{pD}{7k^2}(x^2-x'^2).
\]

The difference is nonzero because \(D\ne0\) and the distinct positive roots
have distinct squares. Thus \(u_3\) selects the unique root \(q^2\), giving
\(q=\sqrt{x}>0\) and \(r=p/q\). A repeated quadratic root already gives a
unique value and requires no selection.

Likewise \(y=a^2\) obeys

\[
p y^2-\frac{15v_2}{k}y+k^3=0,
\]

with root product \(yy'=k^3/p\). The two candidate seventh coefficients
have difference

\[
v_3(y)-v_3(y')
=\frac k7(y^2-y'^2)
\left(u_2-\frac{p^2}{k^2}v_2\right)
=\frac{D}{7k}(y^2-y'^2),
\]

which is again nonzero for distinct positive candidates. Recover
\(a=\sqrt{y}\) and \(b=k/a\). All selections must also respect the contraction
domain. Since the supplied coefficients arise from an admissible pair, at
least one admissible selection exists. The preceding differences give
uniqueness.

This is an exact-data inverse theorem. The displayed differences become small
as \(D\to0\), so the argument does not supply a uniform stable inverse near
the reduction surfaces. It also does not identify unlabeled components without
the additional component-permutation equivalence.

## 3. A worked pair with exact order one

Take

\[
(q,r,a,b)=\left(\frac15,\frac25,\frac35,\frac7{10}\right),\qquad
p=\frac2{25},\quad k=\frac{21}{50}.
\]

At \(\rho=1\), the characteristic matrix has positive eigenvector
\((1/2,1)^T\) with eigenvalue one. Its other eigenvalue is \(-1/10\).
The growth theorem therefore gives exact order one for both components.
Here \(q\ne b\) and \(qb\ne ar\), so \(D\ne0\). The pair is outside both
reduction surfaces and its four labeled parameters are recoverable from the
coefficients through degree seven.

## 4. Verification scope

The identities above are algebraic and the proofs use exact positive parameters.
The companion check script compares the first coefficients against the full
independent recursion, verifies the factorization over a rational grid, checks
the candidate-selection formulas, and tests both reduction surfaces by comparing
many exact Taylor coefficients. Finite checks test the implementation and the
worked examples. The equivalence and recovery theorems follow from the proofs.

Historical priority of these specific statements remains a separate literature
question.
