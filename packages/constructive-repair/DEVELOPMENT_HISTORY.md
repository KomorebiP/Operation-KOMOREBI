# Versioned development ledger

## Inherited v0.1.0

The unmodified baseline archive and its detailed Blocks A–C history are included under `inherited/`. It established exact linear and finite-menu experiments, arithmetic and holonomy regressions, and counterexamples to unrestricted repair claims. Lean was not executed in that audit.

## v0.2.0 / Formalization Block 01 / 19 October 2026

### Runtime recovery

The new environment initially lacked Lean/Lake on PATH and could not resolve the public download host. The existing portable runtime was recovered from five accessible `Lean_Compact_*.zip` Library parts. The joined payload is XZ-compressed despite an earlier working filename using `.zst`.

Joined payload: 2,220,147,424 bytes.  
SHA-256: `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.

The runtime reports Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. The dependency checkout reports Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The proof package uses those exact pins. No new runtime is bundled in the handoff.

### Completed proof work

1. Declared the correction equation and actual quotient obstruction.
2. Proved correction/vanishing, repair/image and family/span equivalences.
3. Proved the dimension lower bound and constructed an attaining map over a field.
4. Proved the stronger legal-subspace attainment and impossibility results.
5. Defined finite menu maps through actual coefficient sums and proved feasibility and monotonicity.
6. Proved conservation obstructions and invariant preservation.
7. Constructed the induced cokernel transport, naturality, faithful restriction and a disappearing-class witness.
8. Defined an executable finite-domain minimum-cost search and proved its soundness, optimality and complete rejection criterion.
9. Proved a quadratic arithmetic digit correction from Bezout data, with exact examples.
10. Formalized the menu/coarse-loss/nonlinear/modular counterexamples and computed the two finite optimizer examples.

The positive library contains 49 named theorem declarations in ten modules. Their novelty is not inferred from this count.

### Development failures and fixes

Compiler attempts are preserved individually, with the corresponding source bytes and SHA-256, under `evidence/development/`.

- A relative-file probe failed because `lake -d` did not change the subprocess's working directory. All final commands use the explicit project cwd.
- Initial proof drafts had local simplification, sign and API-name errors. They were corrected before final verification.
- An initial menu enumeration used a noncomputable finite-set conversion. It was replaced by a sorted finite universe and its computable sublists.
- The concrete kernel-evaluation proof needed `Fin.sort_univ`, not `Finset.sort_univ`.
- The derivative examples required a simplification-aware conversion of the actual `HasDerivAt` proofs. They are not placeholders.
- A standalone `leanchecker --help` invocation was killed. Inspection of the bundled source showed it does not implement a help mode: flags are separated and an absent module argument uses the current/default module. The final verifier supplies a single explicit module each time and uses sequential replay to avoid broad parallel work. No successful all-Mathlib replay is claimed.

### Verification status

The current structured verification record, not this prose, governs pass/fail status. It contains clean-source compilations, an audit of every theorem's transitive axioms, sequential same-kernel replay, rejection controls, and the newly replayed standard-library Python baseline. The allowed theorem axioms are `propext`, `Classical.choice`, and `Quot.sound` only.

The inherited source/code remains unchanged. Its `NOT_RUN` historical Lean metadata is intentionally retained, with new formal evidence stored separately.

### Unresolved obligations

- No direct import/integration with the authoritative Paper III Lean source tree yet.
- No proof connecting the Python Gaussian-elimination optimizer to the Lean finite-domain reference solver.
- No formal matrix rank-difference API theorem yet.
- No integrated graph/holonomy replay from the actual Paper III/Paper XI release yet.
- No general polynomial Hensel or infinite inverse-limit existence theorem in this block.
- No unrestricted nonlinear, arithmetic or categorical minimal-repair theorem.
- No general Komorebi Space semantic-realization theorem, actual Langlands realization, or change to Conjecture 66.
- No change to the established Komorebi Python library; this remains an isolated extension.

### Next restart point

Start from `lean/KomorebiRepair.lean` and the successful verification record. The most direct next step is a formally proved exact certificate checker for rational matrix repairs, including the quotient-rank formula and a serialization bridge to the existing Python prototype. This would allow the practical Python search to propose witnesses while Lean checks the original equations and optimality evidence. Keep graph reuse and genuinely domain-native repairs separate from that implementation-equivalence task.

### Verification harness correction

The first full verification correctly detected the deliberately injected axiom, but its control expected the fully qualified name while Lean printed the shorter name inside the namespace. The harness therefore stopped with FAIL rather than silently accepting it. Axiom display is now explicitly fully qualified. The failed verification and every diagnostic are preserved under `evidence/verification/attempt_01_control_name_failure/`; the complete verifier is rerun after this correction.

A subsequent manual review caught a weaker-than-intended negative control: its failure was a missing Decidable instance, not rejection of a false feasibility claim. That run is explicitly superseded. The control now checks the executable Boolean predicate and Lean reports that the proposition is false. The verifier now requires a control-specific diagnostic and rejects missing-instance failures. The full proof-and-control sequence is rerun after this hardening.

### Final verified state

The hardened full run passes: 10 proof modules, 49 named theorem declarations, complete axiom whitelist coverage, 10 sequential same-kernel replays, five intended compiler rejections, one forbidden-axiom policy rejection, and a fresh replay of the 20 Python unit tests and 3,307-case audit. A separate standard Lake build also passes. See `SUMMARY.json` and the current verification record for the exact scope.


## v0.3.0 / Rational certificate bridge / 19 October 2026

### Completed

Recovered the exact pinned Lean runtime and confirmed the archive checksum. Implemented a standard-library Python producer for P,K,L,F,G,J,Q and E,U,W,H. Original D,R inputs are serialized independently of certificate data. The producer constructs an attaining rational augmentation and checks its identities before export.

Added 20 general Lean matrix-certificate and typed-decoder theorems. They prove rational repair/separator/menu soundness, exact rank certificate soundness, the explicit right-inverse lower bound, exact split detection and the attaining construction. Added 24 concrete exported problems, each with six encoding/identity/optimality proofs, eight menu/rank examples, and six positive corruption-rejection proofs.

Fresh total: **23 modules, 227 named declarations, 23 same-kernel replays**, a complete axiom whitelist audit, six paired corruption controls and a separate forbidden-axiom policy control. The original ten modules and 49 declarations remain byte-for-byte unchanged. All 24 Lean input echoes match their original JSON values. The new Python unit suite passes 34 tests. The seeded 264-case exact matrix comparison agrees with independent SymPy ranks. The old 20-test and 3,307-case Python baseline was rerun successfully.

Executed the single-command `certify_one.py` workflow on a fractional input, with fresh generic/source compilation, axiom checks, same-kernel replay and input echo. It returned `KERNEL_CHECKED_OPTIMAL_REPAIR` with t=1. The logs and generated source are retained under `evidence/one_command_demo`.

Expanded the original monograph from 34 to 48 pages. Added exact rational certificates, constructive matrix attainment, a new declaration register and fresh execution evidence. The LaTeX source remains standalone.

### Failures and fixes

The first interactive tool session was unsupported. Ordinary container execution worked. A broad tactic-import compilation and one accumulated batch were interrupted; direct imports and bounded repeated commands succeeded. Plain `decide` got stuck on rational matrix reduction and was replaced with `decide +kernel`. The wire-validity predicate initially lacked a reducible Decidable instance and was corrected. Ambiguous negative-control diagnostics were replaced with positive rejection proofs plus deliberately invalid false-to-true uses. All final controls verify the intended diagnostic. Three typesetting overflows caused by long code tokens were fixed with breakable code paths. A wording ambiguity about zero added directions was corrected during visual review.

### Scope still open

The whole JSON parser, hashing and source emitter are tested but are not formally verified. Typed numeric decoding and matrix theorem soundness are formally checked. The rank-difference formula has an ordinary proof and independent exact tests but is not newly connected to the earlier Lean cokernel API. The Python free-augmentation search is not proved totally correct; its submitted answers are checked. A production rational-menu exporter and integration into the authoritative Komorebi Python library/Paper III tree are still separate. Nothing here closes an unrestricted nonlinear, integral, arithmetic, Komorebi Space or Conjecture 66 realization problem.

### Next restart point

Start from `scripts/certify_one.py`, `lean/KomorebiRepair/ConstructiveMatrix.lean`, and the PASS verification record. The rational construction-to-certificate path is operational. Next integrate this checker with the existing library's actual matrix API, or formalize the external parsing/statement-binding layer. Preserve the independent original input and the distinction between an invalid certificate and mathematical infeasibility.

## v0.4.0 / Costed rational menus / 19 October 2026

### Completed

Recovered the existing pinned runtime from the five mounted compact parts. The joined payload again matched SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7` before extraction. No public download or new dependency resolution was needed.

