import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from side_reader import catalogue, pane, pair_link, check_pair_links
from urllib.parse import parse_qs, urlsplit
from check_reader_site import Page


class SideReaderTests(unittest.TestCase):
    def test_pair_links_keep_statement_and_proof_anchors_from_nested_pages(self):
        link=pair_link('read/paper/one.html#L45','read/paper/one.html#L60','read/paper/one.html')
        href=Page(link).links[0]
        self.assertEqual(urlsplit(href).path,'../../side-by-side.html')
        self.assertEqual(parse_qs(urlsplit(href).query),{'left':['read/paper/one.html#L45'],'right':['read/paper/one.html#L60']})
        pages={'read/paper/one.html':Page('<p id="L45"></p><p id="L60"></p>'+link),
               'side-by-side.html':Page('<h1>Reader</h1>')}
        self.assertEqual(check_pair_links(pages),{'targets':2,'pairs':1})
        for bad in ['https://example.test/x.html','../x.html','/x.html','read/%2e%2e/x.html','read/x.html?unsafe=1']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):pair_link(bad,'read/ok.html','claims.html')

    def test_link_checker_detects_missing_passages_hidden_inside_query_strings(self):
        pages={'read/one.html':Page('<p id="L1"></p>'),'side-by-side.html':Page('<h1>Reader</h1>')}
        for target in ['read/one.html#missing','read/missing.html#L1','side-by-side.html','https://example.test/one.html']:
            from urllib.parse import urlencode
            href='side-by-side.html?'+urlencode({'left':'read/one.html#L1','right':target})
            pages['claims.html']=Page('<a href="'+href.replace('&','&amp;')+'">Pair</a>')
            with self.subTest(target=target),self.assertRaises(AssertionError):check_pair_links(pages)

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
