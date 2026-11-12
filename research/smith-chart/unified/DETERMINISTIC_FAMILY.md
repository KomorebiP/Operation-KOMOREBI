# Deterministic recognition of the certified families

**Result.** The local cubic certificate now supplies an executable construction,
without numerical rediscovery. Exact endpoint inversion extends that construction
to its lifted rational family. Every successful output is replayed by the retained
physical-graph certificate checker.

## The family being recognized

Let $A$ be the closed seven-dimensional rational coefficient box in
`solver/family.json`. Write its coordinates as

$$y=(P_0,P_1,P_2,P_3,Q_0,Q_1,Q_2),\qquad Q_3=1.$$

The uniform certificate proves that every real $y\in A$ has a unique component
root inside its specified positive box. Its Sylvester bound proves that every
target in $A$ has reduced degree three. Define $\mathcal F_3=A$ and

$$
\mathcal F_{n+1}=\{W_{g,L}(Z):Z\in\mathcal F_n,\ g,L>0\},\qquad
W_{g,L}(Z)=\left[g+\frac1{Ls+Z}\right]^{-1}.
$$

The interior recovers the previously proved open families. Including the faces
of $A$ is legitimate because the uniform certificate covers the closed box.

## Specializing the uniform certificate

For a rational target in $A$, retain the same graph, component center, component
radii and rational preconditioner. Replace the coefficient-box variables by the
target's exact coefficients. This gives an ordinary interval circuit certificate
for the complete coefficient system $QN-PD=0$.

This step needs no numerical solve. Specialization commutes with differentiation
in the component variables and with multiplication by the fixed preconditioner.
The point interval is contained in the original coefficient box. Combining terms
after substitution cannot enlarge their interval sum: $(a+b)I\subseteq aI+bI$.
Consequently the point correction and weighted derivative bounds are no larger
than the verified uniform bounds. Strict self-mapping, contraction and component
positivity survive. The unchanged point checker reconstructs and accepts those
same graph equations. The family Sylvester bound supplies coprimality.

The root remains an exact real algebraic component vector isolated by a rational
box. Its rational center is not substituted as an exact physical circuit value.

## Inverting the endcaps

Normalize the input $U/V$ to coprime polynomials with monic $V$. For reduced degree
$d>3$, require equal numerator and denominator degrees and $U_d>0$. Set

$$
g=U_d^{-1},\qquad H=V-gU,\qquad h=H_{d-1}.
$$

The positive endpoint chart requires $\deg H=d-1$ and $h>0$. Set

$$
L=\frac{U_d}{h},\qquad K=U-sLH.
$$

Require $\deg K=d-1$ and $K_{d-1}>0$. Then the uniquely recovered core is

$$P=K/h,\qquad Q=H/h.$$

Indeed $P+sLQ=U/h$ and $Q+g(P+sLQ)=V/h$. Normalization gives the original
target. These formulas show that rational output coefficients force rational
recovered endcap parameters and core coefficients. Conversely, the forward lift
has these inverse values. Coprimality
follows from $\gcd(K,H)=\gcd(U,V)=1$. Thus each successful inverse removes exactly
one reactive element and introduces no choice among possible roots or topologies.

Repeat until degree three, test exact membership in $A$, specialize its root
certificate and rebuild the endcaps in reverse order. Each endcap adds a positive
series inductor $L$ and a resistor $1/g$ in parallel with the whole arm. This
physically constructs a circuit, rather than only returning a rational identity.

**Recognition theorem.** At the level of exact arithmetic without resource caps,
this procedure terminates for every rational input. It accepts precisely the
rational members of the specified $\mathcal F_n$, for $n\ge3$. Every accepted
target has a positive ordinary uncoupled transformer-free realization with $n$
reactive elements. Its reduced degree is $n$, so that reactive count is globally
minimal within the stipulated circuit model.

The proof is induction using the unique endpoint inverse and the uniform base
certificate. A successful base test supplies the physical leaf; reversing the
induction supplies the graph. Failure of a defining chart condition or the final
box-membership test proves nonmembership in this family, not RLC nonrealizability.

## Executable acceptance and limits

The implementation currently permits degrees three through sixteen and the
retained consumer's rational-bit, expression-depth and graph-size caps. A cap or
unresolved acceptance condition returns `UNKNOWN`. Malformed inputs and invalid
family certificates receive separate statuses. Successful outputs include the
complete portable composition certificate and its exact target/budget binding.

The constructed graph has $n-1$ inductors, one capacitor and $n+1$ resistors:
$2n+1$ physical branches in total. Only the reactive minimum is established.
The method does not assert a minimum resistor count, uniqueness among all circuits,
coverage of every positive-real target or a general efficient minimum solver.

The frozen known-family regression contains 38 exact members, including all
fourteen coordinate-face controls of the base box and lifted members at degrees
3, 4, 6, 8, 12 and 16. All emitted certificates replayed. Fifteen additional
controls cover representation scaling, nonmembership, malformed inputs, consumer
resource scope and corrupted witnesses. This is an exact member regression, not
an independent test of topology discovery. The recognition theorem supplies its
universal family scope; the finite cases test its implementation.

From the extracted current-source archive's root, run
`python -B research/smith-chart/unified/solver/check_deterministic_family.py`.
No solver package or network connection is required.
