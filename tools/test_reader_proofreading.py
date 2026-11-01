"""Editorial notes must remain bound to exact source bytes and passages."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from reader_proofreading import validate, render, publish, verify, REPORT
from check_reader_site import Page


class ReaderProofreadingTests(unittest.TestCase):
    def fixture(self):
        raw=b'Opening.\nHeading.\nDefinition.\n'
        note=dict(id='test-note',work='test',page='read/test/one.html',placement='L2',
                  source=dict(path='book.tex',line=3,expected='Definition.'),
                  title='A & B',text='Keep <the source> unchanged.',
                  references=[dict(path='book.tex',line=3,expected='Definition.',
                                   target='read/test/one.html#L3',label='Read definition')])
        data=dict(schema=1,sources=[dict(path='book.tex',sha256=hashlib.sha256(raw).hexdigest())],notes=[note])
        return data,lambda path:raw,lambda path,line:'read/test/one.html#L'+str(line)

    def test_notes_escape_prose_and_publish_only_after_all_placements_render(self):
        data,read,passage=self.fixture();validate(data,read,passage)
        output={};reader=SimpleNamespace(proofreading_notes=data['notes'],proofreading_record=data,
            rendered_proofreading_notes=[],site=SimpleNamespace(revision='test',rel=lambda target,page:target,write=lambda path,text:output.update({path:text})))
        self.assertEqual(render(reader,'read/other.html','L2'),'')
        with self.assertRaisesRegex(ValueError,'exactly once'):publish(reader)
        markup=render(reader,'read/test/one.html','L2')
        self.assertIn('A &amp; B',markup);self.assertIn('Keep &lt;the source&gt; unchanged.',markup)
        self.assertIn('Editorial reading note',markup)
        publish(reader)
        self.assertEqual(json.loads(output[REPORT])['collection_revision'],'test')
        render(reader,'read/test/one.html','L2')
        with self.assertRaisesRegex(ValueError,'exactly once'):publish(reader)

    def test_stale_bytes_and_moved_source_passages_require_review(self):
        data,read,passage=self.fixture()
        with self.assertRaisesRegex(ValueError,'stale'):validate(data,lambda path:read(path)+b'Changed.',passage)
        changed=deepcopy(data);changed['notes'][0]['source']['expected']='Old definition.'
        with self.assertRaisesRegex(ValueError,'source passage'):validate(changed,read,passage)

    def test_duplicate_notes_wrong_chapters_and_wrong_references_are_rejected(self):
        data,read,passage=self.fixture()
        cases=[]
        duplicate=deepcopy(data);duplicate['notes']*=2;cases.append(duplicate)
        wrong=deepcopy(data);wrong['notes'][0]['page']='read/other.html';cases.append(wrong)
        wrong=deepcopy(data);wrong['notes'][0]['references'][0]['target']='read/test/one.html#L99';cases.append(wrong)
        for changed in cases:
            with self.subTest(changed=changed),self.assertRaises(ValueError):validate(changed,read,passage)

    def test_site_verification_checks_the_note_and_its_reference_link(self):
        data,read,passage=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(path,text):
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
            reader=SimpleNamespace(proofreading_notes=data['notes'],proofreading_record=data,rendered_proofreading_notes=[],
                site=SimpleNamespace(revision='test',rel=lambda target,page:target.split('/')[-1] if '#' in target else target,write=write))
            markup=render(reader,'read/test/one.html','L2')+'<section id="L2"></section><section id="L3"></section>'
            write('read/test/one.html',markup);publish(reader)
            (root/'book.tex').write_bytes(read('book.tex'))
            write('documents/readable-chapters.json',json.dumps([dict(source='book.tex',url='read/test/one.html',nodes=[dict(id='L2',line=2,end_line=2),dict(id='L3',line=3,end_line=3)])]))
            documents=dict(source_revision='test',files=[dict(repository_path='book.tex',file_url='book.tex')])
            pages={'read/test/one.html':Page(markup)}
            self.assertEqual(verify(root,documents,pages)['notes'],1)
            write('read/test/one.html',markup.replace('Keep &lt;the source&gt; unchanged.','Missing note.'))
            with self.assertRaises(AssertionError):verify(root,documents,pages)


if __name__=='__main__':unittest.main()
