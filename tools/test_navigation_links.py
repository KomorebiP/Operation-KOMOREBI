"""Negative controls for the maintained-reader link checker."""
import unittest
from navigation_links import check_links


class NavigationLinkTests(unittest.TestCase):
    def test_encoded_names_nested_parentheses_and_exact_case(self):
        known = {'papers/A file (draft).tex', 'papers/one(two).md'}
        docs = {'docs/index.md': '[Text](../papers/A%20file%20%28draft%29.tex)\n[Other](../papers/one(two).md)'}
        self.assertEqual(check_links(docs,known)['relative_links'],2)
        for target in ['../papers/a%20file%20%28draft%29.tex', '../papers/missing.md', '../../outside.md']:
            with self.subTest(target=target), self.assertRaises(AssertionError):
                check_links({'docs/index.md':'[Bad]('+target+')'},known)

    def test_directory_must_contain_a_file_and_file_cannot_be_directory(self):
        known = {'code/demo.py'}
        self.assertEqual(check_links({'README.md':'[Code](code/)'},known)['directory_links'],1)
        for target in ['code/demo.py/', 'empty/']:
            with self.subTest(target=target), self.assertRaises(AssertionError):
                check_links({'README.md':'[Bad]('+target+')'},known)

    def test_duplicate_headings_have_distinct_targets_and_explicit_ids_are_unique(self):
        content = '# Read\n## Read\n## Read\n<a id="back"></a>\n[First](#read) [Second](#read-1) [Third](#read-2) [Return](#back)'
        self.assertEqual(check_links({'docs/work.md':content},set())['checked_fragments'],4)
        with self.assertRaisesRegex(AssertionError,'Missing navigation anchor'):
            check_links({'docs/work.md':content+'\n[Bad](#read-3)'},set())
        with self.assertRaisesRegex(AssertionError,'Duplicate explicit'):
            check_links({'docs/work.md':content+'\n<a id="back"></a>'},set())

    def test_examples_do_not_create_navigation_or_supply_a_missing_heading(self):
        example = '```md\n# Fake\n[Bad](missing.md)\n```\n`[Example](also-missing.md)`\n'
        self.assertEqual(check_links({'README.md':example},set())['relative_links'],0)
        with self.assertRaisesRegex(AssertionError,'Missing navigation anchor'):
            check_links({'README.md':example+'[Bad](#fake)'},set())

    def test_remote_links_and_unrendered_source_fragments_are_reported_not_certified(self):
        content = '[Remote](https://example.com/path#title) [Source](source.md#unverified)'
        result = check_links({'README.md':content},{'source.md'})
        self.assertEqual(result['external_links_not_checked'],1)
        self.assertEqual(result['source_fragments_not_checked'],1)
        self.assertEqual(result['checked_fragments'],0)

    def test_tex_evaluation_brackets_do_not_become_markdown_file_links(self):
        content = (r'\[\bigl[S^s a\bigr](0)\]'+'\n'
                   r'Inline \([P](0)\) stays mathematical.'+'\n'
                   '[Actual guide](guide.md)')
        result=check_links({'README.md':content},{'guide.md'})
        self.assertEqual(result['relative_links'],1)


if __name__ == '__main__':
    unittest.main()
