"""Higher-order differential Hankel calculus for arbitrary polynomial weights.

Author: Komorebi P.

Let F_P[x^(2m)] = P(m)*binom(2m,m), F_P[x^(2m+1)] = 0,
and L[p] = sum_k c[k] F_P[p^(k)]. P uses falling-factorial
coefficients a[d]. Calculations use exact Fraction arithmetic.

Every strictly separated off-diagonal Chebyshev Gram block has rank
at most 2*(degree(P)+order(L)). The determinant solver uses that
constant-width representation and exact block lookahead for singular
leading minors. This is an arithmetic-operation statement, not a
fixed-bit complexity claim.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial

from sequence_polynomial_hankel import (
    _weights, _mul_linear_factors, _inverse_and_det,
    falling_integer, power_to_falling,
)


def _operator(coefficients):
    return _weights(coefficients)


@lru_cache(maxsize=None)
def chebyshev_derivative_polynomial(d, k):
    """Ascending coefficients b_h of t*sum_h b_h*t^(2h).

    For n>0 with n == k (mod 2), this equals F_d[C_n^(k)].
    The k=d=0 case vanishes for positive n. C_0=2 is exceptional.
    """
    if not isinstance(d, int) or not isinstance(k, int) or d < 0 or k < 0:
        raise ValueError("Derivative order and falling weight must be nonnegative integers")
    if d == k == 0:
        return (Fraction(0),)
    if k == 0:
        squares = [(2*j)**2 for j in range(1,d)]
    elif k % 2:
        half = (k-1)//2
        squares = [v for j in range(1, half+1)
                   for v in ((2*j-1)**2, (2*j-1)**2)]
        squares += [(2*j-1)**2 for j in range(half+1, half+d+1)]
    else:
        half = k//2
        squares = [0] + [v for j in range(1,half)
                         for v in ((2*j)**2, (2*j)**2)]
        squares += [(2*j)**2 for j in range(half, half+d)]
    denominator = 4**(d+k-1)*factorial(d+k-1)
    return tuple(Fraction(value,denominator)
                 for value in _mul_linear_factors(tuple(squares)))


def _odd_value(coefficients, n):
    return sum(a*n**(2*j+1) for j,a in enumerate(coefficients))


def chebyshev_derivative_moment(n, d, k):
    """F_d[C_n^(k)] for n>=0, with parity and endpoint exceptions."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("Chebyshev index must be a nonnegative integer")
    if n == 0:
        return Fraction(2) if d == k == 0 else Fraction(0)
    if n < k or (n-k)%2:
        return Fraction(0)
    return _odd_value(chebyshev_derivative_polynomial(d,k),n)


def derivative_monomial_moment(n, weights, differential):
    """L[x^n] by direct differentiation of a monomial."""
    if n < 0:
        return Fraction(0)
    a = _weights(weights)
    c = _operator(differential)
    total = Fraction(0)
    for k, coeff in enumerate(c):
        if not coeff or k > n or (n-k)%2:
            continue
        m=(n-k)//2
        mass=sum(a[d]*falling_integer(m,d) for d in range(len(a)))
        total+=coeff*falling_integer(n,k)*mass*comb(2*m,m)
    return total


@lru_cache(maxsize=None)
def chebyshev_jet_polynomials(weights, differential):
    """Return the even-k and odd-k aggregated odd Chebyshev polynomials."""
    a = _weights(weights)
    c = _operator(differential)
    even,odd=[],[]
    for d,weight in enumerate(a):
        if not weight:continue
        for k,coefficient in enumerate(c):
            if not coefficient:continue
            poly=chebyshev_derivative_polynomial(d,k)
            target=odd if k%2 else even
            if len(target)<len(poly):
                target.extend(Fraction(0) for _ in range(len(poly)-len(target)))
            for h,value in enumerate(poly):
                target[h]+=weight*coefficient*value
    return tuple(even),tuple(odd)


