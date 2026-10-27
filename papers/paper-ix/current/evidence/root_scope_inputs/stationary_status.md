# The missing stationary-separation bound

Assessment checkpoint: `Euler-stationary-separation-20261005`, 2026-10-05.
The contemporaneous cutoff and assessment are this same checkpoint. The
immutable base archive and exact target are pinned in [TARGET.md](TARGET.md).
There is no Git revision or executable ledger here; the archive, source
hashes, computation manifests, and independent review pins identify evidence.

## Outcome against the requested theorem

The original goal remains open. No actual Euler counterexample was found.
For every admitted ordinary index

\[
r=(17659+2^{18}T)2^{640}-161,\qquad T\ge0,
\]

with true terminal161, the required assertion remains
\(\Phi_r(2^{2r-25})\ne0\). The current work supplies new exact reductions
and tests new arithmetic mechanisms. It does not substitute larger finite
coverage for this quantifier. Even proving this family would leave the
parent's terminal129 and higher-address obligations.

## Actual approximation now has no depth ceiling

The exact undepletion factor

\[
e_{r,q}=\frac{1-2^{2r-1}}{1-2^{2r-1}4^q}
\]

is retained in every Jacobi-model packet. Multiplication by this unit
preserves the all-q moment error. Consequently the actual critical models
satisfy, for every \(m\ge25\),

\[
v_2(\Phi^{\mathrm{act}}_{r,m}-\Phi^{\mathrm{act}}_r)
\ge L_m=8m-4s_2(m)-178\longrightarrow\infty.
\]

This eliminates the earlier undepletion cap; there is no finite carry-rank
restriction in this construction. The strict test
\(v_2(\Phi^{\mathrm{act}}_{r,m})<L_m\) is equivalent to nonvanishing for
each fixed r. Existence of a passing depth remains unproved. A zero limit
is compatible with nonzero models at every depth. See
[the exact proof](root/ACTUAL_LIMIT_AND_SEPARATION.md) and its
[independent review](review/ACTUAL_LIMIT_REVIEW.md).

## The critical problem compresses to one quadratic discriminant

The actual chart has a unique preparation

\[
K_r=U_r(Z)(Z^2+2\beta_r Z+\alpha_r),\qquad
U_r\equiv u_r\pmod{256},\quad u_r\text{ odd}.
\]

