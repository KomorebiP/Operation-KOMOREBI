"""Coverage labels must follow real reading routes and retained PDF resources."""
import json
from pathlib import Path
import unittest
from types import SimpleNamespace

from core_visual_guides import inventory,render,INDEX,REPORT

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

    def test_exactly_twelve_guides_and_four_complete_html_atlases(self):
        rows=inventory(ROOT,self.files)
        self.assertEqual(len(rows),12)
        self.assertEqual([r['work'] for r in rows if r['html_atlas']],['paper-iv','paper-v','paper-vi','paper-vii'])
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
        self.assertEqual(pages[INDEX].count('Read the HTML atlas'),4)
        self.assertEqual(pages[INDEX].count('Visual atlas available in the PDF.'),8)
        self.assertIn('Monograph with visual atlas (PDF)',pages[INDEX])
        self.assertEqual(json.loads(writes[REPORT])['guides'],inventory(ROOT,self.files))


if __name__=='__main__':unittest.main()
