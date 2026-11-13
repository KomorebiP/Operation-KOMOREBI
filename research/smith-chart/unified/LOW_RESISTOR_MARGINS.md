# Whole lossless and one-resistor margins

Author: Komorebi P.

The following result allows all positive physical parameters, at most four
reactive branches and at most one resistor. It is a structural quantitative
subclass result. The earlier classical exclusion was already available; no
priority or hardware-tolerance claim is made.

Use $H=(4+3s+6s^2)/(9+2s+6s^2)$, $\Gamma_Z=(Z-1)/(Z+1)$, and let $E$ be
the maximum reflection error against H at $s=1/2,3/4,1,5/4,3/2,7/4,2$.
**Theorem.** Under the stated model and branch budgets,

$$E>10^{-150}.$$

The proof has project self-review; independent and complete formal assurance
remain separate.

## Lossless parity separator
Delete loops and components not connected to a port; disconnected ports are
an open circuit. For a connected LC port graph, each term of the spanning-tree
denominator contains n-1 admittance factors; each term of the two-forest
numerator contains n-2. Each LC admittance is either C*s or 1/(L*s).
Multiplying both by s^(number of L) yields nonnegative-coefficient polynomials
of degree at most the total reactive count, with opposite parity. This follows
from term parity n-1 and n-2 before the common multiplication; zero terms do
not alter it. Do not assume a nonzero constant coefficient: both polynomials
can have a common power of s. Shorted ports give Gamma=-1.

Normalize P(1)+Q(1)=1. For either opposite-parity pattern through degree four,
the five coefficient variables x have sum one. Define rows
$$A_{jk}=(1-h_j)s_j^k\quad\text{for P columns},\qquad
A_{jk}=-(1+h_j)s_j^k\quad\text{for Q columns},$$

where $h_j=\Gamma_H(s_j)$.
Then A_j*x=(Gamma_Z(s_j)-h_j)*(P(s_j)+Q(s_j)). At these nodes P+Q<=16.
The recorded exact five-row dual weights obey A^T*w=ones, so
$$1\le16\|w\|_1E.$$

The two weak lower bounds are $64425/873090872$ and $1220925/11532772076$.
Thus the conservative lossless bound mu=1/100000 holds, including open/short
ports by direct comparison. The exact row identities, all21 row subsets per
pattern and finite physical controls are replayed by `solver/lossless_separator.py`
and recorded in `verification/current-exact-011`.

## Extreme element rounding
Assume for contradiction E<=delta=$10^{-150}$. The inherited all-three-reactive
margin is strictly $10^{-13}$. Put $\eta=2\cdot10^{-14}=1/50000000000000$. An L or C outside
[eta,1/eta] can be deleted or contracted, reducing the useful reactive count
to at most three with uniform positive-real reflection change <=4*eta.
For small L, contract and use2*s*L; for large L, open and use2/(s*L).
For small C, open and use2*s*C; for large C, contract and use2/(s*C).
These are the inherited positive-real branch surgery estimates, valid at the
seven samples even when deletion or contraction changes connectivity.
If the resulting port is open or short, compare Gamma=1 or-1 directly;
their errors are at least mu. Apply the inherited three-reactive theorem
only to the remaining finite positive port graphs with distinct terminals.
Since delta+4*eta<$10^{-13}$, the result would contradict the inherited margin.
Consequently every useful L/C lies in the stated box; redundant loops or
detached components must first be removed, and if fewer than four useful
reactive edges remain the inherited margin applies immediately.

If no resistor remains, use step1. Otherwise, if R<mu/8 contract it; if
R>8/mu delete it. The change is <=mu/4 and the resulting circuit is lossless
with at most four reactive edges. Its error is <=delta+mu/4<mu, contradicting
step1. Hence the sole resistor also lies in[eta,1/eta]. A resistor irrelevant
to the port response reduces to the lossless case. These arguments need no
assumption about regularity at imaginary resonance or endpoint pole order.