Added `RationalMenuCover.lean`: seven general theorems for column masking, downward separator validity, covered infeasibility, minimum-cost cover soundness, complete admitted-family rejection, and input-table/cost identities. Implemented the standard-library Python primal/dual producer, greedy rejection-cover compression, strict schema checks, original-data emitter, and `certify_menu.py` command.

Fresh combined verification: **37 modules, 378 declarations, 37 same-kernel replays**, with all 23 previous proof modules byte-for-byte unchanged. The added 151 declarations consist of seven general results and 144 concrete proofs. Twenty-four new exported cases have exact original-matrix, cost and admissibility echoes. Eight new paired corruption controls and six old controls pass. The separate forbidden-axiom policy control passes.

New tests: 50 unit tests; 120 exact rational-menu problems; 709 subset comparisons with independent SymPy ranks. Previous 34 rational unit tests and the original 20-unit-test/3,307-record audit were rerun. The positive fractional and negative four-candidate CLI workflows both completed compilation, axiom audit, same-kernel replay and input-binding checks. A deliberately exhausted trial budget returned UNRESOLVED, not no repair.

The monograph is expanded to 59 pages with the costed-menu/rejection-cover chapter, seven-theorem source map, case register, and fresh verification appendix. The previous proof and monograph archives remain unchanged under `inherited/`.

