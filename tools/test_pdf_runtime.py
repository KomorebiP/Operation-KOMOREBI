"""Keep PDF.js publishing trim limited to identified debugger source maps."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import fetch_pdf_runtime as runtime


SOURCE_MAPS = {
    'build/pdf.mjs.map',
    'build/pdf.sandbox.mjs.map',
    'build/pdf.worker.mjs.map',
    'web/viewer.mjs.map',
}


def release_files():
    files = {
        'LICENSE': b'Original upstream license\n',
        'web/viewer.html': (
            b'<!doctype html><html><head>'
            b'<script src="viewer.mjs" type="module"></script>'
            b'</head><body>Original viewer markup</body></html>'
        ),
        'web/viewer.mjs': b'export const viewer = "original";\n',
        'web/viewer.css': b'body { color: black; }\n',
        'build/pdf.mjs': b'export const pdf = "original";\n',
        'build/pdf.worker.mjs': b'export const worker = "original";\n',
        'build/pdf.sandbox.mjs': b'export const sandbox = "original";\n',
        'web/locale/en-US/viewer.ftl': b'pdfjs-document-properties-title = Document properties\n',
        'web/cmaps/Adobe-Japan1-UCS2.bcmap': b'original character map\x00\x01',
        'web/standard_fonts/FoxitSans.pfb': b'original font\x00\x02',
        'web/custom-extension.mjs.map': b'An unlisted map must remain published.\n',
    }
    for name in sorted(SOURCE_MAPS):
        files[name] = json.dumps({'version': 3, 'file': name[:-4]}).encode()
    return files


def release_zip(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        for name, contents in files.items():
            archive.writestr(name, contents)
    return output.getvalue()


class PdfRuntimeTests(unittest.TestCase):
    def test_only_identified_source_maps_are_omitted_with_their_identities(self):
        files = release_files()
        archive = release_zip(files)
        archive_sha = hashlib.sha256(archive).hexdigest()
        with tempfile.TemporaryDirectory() as folder, patch.object(runtime, 'SHA256', archive_sha):
            output = Path(folder) / 'runtime'
            record = runtime.extract(archive, output)

            self.assertEqual(runtime.DEBUG_SOURCE_MAPS, SOURCE_MAPS)
            self.assertEqual(set(record['omitted_source_maps']), SOURCE_MAPS)
            for name in SOURCE_MAPS:
                with self.subTest(omitted=name):
                    self.assertFalse((output / name).exists())
                    self.assertNotIn(name, record['files'])
                    self.assertEqual(record['omitted_source_maps'][name], {
                        'sha256': hashlib.sha256(files[name]).hexdigest(),
                        'size': len(files[name]),
                    })

            for name, contents in files.items():
                if name in SOURCE_MAPS or name == 'web/viewer.html':
                    continue
                with self.subTest(retained=name):
                    self.assertEqual((output / name).read_bytes(), contents)
                    self.assertEqual(record['files'][name], hashlib.sha256(contents).hexdigest())

            viewer = (output / 'web/viewer.html').read_text(encoding='utf-8')
            self.assertIn('Original viewer markup', viewer)
            self.assertEqual(viewer.count('<script src="viewer.mjs" type="module"></script>'), 1)
            self.assertLess(viewer.index('komorebi-config.js'), viewer.index('<script src="viewer.mjs"'))
            self.assertIn('komorebi-config.css', viewer)
            self.assertEqual((output / 'web/komorebi-config.js').read_text(encoding='utf-8'), runtime.CONFIG)
            self.assertEqual((output / 'web/komorebi-config.css').read_text(encoding='utf-8'), runtime.CSS)
            self.assertEqual(record['archive_sha256'], archive_sha)
            self.assertEqual(json.loads((output / 'SOURCE.json').read_bytes()), record)
            self.assertEqual(runtime.verify(output), record)

    def test_retained_worker_integrity_is_still_enforced(self):
        archive = release_zip(release_files())
        with tempfile.TemporaryDirectory() as folder, patch.object(runtime, 'SHA256', hashlib.sha256(archive).hexdigest()):
            output = Path(folder) / 'runtime'
            runtime.extract(archive, output)
            (output / 'build/pdf.worker.mjs').write_bytes(b'Changed worker bytes')
            with self.assertRaisesRegex(ValueError, r'PDF.js file integrity mismatch: build/pdf.worker.mjs'):
                runtime.verify(output)

    def test_unsafe_archive_paths_are_rejected_even_when_they_look_like_maps(self):
        for name in ('../escape.map', '/absolute.map', 'C:/debug.map'):
            with self.subTest(path=name), tempfile.TemporaryDirectory() as folder:
                files = release_files()
                files[name] = b'Unsafe debugger metadata'
                archive = release_zip(files)
                with patch.object(runtime, 'SHA256', hashlib.sha256(archive).hexdigest()):
                    with self.assertRaisesRegex(ValueError, 'Unsafe PDF.js archive path'):
                        runtime.extract(archive, Path(folder) / 'runtime')
                self.assertFalse((Path(folder) / 'escape.map').exists())


if __name__ == '__main__':
    unittest.main()
