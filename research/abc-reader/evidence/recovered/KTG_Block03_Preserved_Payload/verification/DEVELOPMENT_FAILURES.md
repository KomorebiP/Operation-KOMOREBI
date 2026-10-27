# Block 02 Development Failures and Corrections

All failures below were treated as diagnostic evidence.  None is counted as a
successful verification.

## 1. Missing runtime in the initial execution environment

The uploaded predecessor contained no active Lean or Lake executable.  The
seven archived offline-runtime parts were restored from the persistent library
and passed their individual and combined SHA-256 checks.

A full 23-test runtime self-check exceeded the command cap after passing Lean,
Lake, all nine pinned dependency checks, and the core arithmetic proof.  That
timeout was treated as inconclusive.  Project-specific checks were then run
with bounded commands and all passed.

## 2. Untouched predecessor build failure

Log: `current/baseline_build_lean_4.34.0-rc2.log`

The predecessor imported only `Std` but referred to `Set` and `Preorder` as if a
larger library supplied them.  The compiler reported an unknown `Set` and an
invalid class binder for the unresolved `Preorder`.

Correction: define dependency-free `KPreorder` and represent transport output as
a predicate.

## 3. Reserved field name in the grade bridge

Log: `current/block02_build_attempt01.log`

The field name `matches` was parsed as reserved syntax by the verified compiler.

Correction: rename it `grade_compatible`.

## 4. Countermodel reduction mismatch

Log: `current/block02_build_attempt03.log`

A direct `change True = False` did not unfold all wrapper definitions in the
hull-witness target.

Correction: explicitly simplify `HullWitness`, `Witness`, and the concrete
context/hull/measurement definitions.

## 5. Positive example orientation and Boolean conditional errors

Log: `current/block02_examples_build.log`

The normalization preservation equation required the symmetric orientation of
an equality proof.  A proposition-valued `if` was also mistakenly applied to a
Boolean.

Correction: use `Eq.symm` and a Boolean pattern match.

## 6. Verification-script regex error

The first verification-script run completed the clean Lake build but then
raised a Python `re.PatternError` because an inline multiline flag appeared
mid-pattern.

Correction: pass `re.MULTILINE` as the compile flag.  The entire verification
was rerun from scratch and passed.

## Final outcome

`verification/block02_final/verification.json` is authoritative.  Superseded or
failed logs are preserved only for provenance.