### Failures and corrections

The first cover proof used deprecated `if_true`/`if_false` names, which correctly failed under warnings-as-errors. The revised `ite_true`/`ite_false` version compiled. Both source versions and diagnostics are retained in development evidence. The free-repair CLI's audit selection is now restricted to the general modules it imports, rather than all general entries in an expanding registry. No mathematical assumption was added to fix either issue.

### Scope and next restart point

Start from `scripts/certify_menu.py`, `python/rational_menu.py`, `lean/KomorebiRepair/RationalMenuCover.lean`, and the PASS current verification record. The rational finite-menu exporter is now closed as an operational task. Search remains exhaustive with eight-candidate resource guardrails, and greedy certificate compression is not claimed optimal. Invalid evidence and timeouts remain UNRESOLVED.

Next: either add a certified-checker adapter to the actual current Komorebi Python library, or improve search through branch-and-bound while preserving certificate completeness and the independent original-input binding. Do not claim integration until the authoritative library tree is inspected. Full parser verification, exact quotient/rank API integration, native arithmetic realization, and nonlinear/global realization remain distinct obligations. No change to Conjecture 66 or universal Komorebi Space claims.


## v0.5.0 / Proof-carrying branch search / 19 October 2026

### Completed

Added the interval proof-tree checker and six general soundness/monotonicity theorems. Implemented a bounded exact branch-and-bound producer, strict original-input format, source/certificate export, and `certify_branch.py`. All-subsets admissibility requires no powerset table. Explicit admissibility scans only the original list. Search outcomes, witnesses, and costs are checked independently of the producer's elimination steps.

Fresh final combined record: **51 modules, 526 named declarations, 51 same-kernel replays**, complete axiom whitelist and source policy. All 37 v0.4.0 proof modules are unchanged. The increment is **six general and 142 concrete declarations**. Twenty-four new exports contain 18 optimal and six no-admissible-repair results. All original-input, weight and optional-table echoes match.

