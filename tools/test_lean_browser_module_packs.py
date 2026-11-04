import gzip
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import lean_module_packs as pilot


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


class ModulePackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'source'
        self.output = Path(self.tmp.name) / 'output'
        self.source.mkdir(); self.output.mkdir()
        self.members = {module + suffix: (module + suffix + ': original artifact').encode()
                        for module in ['Mathlib/Pilot', 'Aesop/Shared'] for suffix in pilot.SUFFIXES}
        inputs = {}; receipts = {}; origin_packs = []; workspace_packs = []
        # Split every triplet across packs; an unselected original member must
        # never enter the smaller delivery format.
        partitions = [[path for path in self.members if path.endswith('.olean')],
                      [path for path in self.members if not path.endswith('.olean')]]
        for index, paths in enumerate(partitions):
            name = f'artifacts-{index:03d}.pack'
            raw = bytearray(); entries = []; selected = []
            for path in paths + (['Unused.olean'] if index == 0 else []):
                data = self.members.get(path, b'unselected')
                entry = dict(path=path, offset=len(raw), bytes=len(data))
                entries.append(entry); raw.extend(data)
                if path in self.members:
                    selected.append(entry)
                    receipts[path] = dict(source_pack='lean-mathlib/' + name, offset=entry['offset'],
                                          bytes=len(data), sha256=pilot.sha(data))
            compressed = gzip.compress(raw, mtime=0)
            target = self.source / 'lean-mathlib' / name
            target.parent.mkdir(exist_ok=True); target.write_bytes(compressed)
            inputs['lean-mathlib/' + name] = dict(bytes=len(compressed), sha256=pilot.sha(compressed), decoded_bytes=len(raw))
            origin_packs.append(dict(file=name, bytes=len(raw), entries=entries))
            workspace_packs.append(dict(file='../shared/' + name, bytes=len(raw), entries=selected,
                                        compressedBytes=len(compressed), sha256=pilot.sha(compressed)))
        original = dict(leanCommit='lean-pin', mathlibCommit='mathlib-pin', packs=origin_packs)
        raw = encoded(original)
        path = self.source / 'lean-mathlib/real-analysis-layer.json'; path.write_bytes(raw)
        self.receipt = dict(schema=1, policy=pilot.POLICY, workspace=pilot.WORKSPACE,
            build=dict(lean_commit='lean-pin', mathlib_commit='mathlib-pin'), input_packs=inputs,
            upstream_manifest=dict(path='lean-mathlib/real-analysis-layer.json', bytes=len(raw), sha256=pilot.sha(raw)), members=receipts)
        self.receipt_raw = encoded(self.receipt)
        self.workspace = dict(leanCommit='lean-pin', mathlibCommit='mathlib-pin', files=sorted(self.members), packs=workspace_packs)
        self.patch = patch.object(pilot, 'read_receipt', side_effect=lambda: (self.receipt, self.receipt_raw))
        self.patch.start(); self.addCleanup(self.patch.stop)

    def build(self):
        manifest, stats = pilot.generate_module_pilot(self.source, self.output, self.workspace)
        path = self.output / pilot.MANIFEST; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(encoded(manifest))
        data = dict(module_pilots={pilot.WORKSPACE: stats}, files={})
        for path in self.output.rglob('*'):
            if path.is_file():
                raw = path.read_bytes()
                data['files'][path.relative_to(self.output).as_posix()] = dict(size=len(raw), sha256=pilot.sha(raw))
        return manifest, data

    def save(self, manifest):
        (self.output / pilot.MANIFEST).write_bytes(encoded(manifest))

    def replace_pack(self, manifest, data, raw):
        pack = manifest['packs'][0]
        old_asset = 'lean-mathlib/' + pack['file']
        (self.output / old_asset).unlink()
        del data['files'][old_asset]
        compressed = gzip.compress(raw, mtime=0); digest = pilot.sha(compressed)
        pack.update(file='modules/' + digest + '.pack', sha256=digest, bytes=len(raw), compressedBytes=len(compressed))
        asset = 'lean-mathlib/' + pack['file']; (self.output / asset).write_bytes(compressed)
        data['files'][asset] = dict(size=len(compressed), sha256=digest)
        self.save(manifest)

    def test_roundtrip_complete_triplets_and_excludes_unselected_bytes(self):
        manifest, data = self.build()
        self.assertEqual(len(manifest['packs']), 2)
        result = {}
        for pack in manifest['packs']:
            raw = gzip.decompress((self.output / 'lean-mathlib' / pack['file']).read_bytes())
            self.assertEqual(len(pack['entries']), 3)
            for entry in pack['entries']:
                result[entry['path']] = raw[entry['offset']:entry['offset'] + entry['bytes']]
        self.assertEqual(result, self.members)
        pilot.verify_generated_module_pilot(self.output, data)

    def test_original_pack_tampering_rejected(self):
        path = self.source / next(iter(self.receipt['input_packs']))
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'input pack checksum'): self.build()

    def test_original_manifest_tampering_rejected(self):
        path = self.source / 'lean-mathlib/real-analysis-layer.json'; path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'upstream manifest changed'): self.build()

    def test_independent_member_hash_rejects_wrong_original_artifact(self):
        next(iter(self.receipt['members'].values()))['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'original member checksum'): self.build()

    def test_workspace_missing_or_duplicate_members_rejected(self):
        self.workspace['files'].pop()
        with self.assertRaisesRegex(ValueError, 'workspace closure changed'): self.build()

    def test_workspace_offset_tampering_rejected(self):
        self.workspace['packs'][0]['entries'][0]['offset'] += 1
        with self.assertRaisesRegex(ValueError, 'workspace member changed'): self.build()

    def test_incomplete_module_triplet_rejected(self):
        del self.receipt['members']['Mathlib/Pilot.ir.sig']
        with self.assertRaisesRegex(ValueError, 'Incomplete module triplet'): self.build()

    def test_rehashed_forged_output_still_rejected_by_independent_member_hash(self):
        manifest, data = self.build()
        raw = bytearray(gzip.decompress((self.output / 'lean-mathlib' / manifest['packs'][0]['file']).read_bytes()))
        raw[0] ^= 1
        self.replace_pack(manifest, data, raw)
        with self.assertRaisesRegex(ValueError, 'output member checksum'): pilot.verify_generated_module_pilot(self.output, data)

    def test_rehashed_output_trailing_bytes_rejected(self):
        manifest, data = self.build()
        raw = gzip.decompress((self.output / 'lean-mathlib' / manifest['packs'][0]['file']).read_bytes())
        self.replace_pack(manifest, data, raw + b'extra')
        with self.assertRaisesRegex(ValueError, 'length mismatch|trailing bytes'): pilot.verify_generated_module_pilot(self.output, data)

    def test_untrusted_decoded_size_is_rejected_before_decompression(self):
        manifest, data = self.build(); manifest['packs'][0]['bytes'] = 2 ** 40; self.save(manifest)
        with patch.object(pilot, '_decode_exact', side_effect=AssertionError('must not decompress')):
            with self.assertRaisesRegex(ValueError, 'output pack length'): pilot.verify_generated_module_pilot(self.output, data)

    def test_missing_output_part_rejected(self):
        manifest, data = self.build(); manifest['packs'][0]['entries'].pop(); self.save(manifest)
        with self.assertRaisesRegex(ValueError, 'output pack length'): pilot.verify_generated_module_pilot(self.output, data)

    def test_output_member_offset_tampering_rejected(self):
        manifest, data = self.build(); manifest['packs'][0]['entries'][0]['offset'] += 1; self.save(manifest)
        with self.assertRaisesRegex(ValueError, 'output member table'): pilot.verify_generated_module_pilot(self.output, data)

    def test_deleted_pilot_record_does_not_bypass_validation(self):
        _, data = self.build(); data.pop('module_pilots')
        with self.assertRaisesRegex(ValueError, 'Unrecorded module pilot'): pilot.verify_generated_module_pilot(self.output, data)

    def test_rewritten_receipt_cannot_authorize_forged_outputs(self):
        _, data = self.build(); (self.output / pilot.RECEIPT_ASSET).write_bytes(self.receipt_raw + b' ')
        with self.assertRaisesRegex(ValueError, 'independent receipt'): pilot.verify_generated_module_pilot(self.output, data)

    def test_unlisted_or_extra_module_pack_rejected(self):
        manifest, data = self.build(); data['files'].pop('lean-mathlib/' + manifest['packs'][0]['file'])
        with self.assertRaisesRegex(ValueError, 'Unrecorded or duplicate'): pilot.verify_generated_module_pilot(self.output, data)
        _, data = self.build(); (self.output / pilot.MODULE_DIRECTORY / ('0' * 64 + '.pack')).write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError, 'coverage mismatch'): pilot.verify_generated_module_pilot(self.output, data)

    def test_forged_delivery_totals_rejected(self):
        _, data = self.build(); data['module_pilots'][pilot.WORKSPACE]['encoded_bytes'] += 1
        with self.assertRaisesRegex(ValueError, 'delivery totals'): pilot.verify_generated_module_pilot(self.output, data)


