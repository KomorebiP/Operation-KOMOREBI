# Fresh integrated Lean verification: PASS

The unchanged accepted Komorebi Space formal core passed a fresh integrated run
on 25 October 2026. All 229 mathematical, control and verifier input hashes match
the accepted predecessor. No production source or verifier change was needed.

| Actual check | Result |
|---|---:|
| Compiled project targets | 166 |
| Production modules / import roots | 162 / 4 |
| Explicit source theorem and lemma declarations | 1,859 |
| Exported declarations audited | 5,339 |
| Compiled theorem constants, including generated auxiliaries | 3,863 |
| Required commands completed | 262 |
| Positive / elaboration-rejection / policy-rejection controls | 18 / 35 / 3 |
| Timed-out commands | 0 |
| Runtime byte-hash records checked at both endpoints | 130,289 |

All 56 controls had their specified outcomes. The actual transitive axiom union
was `Classical.choice`, `Quot.sound`, and `propext`. Source, object and installed
runtime identities remained unchanged. The full run took 879.115414
seconds; this is an observed execution duration, not a performance guarantee.

The fresh declaration inventory is byte-identical to the accepted predecessor
inventory. Its SHA-256 is `330af11c1d498550db59e3ebe08b53ae05d2d68fc007ce25694b70aad04f78ec`. The completed run receipt
is `run01/receipt.json`, SHA-256 `a81f43744c91ae8873a69d11e32f924156061f8cbb48c0928536d97dbd15c2be`.

The 16 principal theorem-group coverage is the retained accepted mathematical
scope. These declaration and command counts are code/evidence inventories, not
counts of independent discoveries. This run does not add formal statements or
certify every printed illustration or alternate proof route.

The run used the saved pinned Linux Lean 4.34.0-rc2 runtime, the matching external
dependency cache, and the shipped executable-path adapter. All nine Git revisions
were checked, with no tracked changes. There were no failed integrated Lean
attempts in this closeout. Historical failures remain historical evidence.

This was fresh project compilation, a recursive axiom audit and the mixed control
suite. It did not invoke a separate `leanchecker` object replay, rebuild upstream
dependencies, establish an independent kernel, perform a new whole-book semantic
audit, or qualify native Windows execution. `FRESH_REPLAY_GUIDE.md` gives the
setup and reproduction boundary; `FRESH_REPLAY_SUMMARY.json` gives the exact
machine-readable summary.
