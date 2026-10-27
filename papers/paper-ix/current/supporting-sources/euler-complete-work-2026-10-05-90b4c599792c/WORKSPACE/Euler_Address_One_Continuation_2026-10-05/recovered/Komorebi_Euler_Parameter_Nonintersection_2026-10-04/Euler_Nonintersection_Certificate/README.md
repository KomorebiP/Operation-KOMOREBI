# Euler parameter nonintersection certificate

Read `PROOF_AND_BOUNDARY.md` first. This is a computer-assisted arithmetic
continuation, not a Lean release and not a universal Euler simplicity proof.

For r=(17659+2^18*T)*2^640-161, the supplied certificate proves no critical
zero on Z_2 for every integer 0<=T<2^449, using the inherited exact Euler wall
and finite-precision multiplier template theorems stated in the proof.
For all other T retaining the true terminal label 161, only one residue class
modulo 2^450 can still contain a critical zero.

## Files

* `fast_parameter_certificate.py`: local-first template construction and two
  independent finite singular-locus solvers.
* `build_parameter_certificate.py`: slower global-first assembly used as a
  cross-check at 272 bits.
* `verify_parameter_certificate.py`: replay all retained certificates and
  independent arithmetic checks.
* `fast_certificate_629.json`: the main complete finite coefficient certificate.
* `VERIFICATION.json`: execution and check record, including failures and scope.
* `MANIFEST.json`: archive file hashes.

The source under `Euler_Closure_Attempt/Komorebi_Euler_Cubic_Unit_v26/checks/`
is the unchanged inherited Euler arithmetic engine. It is included so the
continuation is runnable without a separate archive.

## Replay

Python 3.10 or newer, standard library only. From this directory:

```text
python verify_parameter_certificate.py
python fast_parameter_certificate.py --precision 629 --out rerun_629.json
```

The constructor refuses to overwrite its named output. The verifier writes a
fresh `VERIFICATION.json` (timing metadata may change). Recreate a manifest after
intentionally changing retained outputs; do not confuse file integrity with a
mathematical proof.

No fonts, model weights or external runtime caches are included.
