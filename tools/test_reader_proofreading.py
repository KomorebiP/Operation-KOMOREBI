"""Editorial notes must remain bound to exact source bytes and passages."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from reader_proofreading import validate, prepare, render, publish, verify, MANIFESTS, REPORT
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

    def records(self, root):
        first,read,_=self.fixture()
        first['review_date']='2026-11-01'
        first['scope']='The retained first review.'
        first['sources'][0]['work']='test'
        second=deepcopy(first)
        second['review_date']='2026-11-03'
        second['scope']='A separate subsequent review.'
        second['retained_evidence']=[dict(path='evidence.csv',sha256='a'*64)]
        second['notes'][0].update(id='later-note',placement='L3')
        other=deepcopy(second['notes'][0])
        other.update(id='other-note',work='other',page='read/other/one.html',placement='L2')
        other['source']['path']='other.tex'
        other['references'][0].update(path='other.tex',target='read/other/one.html#L3')
        second['notes'].append(other)
        second['sources'].append(dict(path='other.tex',work='other',sha256=hashlib.sha256(read('book.tex')).hexdigest()))
        raw={}
        for manifest,data in zip(MANIFESTS,[first,second]):
            path=root/manifest;path.parent.mkdir(parents=True,exist_ok=True)
            raw[manifest]=json.dumps(data,indent=2).encode()
            path.write_bytes(raw[manifest])
        return first,second,read,raw

    def reader(self,root,read,works):
        books={};records={};reads=[]
        for work in works:
            source='book.tex' if work=='test' else 'other.tex'
            config=dict(main=source,index='read/'+work+'/index.html')
            spec=dict(source=source,url='read/'+work+'/one.html')
            chapter=SimpleNamespace(nodes=[dict(id='L2',line=2,end_line=2),dict(id='L3',line=3,end_line=3)])
            books[work]=dict(config=config,chapters=[(spec,read(source),chapter)])
            records[source]=dict(repository_path=source)
        def read_source(record):
            reads.append(record['repository_path']);return read(record['repository_path'])
        return SimpleNamespace(site=SimpleNamespace(root=root,read_source=read_source),
            records=records,readable_books=books),reads

    def test_separate_reviews_preserve_metadata_and_deduplicate_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);first,second,read,raw=self.records(root)
            reader,reads=self.reader(root,read,['test','other'])
            prepare(reader)
            record=reader.proofreading_record
            self.assertEqual([note['id'] for note in record['notes']],['test-note','later-note','other-note'])
            self.assertEqual([source['path'] for source in record['sources']],['book.tex','other.tex'])
            self.assertEqual(reads,['book.tex','other.tex'])
            self.assertEqual([review['metadata']['review_date'] for review in record['reviews']],['2026-11-01','2026-11-03'])
            self.assertEqual(record['reviews'][0]['metadata']['scope'],first['scope'])
            self.assertEqual(record['reviews'][1]['metadata']['retained_evidence'],second['retained_evidence'])
            for review in record['reviews']:
                self.assertEqual(review['manifest_sha256'],hashlib.sha256(raw[review['manifest']]).hexdigest())
                self.assertEqual((root/review['manifest']).read_bytes(),raw[review['manifest']])

    def test_subset_preparation_needs_only_selected_works_and_their_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);_,_,read,_=self.records(root)
            reader,reads=self.reader(root,read,['test'])
            prepare(reader)
            self.assertEqual([note['id'] for note in reader.proofreading_notes],['test-note','later-note'])
            self.assertEqual([source['path'] for source in reader.proofreading_record['sources']],['book.tex'])
            self.assertEqual(reads,['book.tex'])
            self.assertTrue(all(review['selected_works']==['test'] for review in reader.proofreading_record['reviews']))
            reader.readable_books={}
            prepare(reader)
            self.assertEqual(reader.proofreading_notes,[])
            self.assertIsNone(reader.proofreading_record)

    def test_conflicting_review_sources_and_duplicate_note_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);_,second,read,_=self.records(root)
            reader,_=self.reader(root,read,['test'])
            wrong=deepcopy(second);wrong['sources'][0]['sha256']='0'*64
            (root/MANIFESTS[1]).write_text(json.dumps(wrong),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Conflicting proofreading source'):prepare(reader)
            wrong=deepcopy(second);wrong['notes'][0]['id']='test-note'
            (root/MANIFESTS[1]).write_text(json.dumps(wrong),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'duplicate proofreading note'):prepare(reader)

    def test_published_review_cannot_drop_its_note_or_source_bindings(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);_,_,read,_=self.records(root)
            reader,_=self.reader(root,read,['test'])
            prepare(reader)
            for field in ['note_ids','source_paths']:
                wrong=deepcopy(reader.proofreading_record)
                for review in wrong['reviews']:review[field]=[]
                with self.subTest(field=field),self.assertRaisesRegex(ValueError,'review bindings'):
                    validate(wrong,read,lambda path,line:'read/test/one.html#L'+str(line))

    def test_site_verification_checks_the_note_and_its_reference_link(self):
        data,read,passage=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(path,text):
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
            reader=SimpleNamespace(proofreading_notes=data['notes'],proofreading_record=data,rendered_proofreading_notes=[],
                site=SimpleNamespace(revision='test',rel=lambda target,page:target.split('/')[-1] if '#' in target else target,write=write))
            note=render(reader,'read/test/one.html','L2')
            markup='<article id="chapter-text"><section id="L2"></section>'+note+'<section id="L3"></section></article>'
            write('read/test/one.html',markup);publish(reader)
            (root/'book.tex').write_bytes(read('book.tex'))
            write('documents/readable-chapters.json',json.dumps([dict(source='book.tex',url='read/test/one.html',nodes=[dict(id='L2',line=2,end_line=2),dict(id='L3',line=3,end_line=3)])]))
            documents=dict(source_revision='test',files=[dict(repository_path='book.tex',file_url='book.tex')])
            pages={'read/test/one.html':Page(markup)}
            self.assertEqual(verify(root,documents,pages)['notes'],1)
            write('read/test/one.html',markup.replace('Keep &lt;the source&gt; unchanged.','Missing note.'))
            with self.assertRaises(AssertionError):verify(root,documents,pages)
            for changed in [
                '<article id="chapter-text">'+note+'<section id="L2"></section><section id="L3"></section></article>',
                '<article id="chapter-text"><section id="L2">'+note+'</section><section id="L3"></section></article>',
                '<article id="chapter-text"><section id="L2"></section><section id="L3"></section>'+note+'</article>',
            ]:
                write('read/test/one.html',changed)
                with self.subTest(markup=changed),self.assertRaisesRegex(AssertionError,'placement'):
                    verify(root,documents,{'read/test/one.html':Page(changed)})
            write('read/test/one.html',markup)
            with self.assertRaisesRegex(AssertionError,'exactly once'):
                verify(root,documents,{**pages,'read/other.html':Page(note)})

    def test_verification_distinguishes_parent_and_imported_source_lines(self):
        data,read,_=self.fixture()
        data['sources'].append(dict(path='included.tex',sha256=hashlib.sha256(read('book.tex')).hexdigest()))
        data['notes'][0]['references'][0]['target']='read/test/one.html#L2'
        data['notes'][0]['references'].append(dict(path='included.tex',line=3,expected='Definition.',
            target='read/test/one.html#included-L2',label='Imported definition'))
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(path,text):
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
            reader=SimpleNamespace(proofreading_notes=data['notes'],proofreading_record=data,rendered_proofreading_notes=[],
                site=SimpleNamespace(revision='test',rel=lambda target,page:target.split('/')[-1] if '#' in target else target,write=write))
            markup=('<article id="chapter-text"><section id="L2"></section>'+render(reader,'read/test/one.html','L2')
                    +'<section id="included-L2"></section></article>')
            write('read/test/one.html',markup);publish(reader)
            for source in ['book.tex','included.tex']:(root/source).write_bytes(read(source))
            nodes=[dict(id='L2',line=2,end_line=3,source='book.tex',source_spans=[dict(source='book.tex',line=2,end_line=3)]),
                   dict(id='included-L2',line=2,end_line=3,source='included.tex',source_spans=[dict(source='included.tex',line=2,end_line=3)])]
            write('documents/readable-chapters.json',json.dumps([dict(source='book.tex',url='read/test/one.html',nodes=nodes)]))
            documents=dict(source_revision='test',files=[dict(repository_path=source,file_url=source) for source in ['book.tex','included.tex']])
            self.assertEqual(verify(root,documents,{'read/test/one.html':Page(markup)})['notes'],1)

    def test_abstract_note_follows_the_retained_abstract(self):
        data,read,_=self.fixture()
        data['notes'][0].update(page='read/test/index.html',placement='abstract')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def write(path,text):
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
            reader=SimpleNamespace(proofreading_notes=data['notes'],proofreading_record=data,rendered_proofreading_notes=[],
                site=SimpleNamespace(revision='test',rel=lambda target,page:target.split('/')[-1] if '#' in target else target,write=write))
            note=render(reader,'read/test/index.html','abstract')
            abstract='<section id="abstract"><h2>Abstract</h2><p>Retained abstract.</p></section>'
            chapter='<article id="chapter-text"><section id="L3">Definition.</section></article>'
            write('read/test/index.html',abstract+note);write('read/test/one.html',chapter);publish(reader)
            (root/'book.tex').write_bytes(read('book.tex'))
            write('documents/readable-chapters.json',json.dumps([dict(source='book.tex',url='read/test/one.html',nodes=[dict(id='L3',line=3,end_line=3)])]))
            documents=dict(source_revision='test',files=[dict(repository_path='book.tex',file_url='book.tex')])
            pages={'read/test/index.html':Page(abstract+note),'read/test/one.html':Page(chapter)}
            self.assertEqual(verify(root,documents,pages)['notes'],1)
            write('read/test/index.html',note+abstract)
            with self.assertRaisesRegex(AssertionError,'placement'):verify(root,documents,pages)


if __name__=='__main__':unittest.main()
