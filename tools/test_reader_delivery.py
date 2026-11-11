"""Check source, export, native-link and index preservation across packaging."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reader_delivery import asset_name, package, rewrite_links, verify
from publish_reader_downloads import confirm_asset, publish


class DeliveryTests(unittest.TestCase):
    def fixture(self, base):
        root, assets = base/'site', base/'exports'
        root.mkdir()
        source = b'unchanged manuscript and PDF bytes'
        data = json.dumps({'version': 1, 'exact': r'\\Phi  x', 'unicode': '\u03b1', 'rows': ['context '*100]*50}).encode()
        files = {'build-info.json': json.dumps({'collection_revision': 'a'*40}).encode(),
                 'assets/reader-data.js': b'/* loader */', 'assets/vendor/fflate-0.8.3.js': b'/* pinned */',
                 'documents/files/original/source.json': data, 'documents/files/original/book.pdf': source,
                 'notation/data/book.json': data, 'notation/reader/book.json': data,
                 'notation/search.json': data, 'search-index.json': data, 'side-reader-index.json': data,
                 'downloads/book.zip': b'byte-identical archive'}
        bundle = dict(work='book', url='downloads/book.zip', archive_bytes=len(files['downloads/book.zip']),
                      archive_sha256=hashlib.sha256(files['downloads/book.zip']).hexdigest(), files=[{'path': 'book.pdf'}])
        files['downloads/index.json'] = json.dumps([bundle]).encode()
        page = ('<!doctype html><html><head><title>Reader</title></head><body><main><h1>Book</h1>'
                '<a href="../downloads/book.zip">Download</a><a href=data/book.json download>JSON</a>'
                '<form data-source="data/book.json"></form><p>Exact \\Phi and \u03b1</p></main></body></html>')
        files['notation/book.html'] = page.encode()
        files['404.html'] = b'<html><head><title>Missing page</title></head><body><main>Find a page</main></body></html>'
        for path, raw in files.items():
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        return root, assets, files

    def test_packaging_preserves_sources_and_exports_and_reduces_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            root, assets, original = self.fixture(Path(directory))
            report = package(root, assets)
            manifest = verify(root, assets)
            self.assertTrue(report['byte_identity_verified'])
            for path in ('documents/files/original/source.json', 'documents/files/original/book.pdf'):
                self.assertEqual((root/path).read_bytes(), original[path])
            for path, record in manifest['files'].items():
                self.assertFalse((root/path).exists())
                self.assertEqual((assets/record['asset']).read_bytes(), original[path])
                if 'gzip' in record:
                    self.assertEqual(gzip.decompress((root/record['gzip']).read_bytes()), original[path])
            page = (root/'notation/book.html').read_text(encoding='utf-8')
            self.assertIn('data-source="data/book.json"', page)
            self.assertIn('>Download</a>', page)
            self.assertIn('>JSON</a>', page)
            self.assertIn('data-reader-delivery', page)
            self.assertIn('releases/download/reader-downloads-'+'a'*40+'/book.zip', page)
            self.assertIn('notation--data--book.json', page)
            self.assertIn('retained-downloads', (root/'404.html').read_text())
            bundle = json.loads((root/'downloads/index.json').read_bytes())[0]
            self.assertEqual(bundle['local_url'], 'downloads/book.zip')
            self.assertEqual(bundle['files'], [{'path': 'book.pdf'}])

    def test_links_are_rewritten_only_for_known_local_exports(self):
        record = {'export_url': 'https://github.com/example/release/data.json'}
        records = {'notation/data/book.json': record}
        text = '<a href="data/book.json?v=1">Export</a><a href="https://other.test/notation/data/book.json">Other</a><form data-source="data/book.json"></form>'
        result = rewrite_links(text, 'notation/book.html', records)
        self.assertIn('href="'+record['export_url']+'"', result)
        self.assertIn('https://other.test/notation/data/book.json', result)
        self.assertIn('data-source="data/book.json"', result)

    def test_corrupted_compressed_index_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root, assets, _ = self.fixture(Path(directory))
            package(root, assets)
            (root/'notation/data/book.json.gz').write_bytes(gzip.compress(b'wrong'))
            with self.assertRaisesRegex(ValueError, 'Index identity'):
                verify(root, assets)

    def test_unsafe_or_ambiguous_asset_names_are_rejected(self):
        for path in ('../source.json', 'bad--name.json', 'bad?name.json'):
            with self.assertRaises(ValueError): asset_name(path)

    def test_publication_is_bound_to_workflow_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            root, assets, _ = self.fixture(Path(directory))
            package(root, assets)
            with patch.dict('os.environ', {'GITHUB_REPOSITORY': 'other/repo', 'GITHUB_SHA': 'a'*40}):
                with self.assertRaisesRegex(ValueError, 'workflow revision'):
                    publish(root, assets, 'not-a-secret')

    def test_existing_release_assets_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'file.json'
            path.write_bytes(b'unchanged')
            value = dict(size=9, digest='sha256:'+hashlib.sha256(b'unchanged').hexdigest())
            confirm_asset(value, path)
            with self.assertRaisesRegex(ValueError, 'different digest'):
                confirm_asset({**value, 'digest': 'sha256:'+'0'*64}, path)


if __name__ == '__main__':
    unittest.main()