The new 50-unit-test suite passes. There are 204 exact recorded problems, of which 199 small cases agree with independent SymPy rational ranks over 3,173 subsets and with the old exhaustive producer. Five large structured cases exercise 24 candidates. Branch018 certifies minimum cost five with a five-node tree and six linear solves, covering 16,777,216 possible subsets. Branch019 rejects that many selections with one node and one solve. This is compact certification of structured examples, not a general scalability theorem.

Ten new paired corruption controls pass, as do the 14 old controls and a separate forbidden-axiom policy control. The previous 84 rational/menu unit tests and original 20-unit-test/3,307-case audit were freshly rerun. The final positive and negative 24-candidate CLI commands compile, audit, replay and echo the input successfully. A zero-node budget returns UNRESOLVED, not mathematical infeasibility.

The LaTeX monograph now has **68 pages**, with a proof-tree chapter and fresh declaration/case/evidence appendix. It compiled without overfull boxes, missing characters or unresolved references. All pages were rendered and inspected, with new dense pages examined individually. No fonts or large runtime are bundled.

### Failures and corrections

- The first Lean draft used the unavailable `Bool.and_eq_true.mp` API. Replaced by `Bool.and_eq_true_iff.mp`, with failed source and log preserved.
- Basename-only compile labels could overwrite evidence across namespaces. The verifier now uses full relative module names, rejects duplicate labels and refuses existing verification records. The earlier completed run is retained as superseded.
- The first explicit-table predicate had a mathematically valid but computationally wrong inferred decision implementation: it could enumerate every Finset instead of scanning the original list. Replaced by explicit `List.all`; the soundness proof and 24-candidate table regressions were rerun. The final verifier inspects the evaluator and rejects the hidden powerset quantifier. The interrupted run and previous source are retained.
- Input-echo equality now rejects boolean indices, which Python would otherwise compare equal to integers. Imported source names receive an explicit syntax check.
- The final test suite replaced one small case with a large nonhereditary-table regression and added a large empty-table case. The final count is 199 small plus five large, superseding the earlier 200-small development count.
- An orientation spill page and an awkward appendix heading were corrected in typesetting. No mathematical statement changed for layout reasons.

The final authoritative verification completed at 2026-10-19T18:18:59Z. Superseded attempts remain under `evidence/verification/`. The six general theorem dependencies use only the allowed axiom set, as do every other audited declaration.

### Remaining scope and next restart

The external parser/emitter and Python search are tested but not formally proved. Certificate checking is still potentially large, with no polynomial complexity or minimum-evidence claim. Current guards allow 24 candidates, 32-by-32 matrices, 4,096 listed admitted selections, and 8,191 tree nodes.

No authoritative library/Paper III integration, native arithmetic interpretation, universal nonlinear/integral repair, exact quotient-rank API integration, or change to Conjecture 66 is claimed. Komorebi Space supplies the ambient admissibility/realization viewpoint, not an automatic source of native mathematical witnesses.

Restart from `scripts/certify_branch.py`, `python/branch_menu.py`, `lean/KomorebiRepair/BranchCertificate.lean` and the PASS current record. The rational branch-certificate path is operational. The next useful block is an adapter to the actual current Komorebi Python matrix API after inspecting that authoritative tree, or a concrete domain-native constrained application with its own preservation proof.

## 1.0.0rc1 / Release hardening / 19 October 2026

### Scope freeze

The 51 v0.5.0 proof modules and 526 named theorem declarations are unchanged. The rational free-repair, weighted-menu and branch-tree specifications are frozen for the standalone component. No additional foundation, new theorem count, universal arithmetic claim, or main-library adapter is introduced.

### Completed implementation

Added the installable `komorebi-constructive-repair` wheel, public `komorebi_repair` API and `komorebi-repair` CLI. Python-valid status is deliberately separate from kernel-checked status. The source-archive Lean workflows remain the kernel-verification route. Existing rational, menu and branch wire schemas are unchanged.

Strengthened the exact-matrix constructor and immutable storage. Explicit dimensions can no longer be ignored, boolean indices are rejected, and mutable nested storage is rejected. A bounded binary read replaces stat-before-read file sizing. Explicit JSON nesting and integer-token limits protect the parser independently of the interpreter recursion limit. Certificates are also checked against the serialization-size ceiling.