class RemoteModulePackTests(unittest.TestCase):
    setUp = ModulePackTests.setUp

    def build(self):
        generated, data = ModulePackTests.build(self)
        pilot.verify_generated_module_pilot(self.output, data)
        delivery = dict(schema=1, policy='pinned-module-pilot-delivery-v1', receipt_sha256=pilot.sha(self.receipt_raw),
                        compressor=data['module_pilots'][pilot.WORKSPACE]['compressor'], manifest=generated)
        raw = encoded(delivery)
        with patch.object(pilot, 'read_delivery', return_value=(delivery, raw)):
            self.public = Path(self.tmp.name) / 'public'; self.public.mkdir(exist_ok=True)
            manifest, stats, remote = pilot.build_module_pilot(self.source, self.public, self.workspace)
        self.delivery_patch = patch.object(pilot, 'read_delivery', side_effect=lambda: (delivery, raw))
        self.delivery_patch.start(); self.addCleanup(self.delivery_patch.stop)
        path = self.public / pilot.MANIFEST; path.parent.mkdir(parents=True); path.write_bytes(encoded(manifest))
        return manifest, dict(module_pilots={pilot.WORKSPACE: stats}, files={pilot.MANIFEST: {}}, remote_files=remote)

    def test_remote_publication_preserves_members_without_local_binary_corpus(self):
        manifest, data = self.build()
        self.assertFalse((self.public / pilot.MODULE_DIRECTORY).exists())
        self.assertFalse((self.public / pilot.RECEIPT_ASSET).exists())
        self.assertFalse((self.public / pilot.DELIVERY_ASSET).exists())
        self.assertEqual(manifest['files'], sorted(self.members))
        self.assertEqual(len(data['remote_files']), 4)
        pilot.verify_module_pilot(self.public, data)

    def test_recompression_version_differences_do_not_replace_pinned_delivery_hashes(self):
        manifest, data = self.build()
        original = pilot.generate_module_pilot
        def other_compressor(*args):
            result, stats = original(*args)
            for pack in result['packs']:
                pack['sha256'] = '0' * 64; pack['compressedBytes'] += 1
            return result, stats
        with patch.object(pilot, 'generate_module_pilot', side_effect=other_compressor):
            again, _, remote = pilot.build_module_pilot(self.source, self.public, self.workspace)
        self.assertEqual(again, manifest)
        self.assertEqual(remote, data['remote_files'])

    def test_forged_remote_identity_cannot_be_authorized_by_rehashing_source_record(self):
        _, data = self.build()
        for key, value in [('sha256', '0' * 64), ('size', 1), ('url', pilot.ASSET_PREFIX.replace(pilot.ASSET_COMMIT, 'main') + 'modules/x.pack')]:
            forged = copy.deepcopy(data); next(iter(forged['remote_files'].values()))[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'pinned remote assets'):
                pilot.verify_module_pilot(self.public, forged)

    def test_missing_or_extra_remote_assets_rejected(self):
        _, data = self.build()
        for missing in [True, False]:
            forged = copy.deepcopy(data)
            if missing: forged['remote_files'].pop(next(iter(forged['remote_files'])))
            else: forged['remote_files'][pilot.MODULE_DIRECTORY + '/' + '0' * 64 + '.pack'] = next(iter(forged['remote_files'].values()))
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, 'pinned remote assets'):
                pilot.verify_module_pilot(self.public, forged)

    def test_deleted_record_and_forged_totals_rejected(self):
        _, data = self.build()
        forged = copy.deepcopy(data); forged.pop('module_pilots')
        with self.assertRaisesRegex(ValueError, 'Unrecorded module pilot'): pilot.verify_module_pilot(self.public, forged)
        forged['remote_files'] = {}
        with self.assertRaisesRegex(ValueError, 'Unrecorded module pilot'): pilot.verify_module_pilot(self.public, forged)
        data['module_pilots'][pilot.WORKSPACE]['asset_commit'] = '0' * 40
        with self.assertRaisesRegex(ValueError, 'delivery totals'): pilot.verify_module_pilot(self.public, data)

    def test_local_binary_copy_rejected_by_publication_budget_policy(self):
        _, data = self.build()
        path = self.public / pilot.MODULE_DIRECTORY; path.mkdir()
        (path / ('0' * 64 + '.pack')).write_bytes(b'leftover')
        with self.assertRaisesRegex(ValueError, 'outside Pages'): pilot.verify_module_pilot(self.public, data)

    def test_rehashed_workspace_manifest_cannot_change_pinned_pack_table(self):
        manifest, data = self.build(); manifest = copy.deepcopy(manifest)
        manifest['packs'][0]['entries'][0]['offset'] += 1
        (self.public / pilot.MANIFEST).write_bytes(encoded(manifest))
        with self.assertRaisesRegex(ValueError, 'pinned delivery manifest'): pilot.verify_module_pilot(self.public, data)

    def test_asset_host_allowlist_does_not_cover_compiler_or_other_paths(self):
        for path in ['lean-wasm/lean.js', 'lean-mathlib/modules/../compiler.pack', 'lean-mathlib/modules/x.pack']:
            self.assertIsNone(pilot.module_asset_url(path))


