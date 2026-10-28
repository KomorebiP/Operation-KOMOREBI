"""Keep learning routes reversible and preserve the authored calculation."""
import json
from pathlib import Path
import tempfile
import unittest

from reader_experience import introduction, render_learning_pages


class LearningNavigationTests(unittest.TestCase):
    def test_routes_return_to_the_example_and_regenerate_without_duplication(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'manifests').mkdir()
            (root/'docs/examples').mkdir(parents=True)
            example='docs/examples/01_EXAMPLE.md'
            calculation='# Example\n\nThe authored calculation remains here.\n'
            (root/example).write_text(calculation,encoding='utf-8')
            component={'id':'paper-i','title':'Paper I','group':'papers'}
            book={'id':'book','title':'A monograph','group':'monographs'}
            pending={'id':'pending','title':'A research work','group':'research'}
            components=[component,book,pending]
            config={'schema':1,'background':{'papers':'Matrices.'},
                    'glossary':[{'id':'projector','term':'Projector'}],
                    'learning_topics':[{'id':'packets','number':1,'title':'Packets',
                        'example':example,'terms':['projector'],'works':['paper-i','book'],
                        'scope':'Finite example.','code_guide':'https://example.org/guide',
                        'code_guide_label':'Edition instructions','code_guide_note':'Separate tutorial check.',
                        'source_passages':[{'label':'Definition in the paper','path':'papers/paper-i/definition.tex#L4'}]}]}
            (root/'manifests/reader-experience.json').write_text(json.dumps(config),encoding='utf-8')
            first=render_learning_pages(root,config,components)
            self.assertTrue(first[example].startswith(calculation))
            for anchor in ('read','written-proofs','lean','code','evidence'):
                self.assertIn('../works/paper-i.md#'+anchor,first[example])
            self.assertIn('../../papers/paper-i/definition.tex#L4',first[example])
            self.assertIn('## Start from a core paper',first['docs/LEARNING_MAP.md'])
            self.assertIn('works/paper-i.md#worked-examples-for-this-work',first['docs/LEARNING_MAP.md'])
            self.assertIn('## Start from a monograph or another work',first['docs/LEARNING_MAP.md'])
            self.assertIn('works/book.md#worked-examples-for-this-work',first['docs/LEARNING_MAP.md'])
            self.assertIn('2 of 3 work pages',first['docs/EXAMPLE_COVERAGE.md'])
            self.assertIn('works/pending.md#read',first['docs/EXAMPLE_COVERAGE.md'])
            self.assertNotIn('works/pending.md#worked-examples',first['docs/EXAMPLE_COVERAGE.md'])
            self.assertIn('[Edition instructions](https://example.org/guide). Separate tutorial check.',first[example])
            config['learning_topics'][0]['code_guide']='papers/paper-i/README.md'
            relative=render_learning_pages(root,config,components)
            self.assertIn('[Edition instructions](../../papers/paper-i/README.md)',relative[example])
            config['learning_topics'][0]['code_guide']='https://example.org/guide'
            (root/example).write_text(first[example],encoding='utf-8')
            self.assertEqual(first,render_learning_pages(root,config,components))
            back=introduction(root,component,{'scope':'Recorded scope.','next_step':'Pending.'},'docs/works/paper-i.md')
            self.assertIn('../examples/01_EXAMPLE.md',back)
            self.assertIn('../LEARNING_MAP.md#packets',back)


if __name__=='__main__':unittest.main()
