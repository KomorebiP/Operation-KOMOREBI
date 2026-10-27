# Execution notes

The accepted fresh Lean run and documented scientific/example runs passed. Development and reporting issues were retained rather than counted as successful checks.

An initial historical-object lookup failed because the older Technical Record intentionally contains object hashes but no object binaries. The review was corrected to verify the bytes actually present: source snapshots, command logs and declaration/runtime records. New compiled objects are supplied by the current run.

One post-run example-reporting probe raised KeyError because eight legacy visual records lack an arithmetic field. Field-aware extraction fixed the report; the successful scientific run was unchanged.

One package metadata edit was rejected before application because its patch named the same file twice. The edit was applied with valid update operations. No mathematical source was affected.

Reader builds can differ in PDF document identifiers while matching all reviewed page content and geometry. The recorded comparison distinguishes byte identity from pixel/text/link identity. A redundant monograph filename alias was omitted after confirming its bytes were identical to the canonical current monograph.

Package preflight also found a stale example submanifest: it listed a bytecode cache omitted from the release and two external Mathbox provenance helpers despite the handoff saying those helpers were outside the evidence tree. That handoff was incorrect. The public package excludes those three non-scientific files, retains their identities and the original staging manifest, and supplies a corrected exact delivery manifest. The nineteen declared scientific inputs and accepted run records are unchanged.