def chebyshev_jet_gram_entry(i, j, weights, differential):
    """L[C_i*C_j], including the exceptional C_0=2 normalisation."""
    if i < 0 or j < 0:
        raise ValueError("Gram indices must be nonnegative")
    a = _weights(weights)
    c = _operator(differential)
    even,odd=chebyshev_jet_polynomials(a,c)
    if i==j==0:
        return 4*a[0]*c[0]
    if i==j:
        return 2*a[0]*c[0]+_odd_value(even,2*i)
    branch=even if (i-j)%2==0 else odd
    return _odd_value(branch,i+j)+_odd_value(branch,abs(i-j))


def chebyshev_jet_generators(weights, differential, size):
    """u_i, v_i, diagonal; G_ij = u_i dot v_j for i>j."""
    if not isinstance(size,int) or size<0:
        raise ValueError("Matrix size must be nonnegative")
    a = _weights(weights)
    c = _operator(differential)
    D,R=len(a)-1,len(c)-1
    width=D+R
    even,odd=chebyshev_jet_polynomials(a,c)
    rows,cols,diag=[],[],[]
    for i in range(size):
        A=[2*sum(even[h]*comb(2*h+1,2*k)*i**(2*h+1-2*k)
                 for h in range(k,len(even))) for k in range(width)]
        B=[2*sum(odd[h]*comb(2*h+1,2*k)*i**(2*h+1-2*k)
                 for h in range(k,len(odd))) for k in range(width)]
        sign=(-1)**i
        rows.append([(A[k]+B[k])/2 for k in range(width)]+
                    [sign*(A[k]-B[k])/2 for k in range(width)])
        cols.append([Fraction(i**(2*k)) for k in range(width)]+
                    [Fraction(sign*i**(2*k)) for k in range(width)])
        diag.append(4*a[0]*c[0] if i==0
                    else 2*a[0]*c[0]+_odd_value(even,2*i))
    return rows,cols,diag



def _polynomial_product(a,b):
    """Multiply polynomials in ascending coefficient order, exactly."""
    result=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            result[i+j]+=x*y
    return result


def _trim_polynomial(values):
    values=list(values)
    while len(values)>1 and values[-1]==0:
        values.pop()
    return tuple(values)


def algebraic_moment_generating_function(weights, differential):
    """Return (numerator coefficients, twice denominator exponent).

    M(z)=sum_(n>=0) L[x^n] z^n
        =R(z)/(1-4*z**2)**(exponent_twice/2).
    deg R <= exponent_twice - 1 = 2*(degree P + order D).
    The base numerator and each derivative transform are exact rationals.
    No determinant is evaluated.
    """
    a=_weights(weights)
    c=_operator(differential)
    degree=len(a)-1
    order=len(c)-1
    h=[Fraction(1),Fraction(0),Fraction(-4)]
    powers=[[Fraction(1)]]
    for _ in range(max(degree,order)):
        powers.append(_polynomial_product(powers[-1],h))
    numerator=[Fraction(0)]*(2*degree+1)
    for d,coefficient in enumerate(a):
        if not coefficient:
            continue
        monomial=[Fraction(0)]*(2*d)+[
            coefficient*Fraction(factorial(2*d),factorial(d))]
        term=_polynomial_product(monomial,powers[degree-d])
        for j,value in enumerate(term):
            numerator[j]+=value
    # T[A](z)=z(A(z)+zA'(z)). Repeated T maps moments to
    # falling-factorial monomial derivatives.
    total=[Fraction(0)]*(2*(degree+order)+1)
    for k in range(order+1):
        shifted=_polynomial_product(numerator,powers[order-k])
        for j,value in enumerate(shifted):
            total[j]+=c[k]*value
        if k==order:
            break
        nxt=[Fraction(0)]*(len(numerator)+3)
        for j,value in enumerate(numerator):
            nxt[j+1]+=(j+1)*value
            nxt[j+3]+=4*(2*degree+2*k-j)*value
        numerator=list(_trim_polynomial(nxt))
    result=_trim_polynomial(total)
    exponent_twice=2*(degree+order)+1
    if len(result)>exponent_twice:
        raise ArithmeticError("Algebraic generating numerator exceeded the degree bound")
    return result,exponent_twice


