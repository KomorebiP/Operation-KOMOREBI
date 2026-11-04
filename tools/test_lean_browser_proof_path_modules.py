import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import lean_module_packs as base
import lean_proof_path_modules as extension
import test_lean_browser_module_packs as fixtures

encoded = fixtures.encoded


class ProofPathModulesTests(unittest.TestCase):
    def setUp(self):
        fixtures.ModulePackTests.setUp(self)
        generated, _ = base.generate_module_pilot(self.source, self.output, self.workspace)
        self.common = copy.deepcopy(generated)
        self.common['files'] = [e['path'] for e in self.common['packs'][0]['entries']]
        self.common['packs'] = self.common['packs'][:1]
        pack = self.common['packs'][0]; asset = 'lean-mathlib/' + pack['file']
        self.common_remote = {asset: dict(size=pack['compressedBytes'], sha256=pack['sha256'], url=base.module_asset_url(asset))}
        self.manifest = copy.deepcopy(generated)
        self.manifest.pop('modulePilot')
        self.manifest.update(moduleExtension=extension.COHORT, version='komorebi-proof-path-modules-1')
        self.manifest['packs'][1]['file'] = self.manifest['packs'][1]['file'].replace('modules/', 'proof-path-modules/')
        self.ext_receipt = copy.deepcopy(self.receipt)
        self.seeds = {key: ['Mathlib.Pilot'] for key in extension.WORKSPACES}
        self.ext_receipt.update(workspaces=list(extension.WORKSPACES), seeds=self.seeds,
                                base_receipt_sha256=base.RECEIPT_SHA256, base_delivery_sha256=base.DELIVERY_SHA256)
        raw = encoded(self.ext_receipt)
        self.delivery = dict(receipt_sha256=base.sha(raw), base_delivery_sha256=base.DELIVERY_SHA256,
                             compressor={'codec': 'gzip'}, manifest=self.manifest)
        common_members = {path: self.receipt['members'][path] for path in self.common['files']}
        patches = [patch.object(extension, 'read_receipt', return_value=(self.ext_receipt, raw)),
                   patch.object(extension, 'read_delivery', side_effect=lambda: (self.delivery, encoded(self.delivery))),
                   patch.object(base, 'read_receipt', return_value=({'members': common_members}, b'')),
                   patch.object(base, '_delivery_records', return_value=(self.common, {}, self.common_remote))]
        for item in patches:
            item.start(); self.addCleanup(item.stop)
        self.public = Path(self.tmp.name) / 'public'; self.public.mkdir()

    def build(self):
        manifest, stats, remote = extension.build(self.source, self.public,
            {key: copy.deepcopy(self.workspace) for key in extension.WORKSPACES}, self.seeds)
        path = self.public / extension.MANIFEST; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(encoded(manifest))
        modules = sorted(p[:-6].replace('/', '.') for p in manifest['files'] if p.endswith('.olean'))
        return dict(files={extension.MANIFEST: {}}, module_extensions={extension.COHORT: stats},
                    remote_files={**self.common_remote, **remote}, workspace_manifest_aliases=copy.deepcopy(extension.ALIASES),
                    workspace_modules={key: modules for key in extension.WORKSPACES})

    def test_two_workspaces_share_one_manifest_and_reuse_the_existing_pack(self):
        record = self.build()
        self.assertEqual(record['module_extensions'][extension.COHORT]['reused_modules'], 1)
        self.assertEqual(record['module_extensions'][extension.COHORT]['new_modules'], 1)
        self.assertEqual(len(record['remote_files']), 4)
        self.assertFalse((self.public / extension.DIRECTORY).exists())
        extension.verify(self.public, record)

    def test_original_artifact_tampering_is_rejected(self):
        path = self.source / next(iter(self.receipt['input_packs']))
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'original pack checksum'): self.build()

    def test_changed_decoded_member_cannot_be_authorized_by_output_checksums(self):
        self.ext_receipt['members']['Mathlib/Pilot.ir']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'original member checksum'): self.build()

    def test_changed_workspace_members_or_seeds_rejected(self):
        self.workspace['files'].pop()
        with self.assertRaisesRegex(ValueError, 'workspace closure'): self.build()
        self.workspace['files'] = sorted(self.members)
        self.seeds = {key: ['Mathlib.Changed'] for key in extension.WORKSPACES}
        with self.assertRaisesRegex(ValueError, 'import seeds'): self.build()

    def test_reused_pack_identity_and_output_member_table_are_pinned(self):
        self.manifest['packs'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'reused pack identity'): self.build()
        self.manifest['packs'][0]['sha256'] = self.common['packs'][0]['sha256']
        self.manifest['packs'][1]['entries'][0]['offset'] += 1
        with self.assertRaisesRegex(ValueError, 'member table'): self.build()

    def test_rehashed_runtime_cannot_change_remote_url_size_or_checksum(self):
        record = self.build()
        for key, value in [('url', 'https://example.com/unpinned'), ('size', 1), ('sha256', '0' * 64)]:
            forged = copy.deepcopy(record); next(iter(forged['remote_files'].values()))[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'pinned remote records'):
                extension.verify(self.public, forged)

    def test_missing_record_extra_asset_and_forged_totals_rejected(self):
        record = self.build()
        forged = copy.deepcopy(record); forged.pop('module_extensions')
        with self.assertRaisesRegex(ValueError, 'Unrecorded'): extension.verify(self.public, forged)
        for change in ['missing', 'extra', 'totals']:
            forged = copy.deepcopy(record)
            if change == 'missing': forged['remote_files'].pop(next(iter(forged['remote_files'])))
            elif change == 'extra': forged['remote_files'][extension.DIRECTORY + '/' + '0' * 64 + '.pack'] = {}
            else: forged['module_extensions'][extension.COHORT]['reused_modules'] += 1
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'pinned remote records'):
                extension.verify(self.public, forged)

    def test_missing_reused_download_record_rejected_with_extension_intact(self):
        record = self.build(); record['remote_files'].pop(next(iter(self.common_remote)))
        with self.assertRaisesRegex(ValueError, 'pinned remote records'): extension.verify(self.public, record)

    def test_alias_tampering_and_duplicate_manifest_rejected(self):
        record = self.build()
        forged = copy.deepcopy(record); forged['workspace_manifest_aliases']['proof-path-recovery'] = '../untrusted.json'
        with self.assertRaisesRegex(ValueError, 'manifest aliases'): extension.verify(self.public, forged)
        duplicate = self.public / 'lean-mathlib/workspaces/proof-path-recovery.json'; duplicate.write_bytes(encoded(self.manifest))
        with self.assertRaisesRegex(ValueError, 'pinned shared manifest'): extension.verify(self.public, record)

    def test_changed_workspace_module_set_or_pack_table_rejected(self):
        record = self.build(); forged = copy.deepcopy(record)
        forged['workspace_modules']['proof-path-recovery'].pop()
        with self.assertRaisesRegex(ValueError, 'workspace module set'): extension.verify(self.public, forged)
        changed = copy.deepcopy(self.manifest); changed['packs'].pop()
        (self.public / extension.MANIFEST).write_bytes(encoded(changed))
        with self.assertRaisesRegex(ValueError, 'pinned shared manifest'): extension.verify(self.public, record)

    def test_local_binary_corpus_cannot_leak_into_pages(self):
        record = self.build(); (self.public / extension.DIRECTORY).mkdir()
        with self.assertRaisesRegex(ValueError, 'outside Pages'): extension.verify(self.public, record)

    def test_new_asset_namespace_does_not_authorize_other_paths(self):
        for path in ['lean-wasm/lean.js', 'lean-mathlib/modules/' + '0' * 64 + '.pack', extension.DIRECTORY + '/x.pack']:
            self.assertIsNone(extension.asset_url(path))


class ProofPathReceiptPins(unittest.TestCase):
    def test_both_independent_pins_allow_only_checkout_line_endings(self):
        for read, filename in [(extension.read_receipt, 'lean-proof-path-modules.json'),
                               (extension.read_delivery, 'lean-proof-path-delivery.json')]:
            raw = (Path(__file__).resolve().parents[1] / 'manifests' / filename).read_bytes().replace(b'\r\n', b'\n')
            with self.subTest(filename=filename):
                with patch.object(Path, 'read_bytes', return_value=raw.replace(b'\n', b'\r\n')):
                    self.assertEqual(read()[1], raw)
                with patch.object(Path, 'read_bytes', return_value=raw + b' '):
                    with self.assertRaisesRegex(ValueError, 'independent receipt changed'): read()


if __name__ == '__main__': unittest.main()
