"""One bounded delivery pilot over independently pinned compiled module bytes.

This changes transport only. It never compiles or certifies a paper proof.
The committed receipt predates these outputs and binds every original member.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import tempfile
import zlib

from lean_runner import safe_path

WORKSPACE = 'paper-iii-coordinate-naturality'
POLICY = 'complete-module-triplets-from-pinned-packs-v1'
RECEIPT_SHA256 = '81e6d232bf87d801218adebf366a512bab541b8f31c57932bf4ce7de89981c34'
RECEIPT_ASSET = 'lean-mathlib/module-pilot-receipt.json'
MANIFEST = 'lean-mathlib/workspaces/' + WORKSPACE + '.json'
MODULE_DIRECTORY = 'lean-mathlib/modules'
SUFFIXES = ('.ir.sig', '.olean', '.ir')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _decode_exact(compressed, expected, label):
    # The independent receipt supplies the allocation bound, never a mutable
    # output manifest's claimed decoded size.
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(expected + 1)
    if len(raw) != expected:
        raise ValueError(label + ' length mismatch')
    return raw


def read_receipt():
    raw = (Path(__file__).resolve().parents[1] / 'manifests/lean-module-pilot.json').read_bytes().replace(b'\r\n', b'\n')
    if sha(raw) != RECEIPT_SHA256:
        raise ValueError('Module pilot input receipt changed')
    receipt = json.loads(raw)
    if receipt['schema'] != 1 or receipt['policy'] != POLICY or receipt['workspace'] != WORKSPACE:
        raise ValueError('Unexpected module pilot input policy')
    return receipt, raw


def module_groups(members):
    result = {}
    for path in members:
        safe_path(path)
        suffix = next((suffix for suffix in SUFFIXES if path.endswith(suffix)), None)
        if suffix is None:
            raise ValueError('Unexpected module artifact: ' + path)
        result.setdefault(path[:-len(suffix)], []).append(path)
    for module, paths in result.items():
        if set(paths) != {module + suffix for suffix in SUFFIXES}:
            raise ValueError('Incomplete module triplet: ' + module)
    return {module: sorted(paths) for module, paths in sorted(result.items())}


def _checked_input_manifest(source, receipt):
    expected = receipt['upstream_manifest']
    raw = (source / safe_path(expected['path'])).read_bytes().replace(b'\r\n', b'\n')
    if len(raw) != expected['bytes'] or sha(raw) != expected['sha256']:
        raise ValueError('Module pilot upstream manifest changed')
    manifest = json.loads(raw)
    build = receipt['build']
    if (manifest['leanCommit'], manifest['mathlibCommit']) != (build['lean_commit'], build['mathlib_commit']):
        raise ValueError('Module pilot upstream build mismatch')
    packs = {}
    for pack in manifest['packs']:
        name = 'lean-mathlib/' + pack['file']
        safe_path(name)
        if name in packs:
            raise ValueError('Duplicate module pilot input pack')
        packs[name] = pack
    return packs


def _check_workspace(manifest, receipt):
    expected = receipt['members']
    if len(manifest['files']) != len(expected) or set(manifest['files']) != set(expected):
        raise ValueError('Module pilot workspace closure changed')
    seen = set()
    for pack in manifest['packs']:
        if not re.fullmatch(r'\.\./shared/artifacts-[0-9]{3}\.pack', pack['file']):
            raise ValueError('Unexpected module pilot workspace pack')
        source_pack = 'lean-mathlib/' + Path(pack['file']).name
        origin = receipt['input_packs'].get(source_pack)
        if origin is None or (pack['sha256'], pack['compressedBytes'], pack['bytes']) != (
                origin['sha256'], origin['bytes'], origin['decoded_bytes']):
            raise ValueError('Module pilot workspace pack identity changed')
        for entry in pack['entries']:
            path = entry['path']
            member = expected.get(path)
            if path in seen or member is None or (source_pack, entry['offset'], entry['bytes']) != (
                    member['source_pack'], member['offset'], member['bytes']):
                raise ValueError('Module pilot workspace member changed: ' + path)
            seen.add(path)
    if seen != set(expected):
        raise ValueError('Module pilot workspace members incomplete')


def build_module_pilot(source, output, workspace_manifest):
    """Extract one original pack at a time, then compress one complete module.

    Temporary artifact files bound retained RAM to an input pack plus one module,
    rather than keeping the entire selected library in memory.
    """
    receipt, receipt_raw = read_receipt()
    groups = module_groups(receipt['members'])
    _check_workspace(workspace_manifest, receipt)
    originals = _checked_input_manifest(source, receipt)
    selected = {}
    for path, member in receipt['members'].items():
        selected.setdefault(member['source_pack'], {})[path] = member
    if set(selected) != set(receipt['input_packs']):
        raise ValueError('Module pilot input coverage changed')
    output_directory = output / MODULE_DIRECTORY
    output_directory.mkdir(parents=True, exist_ok=True)
    packs = []
    with tempfile.TemporaryDirectory(prefix='lean-module-pilot-') as tmp:
        temporary = Path(tmp)
        for name, expected in sorted(receipt['input_packs'].items()):
            compressed = (source / safe_path(name)).read_bytes()
            if len(compressed) != expected['bytes'] or sha(compressed) != expected['sha256']:
                raise ValueError('Module pilot input pack checksum mismatch: ' + name)
            decoded = _decode_exact(compressed, expected['decoded_bytes'], 'Module pilot input pack')
            original = originals.get(name)
            if original is None or len(decoded) != expected['decoded_bytes'] or len(decoded) != original['bytes']:
                raise ValueError('Module pilot input pack length mismatch: ' + name)
            entries = {entry['path']: entry for entry in original['entries']}
            if len(entries) != len(original['entries']):
                raise ValueError('Duplicate original module member')
            for path, member in selected[name].items():
                entry = entries.get(path)
                offset, size = member['offset'], member['bytes']
                if entry != dict(path=path, offset=offset, bytes=size) or not 0 <= offset <= offset + size <= len(decoded):
                    raise ValueError('Module pilot original member table mismatch: ' + path)
                raw = decoded[offset:offset + size]
                if sha(raw) != member['sha256']:
                    raise ValueError('Module pilot original member checksum mismatch: ' + path)
                target = temporary / safe_path(path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            del decoded, compressed
        for paths in groups.values():
            raw = bytearray()
            entries = []
            for path in paths:
                data = (temporary / path).read_bytes()
                entries.append(dict(path=path, offset=len(raw), bytes=len(data)))
                raw.extend(data)
            compressed = gzip.compress(raw, compresslevel=9, mtime=0)
            digest = sha(compressed)
            target = output_directory / (digest + '.pack')
            if target.exists() and target.read_bytes() != compressed:
                raise ValueError('Module pilot content address collision')
            target.write_bytes(compressed)
            packs.append(dict(file='modules/' + target.name, bytes=len(raw), compressedBytes=len(compressed),
                              sha256=digest, entries=entries))
    target = output / RECEIPT_ASSET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(receipt_raw)
    manifest = dict(leanCommit=workspace_manifest['leanCommit'], mathlibCommit=workspace_manifest['mathlibCommit'],
                    version='komorebi-module-pilot-1', modulePilot=WORKSPACE,
                    files=sorted(receipt['members']), packs=packs)
    stats = dict(receipt=RECEIPT_ASSET, receipt_sha256=sha(receipt_raw), manifest=MANIFEST,
                 modules=len(groups), files=len(receipt['members']),
                 artifact_bytes=sum(member['bytes'] for member in receipt['members'].values()),
                 encoded_bytes=sum(pack['compressedBytes'] for pack in packs),
                 original_pack_bytes=sum(pack['bytes'] for pack in receipt['input_packs'].values()),
                 compressor=dict(codec='gzip', level=9, mtime=0, python=platform.python_version(), zlib=zlib.ZLIB_RUNTIME_VERSION))
    return manifest, stats


def verify_module_pilot(root, source_record):
    """Check outputs against independent member hashes, including after rehashing.

    This needs no original large input packs in the final Pages artifact.
    """
    pilots = source_record.get('module_pilots', {})
    present = (root / RECEIPT_ASSET).exists() or (root / MODULE_DIRECTORY).exists()
    if not pilots:
        if present:
            raise ValueError('Unrecorded module pilot artifacts')
        return
    if set(pilots) != {WORKSPACE}:
        raise ValueError('Unexpected module delivery pilot')
    receipt, receipt_raw = read_receipt()
    if (root / RECEIPT_ASSET).read_bytes() != receipt_raw:
        raise ValueError('Module pilot independent receipt mismatch')
    manifest = json.loads((root / MANIFEST).read_bytes())
    build = receipt['build']
    if (manifest.get('leanCommit'), manifest.get('mathlibCommit'), manifest.get('modulePilot')) != (
            build['lean_commit'], build['mathlib_commit'], WORKSPACE):
        raise ValueError('Module pilot output build mismatch')
    expected = receipt['members']
    groups = module_groups(expected)
    if manifest['files'] != sorted(expected) or len(manifest['packs']) != len(groups):
        raise ValueError('Module pilot output closure mismatch')
    seen = set()
    assets = set()
    encoded_bytes = 0
    for (module, paths), pack in zip(groups.items(), manifest['packs']):
        if not re.fullmatch(r'modules/[0-9a-f]{64}\.pack', pack['file']):
            raise ValueError('Unexpected module pilot output path')
        asset = 'lean-mathlib/' + pack['file']
        if asset in assets or asset not in source_record['files']:
            raise ValueError('Unrecorded or duplicate module pack')
        assets.add(asset)
        compressed = (root / asset).read_bytes()
        digest = sha(compressed)
        if digest != pack['sha256'] or pack['file'] != 'modules/' + digest + '.pack' or len(compressed) != pack['compressedBytes']:
            raise ValueError('Module pilot output pack checksum mismatch')
        expected_bytes = sum(expected[path]['bytes'] for path in paths)
        if pack['bytes'] != expected_bytes:
            raise ValueError('Module pilot output pack length mismatch')
        raw = _decode_exact(compressed, expected_bytes, 'Module pilot output pack')
        offset = 0
        if len(raw) != pack['bytes'] or len(pack['entries']) != 3:
            raise ValueError('Module pilot output pack length mismatch')
        for path, entry in zip(paths, pack['entries']):
            member = expected[path]
            if entry != dict(path=path, offset=offset, bytes=member['bytes']) or path in seen:
                raise ValueError('Module pilot output member table mismatch: ' + module)
            data = raw[offset:offset + entry['bytes']]
            if len(data) != member['bytes'] or sha(data) != member['sha256']:
                raise ValueError('Module pilot output member checksum mismatch: ' + path)
            seen.add(path)
            offset += entry['bytes']
        if offset != len(raw):
            raise ValueError('Module pilot output contains trailing bytes')
        encoded_bytes += len(compressed)
    actual_assets = {path.relative_to(root).as_posix() for path in (root / MODULE_DIRECTORY).rglob('*') if path.is_file()}
    if seen != set(expected) or actual_assets != assets:
        raise ValueError('Module pilot output coverage mismatch')
    stats = pilots[WORKSPACE]
    calculated = dict(receipt=RECEIPT_ASSET, receipt_sha256=sha(receipt_raw), manifest=MANIFEST,
                      modules=len(groups), files=len(expected), artifact_bytes=sum(member['bytes'] for member in expected.values()),
                      encoded_bytes=encoded_bytes, original_pack_bytes=sum(pack['bytes'] for pack in receipt['input_packs'].values()))
    if any(stats.get(key) != value for key, value in calculated.items()):
        raise ValueError('Module pilot delivery totals changed')
