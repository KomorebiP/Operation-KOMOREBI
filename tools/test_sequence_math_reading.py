"""Safety, completeness and markup tests for the source-driven proof reader.

Author: Komorebi P. Source is the same Markdown used on GitHub.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_math_reading import mathematical_reading_fragment, mathematical_example_gallery

ROOT=Path(__file__).resolve().parents[1]


class MathematicalReadingTests(unittest.TestCase):
    def test_central_binomial_proof_retains_all_equations_and_attribution(self):
        source=(ROOT/'research/sequence-closed-forms/CENTRAL_BINOMIAL_RECURRENCE.md').read_text(encoding='utf-8')
        content=mathematical_reading_fragment(source,include_outline=True)
        self.assertNotIn('<h1',content)
        self.assertEqual(content.count('class="arithmatex sl-math-display"'),source.count(r'\['))
        self.assertGreaterEqual(source.count(r'\['),18)
        self.assertIn('math-proof-1-definition-and-universal-recurrence',content)
        self.assertIn('math-proof-2-an-elementary-relation-from-pascal-s-identity',content)
        self.assertIn('math-proof-6-oeis-connections-and-attribution',content)
        self.assertIn('integral domain',content)
        self.assertIn('https://oeis.org/A133444',content)
        self.assertIn('https://arxiv.org/html/2608.22053v2#S7',content)
        self.assertIn('test_sequence_closed_forms_central.py',content)
        self.assertIn('test_sequence_closed_form_handoffs.py',content)
        self.assertEqual(content.count('class="sl-math-proof-code"'),1)

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

    def test_all_worked_examples_retain_their_math_and_native_disclosures(self):
        import re
        source=(ROOT/'research/sequence-closed-forms/ALGEBRAIC_KERNEL_EXAMPLES.md').read_text(encoding='utf-8')
        content=mathematical_example_gallery(source)
        self.assertEqual(content.count('class="sl-kernel-example"'),32)
        self.assertEqual(content.count('class="arithmatex sl-math-display"'),source.count(r'\['))
        self.assertIn('kernel-classical',content)
        self.assertIn('kernel-weighted',content)
        self.assertIn('kernel-polynomial',content)
        self.assertIn('kernel-recurrence',content)
        self.assertIn('Fibonacci',content)
        self.assertNotIn('<h1',content)
        targets=re.findall(r'href="#(kernel-example-\d+)"',content)
        self.assertEqual(targets,['kernel-example-'+str(n) for n in range(1,33)])
        for target in targets:
            self.assertEqual(content.count('id="'+target+'"'),1)
        # A lost or duplicate example must not silently ship an incomplete gallery.
        with self.assertRaises(ValueError):
            mathematical_example_gallery(source.replace('## Example 23.','## Example 24.',1))

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

    def test_rational_hankel_proofs_keep_math_tables_and_separate_heading_ids(self):
        import re
        source=(ROOT/'research/sequence-closed-forms/RATIONAL_HANKEL_TAILS.md').read_text(encoding='utf-8')
        linear=(ROOT/'research/sequence-closed-forms/LINEAR_WEIGHT_RECURRENCE.md').read_text(encoding='utf-8')
        full=mathematical_reading_fragment(source,include_outline=True)
        other=mathematical_reading_fragment(linear,include_outline=True,id_prefix='linear-proof-')
        self.assertEqual(full.count('class="arithmatex sl-math-display"'),source.count(r'\['))
        self.assertEqual(other.count('class="arithmatex sl-math-display"'),linear.count(r'\['))
        self.assertIn('<th scope="col">',other)
        self.assertEqual(other.count('<th scope="row">'),10)
        self.assertIn('aria-label="Scrollable mathematical table"',other)
        self.assertIn('sequence-rational-hankel.html#rational-hankel-proof',other)
        self.assertIn('sequence-differential-hankel.html',full)
        ids=re.findall(r' id="([^"]+)"',full+other)
        self.assertEqual(len(ids),len(set(ids)))
        with self.assertRaises(ValueError):
            mathematical_reading_fragment('| a | b |\n| --- | --- |\n| one |')

    def test_inline_math_is_typeset_without_processing_code(self):
        raw=r'For \(x<y\), use `\(source\)` and **exact** arithmetic.'
        content=mathematical_reading_fragment(raw)
        self.assertIn(r'<span class="arithmatex">\(x&lt;y\)</span>',content)
        self.assertIn(r'<code>\(source\)</code>',content)
        self.assertEqual(content.count('<span class="arithmatex">'),1)

    def test_compression_proofs_preserve_displays_and_disjoint_section_ids(self):
        import re
        parity=(ROOT/'research/sequence-closed-forms/PARITY_HANKEL_RECURRENCES.md').read_text(encoding='utf-8')
        mixed=(ROOT/'research/sequence-closed-forms/MIXED_HANKEL_RECURRENCE.md').read_text(encoding='utf-8')
        sharp=(ROOT/'research/sequence-closed-forms/SHARP_QUADRATIC.md').read_text(encoding='utf-8')
        uniform=(ROOT/'research/sequence-closed-forms/UNIFORM_MIXED_RECURRENCE.md').read_text(encoding='utf-8')
        exceptional=(ROOT/'research/sequence-closed-forms/EXCEPTIONAL_ORDERS.md').read_text(encoding='utf-8')
        rendered=[]
        for source,prefix in [(parity,'parity-proof-'),(mixed,'mixed-proof-'),(sharp,'sharp-proof-'),(uniform,'uniform-mixed-proof-'),(exceptional,'exceptional-proof-')]:
            content=mathematical_reading_fragment(source,include_outline=True,id_prefix=prefix)
            self.assertEqual(content.count('class="arithmatex sl-math-display"'),source.count(r'\['))
            self.assertNotIn('<h1',content)
            targets=re.findall(r'href="#([^"]+)"',content)
            for target in targets:self.assertEqual(content.count('id="'+target+'"'),1)
            rendered.append(content)
        ids=re.findall(r' id="([^"]+)"',''.join(rendered))
        self.assertEqual(len(ids),len(set(ids)))
        self.assertIn('sequence-rational-hankel.html#rational-hankel-proof',rendered[0])


if __name__=='__main__':
    unittest.main()
