"""Coverage labels must follow real reading routes and retained PDF resources."""
import json
from pathlib import Path
import unittest
import tempfile
import shutil
from types import SimpleNamespace

from core_visual_guides import inventory,all_inventory,render,verify,INDEX,REPORT,ALL_REPORT,GUIDES,guide_navigation,guide_choices,is_visual_guide
from quantum_visual_guides import WORK as QUANTUM,PAGE as QUANTUM_INDEX,PDF as QUANTUM_PDF,sequences,publish as publish_quantum
from check_reader_site import Page

ROOT=Path(__file__).resolve().parents[1]


class CoreVisualGuidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=[]
        registry=json.loads((ROOT/'manifests/browse-resources.json').read_bytes())
        for component in registry['components']:
            if not component['id'].startswith('paper-') and component['id']!=QUANTUM:continue
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
        self.assertEqual(pages[INDEX].count('Open visual guide'),13)
        self.assertEqual(pages[INDEX].count('class="visual-guide-preview"'),13)
        self.assertIn('Search all visual pages',pages[INDEX])
        self.assertIn('../search.html?type=Visual+guides',pages[INDEX])
        self.assertIn('Atlas in monograph PDF',pages[INDEX])
        self.assertIn('id="visual-guide-filter"',pages[INDEX])
        self.assertIn('id="visual-guide-list"',pages[INDEX])
        self.assertEqual(json.loads(writes[REPORT])['guides'],inventory(ROOT,self.files))
        self.assertEqual(json.loads(writes[ALL_REPORT])['guides'],all_inventory(ROOT,self.files))
        self.assertNotIn('data-number="None"',pages[INDEX])
        self.assertNotIn('data-number="13"',pages[INDEX])

    def test_production_page_parser_and_destination_verification(self):
        pages={};writes={}
        import posixpath
        site=SimpleNamespace(root=ROOT,revision='test',search=[],
            rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
            page=lambda path,title,body:pages.__setitem__(path,Page(body)),
            write=lambda path,body:writes.__setitem__(path,body))
        render(SimpleNamespace(site=site,records={str(i):r for i,r in enumerate(self.files)}))
        rows=all_inventory(ROOT,self.files)
        visual_urls={INDEX}
        for row in rows:
            for key in ('visual_pdf','manuscript','overview','html_atlas'):
                if row[key]:pages[row[key]]=Page('<h1>Destination</h1>')
            prefix=row['html_atlas'].removesuffix('index.html')
            units=[p['url'] for s in row['sequences'] for p in s['pages']] if row.get('sequences') else [prefix+'unit-'+str(n)+'.html' for n in range(row['units'])]
            for page in [row['html_atlas'],*units]:
                visual_urls.add(page)
                pages[page]=Page('<h1>Guide</h1>'+guide_navigation(row['work'],page))
        publish_quantum(SimpleNamespace(site=site,work_routes=guide_navigation))
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary);target=output/REPORT;target.parent.mkdir(parents=True)
            target.write_text(writes[REPORT],encoding='utf-8')
            (output/ALL_REPORT).write_text(writes[ALL_REPORT],encoding='utf-8')
            documents=dict(source_revision='test',files=self.files)
            for row in rows:
                image=row['preview']['image'];target=output/image;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'website'/image,target)
            search=[dict(url=url,visual_guide=True) for url in sorted(visual_urls)]
            (output/'search-index.json').write_text(json.dumps(search),encoding='utf-8')
            self.assertEqual(verify(output,documents,pages),dict(guides=12,html_atlases=12))
            missing=next(s for s in search if s['url']==sequences()[0]['pages'][0]['url'])
            missing['visual_guide']=False
            (output/'search-index.json').write_text(json.dumps(search),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Missing visual search entry'):verify(output,documents,pages)
            missing['visual_guide']=True
            (output/'search-index.json').write_text(json.dumps(search),encoding='utf-8')
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
        self.assertIn('Search this guide',markup)
        self.assertIn('../../../search.html?type=Visual+guides&amp;work=paper-xii',markup)
        self.assertIn('../../monographs-quantum-and-circuits/visual-guides.html',[a['href'] for a in links])
        self.assertEqual([a['href'] for a in links if a.get('aria-current')=='location'],['index.html'])
        self.assertTrue(all(BOOKS[w]['atlas_index'] for w in GUIDES))
        self.assertEqual([target for work,_,_,target in guide_choices() if work in GUIDES],
                         [BOOKS[work]['atlas_index'] for work in GUIDES])

    def test_previews_counts_and_original_titles_are_bound_to_real_guides(self):
        from readable_chapters import BOOKS
        rows=inventory(ROOT,self.files)
        self.assertEqual(sum(row['units'] for row in rows),377)
        self.assertTrue(all(r['unit_kind']=='visuals' for r in rows))
        self.assertEqual([r['source_unit_kind'] for r in rows[-4:]],['sections','plates','lessons','plates'])
        for row in rows:
            self.assertEqual(row['title'],BOOKS[row['work']]['title'])
            self.assertTrue((ROOT/'website'/row['preview']['image']).is_file())
            self.assertTrue(row['summary']);self.assertGreater(row['preview']['width'],0)

    def test_quantum_inventory_binds_both_complete_sequences_to_existing_pages(self):
        from quantum_reading import CHAPTERS,BOOK
        row=all_inventory(ROOT,self.files)[-1]
        self.assertEqual((row['work'],row['number'],row['units']),(QUANTUM,None,50))
        self.assertEqual(row['html_atlas'],BOOK['visual_guide_index'])
        self.assertEqual([len(s['pages']) for s in row['sequences']],[25,25])
        selected=[p['url'] for s in sequences() for p in s['pages']]
        self.assertEqual(len(set(selected)),50)
        self.assertTrue(set(selected)<={c['url'] for c in CHAPTERS})
        self.assertTrue(all(is_visual_guide(QUANTUM,page) for page in [QUANTUM_INDEX,*selected]))
        self.assertFalse(is_visual_guide(QUANTUM,BOOK['index']))
        self.assertFalse(is_visual_guide(QUANTUM,CHAPTERS[0]['url']))
        self.assertEqual(len(guide_choices()),13)
        markup=guide_navigation(QUANTUM,selected[0])
        self.assertIn('href="visual-guides.html"',markup)
        self.assertIn('Read volume',markup)
        self.assertIn('Paper XII',markup)
        with self.assertRaisesRegex(ValueError,'Missing Quantum'):
            all_inventory(ROOT,[r for r in self.files if r['repository_path']!=QUANTUM_PDF])


if __name__=='__main__':unittest.main()
