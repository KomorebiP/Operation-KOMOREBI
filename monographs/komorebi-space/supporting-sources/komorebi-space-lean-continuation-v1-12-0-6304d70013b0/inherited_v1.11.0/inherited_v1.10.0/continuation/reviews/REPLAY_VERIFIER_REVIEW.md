# Cumulative and overlay verifier review

Review date: 2026-10-12. Scope: bounded, read-only review of `integration/scripts/common.py`, `assemble.py`, `verify.py`, `ExportAudit.lean`, and `integration/overlay/verify_overlay.py`. The cumulative run was still active during this review. None of its input files was edited.

## Conclusion

The compilation and axiom-audit architecture is sound for its stated trust boundary. The base build starts with an empty object directory, compiles the complete declared import closure, and audits the resulting imported declarations. The initial verifier versions have evidence-integrity gaps described below. These are gaps in what a terminal receipt alone establishes, not observed mathematical failures or evidence that any compiled theorem is invalid.

An independent terminal validator has been added outside the active verifier inputs at `integration/postflight/validate.py`. It must pass after the base run reaches terminal PASS and before the overlay is accepted. Its independent receipt is `base/postflight.json`. At the time this review was written, only its Python syntax and command-line interface had been checked; it had not yet validated the still-running base.

## Findings

### F1. The base snapshot recheck omits ancillary copied inputs

`scripts/verify.py` checks the assembled project and helper originals at entry and exit. Its copied workspace is checked at the end only through `graph(workspace)["source_sha256"]` (lines 248–249). That graph includes production source modules but excludes the copied control files, exporter, dependency pins, wanted-module list, type-selection list, and build configuration.

Consequently, persistent edits to those copied inputs during a run are not caught by the base verifier itself. Editing the original inputs would be caught. The overlay already hashes its entire constructed source snapshot before and after its own work, so this omission is specific to the base implementation.

The postflight validator compares the exact full workspace file inventory against the archive-bound project inventory plus the independently reviewed exporter hash. Extra files are also rejected. This closes the persistent endpoint discrepancy. No endpoint-hash scheme detects a transient edit restored before recheck, and no such edit was observed here.

### F2. The base object hash is captured before later compiler invocations

`scripts/verify.py` records `object_sha256` immediately after production compilation (line 215). The axiom exporter and controls then execute. The verifier does not compare the final object tree against that recorded object inventory before PASS.

This leaves a receipt-only gap between the recorded clean-build object set and the objects retained at completion. The original overlay checks the base object tree on entry, which helps when it is actually used, but the standalone base receipt does not perform that terminal check.

The postflight validator requires the final object tree to match the recorded post-compilation hashes and to contain exactly the 144 expected `.olean` paths. Missing objects, extra objects, and persistent changed bytes are rejected.

### F3. Initial overlay acceptance does not require a complete base command inventory

The reviewed initial overlay checks that the supplied base says PASS, says it was clean, reports source preservation and an axiom count, and has matching source, object, and log hashes. It then loops over whatever entries are present in `previous["commands"]` (initial lines 118–120). It does not require the expected complete label list or even a nonempty command list. It also does not anchor that base receipt to the independently reviewed source inventory and verifier schema.

Thus omission of a required compile, audit, or control entry from a supplied receipt is not itself detected by that acceptance loop. A self-consistent but incomplete receipt is insufficient evidence of a completed clean cumulative replay. No omission was observed in the active run.

The new postflight requires the exact unique ordered command sequence, exact compiler and Git argument lists, exact control inventory, correct schema, actual Lean execution, all graph fields, source-archive identity, reviewed inventory hash, and reviewed verifier hashes. The overlay coordinator has been asked to require the postflight PASS and revalidate its source, object, and receipt hashes before use.

### F4. Ordinary negative controls use a broad diagnostic predicate

Both initial executors reject timeout, signal exit, and several environment failures. Placeholder controls require `sorry`, and custom-axiom controls require their specific rejection messages. Other negative controls accept any positive error exit with `error` in the output and none of the listed environment substrings.

