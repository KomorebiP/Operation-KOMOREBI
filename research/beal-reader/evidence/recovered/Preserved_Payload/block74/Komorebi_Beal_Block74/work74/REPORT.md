# Beal research, Block 74
## Uniformizer probes and a three-trace valuation formula

Release7.4.0, 21 September2026. Under the explicitly retained actual geometry, the
fixed-seven valuation defect can now be read from three jointly labelled rank-two
traces at one extra precision. An all-depth form detects n+1+v7(v7(C)).

ALL EIGHT bounded coefficient/character patterns remain. The required joint traces
have not been evaluated on an actual global candidate. This is a written conditional
proof with separate finite arithmetic checks, not a new Lean proof or independent
mathematical review.

## 1. The new depth-one formula

Let T(g)=tr_O rho(g) in the SAME integral rank-two natural representation, and define

    D(tau,g)=T(tau g)-T(tau)-T(g)+2.

There is a local Galois element tau at seven that fixes the required cyclotomic
roots, annihilates the Kummer classes of ALL local units, and evaluates the
uniformizer7 to1. Choose g in the residual kernel with beta(g) nonzero. Then at
actual depth one,

    D(tau,g)=49 nu7(X) beta(g) modulo343,

and therefore

    nu7(X)= beta(g)^-1 * (D(tau,g)/49 modulo7).

The fixed-seven period condition becomes the explicit mixed-trace equation

    D(tau,g)/49 = v7(C)*v/(2epsilon) * beta(g) modulo7.

Here alpha=vw[phi]+r[3]+[sqrt5] is the normalized actual natural class and epsilon
is its actual local coefficient orientation. No lower-left7beta term is removed.

This is not a recipe for combining three unrelated Frobenius polynomials. The
arguments must be tau, g, and THEIR PRODUCT in a single integral representation.
The rank-two coefficient-ring traces, not merely the rational quartic traces,
are required. The old finite tables do not provide those joint labels.

## 2. The probe is an actual Galois-theoretic construction

Over F=Q_7(sqrt5), phi and3 form a basis of the pro-seven unit group. Their exact
logarithmic first digits are5sqrt5 and6, which are linearly independent overF7.
Adding[7] supplies the valuation coordinate.

For every j>=1, pass to L_j=F(mu_(7^j)). Restriction of the three mod7 Kummer
classes remains injective: the cyclotomic quotient is abelian, its seven-primary
subgroup has trivial conjugation action, and the order-six quotient acts
nontrivially on mu7. Its H1 kernel is zero. This is NOT a prime-to-seven-degree
argument for the full cyclotomic extension.

The three classes remain independent at the full7^j level. Kummer theory supplies
an element of the extension dual to(0,0,1), which gives the desired probe tau_j.
It kills every unit coordinate, so it kills the unknown higher unit-period errors
without requiring a longer truncated period expansion.

The actual period valuation matrix is exactly7c I, c=v7(C). Its evaluated
rank-two matrix is therefore

    rho(tau_j)=I+7c P E12 P^-1 modulo7^j.

The local toric line agrees with the natural line modulo7^n, so P21 is divisible
by7^n. The inherited residual comparison fixes (P E12 P^-1)12 modulo7 as
v/(2epsilon). These are actual geometric hypotheses, not deductions from generic
finite matrices.

## 3. An all-depth exact valuation

Put t=1+v7(c). At precision j>=n+t+1 the same probe and a detecting g satisfy

    v7(D(tau_j,g))=n+t=n+1+v7(v7(C)),

    D(tau_j,g)/7^(n+t)
       = (c/7^(t-1))*v/(2epsilon)*beta(g) modulo7.

The coefficient on the right is nonzero. The proof uses the exact elementary
identity D=tr((rho(tau)-I)(rho(g)-I)), retaining every high-order toric matrix
entry until its contribution is known to vanish at the stated precision.
No full global diagonal triviality is assumed at higher depths. The local
character-separation argument proves the required toric-line alignment.

This does not bound n or c. It gives a precise global trace quantity which must
record them when the group elements have the stated labels.

## 4. Stronger comparison, but no numerical exclusion yet

Two depth-one actual candidates with the same normalized residual data and beta
have the SAME nu7 if their three labelled rank-two traces at tau,g,tau g agree
modulo343. Block73's additional equality of the entire inertia data is unnecessary
for this new comparison; neither is complete equality of all trace functions.

However, the three integral traces themselves are not supplied by the eight
residual tuples. We have not calculated nu7 for any one of their global
realizations, shown it is zero, or solved the constrained global adjoint p,q
system. A triangular beta=0 reference is not substituted for an actual candidate.

For illustration, c=1,v=3,epsilon=-1 and a detecting beta(g)=1 REQUIRE the
mixed trace to equal98 modulo343. That is a required value, not an observed
trace of a global Frey representation.

## 5. Controls and observed finite checks

Individual traces do not suffice: U_a=[[1,7a],[0,1]] and V=[[1,0],[7,1]] all have
trace2 and determinant1. Their product traces are51 and100 modulo343 for a=1,2.
The old modulo49 traces lose both signals entirely. A residual-identity element
with an extra diagonal first digit is also not an adequate substitute for the
constructed unit-annihilating probe; an explicit control changes the recovered
digit from1 to3.

Two independently written programs use w^2=5 and phi^2=phi+1 arithmetic. The first
computes matrix conjugates; the second computes the rank-one operator from a
column and a dual row. They agree on the complete deterministic output.

|Check|Actual coverage|
|---|---:|
|Mixed-characteristic matrix family|6480 cases at depths1..6|
|Cases with nonrational entries|6480|
|Cases retaining nonzero toric diagonal entries|6480|
|All residual (nu,beta!=0) pairs|2352|
|Complete unit residues modulo49|2352|
|Cyclotomic generator-value candidates|2401|
|Eigenspace-projection vector checks|2401 finite-model checks|

The matrix family covers c=7^s u with s=0,1,2 and u=1..6, v=1..6, both local
orientations, and five variations. These are finite algebra controls, not6480
Galois representations or Diophantine solutions. The Galois/Kummer realization
is a separate written argument. No new Frobenius point count was made.

The original Block73 default verifier passed cleanly in29.342 seconds. The final
Block74 verifier rebuilds both new result files from scratch, compares full outputs,
checks input and payload hashes, and rejects controlled corruptions. The final
fresh-extraction replay and archive audit are stored externally. No full historical
chain is represented as freshly run.

Two new finite-check assertions were corrected during development: truncating the
valuation bound for a zero modular coefficient, and correcting the expected count
of all units in O_F/49 from2304 to2352. The corrected results passed both complete
implementations. Neither failed run produced an accepted scientific certificate.

## What remains

The next step must obtain or constrain the mixed trace in ONE actual global
integral deformation, with tau and g correctly identified, and compare it to the
fixed-seven target. Merely finding separate allowed polynomials at three primes
would not evaluate this quantity.

All eight bounded patterns, unrestricted conductors/depths, the minus component,
global integral realization, independent upstream acceptance, CM/higher Hilbert
branches, the complete(3,5,7) signature, and full Beal remain unresolved.
