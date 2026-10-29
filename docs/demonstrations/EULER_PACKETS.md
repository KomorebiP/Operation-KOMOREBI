# Euler numbers through packets, polynomials, and residuals

**An extended hand-worked Komorebi example · Komorebi P. · 29 October 2026**

[Machine-native mathematics essay](../essays/MACHINE_NATIVE_MATHEMATICS.md) · [Sequence experiments](SEQUENCE_SHAPES.md) · [Run the exact checks](#run-the-exact-checks)

We will reconstruct the Euler secant numbers through a different sequence, turn the calculation into polynomial identities, and then use the same Euler data in a refinement calculation. At each change of coordinates we will write the transfer explicitly. When a shortcut fails, we will calculate the residual that explains the failure.

The two main numerical destinations are

\[
s_6=2702765
\]

for the coefficient of \(t^{12}/12!\) in \(\sec t\), and

\[
E_8-E_0=1384
\]

for a refinement of the signed Euler sequence. The derivations connect them to reciprocal series, a two-packet matrix, finite-difference coordinates, and an exact correction law.

The Euler numbers and the quartic sequence used below are classical. This example develops them through Komorebi's packet, transfer, and residual language. Its purpose is to make a substantial calculation inspectable from beginning to end. The [source notes](../../verification/euler-packets/SOURCES.md) identify the classical references and the project sources.

You can follow the algebra without running code. The accompanying [Python program](../../examples/euler_packets.py) uses exact integers and fractions and needs only Python's standard library.

## Conventions and three coordinate systems

Euler number conventions vary. We will use the positive secant numbers \(s_n\), indexed by half the ordinary degree:

\[
\sec t=\sum_{n\geq0}s_n\frac{t^{2n}}{(2n)!}.
\]

The first values are

\[
s_0,s_1,s_2,s_3,s_4,s_5,s_6
=1,1,5,61,1385,50521,2702765.
\]

These are [OEIS A000364](https://oeis.org/A000364), with offset zero. The signed Euler numbers \(E_j\) use

\[
\operatorname{sech}t=\frac1{\cosh t}
=\sum_{j\geq0}E_j\frac{t^j}{j!}.
\]

Thus

\[
E_{2n}=(-1)^ns_n,\qquad E_{2n+1}=0.
\]

In the sequence-refinement part we will write \(a(n)=E_{2n}\). In particular, \(a(1)=-1\), even though the full-index number \(E_1\) is zero. The [DLMF definitions](https://dlmf.nist.gov/24.2#ii) and [secant series](https://dlmf.nist.gov/4.19.E5) fix this sign convention.

| Compressed index \(n\) | Ordinary degree \(2n\) | \(s_n\) | \(a(n)=E_{2n}\) |
|---:|---:|---:|---:|
| 0 | 0 | 1 | 1 |
| 1 | 2 | 1 | -1 |
| 2 | 4 | 5 | 5 |
| 3 | 6 | 61 | -61 |
| 4 | 8 | 1385 | 1385 |
| 5 | 10 | 50521 | -50521 |
| 6 | 12 | 2702765 | 2702765 |

We will use three coordinate systems. Their operations have different meanings.

| Coordinates | Object being represented | Operation to keep track of |
|---|---|---|
| Exponential coefficients | A formal series in \(t\) | Products carry binomial weights |
| Residue packets | The same even series, grouped modulo four | Multiplication becomes a matrix with a carry factor |
| Finite differences | The indexed sequence \(a(0),a(1),\ldots\) | Sampling becomes a polynomial in the forward difference |

The series calculations take place over the rational numbers. A formal series is a sequence of coefficients with a multiplication rule. Every coefficient of a product is a finite sum, so the calculations do not require an analytic convergence argument. A series with a nonzero constant coefficient has a unique formal reciprocal.

## Build the secant numbers from the reciprocal equation

Start with

\[
\cos t=\sum_{k\geq0}(-1)^k\frac{t^{2k}}{(2k)!}.
\]

Write an unknown reciprocal as

\[
S(t)=\sum_{n\geq0}s_n\frac{t^{2n}}{(2n)!}.
\]

The equation \(\cos t\,S(t)=1\) gives \(s_0=1\). For \(n\geq1\), its coefficient at ordinary degree \(2n\) is

\[
\sum_{k=0}^n
\frac{(-1)^ks_{n-k}}{(2k)!(2n-2k)!}=0.
\]

Multiplying by \((2n)!\) gives

\[
s_n=\sum_{k=1}^n(-1)^{k+1}
\binom{2n}{2k}s_{n-k}.
\]

The binomial coefficient comes from converting an ordinary product back to exponential normalization. It is part of the transfer law.

Now perform the first six steps. Each row uses only previously calculated values.

\[
\begin{aligned}
s_1&=1,\\
s_2&=6\cdot1-1=5,\\
s_3&=15\cdot5-15\cdot1+1=61,\\
s_4&=28\cdot61-70\cdot5+28\cdot1-1\\
   &=1708-350+28-1=1385,\\
s_5&=45\cdot1385-210\cdot61+210\cdot5-45\cdot1+1\\
   &=62325-12810+1050-45+1=50521,\\
s_6&=66\cdot50521-495\cdot1385+924\cdot61\\
   &\quad-495\cdot5+66\cdot1-1\\
   &=3334386-685575+56364-2475+66-1\\
   &=2702765.
\end{aligned}
\]

The series begins

\[
S(t)=1+\frac{t^2}{2!}+5\frac{t^4}{4!}
+61\frac{t^6}{6!}+1385\frac{t^8}{8!}+\cdots.
\]

For example, the ordinary coefficient of \(t^4\) is \(5/24\). The compressed index is two, but the denominator is \(4!\).

## Split the series into two packets

Every even series can be written uniquely as

\[
F(t)=A(u)+t^2B(u),\qquad u=t^4.
\]

The series \(A\) collects ordinary degrees \(0,4,8,\ldots\). The series \(t^2B\) collects degrees \(2,6,10,\ldots\). These two packets retain every coefficient of the even series.

For the secant series, the packets we want are

\[
\begin{aligned}
A(u)&=1+\frac5{24}u+\frac{1385}{40320}u^2+\cdots,\\
B(u)&=\frac12+\frac{61}{720}u+\frac{50521}{3628800}u^2+\cdots.
\end{aligned}
\]

We will now derive those packets without using their already known values.

Split the denominator in the same way:

\[
\cos t=C(u)+t^2D(u),
\]

where

\[
\begin{aligned}
C(u)&=\sum_{j\geq0}\frac{u^j}{(4j)!}
=1+\frac{u}{24}+\frac{u^2}{40320}+\cdots,\\
D(u)&=-\sum_{j\geq0}\frac{u^j}{(4j+2)!}
=-\frac12-\frac{u}{720}-\frac{u^2}{3628800}-\cdots.
\end{aligned}
\]

Multiply the two packet expressions:

\[
(C+t^2D)(A+t^2B)
=CA+t^2(CB+DA)+t^4DB.
\]

Because \(t^4=u\), the product has packets

\[
(CA+uDB,\;DA+CB).
\]

The product of two degree-two packets returns to the degree-zero packet, with one factor of \(u\). This is the carry that a residue calculation must retain.

Multiplication by \(\cos t\) is therefore represented over \(\mathbb Q[[u]]\) by

\[
L(u)=
\begin{pmatrix}
C&uD\\
D&C
\end{pmatrix}.
\]

The reciprocal problem becomes

\[
L(u)\begin{pmatrix}A\\B\end{pmatrix}
=\begin{pmatrix}1\\0\end{pmatrix}.
\]

This is an exact change of representation. We have replaced multiplication of even series with a two-packet transfer matrix.

## Try a coarser representation and calculate its failure

Suppose we retain only the first packet and replace the full equation by

\[
CA_{\mathrm{coarse}}=1.
\]

Then

\[
A_{\mathrm{coarse}}=C^{-1}
=1-\frac{u}{24}+\frac{69u^2}{40320}+\cdots.
\]

The degree-four numerator would be \(-1\). The correct secant numerator is \(5\).

We can locate the error before calculating any more coefficients. Insert the proposed pair \((C^{-1},0)\) into the full equation. Its residual, with the convention actual output minus required output, is

\[
L\begin{pmatrix}C^{-1}\\0\end{pmatrix}
-\begin{pmatrix}1\\0\end{pmatrix}
=\begin{pmatrix}0\\DC^{-1}\end{pmatrix}.
\]

The second residual has constant coefficient \(-1/2\). The discarded channel already contains a nonzero obligation.

There is also a structural obstruction. Let

\[
f(A,B)=A
\]

be the coarsening map, and let the proposed coarse operator be multiplication by \(C\). Its transport residual is

\[
\partial(f)=Cf-fL
=\begin{pmatrix}0&-uD\end{pmatrix}.
\]

For the vector \(v=(0,1)\),

\[
f(v)=0,\qquad f(Lv)=uD\ne0.
\]

The coarse description identifies \(v\) with zero, but the next operation distinguishes them. There is no operator on the first packet alone that reproduces \(fL\) for every input pair. Any such operator would have to send the same coarse input to both zero and \(uD\).

At constant order in \(u\), the carry is invisible. It appears at the next order. This explains how a coarse calculation can pass an initial check and still fail when the requested resolution increases.

## Repair the transfer by inverting the packet matrix

The determinant is

\[
G(u)=C(u)^2-uD(u)^2.
\]

Its constant coefficient is one, so it is a formal unit. The inverse matrix is

\[
L^{-1}=\frac1G
\begin{pmatrix}
C&-uD\\
-D&C
\end{pmatrix}.
\]

Consequently,

\[
A=\frac C G,\qquad B=-\frac D G.
\]

We can verify both equations without an appeal to the matrix formula:

\[
CA+uDB=\frac{C^2-uD^2}{G}=1,
\]

and

\[
DA+CB=\frac{DC-CD}{G}=0.
\]

Calculate the first terms of the determinant:

\[
\begin{aligned}
C^2&=1+\frac{u}{12}
+\left(\frac1{576}+\frac1{20160}\right)u^2+\cdots,\\
uD^2&=\frac u4+\frac{u^2}{720}+\cdots,\\
G&=1-\frac u6+\frac{u^2}{2520}+\cdots.
\end{aligned}
\]

Writing \(H=G^{-1}\), coefficient inversion gives

\[
H=1+\frac u6+
\left(\frac1{36}-\frac1{2520}\right)u^2+\cdots
=1+\frac u6+\frac{23}{840}u^2+\cdots.
\]

Now multiply:

\[
\begin{aligned}
[u]A&=\frac1{24}+\frac16=\frac5{24},\\
[u^2]A&=\frac1{40320}+\frac1{144}+\frac{23}{840}\\
&=\frac{1+280+1104}{40320}
=\frac{1385}{40320},\\
[u^0]B&=\frac12,\\
[u]B&=\frac1{720}+\frac1{12}=\frac{61}{720},\\
[u^2]B&=\frac1{3628800}+\frac1{4320}+\frac{23}{1680}\\
&=\frac{1+840+49680}{3628800}
=\frac{50521}{3628800}.
\end{aligned}
\]

The missing first-packet coefficient was

\[
\frac5{24}-\left(-\frac1{24}\right)=\frac14.
\]

In the correct product, the order-\(u\) term from \(CA\) is cancelled by the term from \(uDB\), whose leading value is \(-u/4\). The residual identifies the missing interaction exactly.

## Eliminate a packet while retaining its effect

There is a useful second way to solve the same system. Its second equation gives

\[
DA+CB=0\quad\Longrightarrow\quad B=-C^{-1}DA,
\]

because \(C(0)=1\). Substitute this expression into the first equation:

\[
\left(C-uDC^{-1}D\right)A=1.
\]

The effective first-packet operator is therefore

\[
C_{\mathrm{eff}}=C-uDC^{-1}D=\frac GC.
\]

This is the Schur complement of the second diagonal block. It retains the trip from the first packet to the second and back. Solving the reduced equation gives

\[
A=C_{\mathrm{eff}}^{-1}=\frac CG,
\]

and the eliminated packet is recovered by \(B=-C^{-1}DA\).

The first two correction coefficients make the effect visible. Since

\[
D^2C^{-1}=\frac14-\frac{13}{1440}u+O(u^2),
\]

we obtain

\[
\begin{aligned}
C_{\mathrm{eff}}
&=1+\left(\frac1{24}-\frac14\right)u
+\left(\frac1{40320}+\frac{13}{1440}\right)u^2+O(u^3)\\
&=1-\frac5{24}u+\frac{73}{8064}u^2+O(u^3).
\end{aligned}
\]

Its inverse begins

\[
1+\frac5{24}u+
\left(\frac{25}{576}-\frac{73}{8064}\right)u^2+O(u^3)
=1+\frac5{24}u+\frac{277}{8064}u^2+O(u^3).
\]

These are the correct first-packet secant coefficients.

The reduction uses the known second equation of the reciprocal problem. It is an elimination with a reconstruction rule. The earlier coarsening obstruction concerned arbitrary input pairs, for which the first coordinate alone does not determine the next output. A reduced representation becomes useful when the operation and its retained constraints are transformed along with it.

## Identify the quartic reciprocal family

The determinant has a useful scalar interpretation. Since

\[
\cosh t=C(u)-t^2D(u),
\]

we have

\[
G(t^4)=\cos t\cosh t.
\]

Its full series is

\[
G(u)=\sum_{j\geq0}\frac{(-4)^j u^j}{(4j)!}.
\]

Here is a proof of that coefficient formula. Over the harmless scalar extension containing \(i\),

\[
\cos t\cosh t
=\frac{\cos((1+i)t)+\cos((1-i)t)}2.
\]

For an even cosine index \(m=2j\), both powers \((1+i)^{4j}\) and \((1-i)^{4j}\) equal \((-4)^j\). For an odd index \(m=2j+1\), the powers of degree \(4j+2\) cancel. Only degrees divisible by four remain. All resulting coefficients are rational, giving the displayed identity in \(\mathbb Q[[t]]\).

Define the Paper IV denominator and reciprocal coefficients by

\[
D_N(t)=\sum_{j\geq0}(-1)^j\frac{t^{Nj}}{(Nj)!},
\qquad
D_N(t)^{-1}=\sum_{j\geq0}b_N(j)\frac{t^{Nj}}{(Nj)!}.
\]

We have \(D_2(t)=\cos t\) and \(b_2(j)=s_j\). For \(N=4\), put \(b_j=b_4(j)\). The inverse of the determinant is

\[
H(u)=\sum_{j\geq0}4^jb_j\frac{u^j}{(4j)!}.
\]

This follows by replacing \(t^4\) with \(4u\) in the reciprocal relation for \(D_4\). It is a formal substitution in the reduced variable, with no square root needed in the coefficient field.

The quartic recurrence is

\[
b_0=1,\qquad
b_n=\sum_{k=1}^n(-1)^{k+1}\binom{4n}{4k}b_{n-k}.
\]

Work out four steps:

\[
\begin{aligned}
b_1&=1,\\
b_2&=70-1=69,\\
b_3&=495\cdot69-495+1\\
&=34155-495+1=33661,\\
b_4&=1820\cdot33661-12870\cdot69+1820-1\\
&=61263020-888030+1820-1\\
&=60376809.
\end{aligned}
\]

The resulting sequence

\[
1,1,69,33661,60376809,\ldots
\]

is [OEIS A211212](https://oeis.org/A211212). Its published generating function is equivalent to \(D_4(t)^{-1}\). The OEIS also identifies it as counting four-alternating permutations. We will use that interpretation as a separate computational control later.

## Reconstruct the Euler numbers through the quartic sequence

From the matrix calculation,

\[
\sec t=\cosh t\,H(t^4).
\]

Take the coefficient of \(t^{2n}\). A term of degree \(4k\) from \(H\) leaves degree \(2n-4k\) for \(\cosh t\). Therefore

\[
\frac{s_n}{(2n)!}
=\sum_{k=0}^{\lfloor n/2\rfloor}
\frac{4^kb_k}{(4k)!(2n-4k)!}.
\]

After restoring exponential normalization, the bridge is

\[
\boxed{
s_n=\sum_{k=0}^{\lfloor n/2\rfloor}
\binom{2n}{4k}4^kb_k.}
\]

Equivalently, the two packets obey

\[
\begin{aligned}
s_{2m}&=\sum_{k=0}^m\binom{4m}{4k}4^kb_k,\\
s_{2m+1}&=\sum_{k=0}^m\binom{4m+2}{4k}4^kb_k.
\end{aligned}
\]

The packet matrix has supplied one quartic carrier for both Euler lanes. The fixed numerator \(\cosh t\) determines how that carrier reconstructs them.

Check several cases by hand:

\[
\begin{aligned}
s_2&=1+4=5,\\
s_3&=1+15\cdot4=61,\\
s_4&=1+70\cdot4+16\cdot69\\
&=1+280+1104=1385,\\
s_5&=1+210\cdot4+45\cdot16\cdot69\\
&=1+840+49680=50521.
\end{aligned}
\]

For the degree-twelve target,

\[
\begin{aligned}
s_6
&=1+\binom{12}4\,4\,b_1
+\binom{12}8\,16\,b_2+64b_3\\
&=1+495\cdot4+495\cdot16\cdot69+64\cdot33661\\
&=1+1980+546480+2154304\\
&=2702765.
\end{aligned}
\]

This agrees with the direct secant recurrence, but its intermediate objects are different. One route uses all preceding secant coefficients. The other constructs the quartic carrier and transfers it to the two packets. We have proved why the routes agree, so a disagreement in an implementation would expose a convention or arithmetic error.

## Turn the reciprocal calculation into parameter polynomials

The same construction has a polynomial parameter. Define

\[
D_N(t)^{-r}
=\sum_{n\geq0}P_{N,n}(r)\frac{t^{Nn}}{(Nn)!}.
\]

Here \(r\) may be an indeterminate. The definition takes place in \(\mathbb Q[r][[t]]\). Write \(D_N=1+U\), where \(U\) has zero constant coefficient. The formal binomial expansion is

\[
(1+U)^{-r}
=\sum_{k\geq0}\frac{(-1)^k(r)^{\overline k}}{k!}U^k,
\]

where

\[
(r)^{\overline k}=r(r+1)\cdots(r+k-1),\qquad
(r)^{\overline0}=1.
\]

Only \(k\leq n\) can contribute at degree \(Nn\). Thus \(P_{N,n}\) is a polynomial of degree at most \(n\). More explicitly, for \(n>0\),

\[
P_{N,n}(r)
=(Nn)!\sum_{k=1}^n
\frac{(-1)^{n+k}(r)^{\overline k}}{k!}
\sum_{\substack{q_1+\cdots+q_k=n\\q_j\geq1}}
\frac1{(Nq_1)!\cdots(Nq_k)!}.
\]

The inner sum records ordered compositions of the compressed index. Its factorials still use ordinary degrees. The degree is exactly \(n\), because the leading coefficient is

\[
[r^n]P_{N,n}(r)=\frac{(Nn)!}{n!(N!)^n}\ne0.
\]

For a convenient recurrence, differentiate the defining reciprocal power. If \(F=D_N^{-r}\), then

\[
D_NF'+rD_N'F=0.
\]

At degree \(Nn-1\), this gives

\[
\boxed{
P_{N,n}(r)=\sum_{k=1}^n(-1)^{k+1}
\left[
\binom{Nn-1}{Nk}
+r\binom{Nn-1}{Nk-1}
\right]P_{N,n-k}(r).}
\]

We use \(P_{N,0}=1\) and set a binomial coefficient to zero when its lower index lies outside its range.

For \(N=2\), the first steps are

\[
\begin{aligned}
P_{2,1}(r)&=r,\\
P_{2,2}(r)&=(3+3r)r-r=3r^2+2r,\\
P_{2,3}(r)&=(10+5r)(3r^2+2r)-(5+10r)r+r\\
&=15r^3+30r^2+16r.
\end{aligned}
\]

Continuing gives

\[
\begin{aligned}
P_{2,4}(r)&=105r^4+420r^3+588r^2+272r,\\
P_{2,5}(r)&=945r^5+6300r^4+16380r^3+18960r^2+7936r.
\end{aligned}
\]

Setting \(r=1\) recovers the secant numbers. Setting \(r=2\) gives the coefficients of \(\sec^2t\), beginning

\[
1,2,16,272,7936,\ldots.
\]

At \(N=4\), the same recurrence gives

\[
\begin{aligned}
P_{4,1}(r)&=r,\\
P_{4,2}(r)&=35r^2+34r,\\
P_{4,3}(r)&=5775r^3+16830r^2+11056r.
\end{aligned}
\]

The values at one are \(1,69,33661\). The scalar quartic sequence is one specialization of this polynomial family.

There are useful boundary checks. For \(n>0\), \(P_{N,n}(0)=0\). Also

\[
P_{N,n}(-1)=(-1)^n,
\]

because reciprocal parameter \(-1\) returns the original denominator. For \(N=1\), \(D_1(t)=e^{-t}\), so \(P_{1,n}(r)=r^n\). The program checks these boundaries as well as positive parameters.

## Derive the parameter-addition law

Formal powers of the same unit satisfy

\[
D_N^{-(r+\rho)}=D_N^{-r}D_N^{-\rho}.
\]

One way to verify this for formal parameters is to differentiate the product. It satisfies the same equation \(D_NF'+(r+\rho)D_N'F=0\) and has the same constant coefficient as \(D_N^{-(r+\rho)}\). The recurrence above determines its coefficients uniquely.

Comparing the coefficient of \(t^{Nn}\) gives

\[
\boxed{
P_{N,n}(r+\rho)
=\sum_{k=0}^n\binom{Nn}{Nk}
P_{N,k}(r)P_{N,n-k}(\rho).}
\]

For \(N=2,n=2\), this becomes

\[
P_{2,2}(r+\rho)
=P_{2,2}(r)+6r\rho+P_{2,2}(\rho).
\]

The left side expands to

\[
3r^2+6r\rho+3\rho^2+2r+2\rho,
\]

which is exactly the right side. With \(r=\rho=1\), it gives

\[
P_{2,2}(2)=5+6+5=16.
\]

This is a reusable transfer identity for reciprocal powers. Its weights depend on the ordinary degree \(Nn\). Replacing them by \(\binom nk\) changes the law.

## Recover the classical Euler polynomials

There is a second polynomial family that should be kept distinct from \(P_{N,n}(r)\). The classical Euler polynomials \(\mathcal E_m(x)\) are defined by

\[
\frac{2e^{xt}}{e^t+1}
=\sum_{m\geq0}\mathcal E_m(x)\frac{t^m}{m!}.
\]

The parameter \(x\) is a translation variable. The earlier parameter \(r\) was a reciprocal power. Their roles differ even when some coefficients come from the same Euler numbers.

Factor the generating function about the midpoint:

\[
\frac{2e^{xt}}{e^t+1}
=e^{(x-1/2)t}\operatorname{sech}(t/2).
\]

Using the signed Euler numbers already reconstructed, coefficient multiplication gives

\[
\boxed{
\mathcal E_m(x)
=\sum_{k=0}^{\lfloor m/2\rfloor}
\binom m{2k}\frac{E_{2k}}{2^{2k}}
\left(x-\frac12\right)^{m-2k}.}
\]

The first values follow directly:

\[
\begin{aligned}
\mathcal E_0(x)&=1,\\
\mathcal E_1(x)&=x-\frac12,\\
\mathcal E_2(x)&=\left(x-\frac12\right)^2-\frac14
=x^2-x,\\
\mathcal E_3(x)&=\left(x-\frac12\right)^3
-\frac34\left(x-\frac12\right)
=x^3-\frac32x^2+\frac14.
\end{aligned}
\]

For degree four,

\[
\begin{aligned}
\mathcal E_4(x)
&=\left(x-\frac12\right)^4
-\frac32\left(x-\frac12\right)^2+\frac5{16}\\
&=x^4-2x^3+x.
\end{aligned}
\]

The constants cancel: \(1/16-3/8+5/16=0\). The quadratic terms cancel as well. These cancellations provide simple controls on the signs and scaling.

Three whole-family identities follow from the generating function:

\[
\begin{aligned}
\mathcal E_m(x+1)+\mathcal E_m(x)&=2x^m,\\
\mathcal E_m'(x)&=m\mathcal E_{m-1}(x)\quad(m\geq1),\\
\mathcal E_m(1-x)&=(-1)^m\mathcal E_m(x).
\end{aligned}
\]

For the first, add the generating functions at \(x+1\) and \(x\). The factor \(e^t+1\) cancels, leaving \(2e^{xt}\). For the derivative identity, differentiation in \(x\) multiplies the generating function by \(t\). For reflection, the generating function at \(1-x\) is the original one with \(t\) replaced by \(-t\). Each conclusion follows by coefficient comparison.

We have now used one Euler sequence to construct both its residue-packet representation and a classical polynomial basis. The parameter-addition law and the Euler translation identities remain separate, explicitly typed operations.

## Use a residual to certify and improve a finite reciprocal

Return to a formal unit \(D\). For a candidate inverse \(B\), define the reciprocal residual by

\[
R=1-DB.
\]

This sign convention is chosen for the correction rule below. It is the negative of an output-minus-target residual for the multiplication equation.

Set

\[
B_{\mathrm{new}}=B(2-DB)=B(1+R).
\]

In a commutative coefficient ring,

\[
\begin{aligned}
1-DB_{\mathrm{new}}
&=1-DB(2-DB)\\
&=1-2DB+(DB)^2\\
&=(1-DB)^2=R^2.
\end{aligned}
\]

If \(R\) is divisible by \(t^q\), then the new residual is divisible by \(t^{2q}\). Also

\[
D^{-1}-B=D^{-1}R.
\]

Since \(D^{-1}\) is a unit, the residual certifies exactly which initial coefficients of \(B\) agree with the true inverse. This is an algebraic precision statement.

For \(D=\cos t\), start with \(B_0=1\). Put

\[
h=1-\cos t=\frac{t^2}{2}-\frac{t^4}{24}
+\frac{t^6}{720}-\cdots.
\]

The corrections have a particularly simple form:

\[
\begin{aligned}
B_0&=1, &R_0&=h,\\
B_1&=1+h, &R_1&=h^2,\\
B_2&=1+h+h^2+h^3, &R_2&=h^4,\\
B_3&=1+h+\cdots+h^7, &R_3&=h^8.
\end{aligned}
\]

Inductively,

\[
B_j=\sum_{k=0}^{2^j-1}h^k,\qquad R_j=h^{2^j}.
\]

The residual orders are \(2,4,8,16,\ldots\). Thus \(B_2\) determines the secant series through degree six, and \(B_3\) determines it through degree fourteen.

Work out the degree-six calculation:

\[
\begin{aligned}
B_2
&=1+h+h^2+h^3\\
&=1+\frac{t^2}{2}
+\left(-\frac1{24}+\frac14\right)t^4\\
&\quad+\left(\frac1{720}-\frac1{24}+\frac18\right)t^6
+O(t^8)\\
&=1+\frac{t^2}{2}+\frac5{24}t^4+\frac{61}{720}t^6+O(t^8).
\end{aligned}
\]

Here \(O(t^8)\) means divisibility by \(t^8\) in a formal series ring. It is not a numerical error estimate at a chosen real argument.

## Separate a correct jet from a complete reciprocal

Let

\[
S_3(t)=1+\frac{t^2}{2}+\frac5{24}t^4+\frac{61}{720}t^6.
\]

It is a polynomial of degree six. It agrees with \(\sec t\) through that degree. Its first uncancelled reciprocal residual is

\[
1-\cos t\,S_3(t)
=\frac{1385}{40320}t^8+O(t^{10})
=\frac{277}{8064}t^8+O(t^{10}).
\]

To see the coefficient directly, the degree-eight term in the product is

\[
\frac1{40320}-\frac1{1440}+\frac5{576}-\frac{61}{1440}
=-\frac{1385}{40320}.
\]

The residual supplies the next missing ordinary coefficient. A polynomial can be a correct finite jet while still failing the full reciprocal equation.

The program carries the correction calculation out in

\[
\mathbb Q[t]/(t^{32}).
\]

In that quotient, the fourth correction has zero residual. The correct conclusion is that the residual has order at least 32 in the untruncated series. The quotient cannot reveal whether its later coefficients vanish.

No runtime comparison follows from the doubling of formal precision alone. Polynomial multiplication, coefficient sizes, and representation costs would also have to be counted in a performance claim.

## Change from series coefficients to sequence differences

We now use the signed sequence

\[
a(n)=E_{2n}=(-1)^ns_n
=1,-1,5,-61,1385,-50521,\ldots.
\]

The independent variable is the integer sequence index \(n\). Define the forward shift and difference by

\[
(Sa)(n)=a(n+1),\qquad \Delta=S-I.
\]

Write

\[
c_j=(\Delta^j a)(0).
\]

These are Newton difference coordinates. For every nonnegative integer \(n\),

\[
a(n)=\sum_{j=0}^n\binom njc_j.
\]

Indeed, \(S=I+\Delta\), so the ordinary finite binomial theorem gives

\[
S^n=(I+\Delta)^n
=\sum_{j=0}^n\binom nj\Delta^j.
\]

Apply both sides to \(a\) and evaluate at zero. This proof works for any sequence. There is no assumption that the sequence is the restriction of an analytic function.

Construct the difference triangle from the first five Euler values:

| Order | Successive entries |
|---:|---|
| 0 | \(1,-1,5,-61,1385\) |
| 1 | \(-2,6,-66,1446\) |
| 2 | \(8,-72,1512\) |
| 3 | \(-80,1584\) |
| 4 | \(1664\) |

Taking the first entry of each row gives

\[
(c_0,c_1,c_2,c_3,c_4)=(1,-2,8,-80,1664).
\]

Reconstruct \(a(4)\):

\[
\begin{aligned}
a(4)&=c_0+4c_1+6c_2+4c_3+c_4\\
&=1-8+48-320+1664=1385.
\end{aligned}
\]

This is another exact coordinate representation of the Euler data.

## Derive the polyphase transfer kernel

For spacing \(M\geq1\) and offset \(s\geq0\), define the sampled lane

\[
(R_{M,s}a)(q)=a(Mq+s).
\]

For the usual polyphase decomposition, \(0\leq s<M\). The polynomial identity below also allows any nonnegative offset.

Advancing one position in the lane advances \(M\) positions in the original sequence. Therefore

\[
S_qR_{M,s}=R_{M,s}S^M,
\]

and hence

\[
\Delta_q^kR_{M,s}
=R_{M,s}(S^M-I)^k.
\]

The lane's Newton coefficient is

\[
d_{s,k}=(\Delta_q^kR_{M,s}a)(0)
=\bigl[S^s(S^M-I)^ka\bigr](0).
\]

Substitute \(S=I+\Delta\). Define the finite polynomial

\[
K_{M,s,k}(z)=(1+z)^s\bigl((1+z)^M-1\bigr)^k.
\]

Then

\[
\boxed{
d_{s,k}=\sum_{j=k}^{Mk+s}[z^j]K_{M,s,k}(z)\,c_j.}
\]

For \(k=0\), the lower bound is zero. For \(k>0\), the factor raised to the \(k\)-th power has order \(k\) and degree \(Mk\), which proves the stated support. The identity transfers the difference coordinates directly. It does not require reconstructing every intermediate sequence value.

At \(M=2,s=0\),

\[
(1+z)^2-1=2z+z^2.
\]

The first three kernel rows are therefore

\[
\begin{aligned}
K_{2,0,0}&=1,\\
K_{2,0,1}&=2z+z^2,\\
K_{2,0,2}&=4z^2+4z^3+z^4.
\end{aligned}
\]

They give

\[
\begin{aligned}
d_{0,0}&=c_0=1,\\
d_{0,1}&=2c_1+c_2=-4+8=4,\\
d_{0,2}&=4c_2+4c_3+c_4\\
&=32-320+1664=1376.
\end{aligned}
\]

Check directly from the even lane:

\[
R_{2,0}a=(a(0),a(2),a(4),\ldots)=(1,5,1385,\ldots).
\]

Its differences start with \(5-1=4\) and

\[
1385-2\cdot5+1=1376.
\]

For the odd lane, the first-difference kernel is

\[
K_{2,1,1}(z)=(1+z)(2z+z^2)=2z+3z^2+z^3.
\]

Thus

\[
d_{1,1}=2(-2)+3(8)-80=-60,
\]

which agrees with \(a(3)-a(1)=-61-(-1)=-60\). Offset and spacing are both part of the transfer.

## Compose two refinements and recover the same answer

Sample the lane \(R_{M,s}a\) again, now with spacing \(L\) and offset \(r\). Direct substitution gives

\[
R_{L,r}R_{M,s}a(q)
=a(MLq+Mr+s).
\]

Therefore

\[
R_{L,r}R_{M,s}=R_{ML,s+Mr}.
\]

The offsets compose as well as the spacings. When \(s<M\) and \(r<L\), the new offset lies between zero and \(ML-1\).

The same equality holds in difference coordinates. If \(T_{M,s}\) denotes the transfer whose row \(k\) is the coefficient row of \(K_{M,s,k}\), then

\[
T_{L,r}T_{M,s}=T_{ML,s+Mr}.
\]

To verify it, substitute \((1+z)^M-1\) for the difference variable of the second transfer and multiply its offset factor by \((1+z)^s\). The product is

\[
(1+z)^{Mr+s}\bigl((1+z)^{ML}-1\bigr)^k,
\]

which is the direct kernel for spacing \(ML\). Each row has finite support, so the row composition is well defined without an infinite summation argument.

For two even refinements, start from the lane difference coordinates

\[
(1,4,1376,\ldots).
\]

Refining that lane by two gives first difference

\[
2\cdot4+1376=1384.
\]

The direct spacing-four kernel gives

\[
\begin{aligned}
K_{4,0,1}(z)&=4z+6z^2+4z^3+z^4,\\
d_{0,1}^{(4)}&=4(-2)+6(8)+4(-80)+1664\\
&=-8+48-320+1664=1384.
\end{aligned}
\]

Finally, the original values give

\[
a(4)-a(0)=1385-1=1384.
\]

We have three descriptions of the same result: direct sampling, two successive coordinate transfers, and one composed kernel.

## Keep the prime residual when the precision increases

For a prime \(p\), expand

\[
S^p-I=(I+\Delta)^p-I
=\Delta^p+pB_p(\Delta),
\]

where

\[
B_p(z)=\sum_{j=1}^{p-1}\frac{\binom pj}{p}z^j
\in\mathbb Z[z].
\]

For \(1\leq j<p\), the numerator of \(\binom pj\) contains the factor \(p\), while \(j!\) does not. This proves that each displayed quotient is an integer.

Modulo \(p\), the correction vanishes. At higher precision it remains part of the exact operator. For \(p=2\),

\[
S^2-I=\Delta^2+2\Delta.
\]

Apply this to the Euler data at zero:

\[
\underbrace{a(2)-a(0)}_{4}
=\underbrace{c_2}_{8}
+\underbrace{2c_1}_{-4}.
\]

Dropping the residual \(2\Delta\) produces eight. The correct result is four.

Both values are zero modulo four. Modulo eight, they differ:

\[
4\equiv4\pmod8,\qquad8\equiv0\pmod8.
\]

The coarse agreement does not authorize the higher-precision replacement. In this particular calculation the two-adic valuations are also different:

\[
v_2(4)=2,\qquad v_2(8)=3.
\]

These congruences are calculated in integer sequence coordinates. The ordinary Taylor coefficient \(5/24\) from the series calculation cannot be reduced directly modulo two, because its denominator is not invertible there. The integer EGF numerator \(s_2=5\) can be reduced. Moving from rational series to modular arithmetic therefore requires the coefficient and normalization choices we made at the start.

The spacing-four output is \(1384=8\cdot173\), with valuation three. These are values for the displayed inputs. A congruence for an entire branch of Euler indices would require a separate argument controlling all terms.

Primality matters in the integer-polynomial statement. For the composite value four, \(\binom42=6\) is not divisible by four. One cannot replace the prime hypothesis by an arbitrary positive integer while keeping \(B_p\) integral in this form.

## Read the same shift polynomial as a signal filter

The operator \((S^M-I)^k\) also acts on a complex exponential sequence

\[
z(n)=e^{i\omega n}.
\]

Since \(Sz=e^{i\omega}z\), its response is

\[
H_{M,k}(\omega)=\bigl(e^{iM\omega}-1\bigr)^k.
\]

For \(k\geq1\), it vanishes at \(\omega=2\pi j/M\). For example,

\[
(S^4-I)^2=S^8-2S^4+I
\]

has response \((e^{4i\omega}-1)^2\), with zeros at the fourth roots of unity on the frequency circle. On two-sided signals the causal convention is

\[
(I-S^{-M})^k=S^{-Mk}(S^M-I)^k.
\]

It differs by a pure shift and has the same gain. The earlier one-sided Euler calculation uses only forward shifts and does not need an inverse shift.

This frequency response belongs to the finite filter. We have not taken a convergent Fourier transform of the rapidly growing Euler sequence. The arithmetic reading of the polynomial measures divisibility of integer outputs. The signal reading evaluates it on exponential modes. The common shift polynomial connects the two calculations while preserving what each one means.

## Run the exact checks

Download the [standalone checker](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/euler_packets.py), or the [complete source and results bundle](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/source-and-checks.zip). From the download directory, run:

```text
python -B euler_packets.py
```

Python 3.10 or later is sufficient. On Windows, `py -3` can replace `python` when that is how Python is installed. The program makes no network requests. With no options, it writes only this report:

<!-- euler-expected-output -->
```text
Secant numbers: 1, 1, 5, 61, 1385, 50521, 2702765
Quartic reciprocal: 1, 1, 69, 33661, 60376809
Signed Euler difference coordinates: 1, -2, 8, -80, 1664
Spacing-two lane: 1, 5, 1385; differences: 1, 4, 1376
Refinement: 2*4 + 1376 = 1384
Prime residual: 2*(-2) + 8 = 4
Newton residual orders: 2, 4, 8, 16, at least 32
PASS: Euler packets, polynomials and residuals
```

To save exact JSON and CSV files, choose a new results directory:

```text
python -B euler_packets.py --output my-euler-results
```

The program refuses to replace existing result files. The CSV values retain integers and rational numbers, including the ordinary coefficients and their factorial normalization.

You can also inspect the published [coefficient table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/euler-coefficients.csv), [parameter-polynomial table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/power-polynomials.csv), [exact results](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/results.json), and [source identities](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/source-record.json).

The checks use several different routes:

| Subject | Independent or complementary control | Declared range |
|---|---|---|
| Reciprocal coefficients | Compressed derivative recurrence against ordinary rational binomial products | \(N=2,\ldots,6\), indices 0–10, parameters \(-2,-1,0,1/2,1,2,3\) |
| Parameter polynomials | Exact evaluation and coefficient comparison of the two-variable addition law | Evaluation through index 10, addition law through index 8 |
| Classical sequences | Attributed OEIS prefixes | A000364 indices 0–15, A211212 indices 0–11 |
| Permutation interpretation | Rank-based dynamic programming, with small explicit permutation enumerations | Spacings 2–6 through eight blocks, enumeration through eight letters |
| Quartic bridge | Scalar and packet calculations | Secant indices 0–40, packet coefficients through \(u^{11}\) |
| Residual correction | Direct inverse and residual squaring in the same quotient ring | Modulo \(t^{32}\), iterations 0–4 |
| Euler polynomials | Centered reconstruction, shift, derivative, and reflection identities | Degrees 0–12 |
| Sequence transfer | Direct sampled differences against polynomial kernels | Spacings 1–5, every lane, orders 0–5, three specified integer sequences |
| Refinement composition | Every coefficient of composed and direct kernel rows | Both spacings 1–4, every lane, orders 0–3 |
| Prime residuals | Integer polynomial coefficients and application to the three sequences | Primes 2, 3, 5, 7, and 11 |

The permutation control uses a different definition of the numbers. At length \(m\), keep the number of admissible permutations ending at each possible rank. If the next comparison is an ascent, sum the preceding counts below the new rank. For a descent, sum those at or above it. Repeating the prescribed pattern gives the total. The program also enumerates the small permutation sets directly to check this dynamic program. It does not infer a universal enumeration theorem from those samples.

The [bounded run manifest](../../verification/euler-packets/run-001/manifest.json) records the command, Python version, source hashes before and after execution, time limit, observed completion, and result hashes. The [proof self-review](../../verification/euler-packets/PROOF_REVIEW.md) concerns the written algebra separately. There is no new Lean run for this example.

A separate check compares 605 exact coefficient values with the pinned Komorebi Math source, using both its integer sequence API and its logarithmic reciprocal-power implementation. Its [comparison record](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/library-comparison.json) retains the source identity and declared ranges. This checks agreement with the implemented project machinery alongside the standalone derivation.

## What the example establishes

The written calculation gives exact reciprocal recurrences, the two-packet multiplication law and its coarsening obstruction, the quartic reconstruction identity, reciprocal parameter polynomials, classical Euler-polynomial reconstruction, formal residual correction, and sequence-refinement kernels with their composition and prime correction.

The finite program checks implementations of these laws in its declared ranges. Its deliberately wrong controls expose missing carry factors, wrong factorial normalization, discarded residuals, and an invalid composite-number generalization.

The role of Komorebi is visible in the intermediate objects. A packet that appears dispensable at one resolution is needed by the next operation. A residual identifies the lost interaction. A transfer matrix reconstructs the original coefficients through a different carrier. A polynomial kernel moves the resulting sequence into sampled coordinates, and a second residual records what a coarse congruence discards.

The method keeps the representation, operation, preserved data, and remaining defect together throughout the calculation. That is the concrete connection to [machine-native mathematics](../essays/MACHINE_NATIVE_MATHEMATICS.md). Establishing an advantage for an automated discovery system would additionally require a specified system and a controlled comparison.

## Sources and further reading

- [NIST DLMF, Euler numbers and polynomials](https://dlmf.nist.gov/24.2#ii), including the signed convention and polynomial generating function, and the [secant expansion](https://dlmf.nist.gov/4.19.E5).
- [OEIS A000364](https://oeis.org/A000364) and its [coefficient table](https://oeis.org/A000364/b000364.txt), for the positive secant sequence and offset.
- [OEIS A211212](https://oeis.org/A211212), for the quartic reciprocal sequence, and [A181985](https://oeis.org/A181985), for generalized alternating permutations.
- [Paper IV](../works/paper-iv.md), for cyclic denominators and reciprocal-power polynomials. The [sequence experiments](SEQUENCE_SHAPES.md) use the same exponential normalization.
- [Euler Signal Bridge](../works/euler-signal-bridge.md), for the existing finite-difference/FIR interface developed in greater detail here.
- [Paper III](../works/paper-iii.md), for the broader typed transfer and residual language, and [Paper IX](../works/paper-ix.md), for arithmetic packets and local polynomial deformations.
- [Source and overlap notes](../../verification/euler-packets/SOURCES.md), [target and route record](../../verification/euler-packets/TARGET_AND_ROUTES.md), and [proof self-review](../../verification/euler-packets/PROOF_REVIEW.md).

[Back to the essay](../essays/MACHINE_NATIVE_MATHEMATICS.md) · [Explore the sequence graphs](SEQUENCE_SHAPES.md) · [All demonstrations](../DEMONSTRATIONS.md)
