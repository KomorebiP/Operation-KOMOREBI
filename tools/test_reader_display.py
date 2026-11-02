"""Keep shared page chrome separate from every retained manuscript article."""
import re
import unittest
from check_reader_site import Page
from readable_chapters import BOOKS,statement_directory_url
from reader_display import edition,has_statement_finder,standardize
from reader_usability import enhance


class ReaderDisplayTests(unittest.TestCase):
    def test_all_editions_preserve_the_complete_article_and_group_the_actions(self):
        article='<article id="chapter-text"><h2 id="L8">A &amp; B</h2><p>\\(x&lt;y\\)</p><a data-reference-preview="label" href="#L8">Preview source</a></article>'
        save='<div class="reading-save" data-reading-save hidden><button>Save page</button><a href="../../reading-list.html">Saved reading</a><span role="status"></span></div>'
        pair='<p class="side-launch"><a data-side-reader-link href="../../side-by-side.html">Read side by side</a></p>'
        for config in BOOKS.values():
            page=config['chapters'][0]['url']
            body='<p class="eyebrow">Readable manuscript</p><h1>'+config['label']+': Chapter title</h1>'+pair+save+article
            rendered=standardize(body,page)
            self.assertEqual(rendered.count(article),1)
            self.assertIn('<h1>Chapter title</h1>',rendered)
            self.assertIn('<div class="reading-actions">'+save+pair+'</div>',rendered)
            self.assertEqual(rendered.count('Readable manuscript'),0)
            self.assertEqual(Page(rendered).h1,1)
            self.assertEqual(Page(rendered).ids,['chapter-text','L8'])

    def test_source_and_pdf_pages_are_not_reclassified(self):
        original='<h1>Original TeX</h1><pre>Kept source</pre>'
        for page in ('read/paper-i/source-123.html','read/paper-i/pdf-123.html','collection/works/komorebi-space.html'):
            self.assertIsNone(edition(page))
            self.assertEqual(standardize(original,page),original)

    def test_finder_links_exist_only_for_editions_with_a_directory(self):
        special=BOOKS['monographs-special-functions']
        self.assertFalse(has_statement_finder(special))
        body,enabled=enhance('<h1>Contents</h1>',special['index'])
        self.assertTrue(enabled)
        self.assertNotIn('Find statements',body)
        proof=BOOKS['proof-path-theory']
        self.assertTrue(has_statement_finder(proof))
        body,_=enhance('<h1>Statements</h1>',statement_directory_url(proof))
        self.assertIn('../monographs-special-functions/index.html',Page(body).links)
        self.assertNotIn('../monographs-special-functions/statements.html',Page(body).links)

    def test_reference_headers_keep_the_manuscript_text(self):
        for config in BOOKS.values():
            if not config.get('bib_page'):continue
            article='<article id="chapter-text"><section id="ref-a">Retained reference.</section></article>'
            body='<h1>'+config['label']+' bibliography</h1>'+article
            result=standardize(body,config['bib_page'])
            self.assertIn('<h1>References</h1>',result)
            self.assertIn(article,result)

if __name__=='__main__':unittest.main()
