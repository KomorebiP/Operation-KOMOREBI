"""Regression checks for source paths and reader HTML transformations."""
import unittest
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

from build_reader_site import Rewriter, Site, document_url, math_fences, safe_path, selected_files, site_navigation, page_contents
from check_reader_site import Page, check_search_targets
from reader_documents import ReadingDocuments, page_path, source_lines, tex_includes
from fetch_pdf_runtime import extract
from claim_navigation import statements, manuscript_sources, validate_claims, PAPERS
from readable_chapters import Chapter, expand_math, plain_math, readable_url, original_math, render_table, bibliography, formal_note_labels, manuscript_bibliography, presentation_tex, passage_links, reading_options, chapter_text, validate_monolithic, FOURTH_MAIN, FOURTH_CHAPTERS


class ReaderSiteTests(unittest.TestCase):
    def test_png_dimensions_reject_missing_or_invalid_intrinsic_sizes(self):
        from reader_documents import png_dimensions
        header=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        image=header+(1200).to_bytes(4,'big')+(450).to_bytes(4,'big')+bytes(9)
        self.assertEqual(png_dimensions(image),(1200,450))
        for invalid in (b'',image[:24],b'JPEG'+image[4:],
                        header+bytes(4)+image[20:],header+(2**31).to_bytes(4,'big')+image[20:]):
            with self.assertRaises(ValueError): png_dimensions(invalid)

    def test_reading_image_size_checks_match_published_bytes(self):
        from check_reader_site import check_png_image_sizes
        image=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'+(1200).to_bytes(4,'big')+(450).to_bytes(4,'big')+bytes(9)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'figure.png').write_bytes(image)
            page=Page('<img src="../figure.png" width="1200" height="450" alt="A drawing" loading="lazy">')
            check_png_image_sizes(root,'read/plate.html',page.images)
            for attrs in ({}, {'width':'1200','height':'451'}):
                with self.assertRaisesRegex(AssertionError,'dimensions differ'):
                    check_png_image_sizes(root,'read/plate.html',[dict(src='../figure.png',**attrs)])

    def test_table_regions_use_readable_caption_names_and_retain_markup(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><caption id="transfer-caption">Transfer <em>norms</em> '
                     '&amp; &#x3B1; "values"</caption><thead><tr><th>Input</th></tr></thead>'
                     '<tbody><tr><th scope="row">Output 1</th><td>5.0</td></tr></tbody></table>')
        rendered=''.join(rewrite.out)
        self.assertIn('role="region" aria-label="Transfer norms &amp; α &quot;values&quot;" tabindex="0"',rendered)
        self.assertIn('<caption id="transfer-caption">Transfer <em>norms</em> &amp; &#x3B1; "values"</caption>',rendered)
        self.assertIn('<th scope="row">Output 1</th><td>5.0</td>',rendered)

    def test_nested_table_regions_keep_their_own_names_and_numbered_fallback(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><caption>Outer values</caption><tr><td>'
                     '<table><caption>Inner values</caption><tr><td>1</td></tr></table>'
                     '</td></tr></table><table><tr><td>2</td></tr></table>')
        rendered=''.join(rewrite.out)
        self.assertEqual(rendered.count('aria-label="Outer values"'),1)
        self.assertEqual(rendered.count('aria-label="Inner values"'),1)
        self.assertEqual(rendered.count('aria-label="Scrollable table 3"'),1)
        self.assertEqual(rendered.count('tabindex="0"'),3)

    def test_empty_and_blocked_table_captions_keep_numbered_fallbacks(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><caption> <script>Hidden label</script> </caption></table>'
                     '<table><caption>&nbsp;\n </caption></table>')
        rendered=''.join(rewrite.out)
        self.assertIn('aria-label="Scrollable table 1"',rendered)
        self.assertIn('aria-label="Scrollable table 2"',rendered)
        self.assertNotIn('Hidden label',rendered)

    def test_table_caption_names_escape_literal_markup_and_collapse_whitespace(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><caption>  Values<br>&lt;input&gt;<p>  &amp;amp; </p></caption></table>')
        rendered=''.join(rewrite.out)
        self.assertIn('aria-label="Values &lt;input&gt; &amp;amp;"',rendered)
        self.assertNotIn('<input>',rendered)

    def test_paper_iv_ledger_row_headers_preserve_every_cell_and_equation(self):
        from html.parser import HTMLParser
        from readable_chapters import BOOKS
        config=BOOKS['paper-iv']
        source=(Path(__file__).resolve().parents[1]/FOURTH_MAIN).read_text(encoding='utf-8-sig')
        tables=[node for spec in FOURTH_CHAPTERS
                for node in Chapter(chapter_text(source,spec),{},check_refs=False).nodes
                if node['kind'] in {'table','longtable','tabularx'}]
        self.assertEqual(set(config['table_reading_aids']),{n['id'] for n in tables})
        class Cells(HTMLParser):
            def __init__(self,markup):
                super().__init__(); self.cells=[]; self.active=False; self.feed(markup)
            def handle_starttag(self,tag,attrs):
                if tag in {'td','th'}: self.cells.append(''); self.active=True
            def handle_endtag(self,tag):
                if tag in {'td','th'}: self.active=False
            def handle_data(self,data):
                if self.active: self.cells[-1]+=data
        for node in tables:
            chapter=Chapter('',{})
            original=render_table(node,Chapter('',{}))
            rendered=render_table(node,chapter,config['table_reading_aids'][node['id']])
            self.assertEqual(Cells(original).cells,Cells(rendered).cells)
            self.assertEqual(chapter.math,original_math(node['body']))
            self.assertEqual(rendered.count('scope="row"'),15)
            self.assertEqual(rendered.count('scope="col"'),2)
            self.assertIn('<caption>Formalization ledger for version 1.0.0</caption>',rendered)
            self.assertIn('aria-label="Formalization ledger for version 1.0.0"',rendered)

    def test_table_reading_aids_require_reviewed_headers_and_nonempty_row_labels(self):
        aid=dict(caption='Reviewed ledger',headers=['Records','Scope'],row_header_column=0)
        node=dict(kind='tabularx',body=r'{\textwidth}{ll}Records & Scope\\3.1 & $x$\\')
        rendered=render_table(node,Chapter('',{}),aid)
        self.assertIn('<th scope="row">3.1</th><td>',rendered)
        self.assertNotIn('scope="row"',render_table(node,Chapter('',{})))
        for body in (node['body'].replace('Records','New column'),
                     node['body'].replace('3.1 &',' &')):
            with self.assertRaises(ValueError):
                render_table(dict(node,body=body),Chapter('',{}),aid)
        for column in (-1,2,True):
            with self.assertRaises(ValueError):
                render_table(node,Chapter('',{}),dict(aid,row_header_column=column))
        captioned=dict(kind='table',body=r'\caption{Authored caption}\begin{tabular}{ll}Records & Scope\\3.1 & $x$\\\end{tabular}')
        with self.assertRaisesRegex(ValueError,'authored caption'):
            render_table(captioned,Chapter('',{}),aid)

    def test_authored_tables_retain_captions_and_both_header_axes(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<table><caption>Transfer norms</caption><thead><tr>'
                     '<th>Output / input</th><th>Input 0</th></tr></thead>'
                     '<tbody><tr><th scope="row">Output 0</th><td>5.0</td>'
                     '</tr></tbody></table>')
        rendered=''.join(rewrite.out)
        self.assertIn('<table><caption>Transfer norms</caption>',rendered)
        self.assertEqual(rendered.count('scope="col"'),2)
        self.assertIn('<th scope="row">Output 0</th><td>5.0</td>',rendered)

    def test_atlas_plate_boundaries_retain_original_lines_and_reject_reordering(self):
        from reader_atlas import plates
        source='\n'.join('\\vpage{'+str(i)+'}{Title}{Topic}{Section 1 (p. 1).}\nText $x$.' for i in range(1,27))
        parsed=plates(source)
        self.assertEqual(parsed[2]['line'],5)
        self.assertEqual(Chapter(parsed[2]['body'],{}).nodes[0]['line'],6)
        self.assertEqual(parsed[2]['url'],'read/paper-iv/atlas/v03.html')
        with self.assertRaises(ValueError): plates(source.replace(r'\vpage{3}',r'\vpage{4}'))
        with self.assertRaises(ValueError): plates(source+'\n'+r'\vpage{27}{Extra}{Topic}{Reference}')

    def test_atlas_wrappers_preserve_prose_math_and_line_numbers(self):
        from reader_atlas import atlas_tex
        source='\\head{A model}\nText $a$.\n\\vfig{model}\n\\takeaway{Keep $b$.}\n\\platecaption{Scope $c$.}'
        converted=atlas_tex(source)
        self.assertEqual(original_math(source),original_math(converted))
        self.assertEqual(converted.count('\n'),source.count('\n'))
        nodes=Chapter(converted,{}).nodes
        self.assertEqual([n['line'] for n in nodes],[1,2,3,4,5])
        self.assertIn('Evidence note from the source edition',nodes[-1]['title'])

    def test_atlas_drawing_labels_keep_nested_math_and_reject_untranscribed_math(self):
        from reader_atlas import drawing_nodes
        source='\\node[anchor=west] at (1,2) {Value $\\frac{1}{2}$.};\n\\node[] at (2,3) {$y$};'
        nodes=drawing_nodes(source)
        self.assertEqual([n['line'] for n in nodes],[1,2])
        self.assertEqual(nodes[0]['text'],r'Value $\frac{1}{2}$.')
        with self.assertRaises(ValueError): drawing_nodes(source+' $z$')
        with self.assertRaises(ValueError): drawing_nodes(source+r'\node (named) {$z$};')

    def test_atlas_transcript_requires_each_label_once(self):
        from reader_atlas import transcript_order
        from paper_iv_atlas_descriptions import figure,table
        nodes=[dict(text='$x$'),dict(text='$y$')]
        description=figure('Alt','Description',table('Values',['Name','Value'],[['First',0],['Second',1]]))
        self.assertEqual(transcript_order(description,nodes),[0,1])
        description['blocks'][0]['rows'][1][1]=0
        with self.assertRaises(ValueError): transcript_order(description,nodes)
        description['blocks'][0]['rows'].pop()
        with self.assertRaises(ValueError): transcript_order(description,nodes)

    def test_atlas_references_resolve_to_manuscript_statements(self):
        from reader_atlas import source_references
        rendered=source_references('Traditional monograph: Theorem 3.1 (p. 4).',{('Theorem','3.1'):'chapter.html#L346'},lambda x:x)
        self.assertIn('href="chapter.html#L346">Theorem 3.1 (p. 4)</a>',rendered)
        with self.assertRaises(ValueError): source_references('Theorem 3.2 (p. 5).',{},lambda x:x)

    def test_atlas_tables_expose_headers_and_original_label_values(self):
        from reader_atlas import render_drawing
        from paper_iv_atlas_descriptions import figure,table
        drawing=dict(description=figure('Two values','Description',table('Values',['Term','Value'],[['First',0],['Second',1]])),
                     receipt=dict(image='image.png',source='figure.tex'),nodes=[dict(text='$x$'),dict(text='$y$')],width=1200,height=450)
        reader=SimpleNamespace(site=SimpleNamespace(rel=lambda path,page:path),resolve=lambda path,page:'source.html')
        chapter=Chapter('',{})
        rendered=render_drawing(drawing,chapter,reader)
        self.assertEqual(chapter.math,['x','y'])
        self.assertIn('width="1200" height="450"',rendered)
        self.assertIn('<caption>Values</caption>',rendered)
        self.assertEqual(rendered.count('scope="col"'),2)
        self.assertEqual(rendered.count('scope="row"'),2)
        self.assertIn('tabindex="0" role="region"',rendered)
        self.assertIn('id="drawing-label-1"',rendered)

    def test_atlas_return_links_follow_only_explicit_references_and_deduplicate(self):
        from reader_atlas import manuscript_backlinks
        selected=[dict(number=3,title='A filter',url='atlas/v03.html',locator='Theorem 3.1 (p. 4), Theorem 3.1 (p. 4).'),
                  dict(number=4,title='A product',url='atlas/v04.html',locator='Theorem 3.1 (p. 4), Section 3 (p. 3).')]
        references={('Theorem','3.1'):'chapter.html#L30',('Section','3'):'chapter.html#L20',('Proposition','3.2'):'chapter.html#L40'}
        links=manuscript_backlinks(selected,references)
        self.assertEqual([p['number'] for p in links['chapter.html#L30']],[3,4])
        self.assertEqual([p['number'] for p in links['chapter.html#L20']],[4])
        self.assertNotIn('chapter.html#L40',links)
        del references[('Section','3')]
        with self.assertRaises(ValueError): manuscript_backlinks(selected,references)

    def test_atlas_formula_order_includes_diagram_between_source_passages(self):
        from reader_atlas import expected_math
        plate=dict(body=r'$a$\vfig{drawing}$d$')
        figures={'drawing':dict(order=[1,0],nodes=[dict(text='$c$'),dict(text='$b$')])}
        self.assertEqual(expected_math(plate,figures),['a','b','c','d'])

    def test_atlas_long_drawing_formulas_scroll_without_changing_math(self):
        from reader_atlas import render_drawing
        from paper_iv_atlas_descriptions import figure,text
        formula=r'\frac{\partial^{12}f}{\partial x^{12}}+\frac{1}{123456789}'
        drawing=dict(description=figure('A formula','Description',text(0,1)),
                     receipt=dict(image='image.png',source='figure.tex'),
                     nodes=[dict(text='Value $'+formula+'$.'),dict(text='$x$')],width=1200,height=450)
        reader=SimpleNamespace(site=SimpleNamespace(rel=lambda path,page:path),resolve=lambda path,page:'source.html')
        chapter=Chapter('',{})
        rendered=render_drawing(drawing,chapter,reader)
        self.assertEqual(chapter.math,[formula,'x'])
        self.assertEqual(rendered.count('role="group" aria-label="Displayed equation. Scroll horizontally if needed."'),2)
        self.assertEqual(rendered.count('tabindex="0"'),2)

    def test_reading_tools_preserve_proof_links_and_no_script_access(self):
        from html.parser import HTMLParser
        class ToolLinks(HTMLParser):
            def __init__(self, text):
                super().__init__(); self.optional=False; self.links=[]; self.feed(text)
            def handle_starttag(self, tag, attrs):
                attrs=dict(attrs)
                self.assert_visible(attrs)
                if 'passage-tools' in attrs.get('class','').split(): self.optional=True
                if tag=='a': self.links.append((attrs['href'],self.optional))
            def handle_endtag(self, tag):
                if tag in {'span','p'}: self.optional=False
            def assert_visible(self, attrs):
                if 'hidden' in attrs: raise AssertionError('Source links must work without JavaScript')
        source='<a href="source.html#L10">Source line 10</a>'
        proof='<a href="#L20">Read proof</a>'
        parsed=ToolLinks(passage_links(source,proof))
        self.assertEqual(parsed.links,[('#L20',False),('source.html#L10',True)])
        self.assertEqual(ToolLinks(passage_links(source)).links,[('source.html#L10',True)])
        self.assertNotIn('<nav',passage_links(source,proof))
        from readable_chapters import related_reading_links
        chapter=Chapter('',{})
        chapter.url='read/paper-iv/chapter.html'
        chapter.related_readings={'L10':[('Atlas V3: A < B','read/paper-iv/atlas/v03.html')]}
        atlas=related_reading_links(chapter,'L10')
        self.assertIn('A &lt; B',atlas)
        self.assertEqual(ToolLinks(passage_links(source,proof+' · '+atlas)).links,
                         [('#L20',False),('atlas/v03.html',False),('source.html#L10',True)])
        options=Page(reading_options())
        self.assertIn('show-passage-tools',options.labels)
        self.assertEqual(options.inputs[0]['aria-controls'],'chapter-text')
        self.assertIn('#chapter-text',options.links)

    def test_monolithic_ranges_preserve_lines_and_route_claims_to_their_chapter(self):
        source='Preamble\n\\section{One}\nText $x$.\n\\section{Two}\nText $y$.\n'
        spec=dict(start_line=4,end_line=5)
        chapter=Chapter(chapter_text(source,spec),{},section_offset=1)
        self.assertEqual(chapter.nodes[0]['line'],4)
        self.assertEqual(chapter.nodes[0]['number'],'2')
        self.assertEqual(original_math(chapter_text(source,spec)),['y'])
        for spec in FOURTH_CHAPTERS:
            self.assertEqual(readable_url(FOURTH_MAIN,spec['start_line']),spec['url']+'#L'+str(spec['start_line']))
            self.assertEqual(readable_url(FOURTH_MAIN,spec['end_line']),spec['url']+'#L'+str(spec['end_line']))
        self.assertEqual(readable_url(FOURTH_MAIN),FOURTH_CHAPTERS[0]['url'])
        self.assertIsNone(readable_url(FOURTH_MAIN,1))

    def test_monolithic_validation_rejects_changed_boundaries_gaps_and_headings(self):
        source='\\begin{document}\nIntro $x$.\n\\section{One}\nBody $y$.\n\\end{document}'
        config=dict(chapters=[dict(start_line=1,end_line=2,title='Orientation'),dict(start_line=3,end_line=5,title='One')])
        validate_monolithic(source,config)
        with self.assertRaises(ValueError): validate_monolithic('\n'+source,config)
        with self.assertRaises(ValueError): validate_monolithic(source.replace('{One}','{Two}'),config)
        config['chapters'][0]['end_line']=1
        with self.assertRaises(ValueError): validate_monolithic(source,config)

    def test_paper_iv_wrappers_preserve_prose_formulas_and_source_lines(self):
        source=('\\begin{document}\n\\KomorebiCover\n\\KomorebiOpeningNote{Read $a$.\nThen $b$.}\n'
                '\\begin{abstract}Abstract $c$.\\end{abstract}\n'
                '\\modelfigure{model}{Caption $d$.}{fig:model}\n\\end{document}')
        converted=presentation_tex(source)
        self.assertEqual(converted.count('\n'),source.count('\n'))
        chapter=Chapter(source,{})
        self.assertEqual([n['line'] for n in chapter.nodes],[3,5,6])
        self.assertEqual([n['kind'] for n in chapter.nodes],['readerroadmap','readerroadmap','figure'])
        self.assertEqual(original_math(converted),original_math(source))
        self.assertIn('Read $a$.\nThen $b$.',converted)
        self.assertEqual(chapter.labels['fig:model']['line'],6)

    def test_paper_iv_part_numbers_and_upright_math_presentation(self):
        chapter=Chapter(r'\part{Products}\section{Products}\begin{theorem}Text\end{theorem}',{},state=dict(part=3,section=11))
        self.assertEqual(chapter.nodes[0]['number'],'Part IV')
        self.assertEqual(chapter.nodes[2]['number'],'12.1')
        self.assertEqual(expand_math(r'\Thetafun_N',{'Thetafun':r'\symup{\Theta}'}),r'{\mathrm{\Theta}}_N')

    def test_paper_iv_continued_table_header_is_not_a_data_row(self):
        node=dict(kind='longtable',body=r'{ll}\toprule Records & Scope\\\midrule\endfirsthead\toprule Records & Scope (continued)\\\midrule\endhead $x$ & $y$\\\bottomrule')
        chapter=Chapter('',{})
        rendered=render_table(node,chapter)
        self.assertEqual(rendered.count('<th scope="col">'),2)
        self.assertEqual(rendered.count('<td>'),2)
        self.assertEqual(chapter.math,['x','y'])
        node['body']=node['body'].replace('Scope (continued)','Different (continued)')
        with self.assertRaises(ValueError): render_table(node,Chapter('',{}))

    def test_paper_i_lists_keep_math_before_inside_and_after_items(self):
        source=r'$a$ before. \begin{enumerate}\item $b$\item $c$\end{enumerate} After $d$.'
        chapter=Chapter('',{})
        chapter.paragraphs(source)
        self.assertEqual(chapter.math,['a','b','c','d'])
        description=r'$a$ \begin{description}\item[Name $b$.] Meaning $c$.\end{description} $d$'
        chapter=Chapter('',{})
        rendered=chapter.paragraphs(description)
        self.assertEqual(chapter.math,['a','b','c','d'])
        self.assertIn('<dt>Name ',rendered)
        self.assertIn('</dt><dd>',rendered)

    def test_paper_i_literal_argument_macros_keep_nested_groups_and_matrix_rows(self):
        macros={'norm':dict(arguments=1,body=r'\left\lVert#1\right\rVert'),
                'mat':dict(arguments=1,body=r'\begin{pmatrix}#1\end{pmatrix}'), 'R':r'\mathbb R'}
        self.assertEqual(expand_math(r'\norm{\mat{1&2\\3&\R}}',macros),
                         r'{\left\lVert{\begin{pmatrix}1&2\\3&{\mathbb R}\end{pmatrix}}\right\rVert}')
        with self.assertRaises(ValueError): expand_math(r'\norm x',macros)

    def test_paper_i_print_metadata_keeps_source_lines_and_statement_labels(self):
        source=('\\section{One}\n\\begin{theorem}Statement $x$.\\end{theorem}\n'
                '\\RecordID{stable}\n\\Depends{Hidden \\nolinkurl{metadata}.}\n'
                '\\begin{proof}Proof $y$.\\end{proof}')
        chapter=Chapter(source,{})
        self.assertEqual([n['line'] for n in chapter.nodes],[1,2,5])
        self.assertEqual(chapter.labels['record:stable']['line'],2)
        self.assertEqual(chapter.labels['record:stable']['number'],'1.1')

    def test_paper_i_panels_and_conceptual_diagrams_keep_original_math(self):
        source=r'\begin{microexample}[title={A model with $x$}]Use $y$.\end{microexample}'+'\n'+r'\ConceptChain{\(x\longrightarrow y\)}'
        chapter=Chapter(source,{})
        self.assertEqual([n['kind'] for n in chapter.nodes],['microexample','conceptchain'])
        self.assertEqual(chapter.nodes[1]['line'],2)
        for node in chapter.nodes:
            chapter.inline(node['title'])
            chapter.paragraphs(node['body'])
        self.assertEqual(chapter.math,original_math(source))

    def test_paper_i_longtable_has_one_header_and_retains_caption(self):
        node=dict(kind='longtable',body=r'{ll}\caption{Values}\label{tab:v}\\\toprule A & B\\\midrule\endfirsthead\toprule A & B\\\midrule\endhead $x$ & $y$\\\bottomrule')
        chapter=Chapter('',{})
        rendered=render_table(node,chapter)
        self.assertEqual(rendered.count('<th scope="col">'),2)
        self.assertEqual(rendered.count('<td>'),2)
        self.assertIn('<caption>Values</caption>',rendered)
        self.assertEqual(chapter.math,['x','y'])
        node['body']=node['body'].replace(r'\endfirsthead\toprule A',r'\endfirsthead\toprule Changed')
        with self.assertRaises(ValueError): render_table(node,Chapter('',{}))

    def test_paper_i_bibliography_preserves_author_accents_and_link_labels(self):
        source="Introduction\n"+r"\begin{thebibliography}{99}"+"\n"+r"\bibitem{key}Skowro{\'n}ski. \href{https://doi.org/example}{Original DOI}.\end{thebibliography}"
        entries=manuscript_bibliography(source)
        self.assertEqual(entries[0]['line'],3)
        rendered=Chapter('',{}).paragraphs(presentation_tex(entries[0]['body']))
        self.assertIn('Skowroński.',rendered)
        self.assertIn('<a href="https://doi.org/example">Original DOI</a>',rendered)

    def test_navigation_has_nested_relative_links_and_current_page(self):
        from html.parser import HTMLParser
        class Links(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.links=[]
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                if tag == 'a':self.links.append(dict(attrs))
        links=Links(site_navigation('collection/GLOSSARY.html')).links
        self.assertEqual([a['href'] for a in links if a.get('aria-current')=='page'], ['GLOSSARY.html'])
        self.assertIn('../search.html', [a['href'] for a in links])
        self.assertIn('PHYSICS_COLLECTION.html', [a['href'] for a in links])
        self.assertEqual(len(links),15)
        self.assertEqual(len({a['href'] for a in links}),15)
        physics=Links(site_navigation('collection/PHYSICS_COLLECTION.html')).links
        self.assertEqual([a['href'] for a in physics if a.get('aria-current')=='page'], ['PHYSICS_COLLECTION.html'])
        search=Links(site_navigation('search.html')).links
        self.assertEqual([a['href'] for a in search if a.get('aria-current')=='page'], ['search.html'])

    def test_contents_preserves_actual_heading_ids_and_plain_labels(self):
        content=('<h1>Guide</h1><h2 id="a&amp;b">A &amp; <code>B</code></h2>'
                 '<h3 id="detail">Detail</h3><h2 id="two">Second</h2>'
                 '<h2 id="three">Third</h2><h2 id="four">Fourth</h2>')
        rendered=page_contents(content)
        self.assertIn('href="#a%26b">A &amp; B</a>',rendered)
        self.assertNotIn('#detail',rendered)
        self.assertEqual(rendered.count('<li>'),4)
        self.assertIn('<details class="page-contents">',rendered)
        self.assertNotIn(' open',rendered)

    def test_contents_omits_short_guides_and_headings_without_targets(self):
        self.assertEqual(page_contents('<h2 id="one">One</h2><h2>No ID</h2>'*2),'')

    def test_contents_keeps_sections_with_explicit_markdown_anchors(self):
        content=('<p><a id="linear-foundations"></a></p>\n<h2>Linear foundations</h2>'
                 '<a id="unrelated"></a><p>Intervening prose.</p><h2>No target</h2>'
                 '<h2 id="two">Two</h2><h2 id="three">Three</h2><h2 id="four">Four</h2>')
        rendered=page_contents(content)
        self.assertIn('href="#linear-foundations">Linear foundations</a>',rendered)
        self.assertNotIn('#unrelated',rendered)
        self.assertEqual(rendered.count('<li>'),4)

    def test_readable_macro_expansion_preserves_matrix_row_separators(self):
        self.assertEqual(expand_math(r'A\\N+\N',{'N':r'\mathbb N'}),r'A\\N+{\mathbb N}')
        self.assertEqual(expand_math(r'A\\\N',{'N':r'\mathbb N'}),r'A\\{\mathbb N}')

    def test_readable_math_keeps_double_primes_and_accent_groups(self):
        self.assertEqual(expand_math(r"F''(x)+\text{\'e}",{}),"F''(x)+\\text{é}")
        chapter=Chapter('',{})
        self.assertEqual(chapter.preview("The derivative $F''(x)$ exists.")[1]['text'],"F''(x)")

    def test_readable_chapter_ids_are_unique_for_same_line_heading_and_prose(self):
        chapter=Chapter(r'\section{One}\paragraph{Convention.} Same-line prose.',{})
        self.assertEqual([n['id'] for n in chapter.nodes],['L1','L1-2','L1-3'])
        self.assertEqual([n['line'] for n in chapter.nodes],[1,1,1])

    def test_readable_cross_chapter_reference_and_appendix_numbering(self):
        first=Chapter('\\section{One}\n\\begin{theorem}[Exact]\\label{thm:exact}True.\\end{theorem}',{})
        second=Chapter('\\section{Two}\nSee \\cref{thm:exact}.\n\\appendix\n\\section{Notation}\n\\subsection*{Conventions}\n\\subsection{Symbols}',{},state={'section':first.section},check_refs=False)
        second.url='read/book/second.html'
        first.labels['thm:exact']['url']='read/book/first.html'
        second.labels.update(first.labels)
        second.validate_references()
        self.assertIn('href="first.html#L2"',second.inline(r'\cref{thm:exact}'))
        self.assertEqual([n['number'] for n in second.nodes if n['kind'] in {'section','subsection'}],['2','A','','A.1'])

    def test_readable_lists_align_and_labeled_equations_keep_expression_order(self):
        source=r'\begin{enumerate}[label=(\alph*)]\item $x$\item \[y=1\label{eq:y}\]\end{enumerate}'+'\n'+r'\begin{align*}a&=b\\c&=d\end{align*}'
        chapter=Chapter('',{})
        rendered=chapter.paragraphs(source)
        self.assertIn('<ol type="a">',rendered)
        self.assertEqual(chapter.math,original_math(source))
        self.assertNotIn('label{eq:y}',rendered)
        self.assertIn(r'\begin{aligned}',rendered)

    def test_readable_tables_preserve_columns_and_math_cells(self):
        node={'kind':'longtable','body':r'{llll}\toprule A & B & C & D \\\midrule $x$ & $y$ & {group} & four \\\bottomrule'}
        # Grouping in prose is intentionally unsupported, even inside a cell.
        with self.assertRaises(ValueError): render_table(node,Chapter('',{}))
        node['body']=node['body'].replace('{group}','group')
        chapter=Chapter('',{})
        rendered=render_table(node,chapter)
        self.assertEqual(rendered.count('<th scope="col">'),4)
        self.assertEqual(rendered.count('<td>'),4)
        self.assertEqual(chapter.math,['x','y'])

    def test_readable_citations_keep_optional_location_and_literal_key(self):
        chapter=Chapter('',{})
        chapter.citations={'Current1990':('Current1990','references.html#ref-Current1990')}
        rendered=chapter.inline(r'\cite[Chapter~VII, \S4]{Current1990}')
        self.assertIn('[Current1990]',rendered)
        self.assertIn('Chapter\u00a0VII, §4',rendered)
        entries=bibliography('@book{Current1990,author={{An Author}},year={1990}}')
        self.assertEqual(entries[0]['fields']['author'],'{An Author}')
        with self.assertRaises(ValueError): bibliography('@string{unexpected="not a supported record"}')

    def test_readable_formal_notes_preserve_scope_without_creating_a_mapping(self):
        chapter=Chapter('',{})
        chapter.formal_labels=formal_note_labels(r'\newcommand{\statusroadmap}[1]{\par\textbf{Outside the finite formal contract.} #1}')
        rendered=chapter.inline(r'\statusroadmap{Candidate \leanname{Example.notYetProved}.}')
        self.assertIn('Outside the finite formal contract.',rendered)
        self.assertIn('<code>Example.notYetProved</code>',rendered)
        self.assertNotIn('href=',rendered)
        preview=chapter.preview(r'\statusroadmap{Candidate \leanname{Example.notYetProved}.}')
        self.assertEqual(preview,[{'type':'text','text':'Outside the finite formal contract. Candidate Example.notYetProved.'}])

    def test_readable_preview_preserves_parenthesized_math(self):
        self.assertEqual(Chapter('',{}).preview(r'Use \(F\prime\) here.')[1],{'type':'math','text':r'F\prime'})

    def test_original_math_excludes_algorithm_literals(self):
        self.assertEqual(original_math('$x$\n'+r'\begin{lstlisting}cost = "$5" # 50%\end{lstlisting}'+'\n'+r'\(y\)'),['x','y'])

    def test_readable_chapter_preserves_math_order_and_resolves_forward_references(self):
        source = ('\\section{Coordinates}\\label{sec:coordinates}\n'
                  'See \\cref{thm:identity}.\n'
                  '\\begin{theorem}[Identity]\\label{thm:identity}\n'
                  '$x<y$ and \\[A_{i,j}=\\sum_k B_{i,k}C_{k,j}.\\]\n\\end{theorem}\n'
                  '\\begin{proof}Use $I_X$.\\end{proof}')
        chapter = Chapter(source, {}, 2)
        rendered = ''.join(chapter.paragraphs(n['body']) for n in chapter.nodes)
        self.assertEqual(chapter.labels['thm:identity']['number'], '3.1')
        self.assertIn('href="#L3"', rendered)
        self.assertIn('x&lt;y', rendered)
        self.assertEqual(chapter.math, ['x<y','A_{i,j}=\\sum_k B_{i,k}C_{k,j}.','I_X'])
        self.assertEqual(chapter.references,['thm:identity'])

    def test_readable_chapter_stops_for_unsupported_or_unresolved_source(self):
        for source in ('\\begin{unknown}lost\\end{unknown}', '\\section{One}\n\\input{secret}',
                       '\\section{One}\n\\cref{missing}', '\\section{One}\n$x', '\\section{One}\n{unhandled}'):
            with self.subTest(source=source), self.assertRaises((ValueError,KeyError)):
                chapter = Chapter(source,{})
                for node in chapter.nodes: chapter.paragraphs(node['body'])

    def test_readable_math_macros_have_boundaries_and_do_not_change_operators(self):
        self.assertEqual(expand_math(r'\Pcal_i+\PcalOther=\Acal', {'Pcal':r'\mathcal P','Acal':r'\mathcal A'}),
                         r'{\mathcal P}_i+\PcalOther={\mathcal A}')
        with self.assertRaises(ValueError): expand_math(r'\loop', {'loop':r'\loop'})
        self.assertIsNone(readable_url('another/paper.tex',4))
        text, names = plain_math(r'\rho:J\longrightarrow I')
        self.assertIn('ρ',text)
        self.assertIn('rho',names)

    def test_readable_search_preview_keeps_math_and_resolves_reference_names(self):
        chapter=Chapter('\\section{One}\n\\begin{theorem}[Example]\\label{thm:a}True.\\end{theorem}',{})
        parts=chapter.preview(r'By \cref{thm:a}, $P_\alpha=\sum_\beta Q_\beta$ holds.')
        self.assertEqual(parts,[{'type':'text','text':'By theorem 1.1, '},
                                {'type':'math','text':r'P_\alpha=\sum_\beta Q_\beta'},
                                {'type':'text','text':' holds.'}])

    def test_source_backlinks_keep_exact_claim_and_counterpart_locations(self):
        reader = ReadingDocuments.__new__(ReadingDocuments)
        reader.site = SimpleNamespace(rel=lambda target,page:'../../'+target)
        row = dict(id='Exact-Claim', title='A < B', statement_line=2, proof_line=4)
        reader.claims_by_source = {'main.tex':[row]}
        result = source_lines('intro\nstatement\nend\nproof', reader.source_annotations('main.tex','read/work/main.html'))
        page = Page(result)
        self.assertEqual([i for i in page.ids if i.startswith('L')], ['L1','L2','L3','L4'])
        self.assertIn('../../claims.html#exact-claim', page.links)
        self.assertIn('#L2', page.links)
        self.assertIn('#L4', page.links)
        self.assertIn('A &lt; B', result)
        self.assertEqual(result.count('aria-label="Related claim"'), 2)
        self.assertEqual(reader.source_annotations('unmapped.tex','read/work/main.html'), {})

    def test_work_routes_link_examples_only_when_a_route_is_recorded(self):
        reader = ReadingDocuments.__new__(ReadingDocuments)
        reader.site = SimpleNamespace(rel=lambda target,page:target)
        reader.records = {'paper.pdf':dict(work='paper-ii',format='pdf',title='Read PDF',url='read/paper-ii/paper.html')}
        reader.manuscript_roots = {'paper-ii':'main.tex'}
        reader.learning = {'learning_topics':[{'works':['paper-ii'],'example':'docs/examples/transfer.md'}]}
        routes = Page(reader.work_routes('paper-ii','index.html')).links
        self.assertIn('claims.html#paper-ii', routes)
        self.assertIn('search.html?work=paper-ii', routes)
        self.assertIn('collection/works/paper-ii.html#worked-examples-for-this-work', routes)
        other = reader.work_routes('other','index.html')
        self.assertNotIn('Worked examples', other)
        self.assertNotIn('claims.html#other', other)
        self.assertIn('read/paper-iv/atlas/index.html',Page(reader.work_routes('paper-iv','index.html')).links)
        self.assertNotIn('read/paper-iv/atlas/index.html',routes)

    def test_example_search_membership_follows_recorded_learning_routes(self):
        reader = ReadingDocuments.__new__(ReadingDocuments)
        reader.site = SimpleNamespace(components={'paper-i':{},'paper-ii':{}})
        reader.learning = {'learning_topics':[{'works':['paper-i','paper-ii'],'example':'docs/examples/transfer.md'}]}
        self.assertEqual(reader.document_works('collection','docs/examples/transfer.md'), ['paper-i','paper-ii'])
        self.assertEqual(reader.document_works('collection','docs/works/paper-i.md'), ['paper-i'])
        self.assertEqual(reader.document_works('collection','docs/GLOSSARY.md'), [])
        self.assertEqual(reader.document_works('math','docs/examples/transfer.md'), [])

    def test_search_fragments_must_exist_in_the_target_page(self):
        pages={'claims.html':Page('<article id="first"></article>')}
        check_search_targets([{'url':'claims.html#first'}],pages)
        for target in ('claims.html#missing','missing.html#first','https://example.com/claims.html'):
            with self.subTest(target=target), self.assertRaises(AssertionError):
                check_search_targets([{'url':target}],pages)

    def test_statement_locations_ignore_examples_and_do_not_guess_proof_links(self):
        text = ('% \\begin{theorem}[Comment]\\end{theorem}\n'
                '\\begin{verbatim}\\begin{lemma}Fake\\end{lemma}\\end{verbatim}\n'
                '\\begin{theorem}[A {map [a,b]}]\\label{thm:a}\nTrue.\\end{theorem}\n'
                '\\begin{proof}Argument.\\end{proof}\n'
                '\\begin{conjecture}[Still open]Claim.\\end{conjecture}\n'
                'An unrelated paragraph.\n\\begin{proof}Other argument.\\end{proof}')
        rows = statements(text, 'paper/main.tex', 'paper-ii', 'a'*64)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['statement_line'], 3)
        self.assertEqual(rows[0]['proof_line'], 5)
        self.assertEqual(rows[0]['labels'], ['thm:a'])
        self.assertEqual(rows[1]['kind'], 'conjecture')
        self.assertIsNone(rows[1]['proof_line'])
        self.assertEqual(rows[0]['lean'], [])
        self.assertTrue(all(r['status']=='written_statement' for r in rows))

    def test_literal_inputs_resolve_from_main_directory_and_stay_owned(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            texts = {'paper/main.tex':'\\input{parts/first}',
                     'paper/parts/first.tex':'\\input{parts/second}\\input{../../private}',
                     'paper/parts/second.tex':'\\begin{theorem}Yes.\\end{theorem}'}
            owned = {}
            for path, text in texts.items():
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(text.encode())
                owned[path] = {'sha256':hashlib.sha256(text.encode()).hexdigest()}
            sources = manuscript_sources(root, None, 'paper/main.tex', owned)
            self.assertEqual(list(sources), list(texts))

    def test_claim_index_has_all_core_papers_and_preserves_paper_i_statuses(self):
        root = Path(__file__).resolve().parents[1]
        paths = set()
        for work in PAPERS:
            receipt = json.loads((root/('manifests/source-imports/'+work+'.json')).read_bytes())
            paths.update(receipt['destination']+'/'+r['path'] for r in receipt['files'])
        data = validate_claims(root, paths)
        self.assertEqual({r['work_id'] for r in data['records']}, set(PAPERS))
        first = [r for r in data['records'] if r['work_id']=='paper-i']
        self.assertEqual(len(first), 108)
        self.assertEqual(sum(r['status']=='covered' for r in first), 69)

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

    def test_pdf_companions_are_included_and_directories_are_not_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'manifests/source-imports').mkdir(parents=True)
            entries=[dict(path=p,mode='100644',size=12) for p in ('paper.pdf','visual.pdf','formal.pdf')]
            (root/'manifests/source-imports/example.json').write_text(json.dumps(dict(files=entries)))
            component=dict(id='example',destination='papers/example',resources=[
                dict(path='paper.pdf',kind='pdf'),dict(path='visual.pdf',kind='visual'),
                dict(path='formal.pdf',kind='formal_guide'),dict(path='formal/',kind='lean')])
            result=selected_files(root,component)
            self.assertEqual({r['path'] for r in result},{'paper.pdf','visual.pdf','formal.pdf'})

    def test_copied_document_must_match_source_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            raw=b'%PDF-1.7\noriginal'
            (root/'paper.pdf').write_bytes(raw)
            entry=dict(repository_path='paper.pdf',size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
            site=SimpleNamespace(root=root,cache=None)
            self.assertEqual(Site.read_source(site,entry),raw)
            (root/'paper.pdf').write_bytes(raw.replace(b'original',b'modified'))
            with self.assertRaisesRegex(ValueError,'Source receipt mismatch'):
                Site.read_source(site,entry)

    def test_primary_pdf_accepts_a_descriptive_title_without_guessing_between_companions(self):
        reader=ReadingDocuments.__new__(ReadingDocuments)
        original=dict(work='essay',format='pdf',title='Original September 2026 PDF')
        reader.records={'original.pdf':original}
        self.assertIs(reader.primary_pdf('essay'),original)
        reader.records['companion.pdf']=dict(work='essay',format='pdf',title='Companion')
        self.assertIsNone(reader.primary_pdf('essay'))
        original['title']='Read PDF'
        self.assertIs(reader.primary_pdf('essay'),original)

    def test_only_receipted_regular_reading_files_get_local_pages(self):
        reader=ReadingDocuments.__new__(ReadingDocuments)
        reader.records={}
        reader.owned={p:dict(mode=mode,size=size,work='sample',git_blob_sha1='a'*40)
                      for p,mode,size in [('paper.pdf','100644',30),('link.pdf','120000',20),('huge.json','100644',4000000),('tool.exe','100755',40)]}
        self.assertIsNotNone(reader.add('paper.pdf','Read PDF'))
        for path in ('missing.pdf','link.pdf','huge.json','tool.exe'):
            self.assertIsNone(reader.add(path))

    def test_tex_sections_are_linked_without_executing_or_guessing_macros(self):
        owned={'work/main.tex':{},'work/foundations.tex':{},'work/refs.bib':{}}
        text='% \\input{ignored}\n\\input{foundations}\n\\bibliography{refs}\n\\input{\\variable}\n\\input{../../private}\n'
        self.assertEqual(tex_includes(text,'work/main.tex',owned),['work/foundations.tex','work/refs.bib'])
        owned['work/parts/second.tex'] = {}
        self.assertEqual(tex_includes('\\input{parts/second}', 'work/parts/first.tex', owned, 'work/main.tex'), ['work/parts/second.tex'])

    def test_source_lines_preserve_targets_and_escape_active_content(self):
        result=source_lines('line one\n<script>alert(1)</script>\n')
        self.assertIn('id="L2"',result)
        self.assertIn('&lt;script&gt;',result)
        self.assertNotIn('<script>',result)
        self.assertIn('aria-label="Line 2"',result)

    def test_source_navigation_bounds_match_real_lines_and_links_have_targets(self):
        for text in ('', 'one\n', 'one\n\nthree'):
            result=source_lines(text)
            page=Page(result)
            self.assertEqual(len(page.ids),len(set(page.ids)))
            self.assertTrue(all(link[1:] in page.ids for link in page.links if link.startswith('#')))
            lines=text.splitlines()
            self.assertEqual(len(page.inputs),int(bool(lines)))
            if lines:
                control=page.inputs[0]
                self.assertEqual((control['min'],control['max'],control['step']),('1',str(len(lines)),'1'))
                self.assertIn(control['id'],page.labels)
                self.assertIn('class="source-jump" hidden',result)
                self.assertNotIn('class="line-number" tabindex="-1"',result)

    def test_wide_guide_blocks_are_keyboard_reachable_without_javascript(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<div class="arithmatex">\\[x=1\\]</div><pre><code>sample</code></pre>'
                     '<span class="arithmatex">\\(x\\)</span>')
        result=''.join(rewrite.out)
        self.assertEqual(result.count('tabindex="0"'),2)
        self.assertIn('aria-label="Displayed equation. Scroll horizontally if needed."',result)
        self.assertIn('<span class="arithmatex">',result)

    def test_guide_blocks_preserve_existing_accessible_names(self):
        rewrite=Rewriter(lambda value,image:value)
        rewrite.feed('<pre tabindex="0" role="region" aria-label="Original program">x</pre>')
        result=''.join(rewrite.out)
        self.assertEqual(result.count('tabindex='),1)
        self.assertEqual(result.count('aria-label='),1)
        self.assertIn('role="region" aria-label="Original program"',result)

    def test_same_filename_in_different_directories_keeps_distinct_reading_urls(self):
        self.assertNotEqual(page_path('work','one/main.tex'),page_path('work','two/main.tex'))
        self.assertEqual(page_path('work','one/main.tex'),page_path('work','one/main.tex'))

    def test_pinned_pdf_runtime_rejects_corrupt_download_before_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'runtime'
            with self.assertRaisesRegex(ValueError,'integrity mismatch'):
                extract(b'not the released ZIP',output)
            self.assertFalse(output.exists())

    def test_line_references_and_pdf_page_bookmarks_keep_their_targets(self):
        reader=ReadingDocuments.__new__(ReadingDocuments)
        reader.site=SimpleNamespace(rel=lambda target,page:target)
        reader.records={
            'README.md':dict(format='markdown',url='read/work/guide.html',source_url='read/work/guide-source.html'),
            'paper.pdf':dict(format='pdf',url='read/work/paper.html',file_url='documents/files/abc/paper.pdf',work='work')}
        self.assertEqual(reader.resolve('README.md','index.html','L24-L26'),'read/work/guide-source.html#L24')
        self.assertEqual(reader.resolve('README.md','index.html','usage'),'read/work/guide.html#usage')
        result=reader.resolve('paper.pdf','index.html','page=8')
        self.assertIn('assets/pdfjs/web/viewer.html?file=',result)
        self.assertTrue(result.endswith('#page=8'))
        self.assertIn('&work=',result)


if __name__=='__main__':unittest.main()

