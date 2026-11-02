import unittest

from readable_chapters import Chapter,statement_navigation
from statement_navigation import check


class StatementNavigationTests(unittest.TestCase):
    def fixture(self):
        chapter=Chapter('\\section{Results}\n\\begin{theorem}[Finite $N=2$]\\label{thm:finite}\nClaim.\\end{theorem}\n\\begin{proof}Proof.\\end{proof}\n\\begin{conjecture}[Open boundary]Claim.\\end{conjecture}',{})
        theorem=next(n for n in chapter.nodes if n['kind']=='theorem')
        proof=next(n for n in chapter.nodes if n['kind']=='proof')
        report=dict(url='read/paper-i/results.html',nodes=chapter.nodes)
        rows={theorem['line']:dict(proof_line=proof['line'])}
        index=statement_navigation(chapter,rows)
        article=('<article id="chapter-text"><section id="'+theorem['id']+'"><h3>Theorem</h3><p>'
                 '<a href="#'+proof['id']+'">Read proof</a></p></section></article>')
        return chapter,report,index,article

    def test_index_metadata_follows_the_source_without_repeating_math(self):
        chapter,report,index,article=self.fixture()
        self.assertIn('data-statement-labels="thm:finite"',index)
        self.assertIn('data-statement-number="1.1"',index)
        self.assertIn('Finite N=2',index)
        self.assertNotIn('arithmatex',index)
        self.assertEqual(check(index+article,report),dict(statements=2,proof_links=1))
        self.assertEqual(chapter.math,[])

    def test_missing_reordered_or_invented_proof_routes_fail(self):
        _,report,index,article=self.fixture()
        for broken in (index.replace('data-statement-entry="L2"','data-statement-entry="wrong"'),
                       index.replace('data-statement-kind="theorem"','data-statement-kind="conjecture"'),
                       index.replace('data-statement-name="Theorem"','data-statement-name="Conjecture"'),
                       index.replace('data-statement-number="1.1"','data-statement-number="1.10"'),
                       index.replace('href="#L4"','href="#L999"'),
                       index.replace('data-statement-labels="thm:finite"','data-statement-labels="other"')):
            with self.assertRaises(AssertionError):check(broken+article,report)
        with self.assertRaises(AssertionError):check(article,report)


if __name__=='__main__':unittest.main()