def algebraic_moment_differential_equation(weights,differential):
    """Return A(z), B(z) such that A(z)*M'(z)=B(z)*M(z).

    For R(z)/(1-4z^2)**beta, A=(1-4z^2)*R and
    B=(1-4z^2)*R' + 8*beta*z*R.
    If the moment sequence vanishes, A=B=0 is a vacuous relation.
    A zero constant term in A may make the associated coefficient
    recurrence singular: use the recorded initial moments, not division
    by A(0), to recover the sequence.
    """
    numerator,twice_exponent=algebraic_moment_generating_function(
        weights,differential)
    h=(Fraction(1),Fraction(0),Fraction(-4))
    deriv=[j*numerator[j] for j in range(1,len(numerator))]
    if not deriv:
        deriv=[Fraction(0)]
    A=_polynomial_product(numerator,h)
    B=_polynomial_product(deriv,h)
    B+=([Fraction(0)]*(len(A)-len(B)))
    for j,value in enumerate(numerator):
        B[j+1]+=4*twice_exponent*value
    return _trim_polynomial(A),_trim_polynomial(B)


def first_nonzero_moment(weights, differential):
    """Return (first moment index, nonzero moment) or None."""
    a = _weights(weights)
    c = _operator(differential)
    if not any(a) or not any(c):
        return None
    nu=next(j for j,value in enumerate(a) if value)
    kappa=next(j for j,value in enumerate(c) if value)
    index=2*nu+kappa
    mass=c[kappa]*a[nu]*Fraction(factorial(index),factorial(nu))
    return index,mass


def structured_differential_hankel(weights, differential, max_size):
    """Every exact leading Hankel determinant W_0,...,W_max_size.

    The Schur state has width 2*(deg(P)+operator order).
    Zero leading minors are retained and recovered through exact
    nonsingular block lookahead. The direct full Hankel matrices
    are not formed except the first necessarily invertible block.
    """
    if not isinstance(max_size,int) or max_size<0:
        raise ValueError("Maximum size must be a nonnegative integer")
    a=_weights(weights)
    c=_operator(differential)
    result=[Fraction(1)]+[Fraction(0)]*max_size
    first=first_nonzero_moment(a,c)
    if first is None:
        return result
    ell,mass=first
    initial_size=ell+1
    if max_size<initial_size:
        return result

    rows,cols,diagonal=chebyshev_jet_generators(a,c,max_size+1)
    width=len(rows[0])
    def gram(i,j):
        return diagonal[i] if i==j else chebyshev_jet_gram_entry(i,j,a,c)

    initial=[[gram(i,j) for j in range(initial_size)]
             for i in range(initial_size)]
    determinant,inverse=_inverse_and_det(initial)
    if not determinant:
        raise ArithmeticError("The first nonzero Hankel block is unexpectedly singular")
    expected=(-1)**(ell*(ell+1)//2)*mass**initial_size
    if determinant/4!=expected:
        raise ArithmeticError("First nonzero Hankel determinant failed exact anti-diagonal check")
    result[initial_size]=expected

    solved=[[sum(inverse[i][j]*cols[j][q] for j in range(initial_size))
             for q in range(width)] for i in range(initial_size)]
    K=[[sum(cols[i][p]*solved[i][q] for i in range(initial_size))
        for q in range(width)] for p in range(width)]
    m=initial_size
    while m<max_size:
        for length in range(1,max_size-m+1):
            new=list(range(m,m+length))
            Ku=[[sum(K[p][q]*rows[index][q] for q in range(width))
                 for p in range(width)] for index in new]
            schur=[[gram(x,y)-sum(rows[x][p]*Ku[y-m][p]
                                  for p in range(width))
                    for y in new] for x in new]
            block_det,inverse_schur=_inverse_and_det(schur)
            if not block_det:
                continue
            w=[[Ku[index-m][p]-cols[index][p] for p in range(width)]
               for index in new]
            solved=[[sum(inverse_schur[k][ell]*w[ell][q]
                         for ell in range(length)) for q in range(width)]
                    for k in range(length)]
            K=[[K[p][q]+sum(w[k][p]*solved[k][q] for k in range(length))
                for q in range(width)] for p in range(width)]
            determinant*=block_det
            result[m+length]=determinant/4
            m+=length
            break
        else:
            break
    return result


if __name__ == "__main__":
    sample=structured_differential_hankel([1,1],[1,2,1],10)
    print("P(m)=1+m, D=1+2d/dx+d^2/dx^2")
    print([str(value) for value in sample])
