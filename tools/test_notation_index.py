"""Regression cases for notation extraction and source fidelity."""
import unittest
from notation_index import (passages, symbol_tokens, index_document, macro_definitions,
                            aliases, display_math, symbol_id, context_for)


class NotationTests(unittest.TestCase):
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


if __name__=='__main__':unittest.main()