## Coefficient floor without a common-factor assumption
The connected port component now has at most five edges. Let raw P,Q be the
tree/two-forest sums after multiplying by s^l. Every nonzero monomial
coefficient is a positive sum of products of at most five factors chosen
from C,1/L,1/R, all in[eta,1/eta]. Therefore every nonzero raw coefficient
is at least eta^5. There are at most2^5 subsets of the five edges in each
sum, and every product is at most eta^(-5). Thus
 P_raw(1)+Q_raw(1)<=64*eta^(-5).
After normalization, every positive coefficient is at least
 gamma_min=eta^10/64.
This bound includes sparse supports and structural common powers of s.
All-natural polynomial degrees remain at most four. The tree/two-forest formulas follow by Cauchy-Binet on the grounded incidence
matrix; squared minors are1 exactly on the corresponding trees/two-forests.
Finite fixture agreement alone does not establish the covering argument.

## Seven samples control the cross polynomial
Delta=P*Q_H-Q*P_H has degree at most six. At all seven nodes,
 |Delta(s_j)| <= (16*71/2)*E =568*E.
The exact Vandermonde inverse at the seven nodes has infinity norm12800.
Consequently every coefficient of Delta has modulus <=C*E, C=7270400.
Both inverse identities and this rational constant are recorded exactly.

Let k=min(order(P),order(Q)). If the orders differ, the coefficient of s^k
in Delta is9*P_k or-4*Q_k, of modulus at least4*gamma_min. Let d be the
maximum of the degrees. If the degrees differ, the coefficient of s^(d+2)
is6*P_d or-6*Q_d, of modulus at least6*gamma_min. The chosen delta obeys
 C*delta<2*gamma_min, excluding both alternatives. Thus Z has finite positive
DC and infinity limits, irrespective of a common power of s.

## The one-resistor endpoint obstruction
At DC, replace L by wires and C by open circuits; at infinity interchange
the two. For a finite positive endpoint in a positive passive graph with
only one resistor, the reduced one-port value must equal that resistor R.
Every other endpoint is zero or infinity. This endpoint reduction is the
physical endpoint lemma, including singular limits, parallel short paths and
disconnected residual vertices. The following energy proof supplies it.

Endpoint-lemma proof: drive the port at unit voltage.
For each real s>0, the effective conductance is the minimum of
 sum_L (v_u-v_v)^2/(s*L) + sum_R (v_u-v_v)^2/R
     + sum_C s*C*(v_u-v_v)^2
over port-fixed potentials. Clipping to[0,1] never increases the energy, so
the admissible set is compact. If an L-only path joins the ports, its series
impedance tends to zero and Rayleigh comparison forces Z->0. Otherwise,
there are admissible potentials constant on every L-connected component.
On that constraint set, minimize the sole-resistor energy and call the value
Y0. Testing with a minimizer gives limsup Y(s)<=Y0 because its capacitor
energy vanishes. Along any minimizing sequence with bounded energy, every
L drop tends to zero. Compactness yields a subsequential limit in the
constraint set; nonnegativity of all omitted energies then gives
liminf Y(s)>=Y0. Thus Y(s)->Y0. After L contraction and C deletion, a graph
with one resistor has positive conductance only if that resistor connects
the two distinct port components, in which case Y0=1/R. If Y0=0, the port
impedance tends to infinity. Replacing s by1/t exchanges the roles of L
and C for the infinity limit. This proof also covers R loops and detached
components, without assuming a nonsingular imaginary-frequency matrix.

With this lemma, both endpoint ratios equal R. The actual lowest and highest
nonzero coefficients from step4 give
 |R-4/9| <= C*E/(9*gamma_min),
 |R-1| <= C*E/(6*gamma_min).
The triangle inequality then gives
 5/9 <= (5/18)*C*E/gamma_min, hence E>=2*gamma_min/C.
The exact check C*delta<2*gamma_min contradicts E<=delta.



## Evidence and limits

The exact dual identities and interpolation inverse are replayed by
`solver/lossless_separator.py`. There are two parity patterns,21 nonsingular
five-row subsets per pattern, eight lossless physical controls and sixteen
one-R endpoint controls, fourteen with structural common powers of s. The
written proof supplies universal parity, coefficient and endpoint coverage.
The bound is tiny and does not supply a practical arbitrary-R separator.
