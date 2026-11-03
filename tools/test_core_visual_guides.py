"""Coverage labels must follow real reading routes and retained PDF resources."""
import json
from pathlib import Path
import unittest
import tempfile
from types import SimpleNamespace

from core_visual_guides import inventory,render,verify,INDEX,REPORT
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

    def test_exactly_twelve_guides_and_ten_complete_html_guides(self):
        rows=inventory(ROOT,self.files)
        self.assertEqual(len(rows),12)
        self.assertEqual([r['work'] for r in rows if r['html_atlas']],['paper-i','paper-ii','paper-iii','paper-iv','paper-v','paper-vi','paper-vii','paper-viii','paper-ix','paper-x'])
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
        self.assertEqual(pages[INDEX].count('Read the HTML guide'),10)
        self.assertEqual(pages[INDEX].count('Visual guide available in the PDF.'),2)
        self.assertIn('Monograph with visual atlas (PDF)',pages[INDEX])
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
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary);target=output/REPORT;target.parent.mkdir(parents=True)
            target.write_text(writes[REPORT],encoding='utf-8')
            documents=dict(source_revision='test',files=self.files)
            self.assertEqual(verify(output,documents,pages),dict(guides=12,html_atlases=10))
            pages.pop(rows[0]['html_atlas'])
            with self.assertRaises(AssertionError):verify(output,documents,pages)


if __name__=='__main__':unittest.main()
