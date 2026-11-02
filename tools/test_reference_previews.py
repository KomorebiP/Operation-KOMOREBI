import unittest

from readable_chapters import Chapter
from reference_previews import build,Markup,make_entry,check


class ReferencePreviewTests(unittest.TestCase):
    def fixture(self):
        pages={'read/paper-i/a.html':'Paper I · First chapter','read/paper-i/b.html':'Paper I · Second chapter',
               'read/paper-i/references.html':'Paper I references'}
        contents={
            'read/paper-i/a.html':'<a href="b.html#L2" data-reference-preview="thm:finite">Theorem 2</a>'
                                   '<a href="b.html#L4" data-reference-preview="eq:second">(2)</a>'
                                   '<a href="references.html#ref-book" data-reference-preview="book">[1]</a>',
            'read/paper-i/b.html':'<section id="L2"><h3>Theorem 2: Finite scope</h3><p>For every <em>finite</em> model.</p>'
                                '<div class="arithmatex">\\[x&lt;y\\]</div><p class="passage-links">Skip these controls.</p></section>'
                                '<section id="L4"><div class="arithmatex" data-equation-labels="eq:first">\\[x=1\\]</div>'
                                '<div class="arithmatex" data-equation-labels="eq:second eq:alias">\\[y=2\\]</div><span class="equation-number">(2)</span></section>',
            'read/paper-i/references.html':'<section id="ref-book"><h2>Book</h2><p>Author, <em>Original title</em>.</p>'
                                         '<details class="reference-uses"><summary>Return routes</summary></details></section>'}
        return pages,contents

    def test_exact_statements_equations_and_citations_follow_their_recorded_targets(self):
        pages,contents=self.fixture();data=build(contents.__getitem__,'paper-i',pages)
        self.assertEqual(data['links'],3)
        theorem=data['entries']['read/paper-i/b.html#L2|thm:finite']
        self.assertEqual(theorem['context'],'Paper I · Second chapter')
        self.assertIn('finite',str(theorem['parts']))
        self.assertNotIn('Skip these controls',str(theorem['parts']))
        self.assertIn(r'\\[x<y\\]',repr(theorem['parts']))
        equation=data['entries']['read/paper-i/b.html#L4|eq:second']
        self.assertEqual(equation['kind'],'equation')
        self.assertNotIn('x=1',str(equation['parts']))
        self.assertIn('y=2',str(equation['parts']))
        self.assertIn('(2)',str(equation['parts']))
        citation=data['entries']['read/paper-i/references.html#ref-book|book']
        self.assertEqual(citation['kind'],'citation')
        self.assertIn('Original title',str(citation['parts']))
        self.assertNotIn('Return routes',str(citation['parts']))

    def test_missing_or_cross_paper_targets_stop_publication(self):
        pages,contents=self.fixture()
        for target in ('b.html#missing','../paper-ii/b.html#L2','https://example.test/#L2','../../outside.html#L2'):
            broken=dict(contents);broken['read/paper-i/a.html']=contents['read/paper-i/a.html'].replace('b.html#L2',target)
            with self.assertRaises(ValueError):build(broken.__getitem__,'paper-i',pages)

    def test_long_blocks_are_omitted_whole_and_source_markup_is_inert(self):
        markup=Markup('<section id="L1"><h3>Scope</h3><p onclick="bad()">Finite <strong>only</strong>.</p>'
                      '<script>bad()</script><p><a href="javascript:bad()">Literal label</a></p>'
                      '<div class="arithmatex">\\['+'x'*16000+'\\]</div></section>')
        entry=make_entry(markup.ids['L1'],'read/paper-i/a.html','thm:scope','Paper I')
        self.assertTrue(entry['excerpt'])
        self.assertIn('Finite',str(entry['parts']))
        self.assertNotIn('bad()',str(entry['parts']))
        self.assertNotIn('xxxx',str(entry['parts']),'A formula is never cut into partial TeX')

    def test_renderer_keeps_source_math_and_labels_for_exact_formula_previews(self):
        chapter=Chapter('',{})
        raw=r'\[x=1\label{eq:one}\]'
        markup=chapter.inline(raw)
        self.assertIn('data-equation-labels="eq:one"',markup)
        self.assertEqual(chapter.math,[r'x=1\label{eq:one}'])
        self.assertIn(r'\[x=1\]',markup)

    def test_section_previews_are_named_as_excerpts_even_when_short(self):
        markup=Markup('<article><h2 id="L1">Section</h2><p>Introduction.</p><h3>Details</h3><p>Later scope.</p></article>')
        entry=make_entry(markup.ids['L1'],'read/paper-i/a.html','sec:model','Paper I')
        self.assertTrue(entry['excerpt'])
        self.assertIn('Introduction.',str(entry['parts']))
        self.assertNotIn('Later scope.',str(entry['parts']))

    def test_audit_rejects_dropped_pages_context_changes_and_changed_source_math(self):
        import copy
        pages,contents=self.fixture();data=build(contents.__getitem__,'paper-i',pages)
        check(data,contents.__getitem__,'paper-i',pages)
        for change in ('pages','context','math'):
            broken=copy.deepcopy(data)
            if change=='pages':del broken['pages']['read/paper-i/a.html']
            elif change=='context':broken['entries']['read/paper-i/b.html#L2|thm:finite']['context']='Wrong chapter'
            else:broken['entries']['read/paper-i/b.html#L4|eq:second']['parts'][0]['children']=['Wrong formula']
            with self.assertRaises(AssertionError):check(broken,contents.__getitem__,'paper-i',pages)

    def test_reference_and_citation_rendering_both_enable_previews(self):
        chapter=Chapter('\\section{Model}\\label{sec:model}',{})
        chapter.url='read/paper-i/a.html'
        chapter.citations={'book':('1','references.html#ref-book')}
        markup=chapter.inline(r'\cref{sec:model} and \cite{book}')
        self.assertEqual([link.attrs['data-reference-preview'] for link in Markup(markup).references],['sec:model','book'])


if __name__=='__main__':unittest.main()