A syntax error, elaboration failure unrelated to the intended false claim, or unrelated unsolved goal could satisfy that predicate. The fixtures are individually archive-matched and their actual bodies were inspected in this review. They contain explicit false arithmetic, wrong protected values, normalized-certificate failure, finite-prefix misuse, and invalid regularization claims. Final retained logs should still be checked for the intended type mismatch or unsolved false goal before describing each control as a substantive rejection. The broad predicate by itself establishes only compiler rejection under the accepted environment checks.

The terminal validator preserves and rechecks those exact fixtures, command targets, log hashes, and specified diagnostic markers. It does not pretend to turn arbitrary diagnostic text into a semantic proof that the intended false claim was tested. This remains a small log-review obligation.

## Source and audit linkage that checks correctly

- `assemble.py` checks the frozen ZIP SHA-256, matches each copied module and control byte-for-byte against that archive, refuses nonidentical duplicate modules, and checks the 141-production-module/144-target scope.
- `common.graph` rejects missing local imports, local cycles, and production modules omitted from the combined root. Every module in the frozen tree uses the supported one-line import form. Its lexical scan is not relied on as the only axiom check.
- The base sets an isolated Lean search path with the empty fresh build directory first and only the explicitly pinned dependency caches after it. It does not import historical project objects.
- Every expected module is compiled with one worker, warnings as errors, and automatic implicit variables disabled. Compiler failures and timeouts cannot yield a normal successful compile command.
- `ExportAudit.lean` iterates the actual imported environment, attributes constants by originating module, calls Lean's transitive axiom collector, and rejects unsafe declarations or axioms outside `propext`, `Classical.choice`, and `Quot.sound`.
- The Python verifier checks nonempty and duplicate-free audit output, counts, module coverage, and the permitted axiom union independently of the exporter success code. Entry modules need not create declarations, but any declarations they do create remain included by the exporter.
- The overlay refuses to replace inherited source modules. It recompiles every supplied new module and the expanded combined root, then audits the full combined environment. Its advertised build scope correctly says incremental rather than clean cumulative.
- The overlay's exporter transformation inserts an actual Lean `splitOn "\n"` expression and extends type pretty-printing to new modules. The generated Lean still requires successful compiler execution. The string substitution is guarded by exact single-match checks.

## Trust boundary and review limit

The official compiler/kernel, shared runtime libraries, and pinned external compiled dependency caches remain trusted. Git revision and tracked-cleanliness checks are not proofs that imported cache objects were rebuilt from those sources. The recovered offline archive has independent part and combined hash evidence, recorded separately under `continuation/runtime/`.

This review did not add or rerun a large test suite. It did not modify running source or verifier inputs. It is an implementation review plus a terminal validation mechanism, not independent-kernel checking, universal Python verification, or a theorem-to-prose audit.

## Reviewed identities and postflight use

- Base verifier SHA-256: `c4235ab052f48b2dd1923e6ec7097f481ddc295f7877a6af29571577350b32b7`.
- Initial overlay verifier SHA-256: `8b8599cfdf8888a5867022670b349bb190189c40eda9e3853cd6fa50240bd6fa`.
- Independently reviewed inventory SHA-256: `dbcfb506fc91966fd3dbcd7f3d0aa4215109cf1932fb215b1b7872a8e2ed5614`.
- Exporter SHA-256: `62cb9468adf739e56c52f500abdd856c980efde62e5fc9e3d3581e2bbaa0ded6`.

After the base reaches terminal PASS:

```bash
python3 continuation/integration/postflight/validate.py \
  --base /absolute/path/to/continuation/integration/runs/cumulative_base_01
```

The validator refuses to overwrite an existing postflight receipt. Its PASS must not be inferred before it runs. Subsequent overlay changes must be recorded separately from the initial version reviewed here.

## Terminal base follow-up

The base run `cumulative_base_01` subsequently reached terminal PASS with 144 compiled targets, 4,842 audited declarations, two positive control files, and twelve rejection-control files. The independent postflight validator also reached terminal PASS. It confirmed all 178 expected command records, the complete copied source snapshot, final object identity, and retained audit/log hashes.

All twelve rejection logs were read individually after completion. Each exited with code 1 for the intended diagnostic below. The mathematical rows are compiler rejection checks for the supplied false claim or invalid application; they are not separately counted as new theorems.

