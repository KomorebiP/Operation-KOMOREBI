# Strong Artin v0.25 — Graded compatibility and moving-syzygy lifting

Author: Komorebi P.

Status: fresh Lean replay PASS for the exact statements below. This is a
conditional algebraic lifting theorem, not a proof of Strong Artin.

## Ancestry

Primary parent: `Strong_Artin_Lean_v0.24.0_Compatible_Target_Hensel_Checked.zip`
SHA-256: `59fb2857e701e74c86c79f0363b32430a65fb298c3f20770f8773c580902a993`.

Additional unchanged polynomial-theory source:
`Strong_Artin_Lean_v0.20.0_Polynomial_Presentation_Hensel_Checked.zip`
SHA-256: `9dafcfcd6d23871e5a167b18314083afae3159a74c16e9aa4fa9bc65f4b3770f`.

The base archives are retained without modification. No claim is made that
all sibling v0.21-v0.23 developments have been merged into this branch.

## Main theorem

Let q : R -> k be a surjective homomorphism from a commutative ring to a field.
Assume ker(q)=(pi), with pi nilpotent. Let F be a finite coordinate polynomial
system, and let B(x) be a polynomial matrix of relation coefficients. Fix a
residual solution x0.

Assume, throughout the residual fibre of x0:

1. B(x) F(x) = 0 as an exact equation over R.
2. The reduced sequence is exact at the equation space:

       image(Jbar_x0) = kernel(Bbar_x0).

Then there exists x congruent to x0 modulo pi with F(x)=0.

No integral compatible-target retraction, integral right inverse, or full
surjectivity onto the redundant equation space is assumed.

The main declaration is:

    Komorebi.StrongArtin.PolynomialMovingSyzygyHensel.
      exists_exact_root_over_principal_nilpotent_residue

The dual formulation consumes:

    ker(Jbar.dualMap) = range(Bbar.dualMap)

and is named:

    Komorebi.StrongArtin.IntrinsicGradedLiftingCapstone.
      exists_exact_root_from_syzygy_corrected_dual_exactness

## Mechanism

At a nonterminal depth n, write F(x)=pi^n e. An exact moving identity gives
pi^n B(x)e=0. An element of R with nonzero residue is a unit; therefore it cannot
be annihilated by a nonzero power of pi. Coordinatewise, this proves
Bbar_x0(ebar)=0. Residual exactness supplies dbar with Jbar_x0 dbar=-ebar.
Lift dbar and correct x by pi^n d. The polynomial Taylor remainder gains one
power, so the corrected error is divisible by pi^(n+1). At the first zero
power of pi the error is exactly zero.

Only the relation coefficients on the current graded layer are frozen. The
integral nonlinear relation B(x) is allowed to vary with x.

## Actual representation equation specialization

For a group G, associative ring A, and chosen function r:G->A, define

    D(g,h) = r(g)r(h)-r(gh).

Associativity gives the exact moving identity

    r(g)D(h,l)-D(gh,l)+D(g,hl)-D(g,h)r(l)=0.

For a correction b,

    D_(r+b)(g,h) = D_r(g,h) + C_r(b)(g,h) + b(g)b(h),
    C_r(b)(g,h) = b(g)r(h)+r(g)b(h)-b(gh).

If q:A->B has square-zero kernel, r lifts a representation rho:G->B, and b is
kernel-valued, the last term vanishes. The release proves that an actual
multiplicative lift exists if and only if a normalized kernel-valued b cancels
D_r by C_r(b). It does not assert that every compatible defect is correctable,
nor identify this condition with a continuous Galois H^2 theorem.

## Examples and negative controls

The whole polynomial lifting theorem is instantiated for

    F(x) = (x^2+x+c, x(x^2+x+c)),  q(c)=0,
    B(x) = (-x,1).

The residue sequence is proved exact, so an actual root is obtained over any
principal nilpotent residue ring.

The v0.24 example F(x)=(x,x^2) at x=2 in Z/8Z still fails the fixed horizontal
integral-target condition. Its normalized error (1,2), reduced modulo 2, is
horizontal. Additional exact controls prove that x^2+1 has no root modulo 4,
and that a residual unit relation cannot be promoted to an exact annihilator
of the constant error 2 modulo 4.

## Verification

Lean 4.34.0-rc2; mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
All checks use warnings as errors and one compiler thread.

- 7 unchanged direct source dependencies.
- 10 new modules, containing 42 theorems, 12 definitions, and 1 structure.
- 17 source modules plus an audit module freshly compiled.
- All 55 named new constants axiom-audited.
- No active-source proof placeholders, custom axioms, or custom opaque declarations.
- Reported foundations: propext, Classical.choice, Quot.sound.

These are additive counts only. Do not add historical sibling release counts
without a source/ancestry reconciliation.

Run from this directory:

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 6
    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 6
    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 6

The first command always starts a new source replay. An INCOMPLETE message is
not a verification success; a final PASS requires all 18 compiler invocations.

## Boundary

The genuinely arithmetic exact relations and residual exactness remain inputs.
The theorem neither realizes arbitrary auxiliary columns arithmetically nor
shows that an augmented point descends when auxiliary variables are removed.
Local continuous cohomology, Tate duality, Chebotarev application, the
Selmer/cotangent comparison, the automorphic carrier and Strong Artin remain
open. See RESEARCH_BOUNDARY.md and CONTINUE_HERE.md.
