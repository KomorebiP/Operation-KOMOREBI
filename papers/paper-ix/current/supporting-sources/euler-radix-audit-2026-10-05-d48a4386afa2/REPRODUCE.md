# Reproduce the radix checkpoint

Use Python3 and its standard library, from this package root. No Lean build
is needed or asserted. `radix_closure/CURRENT_EVIDENCE.json` identifies current
runs and distinguishes superseded development evidence.

## Validate the four current runs

```bash
python3 audit_helpers/validate_manifest.py radix_closure/radix_descent/certified_run_reviewed/manifest.json --root .
python3 audit_helpers/validate_manifest.py radix_closure/cartier_mask/certified_run_final/manifest.json --root .
python3 audit_helpers/validate_manifest.py radix_closure/cross_radix/certified_run/manifest.json --root .
python3 audit_helpers/validate_manifest.py radix_closure/bridge_inventory/certified_run/manifest.json --root .
```

The independent reviewers replayed all four checkers and obtained identical
scientific results. Cross/Cartier have separately recorded replay manifests;
the other independent review records its exact replay comparisons.

## Replay exact scientific checks

Use a fresh directory named replay. The first three checkers accept output
paths. The bridge checker has a fixed relative output path, so run it from
an isolated directory as shown to preserve the recorded result.

```bash
mkdir replay
python3 radix_closure/radix_descent/check_radix_jets.py replay/radix.json
python3 radix_closure/cartier_mask/check_cartier_mask.py replay/cartier.json
python3 radix_closure/cross_radix/check_cross_radix.py --out replay/cross.json
mkdir -p replay/bridge/radix_closure/bridge_inventory/certified_run
(cd replay/bridge && python3 ../../radix_closure/bridge_inventory/check_bridge_gates.py)
```

Compare against the results.json next to each current manifest. Cross output
records the Python version, so a different interpreter can change that one
metadata field; every scientific value and script hash must still match.
The exact checks are bounded. Their role and limits are stated in each
contract and proof note.

## Verify the complete package

`SOURCE_HASHES.json` records every delivered file except itself. Verify with:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json
for item in json.loads(Path('SOURCE_HASHES.json').read_text()):
    path=Path(item['path'])
    assert path.stat().st_size == item['bytes'], path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], path
print('All delivered file hashes match.')
PY
```

The recovered source ZIPs and selected extracted text sources are included
with their original hashes. The previous Euler checkpoint is included as an
unchanged ZIP. Its earlier proof lineage and reproduction instructions remain
inside that archive; inherited results are not relabeled as new executions.
