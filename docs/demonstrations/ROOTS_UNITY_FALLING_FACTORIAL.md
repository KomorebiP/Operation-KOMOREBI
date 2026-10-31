# Roots of unity, projectors, and falling-factorial coordinates

**An extended hand-worked example · Komorebi P.**

One polynomial will pass through a Fourier-style residue projector, a Newton/falling-factorial coordinate change, a finite-difference operation, and an exact refinement. We will keep the objects and operations separate. In particular, we will see why projecting *after* a change of coordinates requires transporting the projector, not reusing its old formula.

The mathematical identities are classical: the roots-of-unity filter, Stirling inversion, Newton interpolation, umbral polynomial coordinates, and the forward difference. The purpose of this example is to exhibit their precise composition and recovery conditions in the realization-and-transfer language of the collection. No new theorem, Lean compilation, general analytic continuation, or novelty claim is made here.

[Read the complete exact Python source](https://KomorebiP.github.io/Operation-KOMOREBI/read/roots-unity-falling-factorial.html) · [Download all source and results](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/source-and-results.zip) · [Review the generated exact diagram](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/projection-diagram.svg)

## 1. The destination: recover one ordinary power from three packets

Our fixed polynomial is

\[
f(x)=x^5.
\]

For a nonnegative integer \(k\), write the **falling factorial**

\[
x^{\underline{k}}=x(x-1)\cdots(x-k+1),
\qquad x^{\underline0}=1.
\]

The classical Stirling expansion reads

\[
\boxed{x^5
=x^{\underline1}+15x^{\underline2}
+25x^{\underline3}+10x^{\underline4}+x^{\underline5}.}
\]

We will separate those *falling-factorial degrees* into three congruence classes, then evaluate at \(x=4\).

The exact falling factorials at four are

| \(k\) | \(4^{\underline{k}}\) | \(S(5,k)\) | Weighted contribution |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 0 |
| 1 | 4 | 1 | 4 |
| 2 | 12 | 15 | 180 |
| 3 | 24 | 25 | 600 |
| 4 | 24 | 10 | 240 |
| 5 | 0 | 1 | 0 |

Group the weighted contributions by \(k\bmod3\):

\[
\begin{aligned}
r=0:&\quad 25(24)=600,\\
r=1:&\quad 1(4)+10(24)=244,\\
r=2:&\quad 15(12)+1(0)=180.
\end{aligned}
\]

Therefore

\[
\boxed{600+244+180=1024=4^5.}
\]

![Three exact residue packets after falling-factorial transport, with their values 600, 244 and 180 summing to 1024.](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/projection-diagram.svg)

[Download the complete coefficient and contribution table](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/packet-contributions.csv).

The remaining sections explain exactly which projector and coordinate map produce this calculation. They also exhibit a deliberately wrong operation.

## 2. Roots of unity: project onto residue degrees

Work over the polynomial ring \(\mathbb Q(\zeta_m)[z]\), where \(m\ge2\) and \(\zeta_m\) is a primitive \(m\)-th root of unity. For each \(0\le r<m\), define

\[
\boxed{
P_r^{(m)}g(z)=\frac1m\sum_{\ell=0}^{m-1}
\zeta_m^{-r\ell}g(\zeta_m^\ell z).
}
\]

This expression is a finite sum of polynomials. There is no analytic convergence issue.

Apply the operator to a monomial:

\[
P_r^{(m)}z^k
=\left(\frac1m\sum_{\ell=0}^{m-1}
\zeta_m^{(k-r)\ell}\right)z^k
=\begin{cases}
z^k,&k\equiv r\pmod m,\\
0,&k\not\equiv r\pmod m.
\end{cases}
\]

The inner sum is either \(m\), or the geometric series with nonunit ratio and total zero. Consequently, on rational polynomials the result has rational coefficients, despite the cyclotomic expression:

\[
P_r^{(m)}g(z)=
\sum_{k\equiv r\ (m)}[z^k]g(z)\,z^k.
\]

It follows immediately that

\[
P_rP_s=\delta_{rs}P_r,
\qquad
\sum_{r=0}^{m-1}P_r=I.
\]

These are complete, pairwise orthogonal *algebraic* projectors. Orthogonality here means \(P_rP_s=0\), not a claim about a particular inner product.

**Exact check without floating-point roots.** Let \(C\) be the cyclic permutation matrix of size \(m\). Its eigenvalues are precisely the \(m\)-th roots of unity and

\[
\frac1m\operatorname{tr}(C^{k-r})
=\begin{cases}1,&k\equiv r\pmod m,\\0,&\text{otherwise.}\end{cases}
\]

The standalone program verifies this equality using only integer counts of fixed coordinates of the cyclic permutation. This is an independent exact representation of the character filter, not a numerical evaluation of \(\zeta_m\).

## 3. The coordinate change is a linear map, not an algebra homomorphism

Define a \(\mathbb Q\)-linear map on polynomials by specifying its action on the monomial basis:

\[
\boxed{\Phi(z^k)=x^{\underline{k}}.}
\]

Because each falling factorial is monic of degree \(k\), this is a degree-preserving triangular linear isomorphism

\[
\Phi:\mathbb Q[z]\longrightarrow\mathbb Q[x].
\]

Do not read \(\Phi\) as evaluation at a particular \(z\). Its input and output variables name **different coordinate descriptions**.

The coefficients of the two triangular changes are the Stirling numbers:

\[
x^n=\sum_{k=0}^n S(n,k)x^{\underline{k}},
\]

and

\[
x^{\underline{k}}=\sum_{j=0}^k s(k,j)x^j,
\]

where \(s(k,j)\) are the signed Stirling numbers of the first kind. Therefore

\[
\boxed{\Phi^{-1}(x^n)=
\sum_{k=0}^nS(n,k)z^k.}
\]

For our fifth power,

\[
\Phi^{-1}(x^5)=
T_5(z)=z+15z^2+25z^3+10z^4+z^5,
\]

the fifth Touchard polynomial encountered in the [Stirling, Bell and Fubini demonstration](STIRLING_BELL_FUBINI.md).

Why is the word *linear* essential? Consider

\[
\Phi(z)^2=x^2
\qquad\text{but}\qquad
\Phi(z^2)=x(x-1).
\]

Thus

\[
\boxed{\Phi(z^2)\ne\Phi(z)^2.}
\]

We cannot transport multiplication through \(\Phi\) while pretending the product in the target is unchanged. We will construct the correct transported product in Section 8.

## 4. Transport the projector into falling-factorial coordinates

The projector acting on the ordinary polynomial \(f(x)\) is

\[
\boxed{
Q_r^{(m)}=\Phi P_r^{(m)}\Phi^{-1}.
}
\]

For a polynomial expanded as

\[
f(x)=\sum_{k=0}^d a_kx^{\underline{k}},
\]

this becomes the explicit finite operation

\[
\boxed{
Q_r^{(m)}f(x)=
\sum_{\substack{0\le k\le d\\k\equiv r\pmod m}}
a_kx^{\underline{k}}.
}
\]

Because \(\Phi\) is invertible, the transferred operators obey

\[
Q_rQ_s=\delta_{rs}Q_r,
\qquad \sum_{r=0}^{m-1}Q_r=I.
\]

This is the original projector system transported to a new basis, not a new numerical approximation.

For \(f(x)=x^5\) and \(m=3\), the three packets are

\[
\begin{aligned}
Q_0f&=25x^{\underline3},\\
Q_1f&=x^{\underline1}+10x^{\underline4},\\
Q_2f&=15x^{\underline2}+x^{\underline5}.
\end{aligned}
\]

Expanding them in ordinary powers makes the change of basis visible:

\[
\begin{aligned}
Q_0f&=25x^3-75x^2+50x,\\
Q_1f&=10x^4-60x^3+110x^2-59x,\\
Q_2f&=x^5-10x^4+35x^3-35x^2+9x.
\end{aligned}
\]

All unwanted powers cancel in the sum, giving exactly \(x^5\).

There is also a concrete matrix formula. Let

\[
M_{i,k}=s(k,i),\qquad
(M^{-1})_{k,j}=S(j,k)
\]

be the linear coordinate matrices in ascending ordinary-power order. Then

\[
\boxed{
[Q_r]_{\text{power}}
=M\,D_r\,M^{-1},
\qquad
(D_r)_{k,k}=\mathbf1_{k\equiv r\pmod m},
}
\]

so that, for \(i\le j\),

\[
\boxed{
[Q_r]_{i,j}=
\sum_{\substack{i\le k\le j\\k\equiv r\pmod m}}
s(k,i)S(j,k).
}
\]

The source-bound [matrix CSV](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/projector-matrix.csv) gives all three \(6\times6\) rational matrices for degrees zero through five. The checker also verifies these entries directly against independently computed finite differences.

### A wrong projector, with an exact witness

If we mistakenly apply the original degree-filter rule directly to \(x^5\) in the *ordinary-power basis*, we obtain

\[
P_0^{(3)}x^5=0,\qquad
P_1^{(3)}x^5=0,\qquad
P_2^{(3)}x^5=x^5.
\]

At \(x=4\), that allocates the entire value \(1024\) to residue two.

But the **correct transported packets** give \((600,244,180)\). In particular,

\[
\boxed{(P_2x^5)(4)=1024
\quad\ne\quad
(Q_2x^5)(4)=180.}
\]

Both projector systems are mathematically legitimate. They project different coordinate labels. The failure comes from changing the representation without changing the operation.

## 5. Newton differences give a second, independently computable inverse

Write the forward difference as

\[
(\Delta f)(x)=f(x+1)-f(x).
\]

The falling-factorial basis satisfies

\[
\boxed{\Delta x^{\underline{k}}
=kx^{\underline{k-1}}.}
\]

Iterating, evaluating at zero, and using \(0^{\underline{k}}=0\) for \(k>0\) gives the exact Newton coefficient formula:

\[
\boxed{
a_k=\frac{(\Delta^kf)(0)}{k!},
\qquad
f(x)=\sum_{k=0}^{d}\frac{(\Delta^kf)(0)}{k!}
x^{\underline{k}}
}
\]

for any polynomial \(f\in\mathbb Q[x]\) of degree at most \(d\).

This can be proved without Stirling numbers. It also reconstructs the same Stirling coefficients when \(f(x)=x^n\):

\[
\begin{aligned}
(\Delta^k x^n)(0)
&=\sum_{j=0}^k(-1)^{k-j}\binom kj j^n\\
&=k!S(n,k).
\end{aligned}
\]

The second equality counts surjections onto \(k\) labelled targets by inclusion and exclusion; it uses \(0^0=1\) in the usual polynomial-evaluation convention.

For the fifth power, the Newton coefficients are

\[
\left(\frac{\Delta^k x^5(0)}{k!}\right)_{k=0}^5
=(0,1,15,25,10,1).
\]

Thus the same coefficients have **three descriptions**: the Stirling triangle, the inverse linear map \(\Phi^{-1}\), and differences at zero.

The general transported projector can now be written without introducing an auxiliary variable:

\[
\boxed{
Q_r^{(m)}f(x)=
\sum_{\substack{k\le\deg f\\k\equiv r\pmod m}}
\frac{(\Delta^kf)(0)}{k!}\,x^{\underline{k}}.
}
\]

This is a finite, executable formula for every rational polynomial.

## 6. Transport differentiation: a cyclic finite-difference law

Let \(D_z=d/dz\). Since both operators lower their respective basis degrees in the same way,

\[
\Delta\Phi(z^k)
=kx^{\underline{k-1}}
=\Phi D_z(z^k).
\]

By linearity,

\[
\boxed{\Delta=\Phi D_z\Phi^{-1}.}
\]

Differentiation moves degree \(k\) to \(k-1\). Hence it moves residue \(r\) to \(r-1\), and

\[
\boxed{
\Delta Q_r^{(m)}
=Q_{r-1\pmod m}^{(m)}\Delta.
}
\]

In particular, \(\Delta^m\) commutes with every \(Q_r^{(m)}\).

For the fifth-power example, evaluate the differences of the *three correct packets* at \(x=4\):

| Original packet | Difference polynomial | Value at 4 | Target residue |
|---|---|---:|---:|
| \(Q_0f=25x^{\underline3}\) | \(75x^{\underline2}\) | 900 | 2 |
| \(Q_1f=x^{\underline1}+10x^{\underline4}\) | \(1+40x^{\underline3}\) | 961 | 0 |
| \(Q_2f=15x^{\underline2}+x^{\underline5}\) | \(30x^{\underline1}+5x^{\underline4}\) | 240 | 1 |

These add to

\[
900+961+240=2101=5^5-4^5
=(\Delta x^5)(4).
\]

The shift in packet address is part of the operator transfer. Comparing residues without that shift would conflate two different operations.

[Download the finite-difference transfer table](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/difference-transfer.csv).

## 7. Refine the same packets without changing their sum

The same congruence class modulo three splits into two disjoint classes modulo six:

\[
\boxed{
Q_r^{(3)}=Q_r^{(6)}+Q_{r+3}^{(6)},
\qquad r=0,1,2.
}
\]

On \(x^5\), the six child values at \(x=4\) are:

| Parent residue | Child \(r\) | Child \(r+3\) | Parent total |
|---:|---:|---:|---:|
| 0 | 0 | 600 | 600 |
| 1 | 4 | 240 | 244 |
| 2 | 180 | 0 | 180 |

The zeros are meaningful. The degree-zero coefficient of \(x^5\) is zero, and \(4^{\underline5}=0\).

More generally, if \(M\) is a multiple of \(m\),

\[
Q_r^{(m)}=
\sum_{q=0}^{M/m-1}Q_{r+mq}^{(M)}.
\]

This is exact address refinement, not an error-producing truncation. Discarding a child instead leaves the explicitly omitted polynomial, which can be evaluated or reconstructed exactly.

[Download the refinement table](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/refinement.csv).

## 8. Multiplication must also be transported

The linear change \(\Phi\) does not preserve ordinary polynomial multiplication. If we want multiplication in the Newton coordinate algebra to survive, define a *transported* product on \(\mathbb Q[x]\):

\[
\boxed{
f\star g=\Phi\bigl(\Phi^{-1}f\cdot\Phi^{-1}g\bigr).
}
\]

In particular,

\[
x^{\underline a}\star x^{\underline b}
=x^{\underline{a+b}},
\]

so

\[
x\star x=x(x-1)\ne x^2.
\]

This product is associative, commutative and unital because ordinary multiplication in \(\mathbb Q[z]\) has those properties. The transformed difference is a derivation **for \(\star\)**:

\[
\boxed{
\Delta(f\star g)
=(\Delta f)\star g+f\star(\Delta g).
}
\]

Residue packets now multiply by cyclic convolution:

\[
\boxed{
Q_r^{(m)}(f\star g)
=\sum_{\substack{0\le a,b<m\\a+b\equiv r\pmod m}}
(Q_a^{(m)}f)\star(Q_b^{(m)}g).
}
\]

For comparison, ordinary pointwise multiplication satisfies the **shifted** finite-difference product rule

\[
\Delta(fg)=(\Delta f)g+f(x+1)(\Delta g).
\]

The naive differential Leibniz rule fails even for \(f=g=x\):

\[
\Delta(x^2)=2x+1\ne2x.
\]

This is a useful boundary example. We can transport an operation exactly, but the transported operation need not be identical to the familiar operation on the target coordinates.

## 9. General scope and conditions

All statements above are exact for polynomials over \(\mathbb Q\), with integer modulus \(m\ge2\).

- The roots-of-unity formula uses a field containing \(m\)-th roots of unity and an invertible \(m\), but its output on \(\mathbb Q[z]\) is rational.
- The Newton inverse divides by \(k!\). It therefore cannot be transplanted unchanged to an arbitrary ring in which factorials fail to be units. In characteristic \(p\), the unrestricted polynomial isomorphism and ordinary Newton coefficient division require particular care.
- For functions on the nonnegative integers, Newton's formula recovers each fixed value through a finite sum up to that index. The polynomial isomorphism statement does **not** imply arbitrary analytic, \(p\)-adic, or infinite-series convergence.
- The forward difference is the transported derivative. Ordinary differentiation \(d/dx\) is a different operation.
- The transported product \(\star\) is not ordinary multiplication. Claims about multiplicative transport must name the product they use.

The program tests the general finite identities, not merely the displayed numerical example. It checks independent Stirling/finite-difference coefficient routes, inverse triangular matrices, idempotence and orthogonality, exact cyclic traces for moduli two through six, operator conjugation in ordinary-power matrices, finite-difference transport, refinements, transported multiplication and both deliberately incorrect shortcuts.

No assertion about an unrelated arithmetic conjecture follows from these finite polynomial identities.

## 10. Run, inspect, and reproduce

The complete Python program needs only Python 3.10 or later and its standard library. No network, symbolic algebra dependency, complex floating arithmetic, or random inputs are required.

From the repository root:

```text
python -B examples/roots_unity_falling_factorial.py
python -B examples/roots_unity_falling_factorial.py --output roots-results
```

The first command performs the exact checks and prints the three-packet reconstruction. The second also writes five exact CSV tables, one accessible Python-generated SVG, and a JSON summary. Existing output files are not overwritten. The publisher recreates the same files on the website and binds their hashes to the committed program and manuscript.

[Source-and-results ZIP](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/source-and-results.zip) · [Python source](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/roots_unity_falling_factorial.py) · [Source identity record](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/source-record.json) · [Exact results (JSON)](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/roots-unity-falling-factorial/results.json)

### The previous work this example connects

- [Factorial lanes](FACTORIAL_LANES.md) gives the general cyclotomic coefficient projector and distinguishes additive residue packets from multiplicative step-factorial lanes.
- [Euler numbers through packets](EULER_PACKETS.md) develops Newton/Pascal coordinate transformations, conjugated sampling, prime-sensitive difference estimates, and their genuine analytic boundaries.
- [Stirling, Bell and Fubini](STIRLING_BELL_FUBINI.md) develops the triangular inversion, formal exponential substitution, and coupled roots-of-unity packets.
- [Wavelets and polyphase transfer](WAVELET_POLYPHASE.md) illustrates the same requirement to transport the operation, including cross-channel terms that disappear in invalid shortcuts.
- [Paper IV](../works/paper-iv.md), [Paper IX](../works/paper-ix.md), and [Special Functions](../works/monographs-special-functions.md) provide the corresponding broader research contexts, each with its own hypotheses and verification evidence.

This calculation is intentionally a finite polynomial bridge. It does not import the proof status of those other works or claim to resolve their remaining questions.
