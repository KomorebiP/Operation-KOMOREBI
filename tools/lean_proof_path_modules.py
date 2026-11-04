"""A bounded extension sharing qualified module delivery across two workspaces."""
import json
from pathlib import Path
import re

import lean_module_packs as base
from lean_runner import safe_path

COHORT = 'proof-path'
WORKSPACES = ('proof-path-compression', 'proof-path-recovery')
MANIFEST = 'lean-mathlib/workspaces/proof-path-compression.json'
ALIASES = {key: MANIFEST.removeprefix('lean-mathlib/') for key in WORKSPACES}
DIRECTORY = 'lean-mathlib/proof-path-modules'
RECEIPT_ASSET = 'lean-mathlib/proof-path-input-receipt.json'
DELIVERY_ASSET = 'lean-mathlib/proof-path-delivery.json'
RECEIPT_SHA256 = '6078bdd20109ef0f17365762f2424f3dbd71227c7d004703b0f144000db3d13e'
DELIVERY_SHA256 = 'c6ee64da33b72035da991968e27475fe3085b982ee0dead0342c0938f2351432'
ASSET_COMMIT = 'd91c4cd35509edc4e57bd19ee427bf4a36660ce2'
ASSET_PREFIX = 'https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/' + ASSET_COMMIT + '/lean-proof-path/'


def _read(name, digest, policy):
    raw = (Path(__file__).resolve().parents[1] / 'manifests' / name).read_bytes().replace(b'\r\n', b'\n')
    if base.sha(raw) != digest:
        raise ValueError('Proof Path independent receipt changed: ' + name)
    value = json.loads(raw)
    if value['schema'] != 1 or value['policy'] != policy:
        raise ValueError('Unexpected Proof Path receipt policy')
    return value, raw


def read_receipt():
    return _read('lean-proof-path-modules.json', RECEIPT_SHA256, 'proof-path-module-extension-v1')


def read_delivery():
    return _read('lean-proof-path-delivery.json', DELIVERY_SHA256, 'pinned-proof-path-module-delivery-v1')


def asset_url(path):
    metadata = {RECEIPT_ASSET: 'input-receipt.json', DELIVERY_ASSET: 'delivery.json'}
    if path in metadata:
        return ASSET_PREFIX + metadata[path]
    if re.fullmatch(r'lean-mathlib/proof-path-modules/[0-9a-f]{64}\.pack', path):
        return ASSET_PREFIX + 'modules/' + Path(path).name
    return None


def delivery_records():
    receipt, receipt_raw = read_receipt()
    delivery, delivery_raw = read_delivery()
    if (receipt['workspaces'] != list(WORKSPACES) or receipt['base_receipt_sha256'] != base.RECEIPT_SHA256
            or receipt['base_delivery_sha256'] != base.DELIVERY_SHA256
            or delivery['receipt_sha256'] != base.sha(receipt_raw)
            or delivery['base_delivery_sha256'] != base.DELIVERY_SHA256):
        raise ValueError('Proof Path receipt binding changed')
    original, _ = base.read_receipt()
    members = receipt['members']
    if any(members.get(path) != record for path, record in original['members'].items()):
        raise ValueError('Proof Path reused member identity changed')
    common, _, _ = base._delivery_records()
    common_packs = {next(e['path'][:-6] for e in p['entries'] if e['path'].endswith('.olean')): p for p in common['packs']}
    groups = base.module_groups(members)
    manifest = delivery['manifest']
    build = receipt['build']
    if (manifest.get('leanCommit'), manifest.get('mathlibCommit'), manifest.get('moduleExtension'), manifest.get('version')) != (
            build['lean_commit'], build['mathlib_commit'], COHORT, 'komorebi-proof-path-modules-1'):
        raise ValueError('Proof Path delivery build changed')
    if manifest['files'] != sorted(members) or len(manifest['packs']) != len(groups):
        raise ValueError('Proof Path delivery closure changed')
    remote = {}; reused = 0; encoded = 0
    for (module, paths), pack in zip(groups.items(), manifest['packs']):
        offset = 0; entries = []
        for path in paths:
            entries.append(dict(path=path, offset=offset, bytes=members[path]['bytes']))
            offset += members[path]['bytes']
        if pack['entries'] != entries or pack['bytes'] != offset:
            raise ValueError('Proof Path delivery member table changed')
        if module in common_packs:
            if pack != common_packs[module]:
                raise ValueError('Proof Path reused pack identity changed')
            reused += 1
        else:
            asset = 'lean-mathlib/' + pack['file']; url = asset_url(asset)
            if (url is None or asset in remote or pack['file'] != 'proof-path-modules/' + pack['sha256'] + '.pack'
                    or type(pack['compressedBytes']) is not int or pack['compressedBytes'] < 1):
                raise ValueError('Proof Path delivery pack identity changed')
            remote[asset] = dict(size=pack['compressedBytes'], sha256=pack['sha256'], url=url)
        encoded += pack['compressedBytes']
    if reused != len(common_packs):
        raise ValueError('Proof Path common module coverage changed')
    for path, raw in [(RECEIPT_ASSET, receipt_raw), (DELIVERY_ASSET, delivery_raw)]:
        remote[path] = dict(size=len(raw), sha256=base.sha(raw), url=asset_url(path))
    stats = dict(manifest=MANIFEST, workspaces=list(WORKSPACES), modules=len(groups), files=len(members),
                 reused_modules=reused, new_modules=len(groups)-reused, encoded_bytes=encoded,
                 new_encoded_bytes=sum(p['compressedBytes'] for p in manifest['packs'] if p['file'].startswith('proof-path-modules/')),
                 artifact_bytes=sum(m['bytes'] for m in members.values()),
                 original_pack_bytes=sum(p['bytes'] for p in receipt['input_packs'].values()),
                 receipt=RECEIPT_ASSET, receipt_sha256=base.sha(receipt_raw), delivery=DELIVERY_ASSET,
                 delivery_sha256=base.sha(delivery_raw), asset_commit=ASSET_COMMIT,
                 base_asset_commit=base.ASSET_COMMIT, new_pack_compressor=delivery['compressor'])
    return manifest, stats, remote


