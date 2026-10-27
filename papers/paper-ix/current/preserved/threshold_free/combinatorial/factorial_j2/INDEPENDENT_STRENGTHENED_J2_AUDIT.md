# Independent audit of the strengthened factorial route

## Reviewed artifact and scope

Reviewed `../../measure/factorial_route.md`, specifically the elementary Bernoulli central-factorial lemma, its extension to mixed moments with powers of the symmetric Bernoulli umbra, the actual j=2 factorization, the stronger factorial estimate, and the three-bit positive-order surplus. Also checked the scaled-binomial transfer estimates used for j=1 and j=3. This is an independent mathematical audit, not a Lean compilation.

## Result

PASS for the elementary j=2 route and its stated consequences. No missing implication was found. The j=2 proof is self-contained and does not need the external Frobenius theorem. The j=0 route relies on the classical ordinary-Euler statement that the parent separately checked against its primary source; that source check was not repeated in this audit.

## Checks that carry the conclusion

1. The central-factorial polynomial is exact:

   `P_r(Z(Z+1))=prod_(a=0)^(r-1)(Z-a)(Z+a+1)=(2r)! binom(Z+r,2r)`.

   The Bernoulli EGF gives `L(binom(Z,j))=(-1)^j/(j+1)`. Finite Vandermonde and the rational beta identity therefore give exactly

   `L(P_r)=(-1)^r(r!)^2/(2r+1)`.

2. The integer expansion `X^m=sum_r T(m,r)P_r(X)` and recurrence

   `T(m+1,r)=T(m,r-1)+r(r+1)T(m,r)`

   imply `v_2(T(m,r))>=m-r`. After division by m!, each nonzero evaluated term has valuation at least

   `r+s_2(m)-2s_2(r)>=0`.

   The inequality holds since `s_2(m)>=1` for m>0 and `r>=2s_2(r)-1` for r>=1. The m=0 case is separately 1. Thus all `L(X^m/m!)` are integral.

3. With symmetric Bernoulli umbra `B=2Z+1`, `P=(B^2-1)/4`, every even power of B reduces to an integral polynomial in P, using `B^2=1+4P`. Multiplying by gamma_m(P) uses only the integral divided-power product coefficient binom(m+r,m). Every odd B power times a polynomial in P evaluates to zero by the even EGF t/sinh(t). Consequently the required mixed moments `L(B^ell gamma_m(P))` really are integral; the lemma does not only handle ell=0.

4. The actual address-two factorization and the algebraic identity

   `(U^4-1)/4=P+Q-P^2-Q^2+6PQ+iBD(P-Q)`

   are exact with a=(1+i)/2, b=(1-i)/2, U=aB+bD. Every summand has integral divided powers. For example

   `gamma_k(P^2)=[(2k)!/k!] gamma_(2k)(P)`

   and `gamma_k(6PQ)=6^k k! gamma_k(P)gamma_k(Q)`.

   The adjoining relations B^2=1+4P and D^2=1+4Q permit reducing all ordinary powers without introducing denominators. Thus the functional is integral on the entire needed divided-power algebra.

5. The resulting bound

   `v_2(Delta_1^k C_2(n))>=2k+v_2(k!)`

   holds for every natural starting row via the finite expansion U^(4n)=(1+(U^4-1))^n. There is no boundary restriction k<=n.

6. The actual recurrence gives C_2(0)=1, C_2(1)=-1/15, C_2(2)=13/45, and hence a_1=-16/15, a_2=64/45 with valuations 4 and 6. For m>=3, the stronger estimate gives a_m valuation at least 2m+v_2(m!). The exact finite Newton formula for Delta_1^k C_2(n) then proves

   `v_2(Delta_1^k C_2(n))>=k+v_2(k!)+3`, k>=1.

   At k=1 and k=2, the low coefficients and the tail valuation at least 7 provide the required bounds 4 and 6. At k>=3, 2k>=k+3 directly settles the surplus.

7. The finite mixed-step polynomial expansion retains the surplus: every involved ordinary difference order m is at least k, the coefficient 2^m b_m supplies k+sum v_2(H_i), and m! supplies at least v_2(k!). Thus

   `v_2(Delta_(H_1)...Delta_(H_k) C_2(n))>=k+v_2(k!)+sum_i v_2(H_i)+3`, k>=1.

   The stronger no-fixed-surplus bound can also be stated as

   `v_2(Delta_(H_1)...Delta_(H_k) C_2(n))>=2k+v_2(k!)+sum_i v_2(H_i)`.

   This follows by expanding each `(1+4W)^(H_i)-1`: its coefficients are divisible by 2^(2+v_2(H_i)).

8. The scaled-binomial transfer estimate is valid. For `P_i(n)=4^i binom(4n,4i)`, each degree-d coefficient has valuation at least d+1, by counting the even factors in the first-kind Stirling coefficient. Therefore its kth differences have valuation at least k+v_2(k!)+1, including the separate order-zero bound. The infinite transfer sums converge uniformly because the reciprocal factor coefficients h_i are divisible by 4^i. Continuous interpolation correctly supplies C_0(n-i) and C_2(n-i) beyond the original natural domain, so there is no hidden cutoff error.

## Claim boundary

The review establishes the stated lower bounds, analyticity consequences obtainable from factorial Mahler divisibility, and the validity of the j=2 three-bit surplus. It does not establish exact valuations for every higher order or resolve the distinct Euler-tail stationary nonvanishing problem. The previous counterexample to a generic divided negative-eigenvalue inverse lemma remains valid; the new proof avoids that false lemma.