| Control | Category | Observed diagnostic |
|---|---|---|
| `formal/AllProtectedProblemsFeasible` | False mathematical claim | The proposed protected correction leaves the goal `False`. |
| `formal/FalseArithmetic` | False mathematical claim | `decide` explicitly reports that `0 = 1` is false. |
| `formal/FinitePrefixesImplyPoint` | Invalid theorem application | Exact type mismatch between a nonempty finite partial space and a nonempty global point space. |
| `formal/UnnormalizedCertificate` | False mathematical claim | The proposed zero certificate leaves the goal `False`. |
| `formal/WrongPreservedValue` | False mathematical claim | The preserved-coordinate equality leaves the goal `False`. |
| `extension/OmitParameterGain` | False mathematical claim | The incorrectly strengthened error bound leaves the goal `False`. |
| `extension/ReverseDualInequality` | False mathematical claim | The reversed primal–dual inequality leaves the goal `False`. |
| `extension/ZeroParameter` | Invalid positive-parameter application | Supplying the forbidden zero parameter leaves the required goal `False`. |
| `formal/Placeholder` | Compiler placeholder rejection | `declaration uses sorry`. |
| `extension/Placeholder` | Compiler placeholder rejection | `declaration uses sorry`. |
| `formal/CustomAxiom` | Axiom-policy rejection | `AXIOM_POLICY_REJECTION` names the injected unapproved existence axiom. |
| `extension/CustomAxiom` | Axiom-policy rejection | Exact message `custom axiom rejected by the extension policy`. |

No reviewed rejection substituted a missing module, unknown identifier, timeout, compiler crash, or syntax error for the intended control. This closes F4 for this particular completed base run.

The hardened overlay was separately reviewed before launch. Its SHA-256 is `91d45234c2021cceb5dace273caf5ea1a5c9a2b2c792bf742d223f46d1dfeeff`. It requires the independent postflight PASS, exact base schema/graph/command inventory, complete source and object identity, and unchanged base evidence. It also records the exact post-compilation overlay object set, checks every reused inherited object, and verifies that those objects remain unchanged through the fresh axiom audit and controls.

## Terminal overlay follow-up

The overlay `wr01_wr02_overlay_01` subsequently reached terminal PASS. It compiled four targets over the accepted base objects and freshly audited the complete resulting environment: 4,872 declarations, including 30 declarations originating in the three new modules. The run completed four positive files, fourteen compiler rejection files, and two axiom-policy rejection files. It remains an incremental extension over the freshly checked clean base, not a second clean build of every inherited source.

All sixteen rejection logs were read individually. The twelve inherited controls produced the same intended diagnostics recorded in the base table. The four new controls produced the following diagnostics.

| New control | Category | Observed diagnostic |
|---|---|---|
| `WR01DropBudgetBound` | Required-budget hypothesis | The attempt to place the identity solution 2 in the budget-one ball leaves `False` in the `hbound` case. |
| `WR01ShrinkPreservedBudget` | False strengthened conclusion | A valid norm-two solution cannot be silently turned into a norm-one solution. The retained norm-two hypothesis leaves the proposed stronger goal `False`. |
| `WR02ConvexEquality` | False mathematical equality | The proposed affine energy equality for the merely convex example with points 1 and 2 leaves `False`. |
| `WR02MissingBudget` | Invalid theorem application | Exact type mismatch: the theorem still requires a uniform-budget witness, while the attempted goal supplies none. |

The two WR02 negative files include a copy of the production module before their deliberate final misuse. That prefix was compared byte-for-byte with the accepted overlay production source and matched in both cases. Their diagnostics occur only at the appended negative test, after the copied development.

Every reviewed negative log hash matched its terminal receipt. The hardened-overlay file hash matched the one recorded by the executed overlay. The base postflight status remains PASS. `NEGATIVE_CONTROL_DIAGNOSTIC_REVIEW.json` binds this review to both receipt hashes, all 28 rejection-log instances across the two scopes, the postflight receipt, and the hardened overlay verifier.

F1–F3 are closed for these accepted scopes by the independent base postflight and the hardened overlay gates. F4 is closed for these particular runs by individual diagnostic inspection. The generic executors' broad fallback rejection predicate remains a known limitation for future, different control fixtures. No missing environment artifact, syntax error, timeout, or crash was substituted for the intended rejection in either accepted run.
