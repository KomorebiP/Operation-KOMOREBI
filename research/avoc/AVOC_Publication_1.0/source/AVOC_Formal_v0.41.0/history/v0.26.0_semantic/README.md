# AVOC v0.26.0 — verified semantic reuse in bounded synthesis

This cumulative source release extends v0.25 with an executable, kernel-checked semantic representative library. Later grammar layers are generated from the smallest retained program for each exact behavior rather than from the full preceding syntax pool. The finite search loses no attainable behavior or minimum-node solution at its declared depth.

**Scope:** three Boolean inputs, total pure expressions, exact eight-input semantics, finite grammar depth, and declared structural charges. This is generated-library feedback in a fixed synthesizer. It is not autonomous source modification, a new Boolean-identity claim, a production LLM experiment, or a general recursive-improvement result.

## Results

- 83 new theorem/lemma declarations; 1,393 complete audited declarations. These include helper lemmas and examples.
- All 144 local compilation targets pass against the pinned external cache; all 1,393 axiom reports contain only the permitted standard foundations.
- All 67 negative files reject substantively.
- Frozen and feedback search agree on every attained truth table and minimum node count at matched depths 0, 1, and 2.
- At depth 2, frozen construction emits 21,935 cumulative candidates and costs 4,226,171 structural units. Feedback emits 991 cumulative candidates and costs 293,631 units. Both retain 109 behaviors.
- Feedback depth 3 was executed and retains all 256 possible three-input Boolean behaviors. Frozen depth 3 was not executed.
- Existing 123 non-audit source modules are byte-identical to v0.25.

## Start here

Read `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md`, and `REPRODUCE.md`. Current evidence is under `results/v0.26.0/`. Earlier versioned evidence remains historical.

After setting up the pinned runtime and building:

```bash
python tools/run_semantic_synthesis.py examples/semantic/feedback.json
python tools/run_semantic_synthesis.py examples/semantic/frozen.json
python tools/run_semantic_synthesis.py examples/semantic/budget.json
python tools/run_semantic_synthesis.py examples/semantic/campaign.json
```

The new wrapper is read-only apart from temporary requests and output. It does not install generated code, change protected proof stores, or persist/reload semantic libraries. `campaign` executes the existing promotion function in memory and includes search and query charges. Other query output is explicitly diagnostic and its cost is reported separately from search credit.

The ZIP excludes the Lean runtime, external dependency caches, and compiled local outputs. Rebuilding is necessary on another installation.
