"""Regression cases for notation extraction and source fidelity."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from notation_index import (passages, symbol_tokens, index_document, macro_definitions,
                            aliases, display_math, symbol_id, context_for,table_preview,reader_index,context_text,
                            prepare_sources,extract_work,pack_work_data,unpack_work_data,legacy_symbol_anchors)


class NotationLegacyAnchorTests(unittest.TestCase):
    def entry(self, tex):
        return dict(id=symbol_id(tex),tex=tex,occurrences=[0])

    def test_unambiguous_aliases_preserve_canonical_data(self):
        for tex,previous in ((r'\mathbb R_n',r'\mathbbR_n'),
                             ('\\widehat\n T',r'\widehatT')):
            with self.subTest(tex=tex):
                entries=[self.entry(tex),self.entry('x')]
                original=deepcopy(entries)
                self.assertEqual(legacy_symbol_anchors(entries),
                                 {symbol_id(tex):[symbol_id(previous)]})
                self.assertEqual(entries,original)

    def test_authored_joined_command_keeps_its_canonical_anchor(self):
        entries=[self.entry(r'\mathbb R'),self.entry(r'\mathbbR')]
        self.assertEqual(legacy_symbol_anchors(entries),{})

    def test_multiple_whitespace_spellings_do_not_choose_an_arbitrary_target(self):
        entries=[self.entry(tex) for tex in (r'\mathbb R',r'\mathbb  R','\\mathbb\tR')]
        self.assertEqual(legacy_symbol_anchors(entries),{})

    def test_unchanged_braced_command_and_other_arguments_have_no_alias(self):
        for tex in (r'\mathbb{R}',r'\mathbb {R}',r'\widehat\beta',r'\widehat \beta',
                    r'\mathsf1',r'\mathsf 1',r'\mathbbR',r'\custom X',r'\sqrt x',
                    r'x_{\mathbb R}',r'\mathbf{R_{\mathbb R}}'):
            with self.subTest(tex=tex):
                self.assertEqual(legacy_symbol_anchors([self.entry(tex)]),{})

    def test_only_the_leading_separator_is_removed_from_legacy_spelling(self):
        tex=r'\widehat X_{\mathbb R}'
        self.assertEqual(legacy_symbol_anchors([self.entry(tex)]),
                         {symbol_id(tex):[symbol_id(r'\widehatX_{\mathbb R}')]})


class NotationDataEncodingTests(unittest.TestCase):
    def data(self, contexts):
        return dict(version=1,work='sample',title='Notation α',source_revision='revision',
                    sources=[dict(repository_path='sample/main.tex',sha256='source hash',
                                  macros={'R':r'\mathbb{R}'})],pdfs=[],
                    passages=[dict(context=context,source=0,line=i+1,start=i,end=i+1,
                                   expression=r'\alpha+x',kind='use',definition_title=None,
                                   extension={'values':[None,True,'kept']})
                              for i,context in enumerate(contexts)],
                    entries=[dict(tex=r'\alpha',occurrences=list(range(len(contexts))))],
                    extension={'contexts':['This nested field is not reserved.']})

    def encoded(self, data):
        return json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')

    def test_packed_roundtrip_keeps_every_field_and_does_not_mutate_inputs(self):
        first=('A repeated α / 文 context with '+r'\frac{x}{y}'+', "quotes", and\nnewlines.\n')*4
        second='Distinct e\u0301 and é; '+r'\begin{equation}x\end{equation}'
        data=self.data([first,second,first,first,second,first,''])
        original=deepcopy(data)
        packed=pack_work_data(data)
        self.assertEqual(packed['version'],2)
        self.assertEqual(packed['contexts'],[first,second,''])
        self.assertEqual([p['context'] for p in packed['passages']],[0,1,0,0,1,0,2])
        self.assertLess(len(self.encoded(packed)),len(self.encoded(data)))
        self.assertEqual(data,original)
        wire=json.loads(self.encoded(packed));snapshot=deepcopy(wire)
        restored=unpack_work_data(wire)
        self.assertEqual(restored,original)
        self.assertEqual(wire,snapshot)
        restored['passages'][0]['context']='changed after decoding'
        self.assertEqual(wire,snapshot)
        self.assertEqual(data,original)

    def test_legacy_empty_and_short_singleton_data_remain_unchanged(self):
        for contexts in ([],[''],['x'],['x','y']):
            with self.subTest(contexts=contexts):
                data=self.data(contexts);original=deepcopy(data)
                self.assertIs(unpack_work_data(data),data)
                self.assertIs(pack_work_data(data),data)
                self.assertEqual(data,original)

    def test_size_selection_uses_utf8_bytes_instead_of_character_counts(self):
        data=self.data(['α'*8]*2)
        packed=pack_work_data(data)
        self.assertEqual(packed['version'],2)
        self.assertLess(len(self.encoded(packed)),len(self.encoded(data)))
        self.assertGreaterEqual(len(self.encoded(packed).decode()),len(self.encoded(data).decode()))
        self.assertEqual(unpack_work_data(packed),data)

    def test_invalid_logical_inputs_and_reserved_field_are_rejected(self):
        invalid=[None,[],True,'data',{},self.data([])|{'contexts':[]}]
        for version in (None,True,False,1.0,'1',0,-1,3):
            invalid.append(self.data([])|{'version':version})
        for passages in (None,{},'passages',(),[None],[[]],['passage']):
            invalid.append(self.data([])|{'passages':passages})
        missing=self.data([]);del missing['passages'];invalid.append(missing)
        for context in (None,True,0,1.0,[],{}):
            invalid.append(self.data([context]))
        missing=self.data(['x']);del missing['passages'][0]['context'];invalid.append(missing)
        for data in invalid:
            for operation in (pack_work_data,unpack_work_data):
                with self.subTest(data=data,operation=operation.__name__):
                    with self.assertRaises(ValueError):operation(data)

    def test_malformed_packed_tables_references_and_versions_are_rejected(self):
        packed=pack_work_data(self.data(['Repeated context '*20]*3))
        invalid=[]
        for contexts in (None,'context',{},(),[None],[True],[1],[[]],[{}]):
            invalid.append(packed|{'contexts':contexts})
        missing=deepcopy(packed);del missing['contexts'];invalid.append(missing)
        for index in (None,True,False,0.0,'0',-1,len(packed['contexts']),[],{}):
            bad=deepcopy(packed);bad['passages'][0]['context']=index;invalid.append(bad)
        missing=deepcopy(packed);del missing['passages'][0]['context'];invalid.append(missing)
        for version in (None,True,False,2.0,'2',0,3):
            invalid.append(packed|{'version':version})
        for data in invalid:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):unpack_work_data(data)
        with self.assertRaisesRegex(ValueError,'requires logical'):
            pack_work_data(packed)


class NotationTests(unittest.TestCase):
    def notation_site(self, config, sources):
        """Use the document reader's receipt-only registration in a small site."""
        from reader_documents import ReadingDocuments
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        (root/'manifests').mkdir()
        (root/'manifests/notation-sources.json').write_text(json.dumps(config),encoding='utf-8')
        works=sorted({path.split('/')[0] for path in sources})
        site=SimpleNamespace(root=root,revision='revision',
                             registry=dict(components=[dict(id=work,destination=work) for work in works]),
                             components={work:dict(title=work) for work in works})
        reader=ReadingDocuments.__new__(ReadingDocuments)
        reader.site=site;reader.records={};reader.owned={};reader.manuscript_roots={}
        raw={path:text.encode('utf-8') for path,text in sources.items()}
        for path,data in raw.items():
            work,relative=path.split('/',1)
            reader.owned[path]=dict(work=work,path=relative,repository_path=path,mode='100644',
                                   size=len(data),sha256=hashlib.sha256(data).hexdigest(),
                                   git_blob_sha1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
            if not path.endswith('.sty'):reader.add(path)
        site.reader=reader
        site.read_source=lambda record:raw[record['repository_path']]
        prepare_sources(reader)
        return site

    def test_style_macros_follow_one_manuscript_without_indexing_style_passages(self):
        site=self.notation_site(
            dict(additional_entrypoints={'cos':['book/main.tex'],'other':['main.tex']},
                 additional_macro_sources={'cos':{'book/main.tex':['book/monograph.sty']}}),
            {'cos/book/main.tex':r'\usepackage{monograph}\begin{document}\input{chapters/first}\end{document}',
             'cos/book/chapters/first.tex':r'$\R+\Pp+\phit+\eps$',
             'cos/book/monograph.sty':r'\newcommand{\R}{\mathbb R}\newcommand{\Pp}{\mathbb P}'
                                      r'\newcommand{\phit}{\phi_{\theta}}\newcommand{\eps}{\varepsilon}'
                                      r'\newcommand{\layout}{$z_{\mathrm{style}}$}',
             'cos/history/main.tex':r'\begin{document}$\Pp$\end{document}',
             'other/main.tex':r'\begin{document}$\Pp$\end{document}'})
        # ReadingDocuments propagates this root when resolving the literal input.
        site.reader.notation_roots['cos/book/chapters/first.tex']='cos/book/main.tex'
        site.reader.manuscript_roots['cos']='cos/book/main.tex'
        data=extract_work(site,'cos')
        source={row['repository_path']:row for row in data['sources']}
        self.assertIn('cos/book/monograph.sty',site.reader.records)
        self.assertNotIn('cos/book/monograph.sty',source)
        self.assertEqual([row['expression'] for row in data['passages']],[r'\R+\Pp+\phit+\eps',r'\Pp'])
        macros=source['cos/book/chapters/first.tex']['macros']
        self.assertEqual(display_math(r'\Pp',macros),r'{\mathbb P}')
        self.assertEqual(display_math(r'\R',macros),r'{\mathbb R}')
        self.assertIn('varepsilon',aliases(r'\eps',macros))
        entries={row['tex']:row for row in data['entries']}
        self.assertEqual(entries[r'\phit']['display'],r'{\phi_{\theta}}')
        self.assertEqual(source['cos/history/main.tex']['macros'],{})
        self.assertIsNone(entries[r'\Pp']['display'],'An unexpanded historical spelling keeps its separate meaning')
        other=extract_work(site,'other')
        self.assertEqual(other['sources'][0]['macros'],{})
        self.assertIsNone(other['entries'][0]['display'])

    def test_macro_sources_must_belong_to_a_declared_receipt_bound_root(self):
        sources={'cos/main.tex':r'\begin{document}$\R$\end{document}'}
        with self.assertRaisesRegex(ValueError,'Missing notation macro source'):
            self.notation_site(dict(additional_entrypoints={'cos':['main.tex']},
                                    additional_macro_sources={'cos':{'main.tex':['missing.sty']}}),sources)
        with self.assertRaisesRegex(ValueError,'declared manuscript root'):
            self.notation_site(dict(additional_entrypoints={'cos':['main.tex']},
                                    additional_macro_sources={'cos':{'history.tex':['missing.sty']}}),sources)

    def test_definition_titles_follow_the_explicit_source_scope(self):
        text='$a$\n\\begin{definition}[Generator number]\n$x$\n'+('Long explanatory text. '*250)+'\n$y$\n\\end{definition}\n$z$'
        records=index_document(text,'.tex')
        self.assertEqual([row.get('definition_title') for row in records],[None,'Generator number','Generator number',None])
        self.assertEqual(records[2]['kind'],'definition-passage','A long definition retains its source scope')
        for row in records:self.assertEqual(text[row['start']:row['end']],row['expression'])

    def test_nested_and_unnamed_definitions_do_not_borrow_a_title(self):
        text=r'\begin{definition}[Outer]$a$\begin{definition*}$b$\end{definition*}$c$\end{definition}$d$'
        records=index_document(text,'.tex')
        self.assertEqual([row.get('definition_title') for row in records],['Outer',None,'Outer',None])

    def test_commented_or_example_definitions_do_not_name_an_ordinary_use(self):
        text='% \\begin{definition}[Comment]\n$x$\n\\begin{lstlisting}\n\\begin{definition}[Example]\n\\end{lstlisting}\n$y$'
        records=index_document(text,'.tex')
        self.assertEqual(len(records),2)
        self.assertTrue(all(row.get('definition_title') is None and row['kind']=='use' for row in records))

    def test_balanced_definition_titles_retain_their_original_spelling(self):
        title=r'\emph{A [closed] family} over $\mathbb{R}$'
        records=index_document(r'\begin{definition}['+title+r'] $V$.\end{definition}', '.tex')
        self.assertEqual(records[-1]['definition_title'],title)
        self.assertEqual(context_text(title),'A [closed] family over ℝ')

    def test_excerpts_hide_layout_and_nested_bookkeeping_arguments(self):
        source=r'\Needspace{15\baselineskip}\noindent A \textbf{finite} module $M$. \RecordID{PSC-{nested}-ID}\label{a{b}}\index{module!finite}'
        self.assertEqual(context_text(source),'A finite module M.')
        self.assertEqual(context_text(r'\vspace*{2pt}\hspace{1em}Kept.\pagebreak[4] Next.'),'Kept. Next.')

    def test_excerpts_keep_section_names_and_definition_titles(self):
        source=r'\subsection[Short]{Quotient \emph{witnesses}}\begin{definition}[Witness for seed rank] A map $\Phi:M\twoheadrightarrow N$.\end{definition}'
        self.assertEqual(context_text(source),'Quotient witnesses. [Witness for seed rank] A map Φ:M↠ N.')

    def test_excerpt_math_keeps_literal_braces_and_escaped_text_characters(self):
        source=r'Let $S=\{x,y\}$, $U\hookrightarrow V$ and $A\setminus B$. Research \& examples cost \$5 at 50\%. $x$ & Meaning.'
        self.assertEqual(context_text(source),'Let S={x,y}, U↪ V and A∖ B. Research & examples cost $5 at 50%. x · Meaning.')

    def test_unknown_commands_and_mathematical_content_are_retained(self):
        self.assertEqual(context_text(r'A \localmeaning{essential} object $x_{i}$, with \ref{result}.'),
                         'A localmeaningessential object x_i, with [source reference].')
        self.assertEqual(context_text(r'$\rank(M)\le r$',{'rank':r'\operatorname{rank}'}),'rank(M)≤ r')
        self.assertEqual(context_text(r'Uses the bound. \Depends{PSC-I-D-SEED-RANK}'),'Uses the bound. [source reference]')

    def test_a_display_box_is_not_indexed_as_a_mathematical_symbol(self):
        tokens=symbol_tokens(r'\boxed{x_i=y}')
        self.assertNotIn(r'\boxed',tokens)
        self.assertTrue({'x','x_i','i','y','='}<=set(tokens))

    def test_reader_index_remaps_contexts_without_crossing_work_boundaries(self):
        search=dict(source_revision='revision',works=[dict(id='a'),dict(id='b')],
                    contexts=[dict(work='b',excerpt='Other'),dict(work='a',excerpt='First'),dict(work='a',excerpt='Second')],
                    entries=[dict(work='a',tex='x',context=2),dict(work='b',tex='x',context=0),dict(work='a',tex='y',context=1)])
        compact=reader_index(search,'a')
        self.assertEqual(compact['works'],[dict(id='a')])
        self.assertEqual(compact['source_revision'],'revision')
        self.assertEqual([e['context'] for e in compact['entries']],[1,0])
        self.assertEqual([c['excerpt'] for c in compact['contexts']],['First','Second'])
        self.assertEqual(search['entries'][0]['context'],2)

    def test_tex_masks_comments_preamble_and_programs(self):
        text=r'''\newcommand{\fake}{$WRONG$}
\begin{document}
% $WRONG$
\verb|$WRONG$|
\begin{lstlisting}$WRONG$\end{lstlisting}
$x+\alpha$ % $WRONG$
\[y\]
\begin{align}z &= x\end{align}
'''
        self.assertEqual([p[2] for p in passages(text,'.tex')], [r'x+\alpha','y','z &= x'])

    def test_markdown_code_and_math_fences(self):
        text='`$wrong$`\n```python\n$wrong$\n```\n$$x$$\n```math\ny_i = z\n```\n<!-- $wrong$ -->\n$w$'
        self.assertEqual([p[2].strip() for p in passages(text,'.md')], ['x','y_i = z','w'])

    def test_exact_source_and_line_survive_comments(self):
        text='before\n\\[x % ignored\n+ y\\]\n'
        item=index_document(text,'.tex')[0]
        self.assertEqual(item['line'],2)
        self.assertEqual(text[item['start']:item['end']],item['expression'])
        self.assertIn('% ignored',item['expression'])
        self.assertNotIn('g',item['symbols'])

    def test_decorated_symbols_and_case_are_distinct(self):
        tokens=symbol_tokens(r'P_{ij}+p_i+\mathcal{R}_n+\alpha+\text{not notation}')
        self.assertTrue({'P','P_{ij}','p','p_i',r'\mathcal{R}',r'\mathcal{R}_n',r'\alpha','i','j'}<=set(tokens))
        self.assertNotIn('o',tokens)
        self.assertNotEqual(symbol_id('P'),symbol_id('p'))

    def test_unbraced_letter_arguments_keep_their_control_word_separator(self):
        for tex in (r'\mathbb R', r'\mathcal D', r'\widehat T', r'\boldsymbol S',
                    '\\mathsf\tT', '\\hat\n x'):
            with self.subTest(tex=tex):
                tokens=symbol_tokens(tex+'_{n}')
                self.assertIn(tex,tokens)
                self.assertIn(tex+'_{n}',tokens)
                joined=''.join(tex.split())
                self.assertNotIn(joined,tokens)
                self.assertEqual(display_math(tex,{}),tex)
        text=r'Let $\mathbb R^{n\times m}$ be the factor space.'
        passage=index_document(text,'.tex')[0]
        self.assertEqual(passage['expression'],r'\mathbb R^{n\times m}')
        self.assertIn(r'\mathbb R^{n\times m}',passage['symbols'])

    def test_braced_and_command_arguments_keep_their_existing_spellings(self):
        for tex,expected in ((r'\mathcal{D}_n',r'\mathcal{D}_n'),
                             (r'\mathcal {D}_n',r'\mathcal{D}_n'),
                             (r'\widehat\beta_i',r'\widehat\beta_i'),
                             (r'\widehat \beta_i',r'\widehat\beta_i'),
                             (r'\mathsf 1',r'\mathsf1')):
            with self.subTest(tex=tex):
                self.assertIn(expected,symbol_tokens(tex))
        self.assertEqual(symbol_tokens(r'\mathbbR'),[r'\mathbbR'],
                         'Do not reinterpret an authored custom command')

    def test_only_literal_zero_argument_macros_are_displayed(self):
        macros=macro_definitions(r'\newcommand{\RR}{\mathbb{R}}\newcommand{\foo}[1]{#1}\DeclareMathOperator{\rank}{rank}')
        self.assertIn('ℝ',aliases(r'\RR',macros))
        self.assertIn(r'\mathbb{R}',display_math(r'\RR',macros))
        self.assertIsNone(display_math(r'\foo{x}',macros))
        self.assertIsNone(display_math(r'\href{bad}{x}',macros))
        self.assertIsNone(display_math(r'\loop',{'loop':r'\loop'}))

    def test_reviewed_builtin_symbols_keep_their_literal_display_spelling(self):
        for command in ('succeq','preceq','succ','sqcup','arctan','downarrow',
                        'uparrow','lceil','rceil','Longleftrightarrow','Longrightarrow'):
            tex='\\'+command
            with self.subTest(tex=tex):
                self.assertEqual(display_math(tex,{}),tex)

    def test_braced_roman_labels_display_without_rewriting_source(self):
        for tex in (r'\mathcal D_{\rm spectrum}',r'E_{\rm support}',
                    r'M_{ \rm full }',r'\varepsilon_{{\rm req}}',
                    r'x_{\rm lower}^{\rm upper}'):
            with self.subTest(tex=tex):
                self.assertEqual(display_math(tex,{}),tex)
        self.assertEqual(display_math(r'\named',{'named':r'x_{\rm label}'}),
                         r'{x_{\rm label}}')

    def test_incomplete_or_unscoped_declarations_remain_exact_tex_fallbacks(self):
        for tex in (r'\rm',r'{\rm}',r'{{\rm }}',r'\rm x',r'x_{\rm}',
                    r'x_{\rm \alpha}',r'x_{{\rm support}',r'\{\rm x}',
                    r'x_{\rm support}}',r'\overset'):
            with self.subTest(tex=tex):
                self.assertIsNone(display_math(tex,{}))
        self.assertIsNone(display_math(r'\roman',{'roman':r'\rm'}))

    def test_reviewed_commands_do_not_relax_display_safety_boundaries(self):
        for tex in (r'x_{\rm label}\href{https://example.test}{x}',
                    r'x_{\rm label}\htmlClass{external}{x}',
                    r'x_{\rm label}\require{html}',
                    r'x_{\rm label}\input{file}',r'\unknown{x}',
                    r'x_{\rm label}\color{red}',r'\rmLabel',
                    r'x_{\rm '+('a'*501)+'}'):
            with self.subTest(tex=tex):
                self.assertIsNone(display_math(tex,{}))

    def test_no_definition_inferred_from_ordinary_use(self):
        text='Let $x=y$.\n\n\\begin{definition}A space $V$.\\end{definition}'
        records=index_document(text,'.tex')
        self.assertEqual(records[0]['kind'],'use')
        self.assertEqual(records[0]['context'][:3],'Let')
        self.assertEqual(records[1]['kind'],'definition-passage')

    def test_notation_table_recognized_without_assigning_meaning(self):
        text=r'\begin{tabular}{ll}Symbol & Meaning\\$Q_n$ & Local role\\\end{tabular}'
        record=index_document(text,'.tex')[0]
        self.assertEqual(record['kind'],'notation-table')
        self.assertIn('Local role',record['context'])

    def test_conflicting_and_commented_macro_definitions_are_not_guessed(self):
        macros=macro_definitions('% \\newcommand{\\wrong}{X}\n'+r'\newcommand{\A}{X}\renewcommand{\A}{Y}')
        self.assertNotIn('wrong',macros)
        self.assertNotIn('A',macros)

    def test_escaped_dollar_is_not_math_but_even_backslashes_are(self):
        text=r'Cost \$5. Row\\$x$ and $y\$z$.'
        found=passages(text,'.tex')
        self.assertEqual([p[2] for p in found],['x',r'y\ z'])

    def test_table_preview_retains_the_whole_subject_not_its_index_letters(self):
        row=r'$\Pcal=(P_\alpha)$ & Packet system & Pairwise annihilating idempotents.'
        result=table_preview(row,{'Pcal':r'\mathcal{P}'})
        self.assertEqual(result['tex'],r'\Pcal=(P_\alpha)')
        self.assertEqual(result['label'],'Packet system')
        self.assertEqual(result['meaning'],'Pairwise annihilating idempotents.')

    def test_two_column_table_does_not_invent_a_name(self):
        result=table_preview(r'$x_i$ & The coordinate indexed by $i$.',{})
        self.assertEqual(result['label'],'')
        self.assertEqual(result['tex'],'x_i')
        self.assertIsNone(table_preview('Ordinary prose without a table.',{}))


class NotationReadingRouteTests(unittest.TestCase):
    def site(self):
        site=NotationTests.notation_site(self,
            dict(scope='Selected test sources.',additional_entrypoints={'cos':['main.tex']}),
            {'cos/main.tex':'Opening \\(x\\).\n\nParent \\(y\\).\n',
             'cos/included.tex':'Imported \\(z\\).\n\nOutside the rendered range \\(w\\).\n',
             'cos/history.tex':'Historical \\(h\\).\n'})
        chapter=SimpleNamespace(nodes=[
            dict(id='L1',line=1,end_line=1,
                 source_spans=[dict(source='cos/main.tex',line=1,end_line=1)]),
            dict(id='included-L1',line=1,end_line=1,
                 source_spans=[dict(source='cos/included.tex',line=1,end_line=1)]),
            dict(id='L3',line=3,end_line=3,
                 source_spans=[dict(source='cos/main.tex',line=3,end_line=3)])])
        site.reader.readable_books={'cos':dict(
            chapters=[(dict(source='cos/main.tex',url='read/cos/chapter.html'),'unused',chapter)],
            included_sources=[dict(source='cos/included.tex',input_source='cos/main.tex')])}
        site.reader.records['cos/main.tex']['source_url']='read/cos/source-main.html'
        site.reader.records['cos/included.tex']['source_url']='read/cos/source-included.html'
        return site

    def test_every_occurrence_uses_its_actual_source_and_rendered_range(self):
        site=self.site();data=extract_work(site,'cos')
        passages={p['expression']:p for p in data['passages']}
        self.assertEqual(passages['x']['reading_url'],'read/cos/chapter.html#L1')
        self.assertEqual(passages['y']['reading_url'],'read/cos/chapter.html#L3')
        self.assertEqual(passages['z']['reading_url'],'read/cos/chapter.html#included-L1')
        self.assertNotIn('reading_url',passages['w'],'Unrendered lines must keep their source-only route')
        self.assertNotIn('reading_url',passages['h'],'Historical sources must not inherit a chapter route')
        self.assertEqual(unpack_work_data(pack_work_data(data)),data)

    def test_reading_routes_only_add_navigation_to_retained_data(self):
        site=self.site();with_routes=extract_work(site,'cos')
        site.reader.readable_books={}
        source_only=extract_work(site,'cos')
        for passage in with_routes['passages']:passage.pop('reading_url',None)
        self.assertEqual(with_routes,source_only)

    def test_entry_preview_and_search_share_the_reading_route_and_keep_source(self):
        import posixpath
        from notation_index import build
        site=self.site();site.output=site.root/'output';site.search=[]
        def write(path,text):
            target=site.output/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text,encoding='utf-8')
        site.write=write;site.page=lambda path,title,body:write(path,body)
        site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
        site.reader.work_routes=lambda work,page:''
        assets=site.root/'website/assets';assets.mkdir(parents=True)
        for name in ('notation.js','notation-search.js'):
            (assets/name).write_bytes((Path(__file__).resolve().parents[1]/'website/assets'/name).read_bytes())
        build(site)
        html=(site.output/'notation/cos.html').read_text()
        def entry(tex):
            return html.split('id="'+symbol_id(tex)+'"',1)[1].split('<details class="notation-entry"',1)[0]
        self.assertIn('href="../read/cos/chapter.html#included-L1"',entry('z'))
        self.assertIn('href="../read/cos/source-included.html#L1"',entry('z'))
        self.assertIn('>Read passage</a>',entry('z'))
        self.assertNotIn('>Read passage</a>',entry('w'))
        search=json.loads((site.output/'notation/search.json').read_text())
        contexts={row['tex']:search['contexts'][row['context']] for row in search['entries']}
        self.assertEqual(contexts['z']['reading_url'],'read/cos/chapter.html#included-L1')
        self.assertEqual(contexts['z']['source_url'],'read/cos/source-included.html#L1')
        self.assertEqual(contexts['w']['reading_url'],contexts['w']['source_url'])


if __name__=='__main__':unittest.main()