def build(source, output, workspaces, seeds):
    receipt, _ = read_receipt()
    if set(workspaces) != set(WORKSPACES) or {key: seeds.get(key) for key in WORKSPACES} != receipt['seeds']:
        raise ValueError('Proof Path import seeds changed')
    for manifest in workspaces.values():
        base._check_workspace(manifest, receipt)
    originals = base._checked_input_manifest(source, receipt)
    selected = {}
    for path, member in receipt['members'].items():
        selected.setdefault(member['source_pack'], {})[path] = member
    if set(selected) != set(receipt['input_packs']):
        raise ValueError('Proof Path original input coverage changed')
    # Validate one original pack at a time. No recompression or local binary
    # corpus is needed to publish the previously qualified immutable bytes.
    for name, expected in sorted(receipt['input_packs'].items()):
        compressed = (source / safe_path(name)).read_bytes()
        if len(compressed) != expected['bytes'] or base.sha(compressed) != expected['sha256']:
            raise ValueError('Proof Path original pack checksum changed')
        decoded = base._decode_exact(compressed, expected['decoded_bytes'], 'Proof Path original pack')
        original = originals.get(name)
        if original is None or original['bytes'] != len(decoded):
            raise ValueError('Proof Path original pack length changed')
        entries = {entry['path']: entry for entry in original['entries']}
        if len(entries) != len(original['entries']):
            raise ValueError('Proof Path duplicate original member')
        for path, member in selected[name].items():
            offset, size = member['offset'], member['bytes']
            if entries.get(path) != dict(path=path, offset=offset, bytes=size) or not 0 <= offset <= offset+size <= len(decoded):
                raise ValueError('Proof Path original member table changed')
            if base.sha(decoded[offset:offset+size]) != member['sha256']:
                raise ValueError('Proof Path original member checksum changed')
        del decoded, compressed
    if (output / DIRECTORY).exists() or any((output / path).exists() for path in (RECEIPT_ASSET, DELIVERY_ASSET)):
        raise ValueError('Proof Path binaries must remain outside Pages')
    return delivery_records()


def verify(root, record):
    extensions = record.get('module_extensions', {})
    remote = record.get('remote_files', {})
    derived = {path: row for path, row in remote.items() if path.startswith(DIRECTORY + '/')
               or path in (RECEIPT_ASSET, DELIVERY_ASSET) or row.get('url', '').startswith(ASSET_PREFIX)}
    local = (root / DIRECTORY).exists() or any((root / path).exists() for path in (RECEIPT_ASSET, DELIVERY_ASSET))
    path = root / MANIFEST
    manifest = json.loads(path.read_bytes()) if path.exists() else {}
    if not extensions:
        if derived or local or manifest.get('moduleExtension') or record.get('workspace_manifest_aliases'):
            raise ValueError('Unrecorded Proof Path module extension')
        return
    if set(extensions) != {COHORT}:
        raise ValueError('Unexpected module extension')
    expected, stats, expected_remote = delivery_records()
    if local or set(record['files']) & set(expected_remote):
        raise ValueError('Proof Path binaries must remain outside Pages')
    if record.get('workspace_manifest_aliases') != ALIASES:
        raise ValueError('Proof Path manifest aliases changed')
    duplicate = 'lean-mathlib/workspaces/proof-path-recovery.json'
    if MANIFEST not in record['files'] or duplicate in record['files'] or (root / duplicate).exists() or manifest != expected:
        raise ValueError('Proof Path pinned shared manifest changed')
    modules = sorted(p[:-6].replace('/', '.') for p in expected['files'] if p.endswith('.olean'))
    if any(record.get('workspace_modules', {}).get(key) != modules for key in WORKSPACES):
        raise ValueError('Proof Path workspace module set changed')
    _, _, common_remote = base._delivery_records()
    if (derived != expected_remote or extensions[COHORT] != stats
            or any(remote.get(path) != row for path, row in common_remote.items())):
        raise ValueError('Proof Path pinned remote records or totals changed')
