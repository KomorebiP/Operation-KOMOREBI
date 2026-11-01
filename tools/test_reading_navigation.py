"""Check reading order, boundaries and uncluttered access to secondary routes."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from reading_navigation import entries, neighbours, navigation, outline, resources, work_links, Navigation, publish_record, verify


class ReadingNavigationTests(unittest.TestCase):
    def config(self, partial=False):
        return dict(work='test',label='Paper test',index='read/test/index.html',
                    chapters=[dict(url='read/test/one.html',title='I. First part'),
                              dict(url='read/test/two.html',title='II. Second part')],
                    bib_page='read/test/references.html',partial=partial)

    def test_sequence_includes_bibliography_and_reciprocal_neighbours(self):
        config=self.config();sequence=entries(config)
        self.assertEqual([e['url'] for e in sequence],['read/test/one.html','read/test/two.html','read/test/references.html'])
        for i,entry in enumerate(sequence):
            _,position,previous,following=neighbours(config,entry['url'])
            self.assertEqual(position,i)
            if i:self.assertEqual(previous,sequence[i-1])
            if i+1<len(sequence):self.assertEqual(following,sequence[i+1])
        self.assertEqual(neighbours(config,sequence[0]['url'])[2]['url'],config['index'])
        self.assertEqual(neighbours(config,sequence[-1]['url'])[3]['url'],config['index'])

    def test_custom_reader_does_not_duplicate_references(self):
        config=self.config();config['chapters'].append(dict(url=config['bib_page'],title='References'))
        self.assertEqual(len(entries(config)),3)
        self.assertEqual(entries(config)[-1]['title'],'References')

    def test_partial_edition_continues_in_sources(self):
        config=self.config(True)
        self.assertEqual(neighbours(config,config['bib_page'])[3]['url'],'read/test/index.html#source-continuations')
        self.assertIn('Continue reading',navigation(config,config['bib_page']))
        self.assertNotIn('Finished',navigation(config,config['bib_page']))

    def test_current_part_is_marked_and_native_menu_works_without_script(self):
        config=self.config();markup=navigation(config,'read/test/two.html')
        parsed=Navigation(markup).controls[0]
        current=[a for a in parsed['links'] if a.get('aria-current')=='page']
        self.assertEqual(len(current),1);self.assertEqual(current[0]['href'],'two.html')
        self.assertIn('<summary>Chapters &amp; parts</summary>',markup)
        self.assertIn('II. Second part',markup)
        self.assertIn('rel="prev" href="one.html"',markup)
        self.assertIn('rel="next" href="references.html"',markup)
        self.assertNotIn(' hidden',markup);self.assertNotIn('<script',markup)
        self.assertNotIn(' open',outline('<nav>Sections</nav>'))
        self.assertNotIn(' open',resources('Sources'))

    def test_secondary_routes_are_grouped_without_losing_unique_destinations(self):
        targets=[('Read chapters','read/test/index.html'),('Read PDF','read/test/pdf.html'),
                 ('Lean','work.html#lean'),('Evidence','work.html#evidence'),
                 ('Search this work','search.html?work=test'),('Other <route>','more.html')]
        reader=SimpleNamespace(work_route_targets=lambda work:targets,site=SimpleNamespace(rel=lambda url,page:url))
        markup=work_links(reader,'test','read/test/one.html')
        self.assertNotIn('read/test/index.html',markup)
        for label,url in targets[1:]:self.assertEqual(markup.count('href="'+url+'"'),1)
        self.assertIn('Read and explore',markup);self.assertIn('Proofs and implementation',markup)
        self.assertIn('Other &lt;route&gt;',markup)

    def test_unknown_and_duplicate_pages_are_rejected(self):
        config=self.config()
        with self.assertRaisesRegex(ValueError,'outside'):navigation(config,'read/other/one.html')
        config['chapters'].append(config['chapters'][0])
        with self.assertRaisesRegex(ValueError,'unique'):entries(config)

    def test_verifier_rejects_wrong_next_menu_and_missing_footer(self):
        import readable_chapters
        config=self.config()
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            def write(path,text):
                dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
            publish_record(SimpleNamespace(write=write),{'test':config})
            for entry in entries(config):
                write(entry['url'],navigation(config,entry['url'])+'<article>Text</article>'+navigation(config,entry['url'],'bottom'))
            pages={entry['url']:None for entry in entries(config)}
            with patch.dict(readable_chapters.BOOKS,{'test':config},clear=True):
                self.assertEqual(verify(root,pages,dict(files=[])),dict(editions=1,reading_pages=3,navigation_controls=6))
                page=root/'read/test/one.html';original=page.read_text(encoding='utf-8')
                for bad in [original.replace('rel="next" href="two.html"','rel="next" href="references.html"',1),
                            original.replace('data-reading-entry="2" href="two.html"','data-reading-entry="2" href="one.html"',1),
                            navigation(config,'read/test/one.html')]:
                    page.write_text(bad,encoding='utf-8')
                    with self.assertRaises(AssertionError):verify(root,pages,dict(files=[]))
                page.write_text(original,encoding='utf-8')


if __name__=='__main__':unittest.main()
