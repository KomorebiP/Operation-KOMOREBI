"""The packed reading cache must retain complete articles and fail closed."""
from copy import deepcopy
import json,posixpath,re,tempfile,unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
from reading_payload import decode,PREFIX
from machine_native_reasoning_html import load,publish,verify
from test_machine_native_reasoning_expanded import fixture
from check_reader_site import Page
ROOT=Path(__file__).resolve().parents[1]

class HTMLMNRTests(unittest.TestCase):
    def test_proofread_revision_restores_source_names_and_preserves_mathematics(self):
        base=json.loads((ROOT/PREFIX/'READING.json').read_bytes());data=load(ROOT)
        def article(page):
            record=dict(page['payload']);record['path']=PREFIX+record.pop('part');record['figure_root']='mnr-figure/'
            return decode(record)
        math=r'<span\b[^>]*class="[^"]*arithmatex[^"]*"[^>]*>.*?</span>'
        texts={}
        for old,new in zip(base['pages'],data['pages']):
            self.assertEqual(old['file'],new['file'])
            before,after=article(old),article(new);texts[new['file']]=after
            self.assertEqual(re.findall(math,before,re.S),re.findall(math,after,re.S),new['file'])
            self.assertEqual(Page(before).ids,Page(after).ids,new['file'])
            self.assertEqual(Page(before).links,Page(after).links,new['file'])
        self.assertIn('<code>alternative_proofs.json</code>',texts['chapter-50.html'])
        self.assertIn('<code>ViewSections</code>',texts['ks-additional-mathematical-material.html'])
        self.assertIn('in the 64-case example.',texts['chapter-62.html'])
        self.assertIn('visible at least two nodes',texts['chapter-88.html'])
        self.assertNotIn('visible at at least',texts['chapter-88.html'])
        self.assertIn('Plates 10–13 develop',texts['large-signal-model-visual-atlas.html'])
        self.assertNotIn('Plate 17 locates',texts['large-signal-model-visual-atlas.html'])
        for chapter in ['chapter-60.html','chapter-63.html','chapter-66.html']:
            self.assertNotRegex(texts[chapter],r'\bPart\s*<a href="chapter-\d{2}\.html#SII:part:')
            self.assertRegex(texts[chapter],r'\bChapter\s*<a href="chapter-\d{2}\.html#SII:part:')

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
            atlas=(Path(tmp)/'read/research-machine-native-reasoning-wider/large-signal-model-visual-atlas.html').read_text(encoding='utf-8')
            menu=re.search(r'<nav class="chapter-contents"[^>]*>(.*?)</nav>',atlas,re.S)
            self.assertIsNotNone(menu)
            self.assertEqual(menu[1].count('<li>'),13)
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
