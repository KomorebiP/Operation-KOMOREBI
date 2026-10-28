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
            config={'schema':1,'background':{'papers':'Matrices.'},
                    'glossary':[{'id':'projector','term':'Projector'}],
                    'learning_topics':[{'id':'packets','number':1,'title':'Packets',
                        'example':example,'terms':['projector'],'works':['paper-i'],
                        'scope':'Finite example.','code_guide':'https://example.org/guide'}]}
            (root/'manifests/reader-experience.json').write_text(json.dumps(config),encoding='utf-8')
            first=render_learning_pages(root,config,[component])
            self.assertTrue(first[example].startswith(calculation))
            for anchor in ('read','written-proofs','lean','code','evidence'):
                self.assertIn('../works/paper-i.md#'+anchor,first[example])
            (root/example).write_text(first[example],encoding='utf-8')
            self.assertEqual(first,render_learning_pages(root,config,[component]))
            back=introduction(root,component,{'scope':'Recorded scope.','next_step':'Pending.'},'docs/works/paper-i.md')
            self.assertIn('../examples/01_EXAMPLE.md',back)
            self.assertIn('../LEARNING_MAP.md#packets',back)


if __name__=='__main__':unittest.main()
