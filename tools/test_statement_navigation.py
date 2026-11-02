import unittest
from types import SimpleNamespace

from readable_chapters import Chapter,statement_navigation,statement_entries,render_statement_directory
from statement_navigation import check,check_directory


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

    def test_paper_directory_retains_duplicate_numbers_chapter_context_and_exact_proof_routes(self):
        chapter,_,index,_=self.fixture()
        theorem=next(n for n in chapter.nodes if n['kind']=='theorem')
        proof=next(n for n in chapter.nodes if n['kind']=='proof')
        rows={theorem['line']:dict(proof_line=proof['line'])}
        chapters=[('read/paper-i/first.html',index),('read/paper-i/second.html',index)]
        markup='<div class="reading-statement-directory">'
        for url,_ in chapters:
            markup+='<section data-statement-chapter="'+url+'"><ul>'+statement_entries(chapter,rows,url.rsplit('/',1)[-1])+'</ul></section>'
        markup+='</div>'
        page='read/paper-i/statements.html'
        self.assertEqual(check_directory(markup,chapters,page),dict(statements=4,proof_links=2))
        for broken in (markup.replace('second.html#L2','first.html#L2'),
                       markup.replace('second.html#L4','first.html#L4'),
                       markup.replace('Finite N=2','Changed title'),
                       markup.replace('data-statement-chapter="read/paper-i/second.html"','data-statement-chapter="read/paper-i/first.html"')):
            with self.assertRaises(AssertionError):check_directory(broken,chapters,page)

    def test_directory_publication_uses_the_reading_order_and_skips_empty_chapters(self):
        from unittest.mock import patch
        chapter,_,_,_=self.fixture()
        output={};search=[]
        site=SimpleNamespace(rel=lambda target,page:target.rsplit('/',1)[-1],page=lambda path,title,body:output.update({path:body}),search=search)
        book=dict(config=dict(index='read/paper-i/index.html',work='paper-i',label='Paper I',title='Paper I title'),
                  chapters=[(dict(url='read/paper-i/empty.html',title='Orientation'),b'',Chapter('Only prose.',{})),
                            (dict(url='read/paper-i/results.html',title='Results'),b'',chapter)])
        with patch('readable_chapters.chapter_claims',return_value=[]):
            render_statement_directory(SimpleNamespace(site=site),book)
        body=output['read/paper-i/statements.html']
        self.assertNotIn('empty.html',body)
        self.assertIn('data-statement-chapter="read/paper-i/results.html"',body)
        self.assertIn('href="results.html#L2"',body)
        self.assertNotIn('Read proof',body,'Proof locations are never inferred from adjacency')
        self.assertNotIn('arithmatex',body)
        self.assertEqual(search[0]['url'],'read/paper-i/statements.html')


if __name__=='__main__':unittest.main()
