# PSC-I Machine Release v1.0.1

Canonical entrypoint: `PSC_I.machine.json`.

This release is intended for programmatic mathematical reasoning. The PDF is not part of the canonical interface. The bundled TeX is provenance/source material; machine consumers should load the KIR, AST, dependency graph, action registry, evidence index, and release status through the entrypoint.

## JSON API

```bash
python runtime/machine_api.py status
python runtime/machine_api.py record PSC-I-T-OPERATOR-RECONSTRUCTION
python runtime/machine_api.py deps PSC-I-T-BLOCK-MULTIPLICATION --transitive
python runtime/machine_api.py ast PSC-I-T-BLOCK-INTERTWINING
python runtime/machine_api.py actions PSC-I-T-BLOCK-INTERTWINING
python runtime/machine_api.py transport PSC-I-T-BLOCK-MULTIPLICATION profiles/packet_linear.json
python runtime/machine_api.py execute BLOCKIFY_OPERATOR tests/blockify_input.json
```

All commands emit JSON.

## Evidence discipline

`source`, `KIR`, `Python`, and `Lean` are independent evidence dimensions. Exact finite computation never becomes theorem proof. Historical Lean verification is preserved with its manuscript lineage and is not silently promoted to the current source. Unknown preservation of a directly required operation blocks the runtime operation-profile gate. Boundary guards are declarative caller-enforced constraints; the runtime returns them as metadata without evaluating them.

## Release meaning

`v1.0.1` freezes the machine interface and schemas for PSC-I. It does **not** claim that all 108 records are formally certified in the attached Lean source.

## Narrow correction in v1.0.1

Two corollaries now explicitly require every packet space to be nonzero: PSC-I-C-SUPPORT-PATTERN-STAR and PSC-I-C-SOURCE-COMPONENT-COUNT. Statements, AST, hypothesis metadata, and source hashes were updated. Proof bodies and computational action implementations are unchanged. Run `python runtime/nonzero_packet_regression.py` for exact zero-packet witnesses and corrected-statement checks. Historical v1.0.0 is retained separately as provenance.

The runtime transport gate checks direct operation flags only. It does not execute hypothesis classes or boundary guards.