Added a file manifest checker, reproducible offline wheel build command, public API contract, threat model and final-release gates.

### Failures, corrections and final tests

- An initial interactive tool session could not be allocated. Runtime recovery then succeeded with an ordinary process and verified the inherited five-part payload hash. No new runtime was downloaded.
- Baseline API probes confirmed three unwanted accepted cases: ignored explicit width, boolean indexing and mutable nested matrix storage. Each is now rejected by the appropriate regression test.
- The first new deep-nesting test failed because Python accepted more nesting than the test assumed. Added the explicit 128-level structural scanner, including a regression proving that bracket characters inside quoted strings are not counted.
- A second wheel build attempted in the same Python interpreter failed because build-backend state survived the first build. The final command uses a fresh interpreter for each build. Two cleaned local builds are byte-identical.

Final new unit tests: 56/56. Existing rational/menu unit tests: 134/134. All 72 shipped original/certificate pairs pass through the public interface. An additional 128 invertible-coordinate pairs yield 256 branch and 256 free certificate checks, with 1,348 independent subset-rank comparisons. The original 20-test/3,307-record audit is replayed by the full verifier.

Fresh complete formal verification: 51 modules compiled and replayed, 526 theorem axiom lists covered, 24 paired corruption controls, separate forbidden-axiom control, and all original-input echoes. The structured record has 141 commands and 230 passed checks. Permitted axioms remain propext, Classical.choice and Quot.sound.

A clean Python environment with no SymPy installed the wheel offline from outside the source tree. Its 24-candidate certificate was then supplied to the source-archive Lean workflow and received KERNEL_CHECKED_BRANCH_OPTIMAL_MENU. Two cleaned wheel builds matched byte-for-byte. The monograph is 74 pages, with clean LaTeX diagnostics and all pages rendered and visually inspected. Final archive checks are recorded externally to avoid a self-referential artifact hash.

### Remaining final-tag gates and restart point

Choose the public code/document licenses. Validate the intended additional Python and Windows/WSL combinations, or explicitly limit final support to the executed Linux/CPython combination. Accept and recheck the exact frozen archive before tagging final 1.0. None of those gates requires resolving a new mathematical conjecture.

Restart from `docs/RELEASE_READINESS.md`, `python/komorebi_repair/api.py`, `scripts/check_manifest.py`, and the current PASS formal record. Main-library/Paper III integration remains a separate source-informed adapter task. Do not infer that it was completed by this standalone wheel.


## v1.0.0rc2 / Portability and release gates / 19 October 2026

### Completed

- Recovered the existing offline kit from the five mounted chunks and verified the joined payload against the retained SHA-256.
- Reproduced the implicit-ASCII Lean-export failure and added explicit UTF-8 to the maintained text-I/O paths. Same-input export and a complete pinned kernel run now pass with UTF-8 mode disabled.
- Strengthened the free-repair runtime gate: exact Lean commit, exact Mathlib revision, and final certificate-source hash. Wrong-pin fixtures reject before compilation.
- Added `scripts/platform_acceptance.py` and `scripts/installed_probe.py`, exercising the installed wheel outside the source checkout with no SymPy or network index.
- Added twelve regression tests, bringing the current API/release suite to 68. The previous 134 rational/menu tests and original 20-test/3,307-record audit were replayed.
- Rebuilt and replayed all 51 unchanged Lean modules. All 526 declaration axiom lists, 24 paired certificate rejection controls and the forbidden-axiom policy control pass.
- Rebuilt the wheel twice from cleaned directories with identical output bytes. Tested 72 retained cases with 369 installed-probe assertions and 24 platform-workflow checks.
- Compiled and rendered the 77-page monograph, inspected all pages through contact sheets and the dense new pages at higher resolution. Corrected appendix placement after initial render review.
- Retained rc1 unchanged in `inherited/`. The new ZIP receives its own extraction/integrity/installed acceptance and kernel workflow report beside the archive.

### Failures and limits

