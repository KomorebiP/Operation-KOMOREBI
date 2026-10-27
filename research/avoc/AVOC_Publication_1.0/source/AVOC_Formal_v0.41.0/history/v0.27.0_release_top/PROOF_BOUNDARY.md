# AVOC v0.27.0 — exact proof and runtime boundary

## Kernel-checked new scope

1. Constructor lower inequalities imply a node-cost lower bound for every finite expression, without a height bound, over any interpretation of the fixed syntax.
2. Realized semantic/cost witnesses attain the global minimum in that syntax. Accepted exact cost functions are unique; witnesses need not be syntactically unique.
3. Full Bool3 signatures coincide exactly with all-input equivalence. The finite checker covers every signature and every declared constructor inequality.
4. Accepted checked banks yield equivalent globally minimum-node queries, nonincrease, fixed optimum costs and zero further node savings.
5. Paid import/query/batch accounting conserves declared credit. Funded invalid checking retains its tariff; unfunded checking is not attempted.
6. A task-only future-saving bound follows from the certified minimum.
7. Successful source-data parsing connects the accepted rows to the executed checker. Loaded-query soundness/global minimality is proved.
8. Positive examples distinguish a valid lower table without witnesses and correct witnesses without the required lower inequalities.

## Concrete certificate and executable evidence

The delivered 256-entry bank passes the actual Lean importer, independently agrees with size-layer Python enumeration, and matches a fresh export of the existing Lean depth-three feedback generator. Sum of node costs is 1,640; maximum is 10. All 196,869 constructor/primitive checks pass in the executed checker.

A SEPARATE attempt to derive `checkBank concreteTable = true` by monolithic kernel reduction timed out after 30 seconds. It is not counted as a theorem or as successful static certificate reduction. Its source is preserved as `.lean.txt` in results/experiments and its timeout record is included. No `native_decide` or native-evaluation axiom replaced it. Generic checker soundness is kernel-checked; concrete checker execution relies on the installed compiler/runtime.

## Explicit exclusions

- The syntax remains three Boolean inputs, constants, not, and, or, xor. Global means arbitrary **finite tree height in this grammar**, not arbitrary software, DAG/circuit sharing, other operators, effects or a different cost objective.
- The generic algebra theorem does not supply a generalized arbitrary-signature or weighted-cost optimizer.
- File parsing has fuel 64 and a 4,096-node cap per expression; query batches cap at 512 and per-call credit at 1,000,000,000. Those runtime limits do not restrict the comparison class in the proved global minimum theorem.
- Only exact complete signatures are supported. No sampled/approximate equivalence or probabilistic semantic correctness is inferred.
- Validation tariffs are declared full-check accounting rates, not instrumentation of all actual work. Parser, shape validation, computing charges, list/array costs, arbitrary-precision arithmetic, proof erasure, allocation, IO, hashing, startup and runtime costs are not all included.
- Credits are supplied independently to each call. This is not a durable prepaid campaign wallet, a real payment system, or fee-idempotent interrupted validation. Timed-out or malformed calls are not treated as mathematical success.
- No claim that warm use is always cheaper than targeted search. Full revalidation can dominate small jobs. One-host timings are descriptive, not a calibrated break-even or physical speedup theorem.
- The new protected store is a fresh snapshot format, separate from earlier SQLite campaign, recovery and retry stores. No migration, overwrite, automatic repair or crash-resume is added.
- READY-last plus refusal of partial stores has tested controlled-exception behavior, not process-kill, power-loss, concurrency, hostile rollback or arbitrary TOCTOU guarantees. Direct symlink checks do not solve hostile path-component races.
- Python/file/JSON correspondence has bounded tests, not a universal formal refinement. Exact check success concerns supplied bytes/rows, not their historical provenance. Checksums are not signatures or remote attestation.
- Lean's kernel, compiler/interpreter, Std/JSON, pinned external caches, Python, OS, source pins and protected host remain trusted. A source proof is not a separately verified physical machine.
- No arbitrary Lean/mathlib artifact backend, production LLM use, scientific productivity measurement, new Boolean-identity novelty, or autonomous recursive self-modification is claimed.
- The stopping theorem ignores future benefits outside the declared current-task node-saving objective. Global node minimality does not imply globally optimal research strategy.

## Verification scope

54 new declarations, 1,447 total including helpers/examples, 135 non-audit modules, 150 local targets. All local final sources compiled against nine pinned external cache revisions. Full axiom audit: only propext, Classical.choice, Quot.sound. 71 substantive negative proof-file rejections. 25 wire cases, 644 funded global query comparisons, 5,152 individual truth checks, 13 store cases. Historical live, crash, retry and campaign suites were not rerun. The separate rewrite-transfer v0.26 branch remains separate.
