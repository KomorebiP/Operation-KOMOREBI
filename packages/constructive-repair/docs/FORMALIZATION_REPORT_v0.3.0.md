# Constructive Repair v0.3.0: exact rational certificate bridge

## Result

The Python producer constructs a minimum-dimensional rational augmentation from an independently supplied pair of matrices D,R. The generated Lean certificates prove the four structural identities, the original correction equations, validity of all typed rational denominators, and a dimension lower bound against every competing rational augmentation.

The completed fresh verification is recorded in `evidence/verification/current/verification.json`. It reports 23 source modules, 227 named theorem declarations, 23 same-kernel module replays, complete transitive axiom coverage, 24 exported original problems, and six paired corruption rejections. The original 49 declarations in ten modules are unchanged. The new general matrix/decoding layer has 20 declarations. The remaining 158 new declarations are concrete input/certificate proofs, menu examples and rejection examples, not 158 independent mathematical discoveries.

## Mathematical construction

Input: D in Q^(m x n), residual matrix R in Q^(m x s).

Producer output: P,K,L,F,G,J,Q and the derived E,U,W,H. The verifier checks

    LD = 0
    DP + KL = I_m
    LR = FG
    JLRQ = I_t

It then constructs

    E = KF,   U = -PR,   W = -G,   H = JL.

The checked general theorem proves DU+EW=-R. For any competitor DU'+E'W'=-R with w added columns, multiplication gives (HE')(-W'Q)=I_t. This is a right inverse and proves t <= w. Thus the proposed augmentation attains the minimum.

The source also proves LR=0 iff the original matrix correction DX=-R exists, using the complete split. A zero detector alone is not sufficient. The hidden-obstruction rejection example checks this failure explicitly.

## New general source modules

- `RationalCertificates.lean`: repair and separator soundness, finite-menu optimum and complete-rejection soundness, dimension lower certificates, exact rank certificate soundness.
- `ConstructiveMatrix.lean`: explicit attaining repair, exact detection, constructed-optimum soundness, legal-image identity, numeric cell-decoding results.
- `Wire.lean`: typed matrix denominator validity and pointwise decoder correctness. Its numeric echo is diagnostic IO, not a premise in a theorem.

`MatrixMenus.lean` contains rational examples and exact reduction proofs for a two-entry optimum, a restricted-menu rejection, bad data, and rank certificates. `RejectedCertificates.lean` proves the corrupted checkers actually return false. The paired invalid files then try to use those false equalities as true equalities and must fail for that specific type mismatch.

## Executed Python work

- 34 unit tests, including malformed input, denominator rejection, duplicate JSON keys, floats, input substitution, code-injection text and algebraic corruption.
- 264 deterministic exact matrix problems, including 10 fixed examples and 254 seeded random examples.
- Independent SymPy rank calculations on all 264 problems. The checked output t equals rank[D|R]-rank(D) on all of them.
- 24 selected problems exported and proved in Lean. These cover zero target dimension, zero original-domain dimension, empty residual families, zero obstruction, full row rank, deficient rank and genuinely fractional data.
- 24 independently checked Lean input echoes match the original JSON entries.
- The unchanged v0.1.0 Python baseline was rerun: 20 unit tests, 3,307 case records and 71 assertions.

The ordinary matrix rank-difference formula is written in the monograph and checked experimentally. This release does not connect that formula to the earlier abstract cokernel API by a new general Lean theorem. The optimality proof instead uses the stronger concrete right-inverse certificate directly.

## Trust boundary

The certificate module imports D,R from a separately emitted fixed-input module. It cannot supply replacement D,R matrices in its certificate fields. Canonical input hashes, shape validation and a Lean-decoded echo check the external binding. Every generated matrix is decoded from typed integer/natural-number pairs, and every input/certificate proves that all its denominators are nonzero.

The whole JSON grammar, Python parser, source emitter, hashing and file system are not formally verified in Lean. The independent input echo is an executed cross-check of that boundary, not a new theorem about the external bytes. Mathematical correctness is established for the literal typed input that Lean compiles. The user still has to identify that input as the intended problem.

The practical elimination algorithm is intentionally outside the proof trust boundary. Its output is rechecked, not assumed correct. A parser error, false equation, missing witness, timeout or unsuccessful search is UNRESOLVED, never a universal no-repair result.

All 227 audited theorem dependency sets lie in {propext, Classical.choice, Quot.sound}. No sorryAx, extra assumption axiom or native-decision axiom is accepted. Concrete arithmetic uses `decide +kernel`. The same-kernel replay is Lean's own kernel against pinned imported environments, not an independent kernel and not a source rebuild of all Mathlib.

## Development failures retained

1. An interactive container session was unavailable; ordinary command execution worked.
2. The initial broad Mathlib.Tactic import was removed after an interrupted compilation. Minimal direct imports compile. An interrupted multi-module shell run was resumed, then superseded by the successful clean verification.
3. Plain `decide` did not reduce the rational matrix equalities in exported fixtures. It was replaced by `decide +kernel`, not `native_decide`.
4. The wire-validity proposition initially lacked a reducible decidability path. It is now an abbreviation of the finite pointwise predicate, and the wire module compiles.
5. A corruption probe's diagnostic was ambiguous about a stuck reduction. The final paired controls first prove that the corrupted check returns false, then require a separate false-to-true type mismatch. Unrelated errors do not count as successful rejection.

Source snapshots and compiler logs are retained under `evidence/development`. Only the final fresh verification record governs the release status.

## Remaining obligations

This is a completed rational augmentation certificate path, not completion of the entire constructive repair research program. Direct integration into the authoritative Komorebi Python package and Paper III Lean tree remains separate. A production rational-menu exporter is not supplied by the free-augmentation CLI, although the generic menu verifier and concrete rational menu examples are formalized. JSON parsing is tested but not fully formalized. No new result concerns unrestricted nonlinear repair, integral arithmetic realization, the universal Komorebi Space conjectures, or Paper XI Conjecture 66.
