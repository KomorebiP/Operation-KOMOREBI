# Progress ledger — publication 1.7.0 / Python 1.5.0

## Lineage

Started from the delivered 1.6.0 archive after checking all 406 predecessor
manifest entries. `editorial/baseline_1.6.0.json` records the source identity.
The eight original production Lean modules and existing Python implementations
other than the export/version module are unchanged. Historical compiler logs
are retained separately from the fresh `formal_1.7.0` record.

## Completed mathematical work

1. Reconciled the manuscript's attained-output decoder convention with Lean.
   Added iff, uniqueness, collision, composition, joint-task, and hashing laws.
2. Defined seeded closure on the actual Field type and proved least protected
   extension, exact obstruction, partial-value criterion, staged closure, and
   persistence under stronger observations.
3. Introduced typed node/rule transports, checked composition and derivation
   action, model pullback, explicit obstruction witnesses, and a counterexample
   to treating noninjective transport as an equivalence.
4. Proved that node-covering patches have universal gluing exactly when visible
   rules entail each original rule. This is a strengthening of the sufficient
   whole-support condition, not its withdrawal.
5. Added finite producers and independent result checkers, explicit worked
   examples, negative controls, exhaustive small-system comparisons, and two
   additional vector mathematical figures.

## Verification already obtained

The formal run builds and replays 13 modules, audits 149 explicit named
declarations, and includes 93 named theorem declarations. Six proof controls
are rejected for their expected diagnostics. An explicit-extra-axiom example
is accepted relative to the axiom by Lean and rejected by the release policy.
The latest integrated execution report and publication audit carry the exact
final test counts, timing, hashes, and output paths.

The extended finite search covers 1,024 three-node rule fields, 65,536 protected
problems, 223,232 node-covering patch families, 65,536 staged closures, 1,555
factorizations, 4,681 decoder-composition triples, and 22,621 joint-task tests.
These exhaustive finite domains are explicit and do not imply arbitrary-input
correctness of the software.

## Failure and correction record

- Initial runtime extraction exceeded one command timeout. An attempted
  streaming session was unsupported. A complete re-extraction succeeded and
  the pinned compiler/dependency checks passed.
- Recovery compilation first encountered deprecated tactic names under the
  warnings-as-errors policy. Correct names were used and all modules rebuilt.
- Initial obstruction replay rejected valid reuse when stronger observations
  made a prior rule conclusion already known. Witness replay now permits that
  redundancy; the stricter full-closure producer trace still requires new
  conclusions. A malformed witness target is checked before membership lookup.
- The exhaustive test harness initially mislabeled admitted nodes as ordinary
  claims. The input constructor rejected it. Corrected premise kinds were used.
- The first merged-context negative control failed due to an unavailable
  decision instance, not falsehood. Its logical conjunct was exposed explicitly
  and the control then failed with the expected false-proposition diagnostic.
- One pytest invocation omitted the source path and failed collection. The
  corrected source invocation and separately installed-wheel run are distinct.
- Figure generation exposed a missing empty-set glyph in an inherited caption
  and an unbraced mathtext font command in a new label. Both were corrected.
- Rendering exposed end-of-part and appendix orphans and a separated warning
  and retention chart. The prose was tightened, the chart placed with its
  warning, and the ledger/notation tables reflowed without shrinking body text.

Logs are preserved in `evidence/development_1.7.0/`. Do not relabel those failed
intermediate runs as successful checks.

## Remaining obligations

- Prove correctness of an executable closure/trace checker and relate its
  serialized Python certificates to the formal predicate definitions.
- Extend RuleTransport from single mapped rules to derivation-valued rules
  with an explicit translation contract. Characterize equivalences rather
  than infer them from a one-way map.
- Add semantic correctness of native proof-assistant adapters, beyond the
  existing executed syntactic declaration export.
- Complete selected remaining manuscript formalizations. Entropy interpretation
  and social/queue models retain their written and conditional scopes.
- Independent mathematical review, empirical study design, and a license
  decision are not manufactured by the internal release audit.

## Next restart point

Begin with `src/proof_path_theory/extension.py` and
`formal/ProofPath/Extension.lean`. Define a finite replay datatype in Lean,
prove that acceptance of its complete trace and final closure yields the least
seeded model, and connect both positive and forbidden-node JSON certificates
to it. Reuse the exhaustive fixtures before enlarging the scope. Keep the
current mathematical model and the implementation refinement theorem separate.

## Final publication pass

The current manuscript is 69 pages and retains all 131 prior mathematical
environments, adding 18. There are 41 result groups and 24 numbered vector
figures. The final review kept the new code example together and fitted the
implementation table to one page. Source and installed tests each have 169
passing cases. Delivery hashes are recorded after the final cleanup, separately
from the runtime execution report.
