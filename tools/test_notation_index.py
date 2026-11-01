"""Regression cases for notation extraction and source fidelity."""
import unittest
from notation_index import (passages, symbol_tokens, index_document, macro_definitions,
                            aliases, display_math, symbol_id, context_for,table_preview,reader_index)


class NotationTests(unittest.TestCase):
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
