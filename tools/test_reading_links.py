"""Citation returns and figure access must keep source passages and assets exact."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from reading_links import ReadingMarkup,add_reference_routes,citation_routes,figure_controls,return_links,verify


class ReadingLinksTests(unittest.TestCase):
    def config(self):
        return dict(work='paper-i',bib_page='read/paper-i/references.html',chapters=[
            dict(url='read/paper-i/one.html',title='One & two'),
            dict(url='read/paper-i/two.html',title='Second chapter')])

    def test_citations_use_nearest_passage_and_keep_distinct_occurrences(self):
        config=self.config()
        files={config['chapters'][0]['url']:('<article id="chapter-text"><section id="L4"><p>First '
            '<em><a href="references.html#ref-A">A</a></em><br><a href="references.html#ref-A">A again</a>'
            '<a href="references.html#ref-B">B</a></p></section><h2 id="L8">Heading</h2>'
            '<section id="L9"><a href="references.html#ref-A">A later</a></section></article>'),
            config['chapters'][1]['url']:'<article id="chapter-text"><a href="references.html#ref-A">A</a></article>'}
        routes=citation_routes(files.__getitem__,config)
        self.assertEqual([use['url'] for use in routes['ref-A']],['read/paper-i/one.html#L4','read/paper-i/one.html#L9','read/paper-i/two.html#chapter-text'])
        self.assertEqual([use['url'] for use in routes['ref-B']],['read/paper-i/one.html#L4'])
        links=return_links(routes['ref-A'],config['bib_page'])
        self.assertIn('One &amp; two · passage 1',links)
        self.assertIn('One &amp; two · passage 2',links)
        self.assertIn('href="two.html#chapter-text"',links)

    def test_only_rendered_citations_in_this_paper_are_used(self):
        config=self.config();config['chapters']=config['chapters'][:1]
        body=('<a href="references.html#ref-menu">Outside article</a><article id="chapter-text">'
              '<a href="https://example.test/references.html#ref-A">External</a>'
              '<a href="../paper-ii/references.html#ref-A">Other paper</a>'
              '<a href="references.html?q=other#ref-A">Other view</a>'
              '<a href="references.html#ref-A%26B">Encoded key</a></article>')
        self.assertEqual(set(citation_routes(lambda _:body,config)),{'ref-A&B'})

    def test_native_returns_belong_to_the_exact_reference(self):
        config=self.config();config['chapters']=config['chapters'][:1]
        chapter='<article id="chapter-text"><section id="L4"><a href="references.html#ref-A">A</a><a href="references.html#ref-B">B</a></section></article>'
        bibliography='<article id="chapter-text"><section id="ref-A"><h2>A</h2><p>Original \\(x\\).</p></section><section id="ref-B"><h2>B</h2><p>Original B.</p></section></article>'
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(path,text):
                file=root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text,encoding='utf-8')
            write(config['chapters'][0]['url'],chapter);write(config['bib_page'],bibliography)
            add_reference_routes(SimpleNamespace(site=SimpleNamespace(output=root,write=write)),dict(config=config))
            result=(root/config['bib_page']).read_text(encoding='utf-8')
            self.assertEqual(result.replace(return_links([dict(url=config['chapters'][0]['url']+'#L4',title='One & two')],config['bib_page']),''),bibliography)
            write('documents/reading-navigation.json',json.dumps({'paper-i':dict(entries=config['chapters'])}))
            pages={config['chapters'][0]['url']:SimpleNamespace(ids=['L4'])}
            self.assertEqual(verify(root,pages),dict(papers=1,references=2,citing_passages=2,figure_controls=0))
            write(config['bib_page'],result.replace('one.html#L4','one.html#L999',1))
            with self.assertRaises(AssertionError):verify(root,pages)

    def test_unknown_and_duplicate_references_fail(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            ReadingMarkup('<section id="ref-A"></section><section id="ref-A"></section>')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);config=self.config();config['chapters']=config['chapters'][:1]
            path=root/config['chapters'][0]['url'];path.parent.mkdir(parents=True)
            path.write_text('<article id="chapter-text"><a href="references.html#ref-missing">Missing</a></article>')
            (root/config['bib_page']).write_text('<section id="ref-A">A</section>')
            reader=SimpleNamespace(site=SimpleNamespace(output=root,write=lambda *args:None))
            with self.assertRaisesRegex(ValueError,'no bibliography entry'):add_reference_routes(reader,dict(config=config))

    def test_figure_actions_preserve_images_captions_math_and_relative_targets(self):
        figure='<figure id="L5"><img src="../../assets/a.png?x=1&amp;y=2" alt="A &amp; B" width="800" height="600"><figcaption>Original \\(x\\).</figcaption></figure>'
        result=figure_controls(figure)
        self.assertIn(figure.removesuffix('</figure>'),result)
        self.assertIn('href="../../assets/a.png?x=1&amp;y=2" target="_blank" rel="noopener"',result)
        self.assertIn('aria-label="View full-size figure (new tab): A &amp; B"',result)
        self.assertEqual(result.count('Original \\(x\\).'),1)
        paired=figure_controls('<figure><img src="a.png"><img src="b.png"></figure>')
        self.assertIn('View full-size image 1 (new tab)',paired)
        self.assertIn('View full-size image 2 (new tab)',paired)
        external='<figure><img src="https://example.test/a.png"></figure>'
        self.assertEqual(figure_controls(external),external)


if __name__=='__main__':unittest.main()
