# Supplemental exact regression and sharpness frontier

These two small supplemental runs use exact modular arithmetic at 1024-bit
precision, compute actual reciprocal coefficients through index 96, and
cross-check the initial coefficients by rational ordinary-series inversion.
All modular reciprocal denominators are odd. The earlier `run512` code and
manifest inputs were retained unchanged.

## Full four-address regression

`supplemental96/results.json` tests every nondecreasing mixed-step multiset of
length 1 through 5 from `{1,2,3,4,5,7,8,9}`, and every base index for which the
largest required coefficient is at most 96. There are 1,286 step multisets and
96,857 mixed-difference evaluations per address. All evaluations satisfy

\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k} C_j(n))
\ge k+v_2(k!)+\sum_i v_2(u_i)+(0,0,3,1)_j.
\]

For `j=0,1`, exact unit-step equality was also checked at every admissible
`n,k` with `n+k<=96`: 4,656 equalities per address, with no failure.

The proposed equality for arbitrary mixed steps fails. At the first nontrivial
order, with base zero and steps `(1,2)`, the actual exact values are

\[
\Delta_1\Delta_2 C_0(0)=-33728,\qquad
\Delta_1\Delta_2 C_1(0)=-150208/585.
\]

Both have valuation 6, whereas `k+v_2(k!)+sum_i v_2(u_i)=4`. Thus a universal
mixed-step equality without a parity condition is false.

Within this bounded domain, the leading bound is attained for `j=0,1` exactly
when `k` is odd or the number of odd steps is even. All mixed odd-step cases
attain it. The code records the observations and the first strict examples;
the computation itself does not prove this parity rule universally.

For `j=2`, the additional-bit bound

\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k} C_2(n))
\ge 2k+v_2(k!)+1+\sum_i v_2(u_i)
\]

passed 101,513 checks, including unit-step orders through 96. It is sharp at
order two, base zero: `Delta_1^2 C_2(0)=64/45`, of valuation 6.

## Paired filtration and homogeneous sharpness

`paired96/results.json` tests the stronger address-two estimate

\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k} C_2(n))
\ge 2k+v_2(k!)+\lfloor k/2\rfloor+\sum_i v_2(u_i).
\]

Its domain includes the mixed multisets above and all homogeneous steps
`1<=u<=16`, all orders `1<=k<=floor(96/u)`, and all admissible bases. All
111,996 checks pass; 31,922 attain equality. In particular:

| Order | Base and steps | Actual valuation | Paired bound |
|---:|---|---:|---:|
| 1 | base 0, step 1 | 4 | 2 |
| 2 | base 0, steps 1,1 | 6 | 6 |
| 4 | base 0, four unit steps | 13 | 13 |
| 8 | base 0, eight unit steps | 27 | 27 |
| 16 | base 0, sixteen unit steps | 55 | 55 |

The exact low-order witnesses include

\[
\Delta_1 C_2(0)=-16/15,\qquad
\Delta_1^2 C_2(0)=64/45,\qquad
\Delta_1^4 C_2(0)=71426048/69615.
\]

At address zero and one, the homogeneous exact law

\[
v_2(\Delta_u^k C_j(n))=k+v_2(k!)+k v_2(u),\qquad j=0,1,
\]

passes 15,139 checks per address in that domain.

The global constant surplus `(0,0,3,1)` is boundedly sharp at each address:
the first unit difference has valuations `(1,1,4,2)` at base zero. This does
not rule out stronger order-dependent estimates, as the address-two paired
bound demonstrates.

Both supplemental manifests passed hash validation. The runs took 0.76 and
0.19 seconds, respectively. They used no floating-point arithmetic or
randomness. A bounded pass remains evidence for a separate proof, and is not
a universal conclusion.

## Caution beyond the tested mixed-order frontier

The exact address-two unit-step Newton pattern does not extend to arbitrary
mixed steps by simply adding their valuations. Already at order six, base zero,
and steps `(1,1,1,1,1,2)`, independent rational inversion gives

\[
\Delta_1^5\Delta_2 C_2(0)
=-5425207419431026688/22207185,
\]

which has valuation 26. The unit-step value at order six has valuation 22, so
adding the one bit from the even step would incorrectly predict exact valuation
23. This explicit rational identity is a counterexample to that proposed exact
extension. It does not violate either lower-bound theorem. This additional
identity is recorded as a rational exploratory check outside the two bounded
manifest domains above.
