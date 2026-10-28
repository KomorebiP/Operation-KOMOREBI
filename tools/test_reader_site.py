"""Regression checks for source paths and reader HTML transformations."""
import unittest

from build_reader_site import Rewriter, document_url, math_fences, safe_path
from check_reader_site import Page


class ReaderSiteTests(unittest.TestCase):
    def test_math_fences_preserve_matrix_rows_and_escaped_text(self):
        matrix = r'\begin{pmatrix}1&amp;0\\0&amp;1\end{pmatrix}'
        source = '<pre><code class="language-math">'+matrix+'\n</code></pre>'
        self.assertEqual(math_fences(source), '<div class="arithmatex">\\['+matrix+'\n\\]</div>')
        ordinary = '<pre><code class="language-python">print(1)\n</code></pre>'
        self.assertEqual(math_fences(ordinary), ordinary)
        escaped = '<pre><code class="language-math">&lt;script&gt;\n</code></pre>'
        self.assertIn('&lt;script&gt;', math_fences(escaped))
        self.assertNotIn('<script>', math_fences(escaped))

    def test_bundle_paths_cannot_escape(self):
        for path in ('../private.txt','/absolute.txt','folder/../../private.txt','folder\\file.txt','C:/private.txt','file:stream',''):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_path(path)
        self.assertEqual(safe_path('files/paper.tex'),'files/paper.tex')

    def test_active_content_and_event_attributes_are_removed(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<h1>Read</h1><script>alert(1)</script><img src="figure.svg" alt="Diagram" onerror="alert(2)"><a href="javascript:alert(3)">bad</a>')
        result=''.join(rewrite.out)
        self.assertNotIn('alert(',result)
        self.assertIn('alt="Diagram"',result)

    def test_heading_and_existing_fragment_are_preserved_without_duplicates(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<h1 id="title">Title</h1><a id="packet"></a><h2 id="packet">Packet</h2><h1 id="appendix">Appendix</h1>')
        result=''.join(rewrite.out)
        page=Page(result)
        self.assertEqual(page.h1,1)
        self.assertEqual(page.ids,['title','packet','appendix'])
        self.assertIn('<h2 id="appendix">Appendix</h2>',result)

    def test_library_home_and_guide_do_not_overwrite_each_other(self):
        paths=[document_url('math',p) for p in ('README.md','docs/index.md','docs/README.md')]
        self.assertEqual(len(set(paths)),3)

    def test_wide_table_has_keyboard_region(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><tr><th>Term</th><td>Value</td></tr></table>')
        result=''.join(rewrite.out)
        self.assertIn('role="region"',result)
        self.assertIn('tabindex="0"',result)
        self.assertTrue(result.endswith('</table></div>'))


if __name__=='__main__':unittest.main()
