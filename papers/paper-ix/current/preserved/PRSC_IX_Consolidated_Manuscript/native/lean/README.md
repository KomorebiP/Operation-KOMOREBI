# Finite affine obstruction

Author: Komorebi P.

`FiniteAffineObstruction.lean` proves a finite obstruction criterion for every
finite affine integer-linear system `A x = b`, for every positive integer modulus
`p` and every natural `L`. Primality is unnecessary for this affine result.

Starting from an actual solution modulo `p^L`, the proof constructs an integer
residual `r` with `A x - b = p^L r`. Its obstruction is the class of `r mod p` in
the quotient of `(ZMod p)^e` by the image of `A` reduced modulo `p`, viewed as an
integer module. This quotient is finite. Its class is zero if and only if there
is a solution modulo `p^(L+1)` having the original residue modulo `p^L`.

The arithmetic bridge is proved by exact affine transport and cancellation of
the nonzero integer `p^L`. It is not supplied as a hypothesis. Changing a base
representative by `p^L s` changes the residual to `r + A s`; the proof checks that
this leaves its quotient class unchanged.

This is an affine specialization. It does not formalize nonlinear native tower
objects, their Jacobian comparison, support growth, or a prime-independent
normalization theorem. It does not claim to finish the unrestricted conjecture.

## Replay

Use an extracted compatible portable Lean kit:

```sh
python verify_native.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /new/output/directory
```

The output directory must not exist. The verifier compiles project sources from
scratch, one Lean process at a time and one thread per process, with warnings as
errors. Mathlib and the toolchain come from the kit. All 13 declarations in the
main file and all four control theorems receive an explicit axiom audit. The only
permitted axioms are `propext`, `Classical.choice`, and `Quot.sound`.

The controls prove that an identity coefficient map is unobstructed and that a
zero coefficient map can have a nonzero obstruction. The concrete constant
system `0*x = -2` has a solution modulo 2 and none modulo 4. The verifier also
requires Lean to reject both an attempted unconditional vanishing proof and an
attempt to upgrade divisibility by 2 to divisibility by 4.

The successful run is `replay_02/native_affine_audit.json`: both positive modules
passed, both false strengthening attempts were rejected for type mismatches,
and all 17 declarations used only the listed axioms. There are no `sorry`,
`admit`, or added axioms in the checked Lean source files.
