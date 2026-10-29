# Euler numbers through packets, polynomials, and residuals

**An extended hand-worked Komorebi example · Komorebi P. · 29 October 2026**

[Machine-native mathematics essay](../essays/MACHINE_NATIVE_MATHEMATICS.md) · [Sequence experiments](SEQUENCE_SHAPES.md) · [Coefficient matrices](#write-the-coefficient-transform-as-an-infinite-matrix) · [Supercongruences](#state-the-supercongruences-and-check-an-euler-index-shift) · [Run the exact checks](#run-the-exact-checks)

We will reconstruct the Euler secant numbers through a different sequence, turn the calculation into polynomial identities, and then use the same Euler data in a refinement calculation. At each change of coordinates we will write the transfer explicitly. When a shortcut fails, we will calculate the residual that explains the failure.

The two main numerical destinations are

\[
s_6=2702765
\]

for the coefficient of \(t^{12}/12!\) in \(\sec t\), and

\[
E_8-E_0=1384
\]

for a refinement of the signed Euler sequence. The derivations connect them to reciprocal series, a two-packet matrix, finite-difference coordinates, and an exact correction law. We will also reconstruct \(E_8=1385\) from alternating odd powers and from a separate dyadic source. Those calculations will give exact partial sums and precision certificates.

The Euler numbers and the quartic sequence used below are classical. This example develops them through Komorebi's packet, transfer, and residual language. Its purpose is to make a substantial calculation inspectable from beginning to end. The [source notes](../../verification/euler-packets/SOURCES.md) identify the classical references and the project sources.

You can follow the algebra without running code. The accompanying [Python program](../../examples/euler_packets.py) uses exact integers and fractions and needs only Python's standard library.

<a id="conventions-and-three-coordinate-systems"></a>

## Conventions and coordinate systems

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

We will use several coordinate systems. Their operations have different meanings.

| Coordinates | Object being represented | Operation to keep track of |
|---|---|---|
| Exponential coefficients | A formal series in \(t\) | Products carry binomial weights |
| Residue packets | The same even series, grouped modulo four | Multiplication becomes a matrix with a carry factor |
| Local Euler coordinates | Signed Euler numbers reconstructed from an odd-length or dyadic source | A weighted convolution retains a finite truncation error |
| Finite differences | The indexed sequence \(a(0),a(1),\ldots\) | Sampling becomes a polynomial in the forward difference |

The series calculations take place over the rational numbers. A formal series is a sequence of coefficients with a multiplication rule. Every coefficient of a product is a finite sum, so the calculations do not require an analytic convergence argument. A series with a nonzero constant coefficient has a unique formal reciprocal.

For a prime \(p\), \(v_p(x)\) denotes the exponent of \(p\) in the reduced numerator of a nonzero rational number \(x\), minus that in its denominator. We set \(v_p(0)=\infty\). A rational number can be reduced modulo \(p^h\) when its reduced denominator is coprime to \(p\), using the modular inverse of that denominator.

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

Here is a proof of that coefficient formula. Work temporarily over \(\mathbb Q(i)\):

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

## Recover the quartic carrier from an Euler packet

The bridge can also be read backwards. In the first packet, the coefficient of \(b_m\) is \(4^m\), so

\[
b_m=\frac1{4^m}\left[
s_{2m}-\sum_{k=0}^{m-1}\binom{4m}{4k}4^kb_k\right].
\]

The case \(m=0\) gives \(b_0=s_0=1\), with an empty sum. The next steps give

\[
\begin{aligned}
b_1&=\frac{5-1}{4}=1,\\
b_2&=\frac{1385-1-70\cdot4}{16}
=\frac{1104}{16}=69,\\
b_3&=\frac{2702765-1-1980-546480}{64}
=\frac{2154304}{64}=33661.
\end{aligned}
\]

Once that carrier is known, the second packet is determined by the same reconstruction rule. For example,

\[
\begin{aligned}
s_7
&=1+\binom{14}4\,4+\binom{14}8\,16\cdot69
+\binom{14}{12}\,64\cdot33661\\
&=1+4004+3315312+196041664\\
&=199360981.
\end{aligned}
\]

Thus the Euler coefficients at degrees \(0,4,8,12\) recover the carrier through \(b_3\), which also predicts the coefficient at degree fourteen. This uses the reciprocal equation and its fixed numerator. An arbitrary even series would have two independent packets. The reconstruction constraint is what connects them in this example.

## Count the first quartic values without series inversion

There is a concrete permutation interpretation of the same integers. Arrange \(4n\) distinct letters in descending blocks of four. Require an ascent at each boundary between blocks. This is the four-alternating pattern used by the cited OEIS entries.

At length four, only \(4321\) occurs, so \(b_1=1\). At length eight, choose which four letters occupy the first block. Each block then has a unique descending order. There are \(\binom84=70\) choices. Exactly one choice gives a descent at the boundary as well, namely the globally descending permutation. Removing it leaves

\[
b_2=70-1=69.
\]

At length twelve, three descending blocks can be filled in

\[
\frac{12!}{4!4!4!}=34650
\]

ways. A forbidden descent at the first boundary merges its two blocks into a descending block of eight. That leaves \(\binom{12}4=495\) choices. The second forbidden boundary gives another 495. Their intersection is the unique globally descending permutation. Inclusion-exclusion gives

\[
b_3=34650-495-495+1=33661.
\]

At length sixteen there are three internal boundaries. The same calculation gives

\[
\begin{aligned}
b_4
&=\frac{16!}{(4!)^4}
-3\frac{16!}{8!4!4!}
+2\binom{16}4+\binom{16}8-1\\
&=63063000-3\cdot900900+2\cdot1820+12870-1\\
&=60376809.
\end{aligned}
\]

The double-boundary intersections have different shapes. Two adjacent merges give blocks of sizes twelve and four. Two disjoint merges give blocks of sizes eight and eight. Keeping those cases separate explains the two different binomial terms.

For general block length \(N\geq1\) and \(n>0\), a selection of forbidden boundaries merges the blocks into an ordered composition \(q_1+\cdots+q_k=n\). There are \(n-k\) merged boundaries and

\[
\frac{(Nn)!}{(Nq_1)!\cdots(Nq_k)!}
\]

ways to fill the resulting descending blocks. Hence the count is

\[
\sum_{k=1}^n(-1)^{n-k}
\sum_{\substack{q_1+\cdots+q_k=n\\q_j\geq1}}
\frac{(Nn)!}{(Nq_1)!\cdots(Nq_k)!}.
\]

Expanding \(D_N^{-1}=(1+(D_N-1))^{-1}\) gives precisely this expression for \(b_N(n)\). This proves the enumeration identity. Direct permutation enumeration and rank-based dynamic programming provide separate finite checks of its implementation.

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

## Use Euler polynomials to sum alternating powers

The translation law also turns a finite sum into two boundary values. Multiply

\[
\mathcal E_m(x+j+1)+\mathcal E_m(x+j)=2(x+j)^m
\]

by \((-1)^j\), and sum over \(0\leq j<L\). Every interior polynomial value cancels with its neighbor. For every integer \(L\geq0\),

\[
\boxed{
\sum_{j=0}^{L-1}(-1)^j(x+j)^m
=\frac{\mathcal E_m(x)-(-1)^L\mathcal E_m(x+L)}2.}
\]

The empty sum at \(L=0\) is zero. No limiting process is involved.

For example,

\[
1^4-2^4+3^4-4^4+5^4
=1-16+81-256+625=435.
\]

The polynomial calculation gives the same answer:

\[
\frac{\mathcal E_4(1)+\mathcal E_4(6)}2
=\frac{0+(6^4-2\cdot6^3+6)}2
=\frac{870}{2}=435.
\]

The alternating odd-power window needed next is obtained by taking \(x=1/2\) and multiplying by \(2^m\). For an odd positive length \(p\), define

\[
A_{p,m}=\sum_{a=0}^{p-1}(-1)^a(2a+1)^m.
\]

Then

\[
A_{p,m}=2^{m-1}
\left[\mathcal E_m\!\left(\frac12\right)
+\mathcal E_m\!\left(p+\frac12\right)\right].
\]

This includes \(m=0\): the factor is \(1/2\), and the bracket is two. For \(p=3,m=4\), the direct value is \(1-81+625=545\). Since

\[
\mathcal E_4\!\left(\frac12\right)=\frac5{16},
\qquad
\mathcal E_4\!\left(\frac72\right)=\frac{1085}{16},
\]

the polynomial route gives \(8(5+1085)/16=545\) as well.

## Reconstruct Euler numbers from an odd-length window

We now use the local Euler coordinates developed in [Paper IX](../works/paper-ix.md). The source numbers \(A_{p,2n}\) are finite alternating sums. The first question is what operator reconstructs \(E_{2n}\) from them.

Start with their full exponential generating series. The finite geometric sum gives, for positive odd \(p\),

\[
\begin{aligned}
\sum_{m\geq0}A_{p,m}\frac{t^m}{m!}
&=\sum_{a=0}^{p-1}(-1)^ae^{(2a+1)t}\\
&=e^t\frac{1+e^{2pt}}{1+e^{2t}}\\
&=e^{pt}\cosh(pt)\operatorname{sech}t.
\end{aligned}
\]

Average the expression at \(t\) and \(-t\) to retain only even degrees:

\[
\mathcal A_p(t)
:=\sum_{n\geq0}A_{p,2n}\frac{t^{2n}}{(2n)!}
=\cosh^2(pt)\operatorname{sech}t.
\]

The reconstruction kernel is therefore \(\operatorname{sech}^2(pt)\). Write

\[
\operatorname{sech}^2t
=\sum_{r\geq0}\gamma_r\frac{t^{2r}}{(2r)!}.
\]

The earlier reciprocal-power polynomials give

\[
\gamma_r=(-1)^rP_{2,r}(2),
\qquad
(\gamma_0,\ldots,\gamma_4)=(1,-2,16,-272,7936).
\]

These coefficients are integers. One can also see their integrality directly by multiplying the two signed Euler series. Multiplying \(\mathcal A_p\) by the reconstruction kernel and comparing EGF coefficients proves

\[
\boxed{
E_{2n}=\sum_{r=0}^n\binom{2n}{2r}
\gamma_rp^{2r}A_{p,2n-2r}.}
\]

The inverse transfer is equally explicit. Since

\[
\cosh^2(pt)=\frac{1+\cosh(2pt)}2,
\]

its EGF coefficients are

\[
\lambda_{p,0}=1,\qquad
\lambda_{p,r}=2^{2r-1}p^{2r}\quad(r\geq1).
\]

Consequently,

\[
A_{p,2n}=\sum_{r=0}^n\binom{2n}{2r}
\lambda_{p,r}E_{2n-2r}.
\]

For \(p=3,n=2\), this inverse calculation is already visible:

\[
A_{3,4}=5+6\cdot18\cdot(-1)+648=545.
\]

The forward and inverse transfers are triangular and have diagonal one. Oddness of \(p\) is needed for this source identity. Primality is needed only when we interpret the resulting precision in terms of a prime.

## Work the odd-prime reconstruction through to 1385

Choose \(p=3\). The source and kernel values needed for ordinary degree eight are

| \(r\) | Source \(A_{3,2r}=1-3^{2r}+5^{2r}\) | Kernel \(\gamma_r3^{2r}\) |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 17 | -18 |
| 2 | 545 | 1296 |
| 3 | 14897 | -198288 |
| 4 | 384065 | 52068096 |

Insert them into the degree-eight reconstruction:

\[
\begin{aligned}
E_8
&=384065+28(-18)(14897)+70(1296)(545)\\
&\quad+28(-198288)(17)+52068096\\
&=384065-7508088+49442400-94385088+52068096\\
&=1385.
\end{aligned}
\]

Let \(T_L^{(p)}(n)\) retain terms \(0\leq r\leq\min(L,n)\). Every omitted term contains \(p^{2r}\), and all its remaining factors are integers. Thus, for every odd positive \(p\),

\[
p^{2L+2}\mid E_{2n}-T_L^{(p)}(n).
\]

If \(L\geq n\), the omitted sum is empty and the error is zero. For an odd prime this gives a prime-adic precision certificate. It follows from the explicit finite sum for every \(n\), rather than from the size of a tested prefix.

For this particular row, the complete partial sums and errors are

| Depth \(L\) | \(T_L^{(3)}(4)\) | Error \(1385-T_L^{(3)}(4)\) | \(v_3\) of error |
|---:|---:|---:|---:|
| 0 | 384065 | -382680 | 2 |
| 1 | -7124023 | 7125408 | 4 |
| 2 | 42318377 | -42316992 | 6 |
| 3 | -52066711 | 52068096 | 8 |
| 4 | 1385 | 0 | \(\infty\) |

For instance, \(1385\equiv8\pmod9\), while \(-7124023\equiv1385\equiv8\pmod{81}\). The partial sums fluctuate in ordinary size, but their differences from the target acquire the stated powers of three. These are two different ways of measuring the same rational or integer error.

## Build the separate dyadic source and kernel

The odd-length source cannot simply be reused with \(p=2\). Its constant coefficient would be \(1-1=0\). Multiplication by any formal series would still have constant coefficient zero, so it could not reconstruct \(E_0=1\).

Paper IX uses a different source for the dyadic chart. In ordinary even degree \(m\), set

\[
R_m=\frac{3^{m+2}-1}{4(m+1)(m+2)}.
\]

Its generating series is

\[
\mathcal R(t)=\sum_{n\geq0}R_{2n}\frac{t^{2n}}{(2n)!}
=\frac{\cosh(3t)-\cosh t}{4t^2}.
\]

The numerator is divisible by \(t^2\), so this is a well-defined formal series with constant coefficient one. The identity \(\cosh(3t)-\cosh t=4\cosh t\sinh^2t\) gives

\[
\mathcal R(t)\cosh t
=\left(\frac{\sinh(2t)}{2t}\right)^2.
\]

The quotient \(\sinh(2t)/(2t)\) also has constant coefficient one. Define

\[
J(t)=\left(\frac{\sinh(2t)}{2t}\right)^2,
\qquad
K(t)=J(t)^{-1}=\left(\frac{2t}{\sinh(2t)}\right)^2.
\]

Then \(K(t)\mathcal R(t)=\operatorname{sech}t\). If

\[
K(t)=\sum_{r\geq0}\kappa_r\frac{t^{2r}}{(2r)!},
\]

the dyadic reconstruction is

\[
\boxed{
E_{2n}=\sum_{r=0}^n\binom{2n}{2r}\kappa_rR_{2n-2r}.}
\]

We can obtain the kernel entirely by rational inversion. The inverse kernel has coefficients

\[
J(t)=\frac{\cosh(4t)-1}{8t^2}
=\sum_{r\geq0}\lambda_{2,r}\frac{t^{2r}}{(2r)!},
\qquad
\lambda_{2,r}=\frac{2^{4r+1}}{(2r+1)(2r+2)}.
\]

The constant coefficient is one. For \(r>0\), the product equation \(JK=1\) gives

\[
\kappa_r=-\sum_{j=1}^r\binom{2r}{2j}\lambda_{2,j}\kappa_{r-j}.
\]

For example,

\[
\begin{aligned}
\kappa_1&=-\frac83,\\
\kappa_2&=-\frac{256}{15}
-6\left(\frac83\right)\left(-\frac83\right)
=\frac{128}{5},\\
\kappa_3&=-\frac{1024}{7}+\frac{2048}{3}-1024
=-\frac{10240}{21}.
\end{aligned}
\]

The relevant source and kernel values are

| \(r\) | \(R_{2r}\) | \(\kappa_r\) |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | \(5/3\) | \(-8/3\) |
| 2 | \(91/15\) | \(128/5\) |
| 3 | \(205/7\) | \(-10240/21\) |
| 4 | \(7381/45\) | \(229376/15\) |

The dyadic source, kernel and factorial normalization have all changed together. Merely substituting two into the odd-prime formula would miss that change of coordinates.

## Reconstruct 1385 in the dyadic chart

At ordinary degree eight, calculate the five terms separately:

\[
\begin{aligned}
E_8
&=\frac{7381}{45}
+28\left(-\frac83\right)\frac{205}{7}
+70\left(\frac{128}{5}\right)\frac{91}{15}\\
&\quad+28\left(-\frac{10240}{21}\right)\frac53
+\frac{229376}{15}\\
&=\frac{7381}{45}-\frac{6560}{3}+\frac{163072}{15}
-\frac{204800}{9}+\frac{229376}{15}\\
&=\frac{7381-98400+489216-1024000+688128}{45}\\
&=\frac{62325}{45}=1385.
\end{aligned}
\]

Define \(T_L^{(2)}(n)\) by retaining the first \(L+1\) terms, or all terms when \(L\geq n\). The error table for this row is

| Depth \(L\) | \(T_L^{(2)}(4)\) | Error \(1385-T_L^{(2)}(4)\) | \(v_2\) of error |
|---:|---:|---:|---:|
| 0 | \(7381/45\) | \(54944/45\) | 5 |
| 1 | \(-91019/45\) | \(153344/45\) | 8 |
| 2 | \(398197/45\) | \(-335872/45\) | 13 |
| 3 | \(-208601/15\) | \(229376/15\) | 15 |
| 4 | 1385 | 0 | \(\infty\) |

All denominators in this table are odd, so the congruences are meaningful in the ring \(\mathbb Z_{(2)}\) of rationals with odd denominator.

The first term alone already gives the correct answer modulo 32. Indeed,

\[
45\equiv13\pmod{32},\qquad13\cdot5\equiv1\pmod{32},
\]

so

\[
\frac{7381}{45}\equiv21\cdot5\equiv9\equiv1385\pmod{32}.
\]

This modular division uses the inverse of an odd denominator. It is a different operation from attempting to reduce \(5/24\) modulo a power of two, which is undefined because 24 is not a unit.

## Prove the dyadic precision bound and locate its sharp edge

The exact kernel explains the precision pattern. Define the Bernoulli numbers by

\[
\frac{z}{e^z-1}=\sum_{j\geq0}B_j\frac{z^j}{j!},
\qquad B_1=-\frac12.
\]

The regular even series \(Q(z)=z\coth z\) has expansion

\[
Q(z)=1+\sum_{r\geq1}\frac{2^{2r}B_{2r}}{(2r)!}z^{2r}.
\]

This follows from \(Q(z)=z+2z/(e^{2z}-1)\). Differentiation gives

\[
Q(z)-zQ'(z)=\left(\frac z{\sinh z}\right)^2.
\]

Substitute \(z=2t\) and compare coefficients:

\[
\kappa_r=-2^{4r}(2r-1)B_{2r}\qquad(r\geq1).
\]

The [von Staudt–Clausen denominator theorem](https://dlmf.nist.gov/24.10.E1) states that the reduced denominator of \(B_{2r}\), for \(r\geq1\), contains each prime \(q\) with \((q-1)\mid2r\) exactly once. In particular it contains two exactly once. Thus \(v_2(B_{2r})=-1\), and

\[
\boxed{v_2(\kappa_r)=4r-1\quad(r\geq1).}
\]

We also need the source coefficients to be dyadic units. Write \(n+1=2^du\), with \(u\) odd. In

\[
9^{n+1}-1=(9^u-1)\prod_{j=0}^{d-1}(9^{2^ju}+1),
\]

the first factor has valuation three, since \((9^u-1)/(9-1)\) is odd. Each factor in the product has valuation one. Hence \(v_2(9^{n+1}-1)=3+d\). The denominator of \(R_{2n}\) has the same valuation, so \(v_2(R_{2n})=0\).

It follows that the \(r\)-th reconstruction term, for \(1\leq r\leq n\), has exact weight

\[
v_2\!\left(\binom{2n}{2r}\kappa_rR_{2n-2r}\right)
=4r-1+v_2\binom{2n}{2r}.
\]

Every term omitted after depth \(L\) has weight at least \(4L+3\). Their finite sum therefore proves

\[
\boxed{
E_{2n}-T_L^{(2)}(n)\in2^{4L+3}\mathbb Z_{(2)}
\quad(n,L\geq0).}
\]

The bound includes the empty tail, where the error is zero. It is uniformly sharp: at \(n=L+1\), exactly one term is omitted, and that term is \(\kappa_{L+1}\), because the binomial coefficient and \(R_0\) are both one. Its valuation is exactly \(4L+3\).

The first sharpness examples are

\[
\begin{aligned}
E_2-T_0^{(2)}(1)&=-1-\frac53=-\frac83,
&v_2&=3,\\
E_4-T_1^{(2)}(2)&=\frac{128}{5},
&v_2&=7,\\
E_6-T_2^{(2)}(3)&=-\frac{10240}{21},
&v_2&=11,\\
E_8-T_3^{(2)}(4)&=\frac{229376}{15},
&v_2&=15.
\end{aligned}
\]

For the fixed row \(E_8\), the four nonconstant term weights are

\[
3+v_2(28)=5,\quad
7+v_2(70)=8,\quad
11+v_2(28)=13,\quad15.
\]

They are distinct and increase strictly. In each nonempty tail there is a unique term of least valuation, so it cannot be cancelled by terms divisible by a higher power of two. This proves the exact error valuations \(5,8,13,15\) in the table. The uniform bound and the stronger precision of a particular row answer different questions.

## State the supercongruences and check an Euler index shift

The proved local truncation laws can be written as explicit supercongruences. For an odd prime \(p\), every \(n,L\geq0\) satisfies

\[
E_{2n}\equiv T_L^{(p)}(n)\pmod{p^{2L+2}}.
\]

For the separate dyadic source,

\[
E_{2n}\equiv T_L^{(2)}(n)\pmod{2^{4L+3}}
\quad\text{in }\mathbb Z_{(2)}.
\]

Both statements include exact equality at full depth. The word supercongruence here refers to the proved powers of the prime in the reconstruction error. It does not remove the source, depth, or coefficient-domain hypotheses.

For \(E_8\), the guaranteed moduli and resulting residues are

| Depth \(L\) | Odd modulus \(3^{2L+2}\) | Residue | Dyadic modulus \(2^{4L+3}\) | Residue |
|---:|---:|---:|---:|---:|
| 0 | 9 | 8 | 8 | 1 |
| 1 | 81 | 8 | 128 | 105 |
| 2 | 729 | 656 | 2048 | 1385 |
| 3 | 6561 | 1385 | 32768 | 1385 |

Each residue can be obtained from the corresponding partial sum, using a modular inverse for the odd dyadic denominator. The actual error table gives stronger row-specific dyadic precision at the first three depths. The uniform bound remains sharp across all Euler rows.

There is also a useful supercongruence between Euler indices. For an odd prime \(p\) and an even integer \(m\geq2\),

\[
\boxed{E_{m+p(p-1)}\equiv E_m\pmod{p^2}.}
\]

Here is a proof from the depth-zero source. We already know \(E_m\equiv A_{p,m}\pmod{p^2}\). If \(u\) is not divisible by \(p\), multiplication by \(u\) permutes the nonzero residues modulo \(p\). Multiplying them and cancelling their invertible product proves \(u^{p-1}\equiv1\pmod p\). Write \(u^{p-1}=1+pb\). Raising to the \(p\)-th power shows \(u^{p(p-1)}\equiv1\pmod{p^2}\).

Apply this to each odd integer \(2a+1\) in the source window. The one divisible by \(p\) contributes zero modulo \(p^2\), because both exponents are at least two. Every other term is unchanged when the exponent increases by \(p(p-1)\). The two source sums, and therefore the two Euler numbers, are congruent modulo \(p^2\).

At \(p=3,m=2\),

\[
E_8-E_2=1385-(-1)=1386=9\cdot154.
\]

Its three-adic valuation is exactly two. The starting-index restriction matters: \(E_6-E_0=-62\) is not divisible by three. Deeper index-shift claims must also control the binomial weights in the retained correction terms. The depth-zero argument alone does not supply them.

## Write the coefficient transform as an infinite matrix

The local reconstruction formulas are rows of one infinite coefficient transform. Let

\[
K_q(t)=\sum_{r\geq0}q_r\frac{t^{2r}}{(2r)!},\qquad q_0=1,
\]

and let \(A(t)\) have even EGF coefficients \(A_0,A_1,\ldots\), so that its coefficient at \(t^{2j}/(2j)!\) is \(A_j\). Multiplication by \(K_q\) transforms these coefficients through the matrix

\[
\mathsf C(q)_{n,j}=
\begin{cases}
\displaystyle\binom{2n}{2j}q_{n-j},&0\leq j\leq n,\\
0,&j>n.
\end{cases}
\]

Its opening rows are

\[
\mathsf C(q)=
\begin{pmatrix}
1&0&0&0&0&\cdots\\
q_1&1&0&0&0&\cdots\\
q_2&6q_1&1&0&0&\cdots\\
q_3&15q_2&15q_1&1&0&\cdots\\
q_4&28q_3&70q_2&28q_1&1&\cdots\\
\vdots&\vdots&\vdots&\vdots&\vdots&\ddots
\end{pmatrix}.
\]

The row index is the output's compressed degree. The column index is the source's compressed degree. Both refer to ordinary degrees twice as large. If \(\boldsymbol A=(A_0,A_1,\ldots)^T\), then the transformed vector is \(\mathsf C(q)\boldsymbol A\).

This infinite matrix acts on every rational coefficient sequence. Row \(n\) contains only \(n+1\) possible nonzero entries. Each output is therefore a finite sum. No convergence condition or summability prescription is being imposed on the infinite column.

For the odd chart at three, put \(q_r=\gamma_r3^{2r}\), and call the resulting matrix \(\mathsf C_3\). Its block with rows and columns zero through four is

\[
\mathsf C_3^{[4]}=
\begin{pmatrix}
1&0&0&0&0\\
-18&1&0&0&0\\
1296&-108&1&0&0\\
-198288&19440&-270&1&0\\
52068096&-5552064&90720&-504&1
\end{pmatrix}.
\]

The entire five-degree calculation is

\[
\mathsf C_3^{[4]}
\begin{pmatrix}1\\17\\545\\14897\\384065\end{pmatrix}
=\begin{pmatrix}1\\-1\\5\\-61\\1385\end{pmatrix}.
\]

For instance, the degree-four row gives \(1296-108\cdot17+545=5\). The final row is the earlier five-term reconstruction of \(E_8\), written in ascending source degree. Its column index \(j\) corresponds to correction index \(r=4-j\).

For the dyadic chart, use \(q_r=\kappa_r\). The corresponding block is

\[
\mathsf C_2^{[4]}=
\begin{pmatrix}
1&0&0&0&0\\
-\frac83&1&0&0&0\\
\frac{128}{5}&-16&1&0&0\\
-\frac{10240}{21}&384&-40&1&0\\
\frac{229376}{15}&-\frac{40960}{3}&1792&-\frac{224}{3}&1
\end{pmatrix}.
\]

It acts on the different source vector:

\[
\mathsf C_2^{[4]}
\begin{pmatrix}1\\5/3\\91/15\\205/7\\7381/45\end{pmatrix}
=\begin{pmatrix}1\\-1\\5\\-61\\1385\end{pmatrix}.
\]

The same Euler vector has two different coefficient descriptions. Their source vectors and transform matrices must be kept together.

## Compose, invert, and truncate the coefficient matrices

Multiplying two kernels corresponds exactly to composing their matrices. For another normalized kernel sequence \(r\), define the EGF convolution

\[
(q\star r)_m=\sum_{\ell=0}^m\binom{2m}{2\ell}q_{m-\ell}r_\ell.
\]

Then

\[
\boxed{\mathsf C(q)\mathsf C(r)=\mathsf C(q\star r).}
\]

To verify the entry in row \(n\), column \(k\), only intermediate indices \(k\leq j\leq n\) occur. Use

\[
\binom{2n}{2j}\binom{2j}{2k}
=\binom{2n}{2k}\binom{2n-2k}{2j-2k}.
\]

The product entry becomes

\[
\binom{2n}{2k}
\sum_{\ell=0}^{n-k}\binom{2(n-k)}{2\ell}
q_{n-k-\ell}r_\ell,
\]

which is the claimed entry of \(\mathsf C(q\star r)\). All sums used in the proof are finite.

If the series with coefficients \(r\) is the reciprocal of \(K_q\), their convolution is \((1,0,0,\ldots)\). Therefore

\[
\mathsf C(q)^{-1}=\mathsf C(r).
\]

For the odd chart at three, the inverse kernel has coefficients \(1,18,648,\ldots\). The first three rows give an explicit check:

\[
\begin{pmatrix}
1&0&0\\-18&1&0\\1296&-108&1
\end{pmatrix}
\begin{pmatrix}
1&0&0\\18&1&0\\648&108&1
\end{pmatrix}
=I_3.
\]

The lower-left entry is \(1296-1944+648=0\). The next entry in that row is \(-108+108=0\). Thus the inverse restores the source coefficients, rather than merely reproducing one chosen Euler vector.

Finite leading blocks are exact here. Let \(\pi_N\) retain coordinates zero through \(N\), and let \(\mathsf C(q)^{[N]}\) be the corresponding square block. Lower triangularity gives

\[
\pi_N\mathsf C(q)=\mathsf C(q)^{[N]}\pi_N.
\]

Every product entry in these rows uses intermediate indices at most \(N\), so composition and inversion also commute with taking this block. Each block has diagonal one and determinant one. The infinitely many blocks are compatible finite coefficient calculations. No input coefficient beyond \(N\) can change an output coefficient at or below \(N\).

## Change the local coefficient basis and track congruence precision

Let \(\boldsymbol A^{(p)}\) denote the local source vector, with entries \(A_{p,2n}\) for odd \(p\), and \(R_{2n}\) for \(p=2\). Both reconstruct the same Euler vector through \(\boldsymbol e=\mathsf C_p\boldsymbol A^{(p)}\). The exact change from source chart \(p\) to source chart \(q\) is

\[
\boxed{
\boldsymbol A^{(q)}=\mathsf B_{q\leftarrow p}\boldsymbol A^{(p)},
\qquad
\mathsf B_{q\leftarrow p}=\mathsf C_q^{-1}\mathsf C_p.}
\]

These lower-triangular matrices satisfy

\[
\mathsf B_{p\leftarrow p}=I,\qquad
\mathsf B_{r\leftarrow q}\mathsf B_{q\leftarrow p}
=\mathsf B_{r\leftarrow p}.
\]

The intervening factors \(\mathsf C_q\mathsf C_q^{-1}\) cancel, and every matrix entry uses finitely many terms. Changing coordinates directly or through an intermediate chart gives the same result.

For odd source lengths three and five, the scalar kernel of \(\mathsf B_{5\leftarrow3}\) is \(\cosh^2(5t)\operatorname{sech}^2(3t)\). Its first coefficients are \(1,32,896,\ldots\). Thus

\[
\mathsf B_{5\leftarrow3}^{[2]}=
\begin{pmatrix}1&0&0\\32&1&0\\896&192&1\end{pmatrix},
\qquad
\mathsf B_{5\leftarrow3}^{[2]}
\begin{pmatrix}1\\17\\545\end{pmatrix}
=\begin{pmatrix}1\\49\\4705\end{pmatrix}.
\]

The last source value also follows directly from \(1-3^4+5^4-7^4+9^4=4705\). Reducing the input coefficients modulo 81 gives \((1,17,59)\). The final transformed row is

\[
5+30\cdot17+59=574\equiv7\pmod{81},
\]

which agrees with \(4705\equiv7\pmod{81}\). Odd-chart base changes have integer entries and integer inverses, so they preserve coefficientwise congruences for every positive integer modulus. Choosing a new chart does not by itself choose a new modulus.

More generally, consider a finite block \(B\) at a fixed prime \(\ell\), with integers \(d\geq0\) and \(h\). If every entry has valuation at least \(-d\), and an input error vector has every coordinate of valuation at least \(h\), then

\[
v_\ell\bigl((B\,\delta\boldsymbol A)_n\bigr)\geq h-d.
\]

Each summand has that bound, so its finite sum does too. Integral matrices have \(d=0\). A denominator divisible by the working prime can cause a loss of precision.

For a concrete loss, change from the three-chart to the dyadic source. The first kernel coefficients of \(\mathsf B_{2\leftarrow3}\) are

\[
1,\quad \frac83-18=-\frac{46}{3},\quad
\frac{256}{15}-288+1296=\frac{15376}{15}.
\]

The entry taking source degree four to output degree eight is

\[
(\mathsf B_{2\leftarrow3})_{4,2}
=\binom84\frac{15376}{15}=\frac{215264}{3}.
\]

If only that input coordinate is perturbed by nine, the output perturbation is

\[
\delta R_8=\frac{215264}{3}\cdot9=645792,
\qquad v_3(\delta R_8)=1.
\]

The input error had valuation two. This contribution loses one ternary digit. Some dyadic-source values themselves have denominators divisible by three, so this statement is about the valuation of their difference, not an ordinary residue of each value modulo nine.

At the prime two, the dyadic and odd-chart matrices and their inverses all have odd denominators. Their base changes therefore preserve coefficientwise dyadic precision. An exact rational change of basis and its behavior at a specified prime are related facts that must both be checked.

## Separate factorial normalization from ordinary Toeplitz multiplication

The binomial weights arise from a diagonal change of coordinates. Set \(x=t^2\), and define ordinary coefficients

\[
k_r=\frac{q_r}{(2r)!},\qquad
\widehat A_j=\frac{A_j}{(2j)!}.
\]

Multiplication in ordinary \(x\)-coefficients is the lower-triangular Toeplitz matrix

\[
\mathsf L(k)_{n,j}=k_{n-j}\quad(j\leq n),
\]

with zero entries above the diagonal. Its diagonals are constant. Introduce

\[
\mathsf F=\operatorname{diag}(0!,2!,4!,6!,\ldots).
\]

The EGF matrix is its factorial conjugate:

\[
\boxed{\mathsf C(q)=\mathsf F\mathsf L(k)\mathsf F^{-1}.}
\]

Indeed, its \((n,j)\) entry is

\[
\frac{(2n)!}{(2j)!}\frac{q_{n-j}}{(2n-2j)!}
=\binom{2n}{2j}q_{n-j}.
\]

For the Euler output, write \(\widehat e_n=E_{2n}/(2n)!\). At the first nonconstant coefficient of the three-chart example, ordinary multiplication gives

\[
\widehat e_1=-9\cdot1+\frac{17}{2}=-\frac12.
\]

Multiplying by \(2!\) recovers \(E_2=-1\). Using the ordinary Toeplitz row on the unnormalized EGF numerators would instead give \(-9+17=8\). The kernel has not changed, but the coordinate convention has been mixed.

The diagonal conjugation is valid over \(\mathbb Q\), where all factorials are invertible. It does not justify cancelling factorials modulo a prime that divides them. The integral odd-chart matrices and the dyadic matrices over \(\mathbb Z_{(2)}\) retain the coefficient domains established earlier.

## Read the packet matrix as an infinite block operator

The earlier two-by-two matrix has formal series as entries. It also represents an infinite matrix of scalar coefficients. To see the relation, write

\[
g(x)=\sum_{n\geq0}\frac{(-1)^n x^n}{(2n)!}
=C(x^2)+xD(x^2),\qquad x=t^2.
\]

Group the coefficients of any \(f(x)=\sum f_nx^n\) into two packets:

\[
\Pi f=\left(\sum_{j\geq0}f_{2j}u^j,
\sum_{j\geq0}f_{2j+1}u^j\right),\qquad u=x^2.
\]

The scalar multiplication operator becomes

\[
\boxed{
\Pi\mathsf L_x(g)\Pi^{-1}
=\begin{pmatrix}
\mathsf L_u(C)&\mathsf L_u(uD)\\
\mathsf L_u(D)&\mathsf L_u(C)
\end{pmatrix}.}
\]

Here each block is an ordinary coefficient Toeplitz operator in its indicated variable. The formula follows by multiplying \((C+xD)(A+xB)\) and assigning its even and odd powers of \(x\) to the two packets. Each scalar row in each block has finite support. The top-right block starts one degree later because of the factor \(u\).

For the first two coefficients of each packet, use the vector order \((f_0,f_2,f_1,f_3)^T\). The block matrix is

\[
\begin{pmatrix}
1&0&0&0\\
\frac1{24}&1&-\frac12&0\\
-\frac12&0&1&0\\
-\frac1{720}&-\frac12&\frac1{24}&1
\end{pmatrix}.
\]

The entry \(-1/2\) in row two, column three is the first returning carry. The corresponding entry in row one is zero. For the secant input, \([u^0]B=1/2\), so this carry contributes \(-1/4\) to the order-\(u\) first output. It is exactly the interaction missing in the earlier coarse calculation.

For \(h\geq1\), retaining \(h\) coefficients in each packet is exactly the quotient calculation modulo \(u^h\), or modulo \(x^{2h}\) before regrouping. Thus the two-by-two formal matrix and its infinite scalar block operator describe the same operation at their stated resolutions.

## Keep the congruential family and its address visible

There is another kind of base change in the Euler work: changing the family index or its address. Paper IX defines normalized congruential coefficients by

\[
\left(j!\sum_{n\geq0}\frac{t^{Nn}}{(Nn+j)!}\right)^{-1}
=\sum_{n\geq0}C_{N,j}(n)\frac{t^{Nn}}{(Nn)!},
\quad N\geq1,\quad0\leq j<N.
\]

The normalization makes \(C_{N,j}(0)=1\). Removing it gives the original coefficients \(U_{N,j}(n)=j!C_{N,j}(n)\), whose constant is \(j!\).

Clearing factorials gives an infinite triangular system:

\[
\sum_{q=0}^n\binom{Nn+j}{Nq}C_{N,j}(q)=\delta_{n0}.
\]

Its diagonal entry is \(\binom{Nn+j}{Nn}\). Unlike the unit diagonals of the local coefficient matrices, this need not be one. Its divisibility determines where denominators can enter.

For the first nonconstant coefficient,

\[
C_{N,j}(1)=-\binom{N+j}{N}^{-1}.
\]

At \(N=4\), the four addresses give \(-1,-1/5,-1/15,-1/35\). In particular, the address-one coefficient can be reduced modulo powers of two using its odd denominator, but cannot be treated as an integral residue modulo five.

A general denominator bound follows directly from the triangular recurrence. Put

\[
D_{N,j}(n)=\prod_{r=1}^n\binom{Nr+j}{Nr}.
\]

Then \(D_{N,j}(n)C_{N,j}(n)\) is an integer. For the induction step, \(D_{N,j}(n-1)\) clears every earlier coefficient's denominator, and the next diagonal factor clears the division in the recurrence. The empty product at \(n=0\) is one.

Two specializations explain how this family meets the preceding example:

\[
C_{2,0}(n)=E_{2n},\qquad
C_{4,0}(n)=(-1)^nb_n.
\]

The second identity follows because the denominator is the earlier \(C(u)=\sum u^n/(4n)!\), while the quartic carrier denominator uses alternating signs. Consequently,

\[
(C_{4,0}(n))_{n\geq0}=(1,-1,69,-33661,60376809,\ldots).
\]

The coarse inverse \(C(u)^{-1}\) was a valid member of this different family. It failed when used as the classical Euler first packet, whose numerators are \(1,5,1385,2702765,\ldots\). Changing the family index does not automatically preserve the original sequence.

There is also a Bernoulli boundary address. At \(N=2,j=1\), the inverse is \(t/\sinh t\). If \(B(t)=t/(e^t-1)\), then a common-denominator calculation gives \(2B(t)-B(2t)=t/\sinh t\). Thus

\[
C_{2,1}(n)=(2-2^{2n})B_{2n}.
\]

This identifies another exact coefficient family while keeping its normalization and modular denominator obligations visible.

## Combine supercongruences with coprime moduli

A coordinate change can preserve a known modulus. Replacing that modulus by an unrelated one requires additional information. For example, 1 and 82 agree modulo 81 but differ modulo 25. There is no well-defined conversion of that residue class alone into a class modulo 25.

The odd and dyadic reconstructions supply the additional information here. The depth-one odd calculation gives \(E_8\equiv8\pmod{81}\). The row-specific dyadic error bound gives \(E_8\equiv9\pmod{32}\). Solve both conditions by writing

\[
x=9+32t,\qquad32t\equiv-1\pmod{81}.
\]

Since \(32\cdot38-81\cdot15=1\), the inverse of 32 modulo 81 is 38. Therefore

\[
t\equiv-38\equiv43\pmod{81},
\qquad x\equiv9+32\cdot43=1385\pmod{2592}.
\]

Any two solutions differ by a multiple of both 81 and 32, hence by their product 2592. The unique combined residue is 1385 modulo 2592. It agrees with the exact reconstruction already obtained. A residue alone would still need a separate size bound to identify an arbitrary integer uniquely.

We have now distinguished an exact change of source coordinates, a change of congruential family and address, and the combination of independent modular information. Each uses a different map and retains its own hypotheses.

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

## Conjugate sampling by the Pascal coefficient transform

The change from sequence values to Newton coefficients is another infinite matrix pair. Define lower-triangular matrices

\[
\mathsf P_{n,j}=\binom nj,\qquad
\mathsf Q_{n,j}=(-1)^{n-j}\binom nj
\quad(0\leq j\leq n),
\]

with zero entries for \(j>n\). For the value vector \(\boldsymbol a\) and difference vector \(\boldsymbol c\),

\[
\boldsymbol a=\mathsf P\boldsymbol c,
\qquad
\boldsymbol c=\mathsf Q\boldsymbol a.
\]

To verify the inverse, use \(\binom nj\binom jk=\binom nk\binom{n-k}{j-k}\). The \((n,k)\) entry of \(\mathsf P\mathsf Q\) becomes \(\binom nk\) times an alternating binomial sum. It vanishes for \(n>k\) and is one for \(n=k\). The same argument in the reverse order gives \(\mathsf Q\mathsf P=I\).

Let \(\mathsf R_{M,s}\) be the selector matrix whose row \(q\) has a single one in column \(Mq+s\). This is sampling in value coordinates. Sampling in difference coordinates is its Pascal conjugate:

\[
\boxed{\mathsf T_{M,s}=\mathsf Q\mathsf R_{M,s}\mathsf P.}
\]

The rightmost matrix reconstructs values. The middle one selects a lane. The leftmost one forms the lane's differences. Row \(k\) of the product is finite because \(\mathsf Q\) uses only rows \(0,\ldots,k\), the selector reaches at most \(Mk+s\), and \(\mathsf P\) uses only the preceding input columns.

Its entries are

\[
\begin{aligned}
(\mathsf T_{M,s})_{k,j}
&=\sum_{q=0}^k(-1)^{k-q}\binom kq\binom{Mq+s}{j}\\
&=[z^j](1+z)^s\bigl((1+z)^M-1\bigr)^k.
\end{aligned}
\]

Thus the infinite matrix product recovers exactly the previously derived kernel, including its offset and finite support.

For \(M=2,s=0\), the opening rows are

\[
\mathsf T_{2,0}=
\begin{pmatrix}
1&0&0&0&0&0&0&\cdots\\
0&2&1&0&0&0&0&\cdots\\
0&0&4&4&1&0&0&\cdots\\
0&0&0&8&12&6&1&\cdots\\
\vdots&\vdots&\vdots&\vdots&\vdots&\vdots&\vdots&\ddots
\end{pmatrix}.
\]

This matrix is row-finite but is not lower triangular. Its third row needs five input difference coefficients. For the Euler data,

\[
\begin{pmatrix}
1&0&0&0&0\\
0&2&1&0&0\\
0&0&4&4&1
\end{pmatrix}
\begin{pmatrix}1\\-2\\8\\-80\\1664\end{pmatrix}
=\begin{pmatrix}1\\4\\1376\end{pmatrix}.
\]

Cutting the matrix down to three columns instead would give \((1,4,32)^T\). The missing contribution to the third output is

\[
4c_3+c_4=-320+1664=1344,
\qquad32+1344=1376.
\]

In general, outputs through difference order \(K\) require input coefficients through index \(MK+s\). The correct finite calculation therefore uses \(K+1\) rows and \(MK+s+1\) columns. A square cutoff is valid for the earlier lower-triangular coefficient transforms. It cannot be applied to a sampling matrix without checking this larger support.

There is a further infinite-matrix distinction. Every square leading block of \(\mathsf T_{2,0}\) is upper triangular with diagonal \(1,2,4,8,\ldots\), so it is invertible over \(\mathbb Q\). Nevertheless, the infinite operator is not injective on arbitrary coefficient sequences. Consider

\[
\boldsymbol v=(0,-2,4,-8,16,-32,\ldots)^T,
\qquad v_j=(-2)^j\quad(j\geq1).
\]

Its first output is zero because \(v_0=0\). For every row \(k\geq1\), the constant kernel coefficient is zero, so the remaining finite sum can be evaluated as a polynomial:

\[
(\mathsf T_{2,0}\boldsymbol v)_k
=K_{2,0,k}(-2)
=\bigl(2(-2)+(-2)^2\bigr)^k=0.
\]

Thus a nonzero infinite vector lies in the kernel, despite all those nonsingular square blocks. Its later coordinates supply cancellations that a square cutoff discards. This vector is the difference-coordinate form of the bounded signal \((-1)^n-1\), whose even samples are all zero. We will return to that signal below.

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

The same equality holds in difference coordinates. The Pascal conjugation makes it

\[
\mathsf T_{L,r}\mathsf T_{M,s}
=\mathsf Q\mathsf R_{L,r}(\mathsf P\mathsf Q)\mathsf R_{M,s}\mathsf P
=\mathsf T_{ML,s+Mr}.
\]

All matrices here are row-finite, so their products can be associated using finite sums. To verify the same identity directly from the kernels, substitute \((1+z)^M-1\) for the difference variable of the second transfer and multiply its offset factor by \((1+z)^s\). The product is

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

## Compare the residuals at three and five

The next difference coordinate of the Euler sequence is

\[
\begin{aligned}
c_5
&=a(5)-5a(4)+10a(3)-10a(2)+5a(1)-a(0)\\
&=-50521-6925-610-50-5-1=-58112.
\end{aligned}
\]

At spacing three, the operator is

\[
S^3-I=\Delta^3+3\Delta+3\Delta^2.
\]

Its Euler output is

\[
a(3)-a(0)=-80+3(-2)+3(8)=-80+18=-62.
\]

The residual 18 has valuation \(v_3(18)=2\). Thus omitting it happens to preserve this output modulo nine. It fails modulo 27. The extra factor of three comes from the particular input values, since \(c_1+c_2=6\). The operator coefficients alone guarantee only the explicit factor three.

At spacing five,

\[
S^5-I=\Delta^5+5\Delta+10\Delta^2+10\Delta^3+5\Delta^4.
\]

The correction is

\[
5(-2)+10(8)+10(-80)+5(1664)
=-10+80-800+8320=7590.
\]

Therefore

\[
a(5)-a(0)=-58112+7590=-50522,
\]

which agrees with \(-50521-1\). Here \(v_5(7590)=1\), so the discarded residual is already visible modulo 25. Its residue there is 15.

These examples distinguish a divisibility statement about the transfer polynomial from an additional cancellation in one Euler row. Both can be calculated exactly, but they are separate pieces of information. The local reconstruction ladders proved earlier concern different operators and retain their own hypotheses.

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

## See what a single sampled lane forgets

A small bounded signal makes the sampling issue visible without the growth of the Euler numbers. Compare

\[
x(n)=(-1)^n,\qquad y(n)=1\quad(n\geq0).
\]

Their even lanes agree:

\[
R_{2,0}x=R_{2,0}y=(1,1,1,\ldots).
\]

Their odd lanes are different: \(R_{2,1}x=(-1,-1,\ldots)\), while \(R_{2,1}y=(1,1,\ldots)\). Consequently, knowing the even lane alone does not determine the even lane after a one-step shift of the original signal.

More explicitly, set \(v=x-y\) and \(f=R_{2,0}\). Then

\[
f(v)=0,\qquad f(Sv)=(-2,-2,\ldots)\ne0.
\]

This is the same kind of kernel obstruction that appeared when we discarded the second formal-series packet. An operator on the retained data alone could not send the same zero input to both of these outputs.

Retaining both phases repairs the representation. Write \(b_0=R_{2,0}x\) and \(b_1=R_{2,1}x\). A unit shift of the original signal sends the pair to

\[
(b_0,b_1)\longmapsto(b_1,S_qb_0).
\]

Two such operations give \((S_qb_0,S_qb_1)\), as required for an original shift by two. The advance of the lane index is part of this two-phase transfer.

Finally, \((S^2-I)x=0\), because \(x(n+2)=x(n)\). The filter cannot detect this alternating mode at that spacing. This is its zero at frequency \(\omega=\pi\), evaluated on an actual bounded signal. The statement concerns the filter and the retained phases, with no Fourier transform assigned to the Euler sequence.

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
Odd-length and dyadic reconstructions: E_8 = 1385
Dyadic E_8 tail valuations: 5, 8, 13, 15, exact
Matrix checks: inverse, composition, factorial normalization, packets, Pascal sampling
Sampling cutoff control: 3 columns give 32; 5 columns give 1376
Base changes: exact cocycle; prime-dependent precision checked
Supercongruence combination: 8 mod 81 and 9 mod 32 give 1385 mod 2592
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

You can also inspect the published [coefficient table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/euler-coefficients.csv), [parameter-polynomial table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/power-polynomials.csv), [local reconstruction and error table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/local-reconstruction.csv), [matrix-entry table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/coefficient-matrices.csv), [supercongruence table](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/congruence-ladders.csv), [exact results](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/results.json), and [source identities](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/source-record.json).

The matrix table contains twelve-by-twelve blocks of each forward and inverse local transform for charts 2, 3, 5 and 7, the Pascal pair, the displayed three-by-five sampling block, and five-by-five base changes from chart three to charts five and two. These finite tables can be inspected entry by entry. The formulas and proofs above define the infinite operators.

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
| Alternating powers | Direct finite sums against telescoped Euler-polynomial values | Degrees 0–12, lengths 0, 1, 2, 3, 5, 6, and starts \(-1/2,0,1,3/2\) |
| Local Euler charts | Direct power sums or rational sources against formal-series multiplication, reconstruction, and inverse transfer | Charts 1, 2, 3, 5, 7, 9, every even degree 0–20 |
| Local precision | Every finite depth against the exact tail, plus the Bernoulli kernel and first omitted dyadic row | Prime charts 2, 3, 5, 7 through degree 20, sharp dyadic depths 0–9 |
| Infinite coefficient transforms | Both inverse orders, kernel composition, factorial conjugation, and compatible leading blocks | Twelve-by-twelve local blocks, charts 2, 3, 5, 7 |
| Packet block operator | Entrywise comparison with regrouped scalar multiplication | Six coefficients per packet, modulo \(x^{12}\) |
| Pascal sampling | Selector conjugation against polynomial kernels and direct Euler lanes | Spacings 1–3, every lane, orders 0–3, all required input columns |
| Local base changes | Source-vector transfer, every chart triple's composition, and coefficient-domain controls | Charts 2, 3, 5, 7, every eight-by-eight block |
| Supercongruences | Exact partial-sum residues, the precision-loss witness, and coprime combination | Displayed \(E_8\) ladders, modulo 81 and 32 combination |
| Congruential families | Ordinary inversion against the triangular recurrence and denominator clearing | \(N=1,\ldots,6\), every address, indices 0–8 |
| Sequence transfer | Direct sampled differences against polynomial kernels | Spacings 1–5, every lane, orders 0–5, three specified integer sequences |
| Refinement composition | Every coefficient of composed and direct kernel rows | Both spacings 1–4, every lane, orders 0–3 |
| Prime residuals | Integer polynomial coefficients and application to the three sequences | Primes 2, 3, 5, 7, and 11 |

The permutation control uses a different definition of the numbers. At length \(m\), keep the number of admissible permutations ending at each possible rank. If the next comparison is an ascent, sum the preceding counts below the new rank. For a descent, sum those at or above it. Repeating the prescribed pattern gives the total. The program also enumerates the small permutation sets directly to check this dynamic program. It does not infer a universal enumeration theorem from those samples.

The [bounded run manifest](../../verification/euler-packets/run-003/manifest.json) records the command, Python version, source hashes before and after execution, time limit, observed completion, and result hashes. The [matrix and coefficient-transform self-review](../../verification/euler-packets/PROOF_REVIEW_MATRICES.md) links the preceding proof reviews and checks the added arguments separately. There is no new Lean run for this example.

A separate check compares 605 reciprocal coefficient values with the pinned Komorebi Math source, using both its integer sequence API and its logarithmic reciprocal-power implementation. It also makes 1,012 comparisons in the local Euler charts: 220 source, kernel and reconstruction values, 528 truncation values and errors, and 264 row weights, across prime charts 2, 3, 5 and 7 through ordinary degree twenty. Its [comparison record](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/library-comparison.json) retains the source identity and declared ranges.

That supplementary checker also verifies twelve complete rows of the infinite sampling-kernel witness and 18 Euler index-shift supercongruences, for primes 3, 5 and 7 with even starting degree 2–12. It retains the failing degree-zero boundary as a negative control. The universal statements have the written proofs above.

## What the example establishes

The written calculation gives exact reciprocal recurrences, the two-packet multiplication law and its coarsening obstruction, the quartic reconstruction and enumeration identities, reciprocal parameter polynomials, Euler-polynomial power sums, odd-length and dyadic local supercongruences, infinite coefficient matrices and inverse transforms, prime-dependent base changes, congruential families with explicit addresses, coprime modular reconstruction, formal residual correction, and sequence-refinement kernels with their Pascal conjugation, composition and prime correction.

The finite program checks implementations of these laws in its declared ranges. Its deliberately wrong controls expose missing carry factors, wrong factorial normalization, discarded residuals, and an invalid composite-number generalization.

The role of Komorebi is visible in the intermediate objects. A packet that appears dispensable at one resolution is needed by the next operation. A residual identifies the lost interaction. A transfer matrix reconstructs the original coefficients through a different carrier. A polynomial kernel moves the resulting sequence into sampled coordinates, and a second residual records what a coarse congruence discards.

The method keeps the representation, operation, preserved data, and remaining defect together throughout the calculation. That is the concrete connection to [machine-native mathematics](../essays/MACHINE_NATIVE_MATHEMATICS.md). Establishing an advantage for an automated discovery system would additionally require a specified system and a controlled comparison.

## Sources and further reading

- [NIST DLMF, Euler numbers and polynomials](https://dlmf.nist.gov/24.2#ii), including the signed convention and polynomial generating function, and the [secant expansion](https://dlmf.nist.gov/4.19.E5).
- [NIST DLMF, von Staudt–Clausen theorem](https://dlmf.nist.gov/24.10.E1), for the precise Bernoulli denominator input in the dyadic kernel valuation.
- [OEIS A000364](https://oeis.org/A000364) and its [coefficient table](https://oeis.org/A000364/b000364.txt), for the positive secant sequence and offset.
- [OEIS A211212](https://oeis.org/A211212), for the quartic reciprocal sequence, and [A181985](https://oeis.org/A181985), for generalized alternating permutations.
- [Paper IV](../works/paper-iv.md), for cyclic denominators and reciprocal-power polynomials. The [sequence experiments](SEQUENCE_SHAPES.md) use the same exponential normalization.
- [Euler Signal Bridge](../works/euler-signal-bridge.md), for the existing finite-difference/FIR interface developed in greater detail here.
- [Paper III](../works/paper-iii.md), for the broader typed transfer and residual language, and [Paper IX](../works/paper-ix.md), for the odd-length and dyadic Euler reconstruction, sharp precision bounds, arithmetic packets, and local polynomial deformations.
- [Source and overlap notes](../../verification/euler-packets/SOURCES.md), [target and route record](../../verification/euler-packets/TARGET_AND_ROUTES.md), and [proof self-review](../../verification/euler-packets/PROOF_REVIEW.md).

[Back to the essay](../essays/MACHINE_NATIVE_MATHEMATICS.md) · [Explore the sequence graphs](SEQUENCE_SHAPES.md) · [All demonstrations](../DEMONSTRATIONS.md)
