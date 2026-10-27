# Strong Artin Lean v0.12.0 — Transverse obstruction reduction — Checked

This additive checkpoint continues v0.11 and formalizes the first-order obstruction splitting required by the cyclic-relative finite-depth lifting strategy.

## New checked content

`src/CyclicTransverseObstruction.lean` proves:

1. a block Jacobian `J_cyc ⊕ J_perp` correction equation is solvable iff its cyclic part is solvable, provided `J_perp` is surjective;
2. the kernel of the projection to the cyclic cokernel equals the range of the full block Jacobian;
3. consequently, the full cokernel is linearly equivalent to the cyclic cokernel;
4. when the cyclic block is zero, the full obstruction space is the cyclic output space itself;
5. in the scalar cyclic case this obstruction space has dimension exactly one;
6. the residual derivative of the quotient-prime cyclic defect polynomial is identically zero over `ZMod p`;
7. the one-step obstruction class vanishes for the full block iff it vanishes in the cyclic block; when the cyclic derivative is zero, this is equivalent to the cyclic residual coordinate itself being zero.

`src/ProjectorProbeSurjectivity.lean` proves:

8. separating projector/Frobenius probes give an injective evaluation map and hence a surjective dual probe map;
9. relative/transverse version: probes may vanish on a retained defect subspace `D`, and separation modulo `D` gives surjectivity on the dual of `V/D`.

`src/CyclicRelativeProbeObstruction.lean` composes the two mechanisms:

10. transverse probe separation modulo the retained cyclic defect makes the actual transverse correction map surjective;
11. the full first-order obstruction vanishes iff the scalar cyclic residual is zero;
12. in finite dimensions the full quotient-prime obstruction space has dimension exactly one.

## Exact boundary

This checkpoint **does not prove** that the actual Strong Artin transverse Jacobian is surjective, that all higher-order Hecke lift obstructions vanish, that a determinant-bearing Hecke carrier exists to the required finite precision, or Strong Artin.

The next theorem must connect the checked **transverse probe separation** criterion to actual global Taylor–Wiles/Frobenius probes in the Strong Artin quotient-prime deformation problem, and then retain that control through the finite precision required by the attachment theorem. Smith-weighted corrections, derived support, or integral finite-depth Smith/Tate descent remain candidate mechanisms.

See `RESEARCH_CHECKLIST.md` for the live goal ledger.

## Verification commands

Authoritative additive replay used for this checkpoint:

```bash
python3 verify_incremental.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This recompiles the inherited load-bearing cyclic-defect module plus all three new v0.12 modules. It returned exit code 0 in the release run.

`verify_full.py` is also included to replay the complete v0.11+v0.12 source set. In the current execution environment the outer wrapper hit its wall-clock limit after the log itself reached the final PASS line, so that aggregate run is retained as non-authoritative timing evidence rather than the release certificate.