At the actual critical point c, with \(\tau=U'_r(c)/U_r(c)\), the exact
reduced discriminant \(\delta_r=\beta_r^2-\alpha_r\) satisfies

\[
\delta_r=-\frac{\Phi^{\mathrm{act}}_r}{U_r(c)}
\left(1-\frac{\tau^2\Phi^{\mathrm{act}}_r}{4U_r(c)}\right),
\qquad v_2(\delta_r)=v_2(\Phi^{\mathrm{act}}_r).
\]

The bracket is a unit. The relation includes exact zero and retains the
unit-cofactor derivative. It asserts no rationality or algebraicity of
the prepared coefficients. This reduces the former O(P^2) representative
height cost to O(P), about 2P bits. That surviving cost still exceeds the
P-bit precision. A fixed rational double-root control proves why nonzero
integer representatives at every precision do not establish a nonzero
limit. See [quadratic compression](ordinary/QUADRATIC_COMPRESSION_AND_HEIGHT.md)
and [review](review/QUADRATIC_COMPRESSION_REVIEW.md).

## Reconstruction improves height but does not supply the inequality

Exact projective LLL and gcd reduction were executed on only14 frozen
precision/control pairs. At P=93, coefficient heights fall to62 bits;
the smallest reduced discriminant numerators in the declared search still
have114 and112 bits. Two lower-precision rational certificates recover
the already known valuation0. No new multiplier digits were computed.

Exact dual-lattice certificates show globally that the sufficient
coefficient condition \(2H^2<2^P\) is impossible at all14 specified inputs.
This excludes that sufficient test there, not exceptional discriminant
cancellation, future precisions, or all arithmetic representations. See
[reconstruction](ordinary/PROJECTIVE_RECONSTRUCTION.md) and
[independent review](review/PROJECTIVE_RECONSTRUCTION_REVIEW.md).

## Full recurrence and exterior contact retain the cancellation

The actual Bernoulli cubic, complete finite prefix defect, nonlinear tail,
and ordinary derivatives give nonzero forcing jets of valuations155 and156.
At hypothetical double contact they are exactly balanced by the index
derivatives \(2V\) and \(2V_x\), which ordinary stationarity does not
annihilate. The genuine operator square has value valuation307 and
derivative valuation306; replacing it by the square of G would be false.
See [full recurrence](coefficient/FULL_RECURRENCE_CONTACT.md) and
[independent review](review/COEFFICIENT_REVIEW.md).

The integer-shift continuation retains the complete source denominator and
both derivatives of the shift product. Its contact equations have valuations
154 and155 on both sides. The nonzero neighboring value G(x-1) and its
derivative balance the same surviving index jets. Two derivative terms of
valuation153 cancel to valuation155; deleting either would manufacture a
false contradiction. See [integer-shift proof](coefficient/integer_shift/INTEGER_SHIFT_CONTACT.md)
and [review](review/INTEGER_SHIFT_REVIEW.md).

The proposed exterior/logarithm separation also fails for the prescribed
coefficients: both terms have valuation309 and unit5 modulo8. Their complete
mismatch has one zero \(\zeta_r\) on every actual chart, with

\[
v_2(\zeta_r-c_r)=13+v_2(\Phi^{\mathrm{act}}_r),\qquad
W_r(c_r)=2^{333}\Theta_r(c_r)\Phi^{\mathrm{act}}_r,
\quad\Theta_r\equiv1\pmod8.
\]

Thus proving that these centers differ is the original nonvanishing
obligation again. The first24 bits of cancellation are automatic at a
stationary point. See [contact proof](contact/SOURCE_CONTACT_AND_EXTERIOR.md)
and [independent review](review/CONTACT_REVIEW.md).

## Finite exponential models: a new bridge with a quantified cost

With the complete source retained, each finite Jacobi moment model has an
exact finite exponential representation after multiplication by

\[
D_r(x)=\prod_{j=1}^{2r+2}(2x+j).
\]

The dictionary handles Jordan blocks, so it assumes no diagonalization.
The clearing factor has zeros on the actual chart; contact there needs
separate order accounting. Finite exponential representation alone supplies
neither coprimality nor a bound for the dyadic critical value.

Exact undepletion makes even these finite-model moment sequences
nonrational. Their generating functions obey
\(M(z)-\varepsilon_r M(4z)=(1-\varepsilon_r)R_m(z)\),
where \(\varepsilon_r=2^{2r-1}\) and the rational Jacobi resolvent has
poles of valuation0. Comparing the extreme valuations of a hypothetical
finite pole set proves that no rational M satisfies this identity.

Nevertheless normalized finite geometric truncation of the correction
constructs finite actual moment approximants of rank at most mJ, where

\[
J=\left\lceil\frac{h_m}{2r-1}\right\rceil,
\qquad h_m=8m-4s_2(m).
\]

They retain the original all-q error h_m and actual stationary error L_m.
Only packet0 is forced to match exactly; lower packets remain controlled
by the error bound. After clearing D_r, their differential order is at
most \(4r+2+8mJ\). This gives genuinely finite exponential approximants
at every depth, but their order grows with precision.

There is also a proved cost for this particular construction. At packet1,
its reduced correction numerator has logarithmic height greater than
\((2r)J-(2r-1)-2\), while the correction precision is \((2r-1)J\).
For fixed r and sufficiently large J, that height exceeds the precision.
The exact packet1 correction is one fixed rational number; the growing
height belongs to these chosen approximants. It does not bound every
possible discriminant after further cancellation. Expanding the exact
infinite source-block sum term by term is invalid as well: individual
cleared exponential coefficients fail to tend to zero.

See [the finite-exponential and actual-model proof](ordinary/exponential_model/FINITE_EXPONENTIAL_ACTUAL_MODELS.md).
This is a completed representation and approximation bridge, with explicit
arithmetic costs. The required strict stationary separation remains open.

A final [finite prefix repair](root/PREFIX_REPAIR_AND_HEIGHT_SCOPE.md) tests
the scope of the packet1 cost. Replacing the first2m approximant moments by
their exact actual values changes the rational generating function only
by a polynomial. It preserves the all-q error, gives rank at most mJ+2m,
and adds only polynomial prefactors at bases1 and9 to the source formula.
Thus finite models can also retain exact prefix agreement. The packet1
height cost is avoidable by this repair; the heights of its new Bernoulli
combinations and stationary discriminant remain uncontrolled. No strict
comparison follows from the repair.

## Remaining input and resumption conditions

The next arithmetic obligation is \(\delta_r\ne0\) for every admitted r.
A sufficient quantitative form is an actual projective quadratic whose
reduced rational discriminant has nonzero numerator n with \(|n|<2^P\)
at an explicitly bounded precision. No depth-independent bound forcing
such a certificate is proved.

Preparation and actual convergence are completed auxiliary constructions.
The height route remains open: resume it with a new constraint on reduced
numerators or a representation overcoming the proved finite-precision
height obstruction. The recurrence route remains open for a combination
of shifted terms and prefix defect independent of the unknown scalar;
the tested local forcing reduction is closed because its balancing terms
were computed exactly. The tested exterior strict-dominance construction
is closed because its premise is false on the actual chart. Separating its
two centers requires a new independent arithmetic invariant.

The finite-exponential route remains open for a quantitative separation
theorem that handles growing order, the displayed height cost, and zeros
of D_r. Its exact finite-recurrence continuation is closed by the pole
argument; applying a finite common-zero theorem directly to the exact
reinserted moment model is unsupported. No presently checked external
theorem supplies the required bound. Further use needs that new input,
rather than another truncation of the same model.

These conditions preserve plausible future research without treating
unexecuted inequalities as results. The source-product development error
and its correction are retained separately in
[DEVELOPMENT_CORRECTION.md](coefficient/product/DEVELOPMENT_CORRECTION.md).
No external theorem was imported; the bounded literature transfer check
is recorded in [SOURCE_CHECK.md](SOURCE_CHECK.md).
