# Usable pure-type margins and a smaller mixed search

The universal mixed-RLC margin remains the earlier extremely small bound.
For the entire RC-only and RL-only classes, usable explicit bounds can already
be obtained from elementary response shapes. No resistor or storage-count
restriction is imposed on these two subclasses.

## The fixed target and samples

Keep the same normalized target and seven positive real Laplace arguments:

$$H(s)=\frac{4+3s+6s^2}{9+2s+6s^2},\qquad
\gamma_H=\frac{H-1}{H+1},\qquad
s_j\in\{1/2,3/4,1,5/4,3/2,7/4,2\}.$$

These are not imaginary-axis measurement frequencies. The current arithmetic
module reconstructs the samples from these polynomials; no fitted values enter.

## All RC networks

Increasing a positive real Laplace argument increases every capacitive
conductance while leaving the resistor conductances fixed. Rayleigh
monotonicity makes the input resistance, and hence its reflection, nonincreasing.
Equivalently, the classical RC Stieltjes representation gives that property
directly. Open, short and constant limits obey the same inequality.

The target instead has $\gamma_H(1/2)=-9/37$ and $\gamma_H(2)=-3/71$.
If an RC response differs by at most $\delta$ at the seven samples,

$$\delta\ge\frac{\gamma_H(2)-\gamma_H(1/2)}2
 =\frac{264}{2627}.$$

Lean checks this two-sample error implication with the exact fractions.

## All RL networks

For an RL driving point, $1/(1+Z)$ is Stieltjes. One way to see the Cayley step
is to write the classical RL Foster form

$$Z=R_0+L_\infty s+\sum_j b_j\frac{s}{s+p_j},
\qquad R_0,L_\infty\ge0,\quad b_j,p_j>0.$$

Between its negative real poles $Z'>0$. The zeros of $1+Z$ therefore
interlace the poles, are simple and negative, and have positive reciprocal
residues. The constant of $1/(1+Z)$ at infinity is nonnegative. Thus

$$\gamma(s)=c-\sum_j\frac{a_j}{s+p_j},\qquad a_j\ge0,\quad p_j\ge0,$$

including empty sums and limits. This uses the classical two-element-kind
characterizations, not an assumption about the circuit being series-parallel.
See Morelli, Theorems 2.2–2.3, printed page 11, and the constructive argument
in the preceding synthesis section.

For five successive arguments separated by $1/4$, set

$$\mathcal L(f)=f(1/2)-4f(3/4)+6f(1)-4f(5/4)+f(3/2).$$

For every $p\ge0$,

$$\mathcal L\left(\frac1{s+p}\right)
 =\frac{3/32}{(p+1/2)(p+3/4)(p+1)(p+5/4)(p+3/2)}>0.$$

Consequently $\mathcal L(\gamma)\le0$ for every RL network. But exact target
arithmetic gives $\mathcal L(\gamma_H)=401/330410$. The stencil's coefficient
absolute sum is sixteen, so

$$\max_j|\gamma(s_j)-\gamma_H(s_j)|
 \ge\frac{401}{5286560}.$$

Lean checks the kernel identity, passage to any finite positive Stieltjes sum,
and the final error implication. The physical-network-to-Stieltjes theorem is
an authenticated classical dependency with a written translation; it is not
silently included in the formal coverage claim. These are valid lower bounds,
not claims of best approximation.

## Canonical mixed reactive skeletons

After arbitrary-resistor elimination, retain the two ports and the endpoints
of at most four reactive branches. The resistor part remains a complete graph
of freely variable nonnegative conductances on those retained vertices. The
new enumeration changes only the discrete reactive placement problem.

Fix both port labels. Within each reactive kind, permute edges, reverse their
orientations, and rename internal vertices in order of first occurrence. Take
the lexicographically least resulting edge list. This is a complete canonical
key: a vertex relabeling does not change any first-occurrence list, and an
isomorphism preserves the two ports and reactive kinds and hence induces one
of the enumerated edge permutations and reversals. Conversely, equality of the
lists explicitly gives such an isomorphism. Parallel edges remain allowed.

Generate the next level by adding an edge between two old vertices, an old
and a fresh vertex, or two fresh vertices. This covers every graph by induction:
delete one edge from a target graph, remove only internal vertices no longer
incident to a reactive edge, invoke the induction hypothesis, and reinsert the
deleted edge and at most two new vertices. Resistor-only internal vertices have
already been eliminated. A reactive self-loop can be deleted, reducing budget.

The resulting counts are:

| Reactive branches | Canonical classes | Mixed classes | Mixed, no same-kind parallel pair |
|---|---:|---:|---:|
| 0 | 1 | 0 | 0 |
| 1 | 8 | 0 | 0 |
| 2 | 60 | 26 | 26 |
| 3 | 436 | 298 | 246 |
| 4 | 3190 | 2628 | 1858 |

Same-kind parallel branches can be combined by adding capacitances or adding
reciprocal inductances, with no change in the port response and a lower
reactive count. The preceding margins already exclude the pure RC/RL cases
for any proposed seven-sample margin below $401/5286560$.
It therefore suffices for the remaining small-margin task to treat 2,130 mixed
representatives across budgets two, three and four. Their continuous resistor
and reactive parameters are still unrestricted; this is not a value-grid search.

