# Euler arithmetic nonvanishing: shifted-series continuation

Checkpoint: `Euler-shifted-obstruction-20261005`.
Parent: `Euler-arithmetic-nonvanishing-20261005`.
Parent archive SHA256: `15e1f9114380e180adcf4f7306d894100d6fd499929ee7a841d8629bd27e7464`.

**The focused actual-index nonvanishing theorem remains open.** This work
continues the shifted Bernoulli remainder and its derivative together. It
contains exact new identities, uniform valuation results, finite checks, and
counterexamples to proposed proof implications. None is an actual singular
Euler residual.

## Exact target

For every ordinary T>=0 for which

    r=(17659+2^18 T)2^640-161

has true terminal161, prove

    Phi_r(2^(2r-25)) != 0.

Phi_r is the stationary value in the fixed-r independent undepletion family.
The argument2^(2r-25) is the actual Euler member. This target is one focused
obligation in the larger universal simplicity problem; other addresses are
outside the present continuation.

## What changed

1. **The shifted remainder and its derivative are identified exactly.**
   Volkenborn reflection relates the scale4/3 and scale4 Bernoulli remainders,
   with the finite cutoff defect and its logarithmic derivative retained.
   Odd integer translations introduce no second independent moment equation.
   See `moment/SCALE_REFLECTION_AND_PREFIX.md`.

2. **The full regularized Euler function has exact all-order arithmetic.**
   For b(s)=(1+3*9^s)Ecal(s), all s in Z_2 and k,j>=0,

       v_2(Delta^k b(s))=3k+2,
       v_2(b^(j)(s))=3j+2.

   An elementary compatible-residue measure construction, symmetry, and one
   exact group-ring identity prove these assertions. They are not inferred
   from bounded numerical tests. See `root/EXACT_REGULARIZED_MOMENTS.md`.

3. **That bounded-measure control cannot simply be transferred to the prefix.**
   The actual regularized finite prefix retains a nonzero double pole at a
   primitive eighth root in its moment transform. Exact rational examples
   also falsify the proposed transferred finite-difference bound. The proof
   retains every cutoff term; the obstruction is not a missing tail estimate.

4. **The transformed derivative cancellation is now uniform.**
   At every stationary point in the actual chart, the shifted derivative
   term and the commutator term each have valuation156. Their sum has exact
   valuation158. The reciprocal kernel identity retains a cutoff forcing
   which cancels its proposed independent obstruction. See
   `weighted/RECIPROCAL_CUTOFF_AND_ACTUAL_COMMUTATOR.md`.

5. **Value and stationarity admit one exact local arithmetic certificate.**
   The quotient by K_Z/2 has rank one, with the explicit identity

       K-A(K_Z/2)=Phi.

   Finite complete coefficient data give p-A_P q=R_P modulo2^P, with
   R_P=Phi modulo2^P. Rational polynomial inputs exist for every actual
   ordinary index, with proved truncation bounds. The available height
   estimate does not force R_P to be nonzero. See
   `critical_arithmetic/LOCAL_ARITHMETIC_CERTIFICATE.md`.

6. **All low-order derivative valuations already agree automatically.**
   The actual regularized tail is coefficientwise divisible by2^(3r+2).
   Consequently C_r^(j) has exactly the same valuation3j+2 as b^(j) for
   every j<r. A two-jet construction shows why the Bernoulli coefficients
   themselves must enter a nonvanishing proof: small free dyadic coefficient
   changes can impose exact double contact while retaining those valuation
   laws. The construction is not an actual Euler counterexample. See
   `critical_arithmetic/newton/PREFIX_CONTACT_AND_WRONSKIAN.md`.

## The remaining arithmetic step

At a repeated residual zero, the regularized finite prefix C_r=mS_r would
satisfy both C_r(s)=b(s) and C_r'(s)=b'(s). The exact reflection and kernel
identities do not forbid this contact. Nor does a finite zero value of R_P
prove an exact zero. What is missing is a property of the actual Bernoulli
coefficients that forces a nonzero stationary remainder, with every cutoff
term retained.

The next continuation must change this implication: it must give a strict
value/derivative estimate for the actual finite prefix, or an arithmetic
nonzero certificate for every admitted ordinary index. More multiplier digits,
a discarded cutoff, generic rationality of a localized scalar, and a transfer
of the full Euler measure norm do not supply that implication.

## Evidence and review

Current executable runs and their manifest roots are recorded in
`CURRENT_EVIDENCE.json`. Older changed-source manifests are retained only as
superseded development history. The independent review pins the exact current
proofs and reconstructs the new implications. The inherited checkpoint is
included without changes. No Lean compilation was performed.
