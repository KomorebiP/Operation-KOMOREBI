# Komorebi Neuralese Invariant Observable Kernel v0.6.0

**Author:** Komorebi P.

This developmental block tests whether the recurrent-instability problem is
better posed as an ambient-space closure problem: preserve a seven-dimensional
observable quotient while making its five-dimensional centered-observation
kernel forward invariant.

## Current outcome: stopped at calibration

The final pre-screen rehearsal on retired development seed `887` triggered the
frozen stop rule. **Untouched screen seed `947` was not run, and the five-seed
pilot was not opened.** The retained outcome is therefore calibration-only,
not screen evidence and not a failed confirmatory experiment.

The compiled hard-kernel arm demonstrated the intended structural mechanism:
rank-seven observation, negligible semantic/null cross-block leakage, bounded
orthogonal recurrence, and nontrivial dormant ambient curvature. It did not
learn a sufficiently flat observable action. Its robust D4 accuracy fell from
`1.0000` at depth 32 to `0.8555` at depth 128 and `0.3984` at depth 512; its
semantic path-defect median/p95 were `0.0511 / 0.0879`, missing the registered
`0.02 / 0.08` limits.

The unrestricted learned-intertwiner arm retained `0.8203` robust accuracy at
depth 512 and achieved small local centered-readout and generator leakage, but
it did not produce the registered quotient. The suffix observer remained
rank 12, `sigma8/sigma1` was `0.04995` rather than at most `0.001`, and
length-64 leakage reached `0.3569` at p95 and `0.6556` at maximum.

A posthoc no-training localization then held the quotient action exact. Both
the exact quotient and quotient-curved ambient controls retained `1.0000`
robust accuracy through depth `16,384`. This shows that ambient curvature is
compatible with stable semantics; the failed learned arms retained approximate
quotient composition error.

These results support a narrow engineering diagnosis:

> Exact radial stability and small one-step cross-block residuals do not imply
> global observable closure. Small angular/path errors can accumulate under
> products, while behavior remains temporarily strong.

The exact retained numbers and stop decision are in
`results/invariant_kernel_seed887_final_rehearsal/REHEARSAL_SUMMARY.json`.
They may guide a later block, but they cannot be promoted into v0.6 evidence.

## Ambient-space formulation

Let the declared behavioral interface be centered logits,

\[
C=I_8-\frac18\mathbf 1\mathbf 1^\mathsf T.
\]

The block studies the exact sequence

\[
0\longrightarrow N\longrightarrow H
\xrightarrow{\Pi}\bar S\longrightarrow0,
\]

with `dim(H)=12`, `dim(Sbar)=7`, and `dim(N)=5`. Scientific content requires
more than a rank-seven map: `N` must equal the centered-readout kernel, remain
invariant under every executed generator, and induce a noncollapsed,
behaviorally correct action on the quotient.

The compiled positive control registers the finer typed split

\[
H=S_h\oplus L\oplus K,
\qquad (\dim S_h,\dim L,\dim K)=(7,1,4),
\]

and executes

\[
M_g=W\operatorname{diag}(A_g,1,R_g)W^\mathsf T.
\]

Here `L` is the common-logit gauge line and `K` is a dormant ambient fiber.
The learned arm identifies only an untyped candidate split `H=S_h+N`; it does
not establish a learned `L/K` decomposition or useful ambient memory.

## Six-arm developmental panel

| Arm | Geometry | Role |
|---|---|---|
| `polar_supervised` | unrestricted `O(12)` | terminal/construction baseline |
| `polar_cr` | unrestricted `O(12)` | inherited composition/return baseline |
| `polar_exact` | unrestricted `O(12)` | full-space relation-flat comparator |
| `learned_intertwiner` | unrestricted `O(12)` plus learned `Pi(7x12)` | explicitly induced quotient test |
| `hard_kernel_supervised` | compiled `7+1+4` split | architectural sufficiency control |
| `hard_kernel_semantic_flat` | compiled `7+1+4` split | semantic-flat positive control |

The learned observer is initialized from the instantaneous centered-readout
rowspace. This is output-informed, data-free scaffolding: it uses no operator,
example, target value, continuation, or future observability information, but
it is still an initialization advantage. The quotient-anchor loss constrains a
basis-free centered-simplex Gram matrix rather than selecting a Helmert chart.

Every profile uses the first eight accepted terminal contexts per update and
all nine anonymous relation cells per context. The 72 context-cell terms are
averaged, not summed, and the same deterministic contexts are paired across all
six arms.

## Run and verify

Python 3.11 or newer is required. Install the dependencies in
`requirements.txt`; no model download or network access is needed.

On Windows PowerShell, run the 40-step infrastructure smoke in a fresh,
timestamped directory:

```powershell
.\RUN_INVARIANT_KERNEL_SMOKE.ps1
```

Verify a particular retained v0.6 result directory:

```powershell
.\VERIFY_INVARIANT_KERNEL.ps1 --result-dir C:\path\to\completed\v0.6\run
```

After the final manifest is built, verify the complete package, all tests, the
retained smoke, and the calibration-stop receipt:

```powershell
.\VERIFY.ps1
```

Equivalent direct commands are:

```powershell
python -E -P -B .\run_invariant_kernel.py --profile smoke --output-dir .\results\local\invariant_kernel_smoke
python -E -P -B .\verify_invariant_kernel.py --result-dir .\results\local\invariant_kernel_smoke
python -E -P -B .\verify_package.py
```

`RUN_INVARIANT_KERNEL_SCREEN.ps1` deliberately refuses to run while the
retained calibration decision is `CALIBRATION_FAILURE_STOP_BEFORE_SCREEN`.
This protects untouched seed `947` and enforces the preregistered branch rule.

The runner refuses to overwrite a nonempty output directory. The smoke and
screen launchers use timestamped paths under `results/local/`, which are
excluded from the archival manifest. Smoke results test execution and assay
integrity only; they carry no scientific adjudication.

## Reading order

1. `INVARIANT_KERNEL_CALIBRATION_FINDINGS.md`
2. `results/invariant_kernel_seed887_final_rehearsal/REHEARSAL_SUMMARY.json`
3. `results/invariant_kernel_seed887_final_rehearsal/POSTHOC_EXACT_DEPTH.json`
4. `AMBIENT_SPLITTING_THEOREM.md`
5. `NEXT_CONNECTION_BLOCK.md`
6. `INVARIANT_KERNEL_PROTOCOL.md`
7. `INVARIANT_KERNEL_PREREGISTRATION.json`
8. `DEVELOPMENT_LOG.md`
9. `AMBIENT_CONNECTION_SYNTHESIS.md`
10. `LINEAGE.md`

## Claim boundary

The v0.6 calibration supports only the diagnosis above and the feasibility of
the compiled invariant-fiber construction. It does not establish an induced
invariant kernel in the unrestricted model, spontaneous Neuralese, useful
ambient memory, architecture-independent emergence, a learned cross-model
language, unlimited stable recurrence, the mechanism of a pretrained language
model, awareness, or consciousness.
