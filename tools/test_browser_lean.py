import hashlib
import json
from pathlib import Path
import posixpath
import tempfile
from types import SimpleNamespace
import unittest
from urllib.parse import parse_qs, urlsplit

from browser_lean import SOURCE, WORK, PAGE, SUFFIX, HOST, action, build, editor_url, verify


class BrowserLeanTests(unittest.TestCase):
    def fixture(self, output):
        root=Path(__file__).resolve().parents[1]
        raw=(root/SOURCE).read_bytes()
        record=dict(repository_path=SOURCE, work=WORK, url='read/paper-xii/idempotents.html',
                    file_url='documents/files/LocalIdempotents.lean', sha256=hashlib.sha256(raw).hexdigest())
        def write(path, text):
            dest=output/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
        site=SimpleNamespace(root=root,search=[],revision='a'*40,write=write,
                             rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
                             page=lambda path,title,body:write(path,body),read_source=lambda record:raw)
        dest=output/record['file_url'];dest.parent.mkdir(parents=True);dest.write_bytes(raw)
        return SimpleNamespace(site=site,lean_works={WORK:[record]}),record,raw

    def test_editor_starts_with_exact_source_and_is_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);reader,record,raw=self.fixture(out)
            build(reader)
            self.assertEqual(verify(out,dict(files=[record]))['source_identity'],'PASS')
            parts=urlsplit(editor_url(raw.decode('utf-8-sig')+SUFFIX))
            self.assertEqual(parts.scheme+'://'+parts.netloc+'/',HOST)
            self.assertEqual(parse_qs(parts.fragment)['code'],[raw.decode('utf-8-sig')+SUFFIX])
            markup=(out/PAGE).read_text(encoding='utf-8')
            self.assertNotIn('<iframe',markup)
            self.assertIn('data-lean-open hidden',markup)
            self.assertIn('<noscript>',markup)
            self.assertIn('code you enter is sent there',markup)
            self.assertIn('or update recorded verification and coverage labels',markup)
            self.assertEqual((out/record['file_url']).read_bytes(),raw)
            data=json.loads((out/'lean/playground.json').read_bytes())
            self.assertFalse(data['build_runs_lean'])
            self.assertFalse(data['changes_recorded_verification'])

    def test_missing_or_tampered_source_cannot_be_published_as_the_pilot(self):
        with tempfile.TemporaryDirectory() as temp:
            reader,record,raw=self.fixture(Path(temp))
            record['sha256']='0'*64
            with self.assertRaises(ValueError):build(reader)
            reader.lean_works={}
            with self.assertRaises(ValueError):build(reader)

    def test_verifier_rejects_changed_editor_code_or_auto_loaded_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);reader,record,raw=self.fixture(out);build(reader)
            original=(out/PAGE).read_text(encoding='utf-8')
            for change in (original.replace('%23check','%23eval'), original+'<iframe src="'+HOST+'"></iframe>'):
                (out/PAGE).write_text(change,encoding='utf-8')
                with self.assertRaises(AssertionError):verify(out,dict(files=[record]))

    def test_only_selected_work_and_source_receive_try_links(self):
        site=SimpleNamespace(rel=lambda target,page:target)
        self.assertIn(PAGE,action(site,'page.html',work=WORK))
        self.assertIn(PAGE,action(site,'page.html',source=SOURCE))
        self.assertEqual(action(site,'page.html',work='paper-i'),'')
        self.assertEqual(action(site,'page.html',source='different.lean'),'')


if __name__ == '__main__':unittest.main()
