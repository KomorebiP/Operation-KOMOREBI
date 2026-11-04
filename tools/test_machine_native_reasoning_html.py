"""The packed reading cache must retain complete articles and fail closed."""
from copy import deepcopy
import json,posixpath,tempfile,unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
from reading_payload import decode,PREFIX
from machine_native_reasoning_html import load,publish,verify
from test_machine_native_reasoning_expanded import fixture
from check_reader_site import Page
ROOT=Path(__file__).resolve().parents[1]

class HTMLMNRTests(unittest.TestCase):
    def test_authenticated_article_inventory_and_corruption(self):
        data=load(ROOT);proofs=statements=0
        for page in data['pages']:
            record=deepcopy(page['payload']);record['path']=PREFIX+record.pop('part');record['figure_root']='https://example.org/figures/'
            text=decode(record);proofs+=text.count('class="proof"');statements+=text.count('data-statement-number=')
        self.assertEqual((proofs,statements),(527,803))
        for field,value in [('part_sha256','0'*64),('offset',-1),('html_sha256','0'*64)]:
            bad=deepcopy(record);bad[field]=value
            with self.assertRaises(ValueError):decode(bad)

    def test_real_reader_chrome_all_cross_references_and_sequence(self):
        from machine_native_reasoning_expanded import publish as whole
        with tempfile.TemporaryDirectory() as tmp:
            site=fixture(tmp,True);whole(site);self.assertEqual(verify(tmp)['pages'],121)
            pages={p.name:Page(p.read_text(encoding='utf-8')) for p in (Path(tmp)/'read/research-machine-native-reasoning-wider').glob('*.html')}
            checked=0
            for name,page in pages.items():
                self.assertEqual(len(page.ids),len(set(page.ids)),name)
                for href in page.links:
                    url=urlsplit(href)
                    if url.scheme or url.netloc:continue
                    target=posixpath.normpath(url.path) if url.path else name
                    if target in pages and url.fragment:
                        self.assertIn(unquote(url.fragment),pages[target].ids,(name,href));checked+=1
            self.assertGreater(checked,2000)
            self.assertLess(sum(p.stat().st_size for p in Path(tmp).rglob('*') if p.is_file()),1900000)

if __name__=='__main__':unittest.main()
