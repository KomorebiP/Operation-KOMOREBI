import unittest
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from readable_chapters import Chapter, prose_list
from reader_copyediting import MANIFEST, MARKDOWN_MANIFEST, apply_markdown, prepare, transform, validate


class CopyeditingTests(unittest.TestCase):
    def row(self, **values):
        return dict(id='comma-1', page='read/paper-i/chapter.html', anchor='L5',
                    before='one, two and three', after='one, two, and three', count=1, **values)

    def test_only_bound_prose_changes_and_round_trip_is_exact(self):
        phrase='one, two and three'
        body=('<p>'+phrase+'</p><nav><a href="#L5">'+phrase+'</a></nav><article id="chapter-text"><section id="L5">'
              '<p title="'+phrase+'">'+phrase+'</p><span class="arithmatex">\\('+phrase+'\\)</span>'
              '<pre><code>'+phrase+'</code></pre><p class="passage-links">'+phrase+'</p></section>'
              '<section id="L6"><p>'+phrase+'</p></section></article>')
        edited=transform(body,[self.row()])
        self.assertEqual(edited.count('one, two, and three'),2)
        self.assertEqual(transform(edited,[self.row()],reverse=True),body)

    def test_stale_passages_and_duplicate_occurrences_stop_the_build(self):
        for text in ['changed text','one, two and three; one, two and three']:
            with self.assertRaises(ValueError):
                transform('<article id="chapter-text"><p id="L5">'+text+'</p></article>',[self.row()])

    def test_words_math_and_existing_commas_cannot_be_rewritten(self):
        for after in ['one, two, and four','one two, and three','one, two, and $x$']:
            row=self.row();row['after']=after
            with self.assertRaises(ValueError):validate(dict(schema=1,mathematical_token_changes=0,changes=[row]))

    def test_source_changes_require_review_and_partial_books_stay_independent(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);path=root/MANIFEST;path.parent.mkdir()
            row=self.row(source='papers/paper-i/chapter.tex',source_sha256=hashlib.sha256(b'original').hexdigest())
            path.write_text(json.dumps(dict(schema=1,mathematical_token_changes=0,changes=[row])),encoding='utf-8')
            reader=SimpleNamespace(site=SimpleNamespace(root=root),readable_books={})
            prepare(reader)
            self.assertEqual(reader.copyediting,[])
            spec=dict(url=row['page'],source=row['source'])
            reader.readable_books={'paper-i':dict(chapters=[(spec,b'changed',None)])}
            with self.assertRaisesRegex(ValueError,'stale copyediting source'):prepare(reader)
            reader.readable_books['paper-i']['chapters']=[(spec,b'original',None)]
            prepare(reader)
            self.assertEqual(reader.copyediting,[row])

    def test_grouped_references_have_conjunctions_but_citations_keep_their_format(self):
        self.assertEqual(prose_list(['A']),'A')
        self.assertEqual(prose_list(['A','B']),'A and B')
        self.assertEqual(prose_list(['A','B','C']),'A, B, and C')
        chapter=Chapter('',{})
        chapter.labels={key:dict(kind='section',number=str(i),id='L'+str(i),title='',reference_label='Section '+str(i)) for i,key in enumerate(['a','b','c'],1)}
        chapter.citations={'first':(1,'#one'),'second':(2,'#two')}
        chapter.url='read/paper-i/a.html'
        self.assertIn('</a> and <a',chapter.inline(r'\cref{a,b}'))
        self.assertIn('</a>, and <a',chapter.inline(r'\cref{a,b,c}'))
        self.assertIn('</a>, <a',chapter.inline(r'\cite{first,second}'))
        self.assertEqual(chapter.preview(r'\cref{a,b}')[0]['text'],'Section 1 and Section 2')

    def test_markdown_reading_correction_preserves_the_archived_bytes(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);source='example.md'
            raw=b'One, two and three.\r\n`x and y` and $a and b$.\r\n'
            text=raw.decode().replace('\r\n','\n');position=text.index(' and three')
            after=text[:position]+','+text[position:]
            (root/source).write_bytes(raw)
            manifest=root/MARKDOWN_MANIFEST;manifest.parent.mkdir()
            row=dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),
                     after_normalized_sha256=hashlib.sha256(after.encode()).hexdigest(),comma_positions=[position])
            manifest.write_text(json.dumps(dict(schema=1,mathematical_token_changes=0,changes=[row])))
            self.assertEqual(apply_markdown(root,source,text),after)
            self.assertEqual((root/source).read_bytes(),raw)
            (root/source).write_bytes(raw+b'changed')
            with self.assertRaisesRegex(ValueError,'stale Markdown'):apply_markdown(root,source,text)

    def test_markdown_positions_cannot_edit_code_or_mathematics(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);source='example.md'
            text='`x and y`\n\\(a and b\\)\n$$c and d$$\n```\ne and f\n```\n'
            (root/source).write_text(text,encoding='utf-8')
            manifest=root/MARKDOWN_MANIFEST;manifest.parent.mkdir()
            for position in [m.start() for m in re.finditer(' and ',text)]:
                row=dict(source=source,source_sha256=hashlib.sha256((root/source).read_bytes()).hexdigest(),
                         after_normalized_sha256='unused',comma_positions=[position])
                manifest.write_text(json.dumps(dict(schema=1,mathematical_token_changes=0,changes=[row])))
                with self.subTest(position=position),self.assertRaisesRegex(ValueError,'prose comma'):
                    apply_markdown(root,source,text)


if __name__=='__main__':unittest.main()