The interactive tool session failed before command execution, then an attempted command saw its expected directory absent. Normal execution recovered the runtime afterward. Additional Python interpreter downloads failed DNS resolution and are not test passes. The first appendix insertion continued the preceding section numbers because it followed backmatter. It was moved and rebuilt. Product, layout and orchestration diagnostics are retained under `evidence/rc2_development/`.

Windows/WSL and additional interpreters remain untested. The declared release-tested scope is Linux x86_64 / CPython 3.13.5. The parser, emitter and Python search remain outside a fully formal implementation proof. No main-library or authoritative Paper III integration was performed.

### Next restart point

The technical candidate is frozen for its declared scope. Obtain the author's explicit code and monograph license choices. Add only the selected texts and metadata, rebuild the affected wheel/document, rerun the exact final archive checks, and tag the scoped 1.0 only after those checks. Do not invent licensing or reopen foundational research to fill this remaining publication decision. Expand platform support only after running `scripts/platform_acceptance.py` on the relevant machine.


## v1.0.0rc3 / Compact distribution and artifact consistency / 19 October 2026

The user's continuation did not select licenses. No permission grant or public
upload was made. The latest rc2 ZIP was recovered and its exact checksum matched
its recorded release receipt before extraction. Lean was recovered from the five
previously mounted compact parts; the full compressed hash matched the retained
pin. No external service received the source.

### Completed work

- Removed recursive predecessor ZIP embedding from the current distribution.
  Extracted 121 exact proof snapshots from v0.2.0/v0.3.0/v0.4.0/v0.5.0 archives
  and recorded their original archive hashes. The full verifier checks every
  snapshot against current code. Whole old archives remain separate artifacts.
- Added a release gate for the strict manifest, source-bound formal receipt,
  exact axiom inventory, wheel/source agreement, installed-wheel acceptance,
  current test-source bindings, and LaTeX/PDF build binding.
- Added 32 isolated artifact-binding regression tests. Synthetic receipts in
  those unit fixtures test checker structure and are not kernel proof evidence.
- Retained all Python engines/API/CLI byte-for-byte except package version.
  Retained all 51 mathematical modules, 526 theorem declarations and wire schemas.
- Consolidated the two chronological release appendices into one current release
  contract. Mathematical chapters and existing declaration registers are exactly
  retained. The monograph is 73 pages rather than 77.
- Created source-bound acceptance and document build receipts, with a read-only
  release gate that does not create local bytecode cache files.

### Development failures and corrections

- The first runtime recovery launch requested a streaming container session,
  which is not supported. No extraction command ran in that attempt. A normal
  subprocess recovered the runtime and verified its full hash.
- The first test command omitted the source import path, causing import errors.
  The tests now resolve their own known project source path. The same run exposed
  the old archive-path assertion and one implicit test-file encoding. The former
  now checks the exact provenance snapshots, and the latter explicitly uses UTF-8.
- The first passing Python acceptance was superseded after the document build
  script and artifact-fault runner were added. Its receipt remains separately
  labeled. The final acceptance was rerun against the final script bytes.

### Fresh verification

The full formal run completed 141 commands and passed all 230 checks, including 51 source
builds/replays, 526 axiom lists, 24 paired rejection controls, the deliberate
forbidden-axiom policy control, and the original 20-test/3,307-record audit.
The release acceptance passed 100 public/API/portability/artifact tests, all 134
engine tests, 72 installed input/certificate pairs, 369 installed assertions,
and 24 platform checks. Two clean wheel builds were byte-identical. The PDF
compiled cleanly and all 73 pages were rendered and visually inspected.

### Final artifact and next restart point

The separate extracted-archive report governs the final ZIP's checks. The fault
runner mutates a disposable extracted copy, regenerates its ordinary manifest,
and requires the source/receipt gate to reject the stale or corrupted artifact.
The 1.0 technical work is closed within the stated Linux/CPython scope; the author
must still choose code and document licenses. Do not invent a rights grant or
another foundational prerequisite. Any later license/metadata change needs a
new wheel, manifest and appropriate acceptance checks. Native Windows/WSL,
other interpreters, authoritative Paper III imports and main-library integration
remain separate, explicitly uncompleted scopes.
