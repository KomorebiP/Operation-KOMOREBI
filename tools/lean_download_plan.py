"""Conservative standard-library delivery plans for unchanged workspace imports."""
import json
import posixpath

from lean_runner import safe_path


def download_plan(root, record, mathlib_manifest=None):
    """Count unique response bodies, including the download record itself.

    All three standard-library roots are budgeted. The actual checker can need
    fewer; edited imports and switching modes can need the broader Mathlib layer.
    Asset paths use the worker's packBase rules, not the manifest file's folder.
    """
    records = {**record.get('remote_files', {}), **record['files']}
    assets = {'lean-wasm/lean.js', 'lean-wasm/lean.wasm.gz'}
    def layer(path, base):
        assets.add(path)
        manifest = json.loads((root / safe_path(path)).read_bytes())
        for item in [*manifest.get('packs', []), *manifest.get('loose', [])]:
            name = posixpath.normpath(posixpath.join(base, item['file']))
            safe_path(name)
            assets.add(name)
    layer('lean-wasm/core-layer.json', 'lean-wasm/core-lib')
    for name in ['Lean', 'Std', 'Batteries']:
        layer('lean-lib/' + name + '-layer.json', 'lean-lib')
    if mathlib_manifest is not None:
        layer('lean-mathlib/' + safe_path(mathlib_manifest), 'lean-mathlib')
    missing = assets - records.keys()
    if missing:
        raise ValueError('Download plan references unrecorded assets: ' + ', '.join(sorted(missing)))
    return dict(files=len(assets) + 1,
                bytes=sum(records[path]['size'] for path in assets) + (root / 'SOURCE.json').stat().st_size)