class ReceiptPinTests(unittest.TestCase):
    def test_independent_delivery_receipt_tolerates_only_checkout_line_endings(self):
        path = Path(__file__).resolve().parents[1] / 'manifests/lean-module-pilot-delivery.json'
        original = path.read_bytes().replace(b'\r\n', b'\n')
        with patch.object(Path, 'read_bytes', return_value=original.replace(b'\n', b'\r\n')):
            _, raw = pilot.read_delivery(); self.assertEqual(raw, original)
        with patch.object(Path, 'read_bytes', return_value=original + b' '):
            with self.assertRaisesRegex(ValueError, 'delivery receipt changed'): pilot.read_delivery()

    def test_independent_receipt_tolerates_only_checkout_line_endings(self):
        path = Path(__file__).resolve().parents[1] / 'manifests/lean-module-pilot.json'
        original = path.read_bytes().replace(b'\r\n', b'\n')
        with patch.object(Path, 'read_bytes', return_value=original.replace(b'\n', b'\r\n')):
            receipt, raw = pilot.read_receipt()
            self.assertEqual(raw, original)
            self.assertEqual(receipt['totals']['files'], 894)
        with patch.object(Path, 'read_bytes', return_value=original + b' '):
            with self.assertRaisesRegex(ValueError, 'input receipt changed'): pilot.read_receipt()


if __name__ == '__main__': unittest.main()
