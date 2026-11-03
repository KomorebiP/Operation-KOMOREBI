"""Source coverage and fail-closed publication checks for the LSM visual guide."""
import json
import html
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import tempfile
import unittest

from check_reader_site import Page
from large_signal_atlas import (SOURCE, INDEX, REPORT, FIGURES, metadata,
    specs, normalize, validate_source, sequence, verify)
from readable_chapters import original_math
from reading_navigation import Navigation
from test_large_signal_reading import ROOT, publish_fixture


class Images(HTMLParser):
    def __init__(self, markup):
        super().__init__(); self.images = []; self.feed(markup)
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))


class LargeSignalAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        cls.reader = publish_fixture(cls.output)
        cls.documents = dict(source_revision=cls.reader.site.revision,
            files=list(cls.reader.records.values()))
        cls.pages = {p.relative_to(cls.output).as_posix():Page(p.read_text(encoding='utf-8'))
                     for p in cls.output.rglob('*.html')}

    def test_complete_source_math_and_ranges(self):
        source = (ROOT/SOURCE).read_text(encoding='utf-8-sig')
        selected = specs(source)
        self.assertEqual([p['number'] for p in selected],list(range(18)))
        self.assertEqual([m for p in selected for m in original_math(p['body'])],
            original_math(source.split(r'\begin{document}',1)[1]))
        self.assertEqual(sum(len(original_math(p['body'])) for p in selected),194)
        for p in selected:
            self.assertEqual(original_math(normalize(p['body'])),original_math(p['body']))
            self.assertEqual(normalize(p['body']).count('\n'),p['body'].count('\n'))
        def changed(path):
            raw=(ROOT/path).read_bytes()
            return raw+b'\nChanged source' if path==SOURCE else raw
        with self.assertRaisesRegex(ValueError,'Review changed LSM visual source'):
            validate_source(changed)

    def test_source_identity_math_proofs_diagrams_and_backlinks(self):
        self.assertEqual(verify(self.output,self.documents,self.pages),
            dict(plates=17,orientation_pages=1,diagrams=16,
                 math_expressions=194,proof_route_links=126))
        report=json.loads((self.output/REPORT).read_bytes())
        self.assertEqual(len({r['number'] for rows in report['proof_routes'].values() for r in rows}),38)
        self.assertEqual(len([item for item in self.reader.site.search if item.get('visual_guide')]),19)
        self.assertTrue(all(item.get('work_ids')==['monographs-large-signal-model']
            for item in self.reader.site.search if item.get('visual_guide')))

    def test_navigation_images_and_progressive_enhancement(self):
        routes=sequence()
        stems=[]
        for i,p in enumerate(routes):
            markup=(self.output/p['url']).read_text(encoding='utf-8')
            nav=Navigation(markup)
            self.assertEqual(len(nav.controls),2)
            for control in nav.controls:
                self.assertEqual(control['attrs']['data-reading-position'],str(i+1))
                self.assertEqual(control['attrs']['data-reading-total'],'18')
            links=self.pages[p['url']].links
            for destination in [routes[i-1]['url'] if i else INDEX,
                                routes[i+1]['url'] if i+1<len(routes) else INDEX]:
                self.assertIn(posixpath.relpath(destination,posixpath.dirname(p['url'])),links)
            images=[image for image in Images(markup).images if '/atlas/' in image['src']]
            expected=0 if i in (10,17) else 1
            self.assertEqual(len(images),expected)
            for image in images:
                stem=Path(image['src']).stem;stems.append(stem)
                self.assertEqual(image['alt'],FIGURES[stem][0])
                self.assertIn(html.escape(FIGURES[stem][1]),markup)
                self.assertGreater(int(image['width']),0)
                self.assertGreater(int(image['height']),0)
            self.assertNotRegex(markup,r'\\(?:claim|boundary|nav|diagram)\{')
            self.assertNotIn('[5pt]',markup)
        self.assertEqual(set(stems),set(FIGURES))
        markup=(self.output/routes[3]['url']).read_text(encoding='utf-8')
        self.assertIn('data-lsm-explorer',markup)
        self.assertIn('class="lsm-explorer-controls" hidden',markup)
        self.assertIn('Available after one observation',markup)
        self.assertIn('data-lsm-b-next>1</dd>',markup)
        self.assertIn('min="-2" max="2" step="1"',markup)
        index=(self.output/INDEX).read_text(encoding='utf-8')
        self.assertEqual(index.count('class="lsm-atlas-card"'),17)
        self.assertIn('role="search" hidden',index)

    def test_omitted_proof_route_is_rejected(self):
        path=self.output/REPORT;before=path.read_bytes()
        try:
            data=json.loads(before);data['proof_routes']['3']=[]
            path.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaises(AssertionError):verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(before)

    def test_changed_display_math_is_rejected(self):
        path=self.output/sequence()[3]['url'];before=path.read_bytes()
        try:
            markup=before.decode('utf-8')
            markup,count=re.subn(r'(class="arithmatex">\\[\[(])',r'\g<1>1+',markup,count=1)
            self.assertEqual(count,1)
            path.write_text(markup,encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Changed LSM visual mathematics'):
                verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(before)

    def test_changed_diagram_is_rejected(self):
        report=json.loads((self.output/REPORT).read_bytes())
        path=self.output/report['figures'][0]['image'];before=path.read_bytes()
        try:
            path.write_bytes(before+b'Changed image')
            with self.assertRaises(AssertionError):verify(self.output,self.documents,self.pages)
        finally:path.write_bytes(before)


if __name__=='__main__':unittest.main()
