"""Regression cases for notation extraction and source fidelity."""
import unittest
from notation_index import (passages, symbol_tokens, index_document, macro_definitions,
                            aliases, display_math, symbol_id, context_for,table_preview,reader_index,context_text)


class NotationTests(unittest.TestCase):
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

    def test_only_literal_zero_argument_macros_are_displayed(self):
        macros=macro_definitions(r'\newcommand{\RR}{\mathbb{R}}\newcommand{\foo}[1]{#1}\DeclareMathOperator{\rank}{rank}')
        self.assertIn('ℝ',aliases(r'\RR',macros))
        self.assertIn(r'\mathbb{R}',display_math(r'\RR',macros))
        self.assertIsNone(display_math(r'\foo{x}',macros))
        self.assertIsNone(display_math(r'\href{bad}{x}',macros))
        self.assertIsNone(display_math(r'\loop',{'loop':r'\loop'}))

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


if __name__=='__main__':unittest.main()