The implementation was compared with a different canonicalizer that exhausts
all internal-vertex permutations on three finite universes: 900 labeled
placements on six vertices at budget two, 8,000 on five vertices at budget
three, and 20,736 on four vertices at budget four. Both coverage and uniqueness
agree there. The induction above, not those finite comparisons, supplies the
general vertex bound and coverage. Ten-vertex representatives are retained;
the earlier five-node census is not substituted for this population.

## One mixed representative now has an exact refutation

When the L and C both connect the two terminals, arbitrary resistor-only
material reduces to a shunt conductance. The total admittance is

$$Y(s)=g+Cs+h/s,\qquad g,C,h\ge0.$$

At the first four samples the weights
$w=(-1/2,9/4,-3,5/4)$ annihilate all three basis functions $1,s,1/s$.
Thus $\sum_iw_iY(s_i)=0$ for every finite choice of those parameters.

Assume the reflection errors are at most $\delta=1/1000$.
Writing $h_i=\gamma_H(s_i)$, exact Cayley inversion gives the necessary bounds

$$\ell_i=\frac{1-h_i-\delta}{1+h_i+\delta}
 \le Y(s_i)\le
 u_i=\frac{1-h_i+\delta}{1+h_i-\delta}.$$

All denominators are positive. A shorted port has reflection minus one and
already violates the assumed error interval, so no infinite-admittance face
is lost. Opens are included by zero coefficients.

For the exact target fractions, the interval lower bound
$\beta=\sum_{w_i>0}w_i\ell_i+\sum_{w_i<0}w_i u_i$ is strictly positive.
Introduce one slack square for each selected interval bound:
$E_i=Y_i-\ell_i-t_i^2$ for positive $w_i$, and
$E_i=u_i-Y_i-t_i^2$ for negative $w_i$. With $E=\sum_iw_iY_i$,

$$-1=\sum_i\frac{|w_i|}{\beta}t_i^2
 +\sum_i\frac{|w_i|}{\beta}E_i-\frac{1}{\beta}E.$$

The unchanged rational refutation consumer verifies this polynomial identity
exactly. The source-bound certificate reconstructs the physical basis, target,
Cayley intervals and margin before replaying it. This is an all-parameter
exclusion for this specific mixed representative, independent of the optional
SMT backend. Its maximum sample error is strictly greater than $1/1000$.

## Extending the certificate to arbitrary RC material

The same obstruction covers a much larger class: one inductor connected
directly across the port, in parallel with an arbitrary finite RC network.
There is no series-parallel assumption on that RC material and no bound on
its resistor or capacitor count. The RC impedance is Stieltjes. Its reciprocal
admittance has negative residues at its negative real poles: between the
Stieltjes poles its derivative is strictly negative, so each reciprocal
residue is negative. Its polynomial part is affine. Consequently the total
admittance has the form

$$Y(s)=h/s+a+bs-\sum_j\frac{c_j}{s+p_j},\qquad c_j,p_j\ge0.$$

The empty sum includes constant and direct-capacitor cases. The weights above
annihilate $1,s,1/s$. Their exact kernel identity is

$$\sum_i\frac{w_i}{s_i+p}
 =\frac{3p/32}{(p+1/2)(p+3/4)(p+1)(p+5/4)}\ge0,\qquad p\ge0.$$

It follows that $E=\sum_iw_iY(s_i)\le0$ throughout this mixed class. Lean
checks this kernel identity and passage to arbitrary finite positive sums.
The classical physical RC characterization and reciprocal translation remain
explicit source and written-proof leaves.

To replay the interval contradiction, replace $E=0$ by $E'=E+u^2=0$.
The refutation identity simply gains the additional positive square $u^2/\beta$:

$$-1=\sum_i\frac{|w_i|}{\beta}t_i^2+\frac{u^2}{\beta}
 +\sum_i\frac{|w_i|}{\beta}E_i-\frac{E'}{\beta}.$$

The unchanged rational consumer accepts this five-square certificate.
The verifier rebuilds the target, margin, intervals and declared physical shape
before checking the identity. Infinite admittance again gives the excluded
short response; zero coefficients and open faces are retained.

Among the 2,130 irreducible mixed representatives, this class covers four at
budget two, thirteen at budget three and forty-three at budget four: sixty in
total, including the original direct-L/C case. This is fifty-nine additional
whole-parameter exclusions. The remaining small-margin task has 2,070 mixed
representatives. The theorem itself permits arbitrarily large RC subnetworks;
these counts describe only its intersection with the four-reactive search.

A bounded optional exact-NRA probe processed all 26 budget-two representatives
and one representative of each higher-budget size/type-count bucket: 62
models in total. It reported one UNSAT and 61 UNKNOWN at the stated resource
limit. The UNSAT case is the shunt case independently refuted above. The
UNKNOWN verdicts supply no conclusion. Some of those cases are now covered by
the separate analytic certificate above; other cases still require a new
argument. Neither solver outcomes nor the topology reduction is a global
exclusion certificate. The universal mixed-RLC bound is unchanged.
