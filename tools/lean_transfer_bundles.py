"""Optional bounded transfers of unchanged, individually checked encoded assets."""
import json
from pathlib import Path
import re

from lean_module_packs import sha, DELIVERY_SHA256 as BASE_DELIVERY
from lean_proof_path_modules import DELIVERY_SHA256 as EXTENSION_DELIVERY
from lean_runner import safe_path

CATALOG_SHA256 = '5609899b76c98512a3f34c619c5e2194aeba2c87a58480c29d7f8e7a480c0ee1'
ASSET_COMMIT = '79b101ea1cf3f769baaa229039b09e8b03e60b07'
ASSET_PREFIX = 'https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/' + ASSET_COMMIT + '/lean-transfer-bundles/'
MAX_BYTES = 1024 * 1024
CATALOG_ASSET = 'transfers/catalog.json'


def read_catalog():
    from prepare_lean_wasm import UPSTREAM, LEAN, MATHLIB
    raw = (Path(__file__).resolve().parents[1] / 'manifests/lean-transfer-bundles.json').read_bytes().replace(b'\r\n', b'\n')
    if sha(raw) != CATALOG_SHA256:
        raise ValueError('Independent transfer catalog changed')
    catalog = json.loads(raw)
    if (catalog['schema'] != 1 or catalog['policy'] != 'encoded-artifact-bundles-v1'
            or catalog['max_bytes'] != MAX_BYTES or catalog['base_delivery_sha256'] != BASE_DELIVERY
            or catalog['extension_delivery_sha256'] != EXTENSION_DELIVERY
            or catalog['build'] != dict(upstream=UPSTREAM, lean=LEAN, mathlib=MATHLIB)):
        raise ValueError('Unexpected transfer catalog policy')
    return catalog, raw


def asset_url(path):
    if path == CATALOG_ASSET:
        return ASSET_PREFIX + 'catalog.json'
    if re.fullmatch(r'transfers/[0-9a-f]{64}\.bundle', path):
        return ASSET_PREFIX + path.removeprefix('transfers/')
    return None


def eligible(path):
    safe_path(path)
    return (bool(re.fullmatch(r'lean-mathlib/(modules|proof-path-modules)/[0-9a-f]{64}\.pack', path))
            or path.startswith('loose/') and path.endswith('.gz'))


def records(original):
    catalog, raw = read_catalog()
    members = catalog['members']
    selected = {path: row for path, row in original.items() if eligible(path)}
    if selected != members:
        raise ValueError('Transfer member identities changed')
    remote = {}; seen = set(); groups = []
    for group in catalog['groups']:
        path = group['file']; url = asset_url(path)
        if (url is None or path in remote or path != 'transfers/' + group['sha256'] + '.bundle'
                or type(group['size']) is not int or not 0 < group['size'] <= MAX_BYTES
                or not 2 <= len(group['members']) <= 1024):
            raise ValueError('Invalid bounded transfer identity')
        size = 0
        for member in group['members']:
            if member not in members or member in seen:
                raise ValueError('Duplicate or unknown transfer member')
            row = members[member]
            if type(row['size']) is not int or not 0 < row['size'] <= MAX_BYTES:
                raise ValueError('Invalid encoded transfer member size')
            size += row['size']; seen.add(member)
        if size != group['size']:
            raise ValueError('Transfer member lengths changed')
        remote[path] = dict(size=size, sha256=group['sha256'], url=url)
        groups.append(dict(file=path, members=group['members']))
    singles = catalog['unbundled']
    if len(set(singles)) != len(singles) or set(singles) & seen or set(singles) | seen != set(members):
        raise ValueError('Incomplete transfer member coverage')
    remote[CATALOG_ASSET] = dict(size=len(raw), sha256=sha(raw), url=asset_url(CATALOG_ASSET))
    plan = dict(schema=1, max_bytes=MAX_BYTES, catalog_sha256=sha(raw), groups=groups)
    return plan, remote


def verify(root, source):
    remote = source.get('remote_files', {})
    derived = {p: r for p, r in remote.items() if p.startswith('transfers/') or r.get('url', '').startswith(ASSET_PREFIX)}
    local = (root / 'transfers').exists()
    plan = source.get('transfer_groups')
    if plan is None:
        if derived or local:
            raise ValueError('Unrecorded transfer assets')
        return
    original = {p: r for p, r in remote.items() if p not in derived}
    expected_plan, expected_remote = records(original)
    if (local or set(source['files']) & set(expected_remote) or plan != expected_plan or derived != expected_remote):
        raise ValueError('Pinned transfer records changed or leaked into Pages')
