"""Safety, completeness and markup tests for the source-driven proof reader.

Author: Komorebi P. Source is the same Markdown used on GitHub.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_math_reading import mathematical_reading_fragment

ROOT=Path(__file__).resolve().parents[1]


class MathematicalReadingTests(unittest.TestCase):
    def test_math_note_is_complete_and_readable(self):
        source=(ROOT/'research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md').read_text(encoding='utf-8')
        content=mathematical_reading_fragment(source)
        self.assertNotIn('<h1',content)
        self.assertGreaterEqual(content.count('<h2'),5)
        self.assertGreaterEqual(content.count('class="arithmatex sl-math-display"'),12)
        self.assertIn('rank}',content)
        self.assertIn('2(D+r)',content)
        self.assertIn('Weight-raising',content) if 'Weight-raising' in source else self.assertIn('weight-raising',content)
        self.assertIn('Chebyshev',content)
        self.assertIn('math-proof-algebraic-ordinary-generating-function-for-every-finite-differential-operator',content)
        self.assertIn('R_{P,\\mathbf c}',content)
        self.assertIn('(1-4z^2)',content)
        self.assertIn('Initial',content)
        self.assertIn('differential',content.lower())
        self.assertIn('https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/',content)
        self.assertNotIn('href="POLYNOMIAL_HANKEL_STRUCTURE.md"',content)
        self.assertEqual(content.count('class="arithmatex sl-math-display"'),source.count(r'\['))
        self.assertIn(r'\boxed',content)
        self.assertEqual(content.count('class="sl-math-proof-code"'),1)
        self.assertIn('aria-label="Scrollable code example"><code class="language-bash">',content)
        self.assertNotIn(r'\`\`\`',content)
        self.assertGreater(content.count('<span class="arithmatex">'),100)

    def test_outline_links_match_rendered_headings(self):
        import re
        source=(ROOT/'research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md').read_text(encoding='utf-8')
        content=mathematical_reading_fragment(source,include_outline=True)
        self.assertIn('<nav aria-label="Proof sections">',content)
        targets=re.findall(r'<a href="#(math-proof-[^"]+)"',content)
        headings=re.findall(r'<h[23] id="(math-proof-[^"]+)"',content)
        self.assertEqual(targets,headings)
        self.assertEqual(len(targets),8)

    def test_source_renderer_escapes_markup_and_rejects_active_urls(self):
        raw=(
            '# Title\n\n## Section\n\n'
            'A **strong** theorem and '+chr(96)+'code'+chr(96)+'.\n\n'
            '<script>alert("no")</script> [unsafe](javascript:alert(1))\n\n'
            r'\['+'\n'+r'x<y'+'\n'+r'\]'+'\n\n'
            '- First point\n- Second point\n'
        )
        content=mathematical_reading_fragment(raw)
        self.assertNotIn('<script>',content)
        self.assertIn('&lt;script&gt;',content)
        self.assertNotIn('href="javascript:',content)
        self.assertIn('<strong>strong</strong>',content)
        self.assertIn('<code>code</code>',content)
        self.assertIn('<ul><li>First point</li><li>Second point</li></ul>',content)
        self.assertIn('aria-label="Displayed mathematical equation"',content)
        self.assertIn(r'x&lt;y',content)

    def test_unclosed_tex_or_code_fails_closed(self):
        with self.assertRaises(ValueError):
            mathematical_reading_fragment('# Example\n\n'+r'\['+'\na+b')
        with self.assertRaises(ValueError):
            mathematical_reading_fragment('# Example\n\n'+chr(96)*3+'python\nprint(1)')

    def test_inline_math_is_typeset_without_processing_code(self):
        raw=r'For \(x<y\), use `\(source\)` and **exact** arithmetic.'
        content=mathematical_reading_fragment(raw)
        self.assertIn(r'<span class="arithmatex">\(x&lt;y\)</span>',content)
        self.assertIn(r'<code>\(source\)</code>',content)
        self.assertEqual(content.count('<span class="arithmatex">'),1)


if __name__=='__main__':
    unittest.main()
