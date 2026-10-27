# Formal sources

`CoupledFormal.lean` is the new 29-declaration coupled-functions module. `CoupledFormalAudit.lean` lists every theorem for an exact axiom audit. Its definitions construct the infinite recurrence rather than assuming the six jet formulas.

`BrowserCoreLocal.lean` and `BrowserCoreAxiomAudit.lean` preserve the 39-declaration projector/coefficient core. The original source and its small compatibility patch are unchanged. That audit harness repeats the core source and is not a second independent declaration count.

`controls/` contains deliberately false statements and a placeholder fixture. They must be rejected. None is a production theorem.

Use `../tools/verify_coupled_block.py` with the stored compiler/cache and a fresh work directory. Read `../formalization/Block01/CLAIM_MAP.json` before translating a code result into a manuscript certification claim. No compiled cache is required inside this source package.
