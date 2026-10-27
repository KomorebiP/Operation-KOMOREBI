# Cyclotomic Shell Integral Lattice — v0.11.0

## Certified theorem block

Let `T>0` and let `c | T` label a primitive Fourier/cyclotomic shell. Put

`q = T/c`.

The primitive-shell Möbius expansion only contains Reynolds widths `c*r` with
`r | q` and `mu(r) != 0`. Since nonzero Möbius indices are squarefree, the exact
least common denominator

`D_c = lcm { c*r : r | q, mu(r) != 0 }`

has prime exponent

`v_p(D_c) = v_p(c) + 1_{p | q}`.

Lean also proves

`c | D_c | T`.

Thus no new denominator prime is introduced by primitive-shell resolution, and each
conductor prime contributes at most one extra prime-power layer beyond the shell label.

## Cleared shell numerator

On integer cyclic packets `x : ZMod T -> Z`, v0.11 defines the unnormalized subgroup
Reynolds numerator for every divisor width, then forms the exact Möbius combination after
clearing `D_c`. The resulting integral linear map is `cyclotomicShellNumerator`.

The maximal integral shell lattice is

`L_c = { x : D_c divides cyclotomicShellNumerator(x)(t) for every t }`.

This is implemented as the kernel of reduction of the cleared numerator modulo `D_c`.

## Defect theorem

The residual defect is the image of the cleared numerator modulo `D_c`, and the first
isomorphism theorem gives

`Z^(ZMod T) / L_c ~= Defect_c`.

The defect is finite, is annihilated by `D_c`, and hence also by `T`. The lattice `L_c`
has a Smith normal form over `Z`, providing canonical invariant-factor data for the
integral failure of shell projection.

## Boundary

This block does not yet prove that a declared arithmetic sequence class automatically
lies in `L_c`. That requires importing the weighted root/trace cancellation estimates
from the p-adic transfer program. It also does not yet identify the Smith coefficients
with explicit Fitting ideals prime by prime.
