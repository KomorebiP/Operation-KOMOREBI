import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from side_reader import catalogue, pane
from check_reader_site import Page


class SideReaderTests(unittest.TestCase):
    def test_catalogue_excludes_the_workspace_and_vendor_viewer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['read/work/main.html','collection/works/work.html','assets/pdfjs/web/viewer.html','side-by-side.html','404.html']:
                target=root/name
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text('<title>A &amp; B · Komorebi</title>',encoding='utf-8')
            site=SimpleNamespace(output=root,revision='a'*40,
                search=[dict(url='read/work/main.html#L3',title='A claim',kind='Claims',work_ids=['work'],text='Source text'),
                        dict(url='missing.html',title='Missing')],
                components={'work':{'title':'Work'}},registry={'components':[{'id':'work'}]},
                reader=SimpleNamespace(primary_pdf=lambda work:None),editorial_editions={})
            data=catalogue(site)
            self.assertEqual(set(data['pages']),{'read/work/main.html','collection/works/work.html'})
            self.assertEqual(data['pages']['read/work/main.html'],'A & B')
            self.assertEqual(data['entries'][0]['url'],'read/work/main.html#L3')
            self.assertNotIn('missing.html',[row['url'] for row in data['entries']])
            self.assertEqual(data['works'][0]['right'],'collection/works/work.html#written-proofs')

    def test_both_panes_have_distinct_labels_and_named_frames(self):
        page=Page(pane('left')+pane('right'))
        self.assertEqual(len(page.ids),len(set(page.ids)))
        self.assertEqual(len(page.iframes),2)
        for frame in page.iframes:
            self.assertTrue(frame['title'])
            self.assertNotIn('src',frame)
        for control in page.inputs:
            self.assertIn(control['id'],page.labels)


if __name__=='__main__':unittest.main()
