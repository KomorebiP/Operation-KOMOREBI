# Canonical Examples

- `and_dag.json`: one fixed certified derivation plus optional discovery material
- `alternative_proofs.json`: two certified routes with different declared costs and values
- `set_cover_certificate.json`: direct finite Set Cover encoding used by the NP-completeness theorem

Run all three:

```powershell
proof-path validate .\examples\and_dag.json
proof-path core .\examples\and_dag.json
proof-path minimum .\examples\alternative_proofs.json
proof-path minimum .\examples\set_cover_certificate.json
```


## v1.1 finite realization bridge

`ambient_realization.py` illustrates a coherent finite view system, a positive GF(2) realization fiber, the information gained by observing one coordinate, and a separate checked impossibility witness for inconsistent protected data. Run with `PYTHONPATH=src python examples/ambient_realization.py`.

## v1.2 checked bridge

`data/bridge_examples.json` records four generated binary examples and their
stacked inputs. `formal/ProofPath/Generated.lean` contains the corresponding
kernel-checked solution, row-obstruction and count propositions.

`data/native_lean_field.json` is exported from five actual compiled Lean roots,
with direct dependencies as explicit external leaves. It is not recovered
discovery history. `scripts/verify_bridge.py` independently checks 5,039 binary
systems and the declared closure of this native field.

The finite patch examples and the counterexample to pairwise AND-rule coverage
are exercised in `tests/test_bridge_completion.py` and formalized in
`ProofPath.Field`, `ProofPath.Realization`, and `ProofPath.Examples`.
