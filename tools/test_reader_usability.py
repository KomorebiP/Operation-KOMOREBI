"""Shared controls must preserve the source article and every reading route."""
import re
import unittest

from check_reader_site import Page
from readable_chapters import BOOKS, Chapter, navigation_title
from reader_usability import enhance
from reading_navigation import navigation, chapter_layout, outline


class ReaderUsabilityTests(unittest.TestCase):
    def test_tex_dashes_render_in_prose_while_math_and_code_remain_exact(self):
        markup=Chapter('',{}).inline(r'Pages 10--12---a range. $1--2$ \texttt{--flag}')
        self.assertIn('Pages 10–12—a range.',markup)
        self.assertIn(r'\(1--2\)',markup)
        self.assertIn('<code>--flag</code>',markup)
        self.assertEqual(navigation_title(r'Pages 10--12 and $1--2$'),'Pages 10–12 and 1--2')

    def test_navigation_labels_remove_print_spacing_and_raw_math_delimiters(self):
        self.assertEqual(navigation_title(r'Part II\quad Extended mathematical development'),
                         'Part II · Extended mathematical development')
        self.assertEqual(navigation_title(r'Weighted bounds in the actual ring $\Z_p$'),
                         'Weighted bounds in the actual ring Z_p')
        self.assertEqual(navigation_title(r'Why a $p$-adic unit supplies one factor of $p$'),
                         'Why a p-adic unit supplies one factor of p')
        self.assertEqual(navigation_title(r'Transport through \(R\cong T\)'),
                         'Transport through R≅ T')

    def test_every_core_paper_has_all_twelve_destinations_and_one_current_work(self):
        books = {work:config for work,config in BOOKS.items() if re.fullmatch(r'paper-[ivx]+',work)}
        self.assertEqual(len(books),12)
        for work, config in books.items():
            body, enabled = enhance('<h1>Contents</h1>', config['index'])
            self.assertTrue(enabled)
            parsed = Page(body)
            self.assertEqual(len(re.findall(r'<li><a ',body)),12)
            self.assertEqual(body.count('aria-current="page"'),1)
            for other in books.values():
                target = '../'+other['work']+'/index.html' if other['work'] != work else 'index.html'
                self.assertIn(target,parsed.links)
            self.assertNotIn('Text settings',body)

    def test_chapter_controls_preserve_exact_article_and_navigation(self):
        for work,config in BOOKS.items():
            if not re.fullmatch(r'paper-[ivx]+',work):continue
            page = config['chapters'][0]['url']
            article = '<article id="chapter-text"><h2 id="L5">A &amp; B</h2><p>\\(x&lt;y\\)</p></article>'
            body = navigation(config,page)+outline('<nav class="chapter-contents"><a href="#L5">A &amp; B</a></nav>')+article+navigation(config,page,'bottom')
            body = chapter_layout(body)
            enhanced, enabled = enhance(body,page)
            self.assertTrue(enabled)
            self.assertEqual(enhanced.count(article),1)
            self.assertEqual(enhanced.count('aria-label="Keep reading"'),1)
            self.assertEqual(enhanced.count('class="reading-return"'),1)
            self.assertNotIn('class="reading-shortcuts"',enhanced)
            self.assertEqual(enhanced.count('aria-current="location"'),1)
            self.assertIn('class="reading-display" hidden',enhanced)
            parsed = Page(enhanced)
            self.assertEqual(len(parsed.ids),len(set(parsed.ids)))
            self.assertTrue(all(control['id'] in parsed.labels for control in parsed.inputs))
            self.assertEqual(enhanced.count('data-reading-placement="top"'),1)
            self.assertEqual(enhanced.count('data-reading-placement="bottom"'),1)

    def test_bibliographies_get_text_settings_without_a_fake_sidebar(self):
        config = BOOKS['paper-xii']
        body = navigation(config,config['bib_page'])+'<article id="chapter-text">References</article>'
        result, enabled = enhance(body,config['bib_page'])
        self.assertTrue(enabled)
        self.assertIn('Text settings',result)
        self.assertNotIn('Keep reading',result)

    def test_paper_finders_switch_between_finders_and_return_to_full_contents(self):
        for work,config in BOOKS.items():
            if not re.fullmatch(r'paper-[ivx]+',work):continue
            body,enabled=enhance('<h1>Statements</h1>',f'read/{work}/statements.html')
            self.assertTrue(enabled)
            self.assertIn('<a href="index.html">All chapters</a>',body)
            self.assertIn('aria-current="page"',body)
            self.assertNotIn('Text settings',body)
            for other in BOOKS:
                if re.fullmatch(r'paper-[ivx]+',other):
                    self.assertIn('statements.html' if other==work else f'../{other}/statements.html',Page(body).links)
            chapter,_=enhance('<article id="chapter-text">Source article.</article>',config['chapters'][0]['url'])
            self.assertIn('<a href="statements.html">Find statements</a>',chapter)

    def test_pdf_source_and_noncore_pages_are_unchanged(self):
        for page in ('read/paper-i/pdf.html','read/paper-i/source.html','read/index.html',
                     'collection/works/paper-i.html','read/monographs-special-functions/index.html'):
            body = '<h1>Source</h1><p>Retained content.</p>'
            self.assertEqual(enhance(body,page),(body,False))


if __name__ == '__main__':unittest.main()
