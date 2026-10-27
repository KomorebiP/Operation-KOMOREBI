# AVOC Formal v0.25.0 — bounded generated-program synthesis

This cumulative release adds a deterministic proposer to the verified upgrade system.
Candidates are generated as Boolean expression trees, not selected from the old three
named components. The executed Lean checker proves equivalence over all eight possible
three-Boolean inputs before a generated program can be promoted. A protected campaign
reserves credit before search and persists the generated program and its replayable
promotion ledger.

**Current block:** 74 new named theorem/lemma declarations; 1,310 total; 136 current
local compilation targets; 63 substantive negative rejections. The 117 inherited
non-audit modules are byte-identical to the preserved v0.24 archive. Counts include
helpers and examples, not independent discoveries.

## First run

With the pinned runtime configured and current local modules built:

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python tools/synthesize_upgrade.py search examples/synthesis/pair.json
python tools/synthesize_upgrade.py run examples/synthesis/pair.json --run-dir /tmp/avoc-synthesis-new
python tools/synthesize_upgrade.py invoke --run-dir /tmp/avoc-synthesis-new
```

`search` is read-only and reports modeled charges; `run` first persists a protected
credit reservation, then generates/evaluates/promotes, and commits its result.
`inspect` and `invoke` recheck the persisted generated-program journal without rerunning
the synthesis enumeration. The directory must be new; no earlier run format is migrated.

## Demonstrations

- `pair.json`: generates `x0 AND x1` from primitive grammar, replacing a 6-node equivalent
  with a 3-node program. All 85 examined candidates are charged. Total declared charge
  6,971; benefit over 10,000 declared calls 30,000; endpoint net 23,029.
- `guard.json`: generates a 5-node three-flag conjunction from a 9-node reference after
  examining a 400-element prefix of a 21,845-entry grammar. Total charge 76,456; endpoint
  net 323,544 over 100,000 declared calls.
- `pair_unprofitable.json`: the same valid smaller program is promoted, but with only
  one declared call the complete search campaign has net -6,968.
- `guard_full.json`: sufficient credit and trial allowance to examine the full depth-2
  pool. The general theorem characterizes optimum over the incumbent plus that pool.
- `no_search_credit.json`: no unfunded enumeration; retains the original program.

The cost metric counts eager Boolean-expression visits and fixed conservative search
charges. These are not wall-clock speedups or full physical computation costs.

## Read these first

`FORMAL_THEORY.md` gives the contracts and proof boundaries. `PROOF_BOUNDARY.md` lists
non-claims. `REPRODUCE.md` gives exact commands. Current proof/test provenance is under
`results/v0.25.0/`; earlier results are historical. `THEOREM_INDEX.md` is the complete
name inventory. `GAP_LEDGER.md` distinguishes the new bounded proposer from the still-open
recursive-improver experiment.

Runtime binaries and the external dependency cache are not in this source package.
