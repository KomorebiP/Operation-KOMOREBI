# Recurrence families and sequence transfers

These derivations use ordinary formal power series. A statement about a stored
prefix is identified separately from an identity of infinite formal series.
Classical sequences and derived parameter instances carry no claim of historical
novelty or pairwise distinctness.

## Generalized k-step coefficients

Fix integers k>=2, r>=1 and c>=1. Define

    A(z) = (1-c(z+z^2+...+z^k))^(-r) = sum a(n) z^n.

Thus a(0)=1. Differentiating D A' = -r D' A gives the exact recurrence

    n a(n) = c sum_(j=1)^min(k,n) (n+(r-1)j) a(n-j), n>=1.

For r=1 these are weighted k-step compositions. When c=1, the conventional
k-bonacci sequence T has k-1 initial zeros followed by one and
T(n;k)=a(n-k+1) for n>=k-1. The initial zero prefix must be retained when
comparing the two conventions.

The maintained source convention and finite binomial formula are in
[komorebi-math families.py](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/src/komorebi_math/sequences/families.py#L81).
The r,c extension below is derived here from that ordinary generating function.

Set H(m)=0 for m<0. Factoring the denominator gives

    A(z) = (1-z)^r / (1-(c+1)z+c z^(k+1))^r,
    a(n) = sum_(ell=0)^min(r,n) (-1)^ell binom(r,ell) H(n-ell),
    H(m) = sum_(j=0)^floor(m/(k+1))
           (-c)^j (r)_(m-kj) (c+1)^(m-(k+1)j)
           / (j! (m-(k+1)j)!).

Here (u)_j is the rising factorial, including (u)_0=1. Expand the denominator
first in c z^(k+1)/(1-(c+1)z). The coefficient of z^m has the displayed finite
range. The identity (r)_j (r+j)_h=(r)_(j+h) gives its numerator. Multiplication
by (1-z)^r proves the formula for every n, without an analytic convergence claim.
Integrality also follows from expanding the original denominator as r copies
of the geometric series with integer coefficients.

### Finite hypergeometric convention

For m>=0, let J=floor(m/(k+1)) and

    alpha_i=(i-m)/(k+1), i=0,...,k,
    beta_i=(i+1-r-m)/k, i=0,...,k-1,
    q=c (k+1)^(k+1)/((c+1)^(k+1) k^k).

Then the precise finite formula is

    H(m)=(c+1)^m (r)_m/m!
         sum_(j=0)^J product_i (alpha_i)_j / product_i (beta_i)_j * q^j/j!.

The ratio of consecutive summands agrees with the finite binomial formula,
and the j=0 values agree. One upper parameter is -J. A nonpositive integral
lower parameter is -floor((m+r-1)/k), whose first zero occurs strictly after J.
No denominator vanishes within the stated sum. This proves the finite formula
including m=0. Cancelling upper and lower parameters before applying the cutoff
can change that boundary value. An unrestricted analytic pFq evaluation is not
used by the exact generator.

The library enumerates k=2..16, r=1..4 and c=1..2: 120 parameter records. Each
stores 24 ordinary coefficients. The formulas describe the stated general
family; finite software checks validate only their recorded tested ranges.

## Ordinary convolution transfers

Let A and B be ordinary formal series over Q with nonzero constant terms.
There is a unique H=B/A in Q[[z]] such that H A=B. Its coefficients satisfy

    h(0)=b(0)/a(0),
    h(n)=(b(n)-sum_(j=0)^(n-1) h(j)a(n-j))/a(0).

The inverse kernel is K=A/B. Each convolution row is finite and HK=1. The
lower-triangular matrix L(H) has entry h(n-j) for j<=n and zero otherwise.
These identities prove the transfer on infinite formal series when the series
are specified. Calculating L coefficients from stored data proves the same
identities only modulo z^L. It does not determine unrecorded terms.

If the original streams have leading zero orders v and w, write them as z^v A
and z^w B with nonzero constant terms. The transfer includes the explicit shift
z^(w-v), together with H. Source and target anchors and original indices remain
part of the record. A window containing only zeros supplies no nonzero anchor
from which this unique unit transfer can be calculated.

The tail kernels are units. If v and w differ, the full shifted transfer is a
bijection between the corresponding prescribed-zero-prefix classes, not a unit
automorphism of all Q[[z]]. A negative power of z is applied only to a stream
with the required vanishing prefix. The tool retains these domain conditions.

Over Z, a nonzero constant need not be a unit. The tool therefore computes over
Q and reports whether both kernels are integral. It never rounds coefficients.
The inputs are treated as ordinary coefficient streams; original EGF or
compressed-Taylor normalization is not silently substituted.

## Euler and Fibonacci

The maintained [Euler derivation](../../docs/demonstrations/EULER_PACKETS.md#transfer-the-euler-sequence-to-fibonacci-values)
uses a(n)=E_(2n)=1,-1,5,-61,1385,... as ordinary coefficients and
b(n)=F_(n+1)=1,1,2,3,5,... . Define

    R(z)=(1-z-z^2) A(z), H(z)=1/R(z).

Then H A=1/(1-z-z^2). The first kernel values are
1,2,-1,53,-1200,46233. This is the source's reversible sequence transfer,
including its required Fibonacci shift.

The same source derives the transported operation. For the forward shift S,
epsilon_0 extracting the first coefficient and u(n)=h(n+1),

    S L(H)-L(H)S = u epsilon_0,
    L(H) S L(R) = S-u epsilon_0.

The source Euler stream has nonzero Fibonacci defects. Its homogeneous
Fibonacci recurrence is obtained only after carrying the transfer and inverse
with the operation. A finite truncated shift matrix has an additional far-edge
boundary; the tool does not identify it with the infinite operator formula.
