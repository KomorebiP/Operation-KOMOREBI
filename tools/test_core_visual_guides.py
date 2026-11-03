"""Coverage labels must follow real reading routes and retained PDF resources."""
import json
from pathlib import Path
import unittest
import tempfile
import shutil
from types import SimpleNamespace

from core_visual_guides import inventory,render,verify,INDEX,REPORT,GUIDES,guide_navigation
from check_reader_site import Page

ROOT=Path(__file__).resolve().parents[1]


class CoreVisualGuidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=[]
        registry=json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
        for component in registry['components']:
            if not component['id'].startswith('paper-'):continue
            receipt=json.loads((ROOT/('manifests/source-imports/'+component['id']+'.json')).read_bytes())
            owned={r['path']:r for r in receipt['files']}
            for resource in component['resources']:
                if resource['kind'] not in ('pdf','visual'):continue
                cls.files.append(dict(repository_path=component['destination']+'/'+resource['path'],
                    url='pdf/'+component['id']+'/'+resource['kind']+'.html',sha256=owned[resource['path']]['sha256']))

    def test_exactly_twelve_complete_html_guides(self):
        rows=inventory(ROOT,self.files)
        self.assertEqual(len(rows),12)
        self.assertEqual([r['work'] for r in rows if r['html_atlas']],['paper-i','paper-ii','paper-iii','paper-iv','paper-v','paper-vi','paper-vii','paper-viii','paper-ix','paper-x','paper-xi','paper-xii'])
        self.assertTrue(rows[0]['integrated_pdf'])
        self.assertTrue(all(not r['integrated_pdf'] for r in rows[1:]))
        self.assertEqual(len({r['visual_pdf'] for r in rows}),12)

    def test_a_missing_pdf_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Missing visual'):
            inventory(ROOT,[])

    def test_published_routes_and_report_match_the_inventory(self):
        pages={};writes={}
        import posixpath
        site=SimpleNamespace(root=ROOT,revision='test',search=[],
            rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
            page=lambda path,title,body:pages.__setitem__(path,body),
            write=lambda path,body:writes.__setitem__(path,body))
        reader=SimpleNamespace(site=site,records={str(i):r for i,r in enumerate(self.files)})
        render(reader)
        self.assertEqual(pages[INDEX].count('Open visual guide'),12)
        self.assertEqual(pages[INDEX].count('class="visual-guide-preview"'),12)
        self.assertIn('Atlas in monograph PDF',pages[INDEX])
        self.assertIn('id="visual-guide-filter"',pages[INDEX])
        self.assertIn('id="visual-guide-list"',pages[INDEX])
        self.assertEqual(json.loads(writes[REPORT])['guides'],inventory(ROOT,self.files))

    def test_production_page_parser_and_destination_verification(self):
        pages={};writes={}
        import posixpath
        site=SimpleNamespace(root=ROOT,revision='test',search=[],
            rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
            page=lambda path,title,body:pages.__setitem__(path,Page(body)),
            write=lambda path,body:writes.__setitem__(path,body))
        render(SimpleNamespace(site=site,records={str(i):r for i,r in enumerate(self.files)}))
        rows=inventory(ROOT,self.files)
        for row in rows:
            for key in ('visual_pdf','manuscript','overview','html_atlas'):
                if row[key]:pages[row[key]]=Page('<h1>Destination</h1>')
            prefix=row['html_atlas'].removesuffix('index.html')
            for page in [row['html_atlas'],*[prefix+'unit-'+str(n)+'.html' for n in range(row['units'])]]:
                pages[page]=Page('<h1>Guide</h1>'+guide_navigation(row['work'],page))
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary);target=output/REPORT;target.parent.mkdir(parents=True)
            target.write_text(writes[REPORT],encoding='utf-8')
            documents=dict(source_revision='test',files=self.files)
            for row in rows:
                image=row['preview']['image'];target=output/image;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'website'/image,target)
            self.assertEqual(verify(output,documents,pages),dict(guides=12,html_atlases=12))
            pages.pop(rows[0]['html_atlas'])
            with self.assertRaises(AssertionError):verify(output,documents,pages)

    def test_switching_guides_preserves_format_and_current_paper(self):
        from readable_chapters import BOOKS
        from html.parser import HTMLParser
        class Switch(HTMLParser):
            def __init__(self,markup):super().__init__();self.links=[];self.feed(markup)
            def handle_starttag(self,tag,attrs):
                if tag=='a':self.links.append(dict(attrs))
        page='read/paper-xii/atlas/v07.html';markup=guide_navigation('paper-xii',page);links=Switch(markup).links
        self.assertIn('../../visual-guides.html',[a['href'] for a in links])
        self.assertEqual(sum('/atlas/index.html' in a['href'] or a['href']=='index.html' for a in links),13)
        self.assertIn('Switch guide',markup)
        self.assertEqual([a['href'] for a in links if a.get('aria-current')=='location'],['index.html'])
        self.assertTrue(all(BOOKS[w]['atlas_index'] for w in GUIDES))

    def test_previews_counts_and_original_titles_are_bound_to_real_guides(self):
        from readable_chapters import BOOKS
        rows=inventory(ROOT,self.files)
        self.assertEqual(sum(row['units'] for row in rows),377)
        self.assertEqual([r['unit_kind'] for r in rows[-4:]],['sections','plates','lessons','plates'])
        for row in rows:
            self.assertEqual(row['title'],BOOKS[row['work']]['title'])
            self.assertTrue((ROOT/'website'/row['preview']['image']).is_file())
            self.assertTrue(row['summary']);self.assertGreater(row['preview']['width'],0)


if __name__=='__main__':unittest.main()
