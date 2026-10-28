"""Regression checks for source paths and reader HTML transformations."""
import unittest
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

from build_reader_site import Rewriter, Site, document_url, math_fences, safe_path, selected_files
from check_reader_site import Page
from reader_documents import ReadingDocuments, page_path, source_lines, tex_includes
from fetch_pdf_runtime import extract


class ReaderSiteTests(unittest.TestCase):
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

    def test_source_lines_preserve_targets_and_escape_active_content(self):
        result=source_lines('line one\n<script>alert(1)</script>\n')
        self.assertIn('id="L2"',result)
        self.assertIn('&lt;script&gt;',result)
        self.assertNotIn('<script>',result)
        self.assertIn('aria-label="Line 2"',result)

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
