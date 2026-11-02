import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from lean_reader import build, code_view, declarations, highlight_lines, prepare, selected_paths, source_controls, verify
from reader_documents import ReadingDocuments, source_lines


class LeanReaderTests(unittest.TestCase):
    def test_declarations_ignore_nested_comments_strings_and_keep_actual_lines(self):
        text = ('/- theorem hidden : True := by trivial\n/- def nested := 0 -/ -/\n'
                'def message := "theorem fake\nlemma fake2"\n'
                '-- axiom nope : False\n\n'
                'private noncomputable theorem real : True := by trivial\n'
                'structure Pair where\n  x : Nat\n'
                'instance : Inhabited Nat := ⟨0⟩\n'
                'lemma «named result» : True := by trivial\n'
                'def escaped := "a\\\" -- theorem nope"\n'
                '@[simp] theorem attributed : True := by trivial\n'
                '@[simp,\n  aesop safe [constructors]]\nlemma multiline : True := by trivial\n'
                'axiom assumption : Prop\n')
        result = declarations(text)
        self.assertEqual([(d['kind'],d['name']) for d in result],
                         [('def','message'),('theorem','real'),('structure','Pair'),
                          ('lemma','«named result»'),('def','escaped'),('theorem','attributed'),
                          ('lemma','multiline'),('axiom','assumption')])
        lines = text.splitlines()
        for d in result:self.assertIn(d['kind']+' '+d['name'],lines[d['line']-1])

    def test_selections_respect_ownership_directory_boundaries_and_exclusions(self):
        c=dict(id='paper-i',destination='papers/current',resources=[dict(kind='lean',path='formal/'),
                dict(kind='lean',path='formal/Main.lean'),dict(kind='formal_guide',path='other/guide.lean')])
        paths=['formal/Main.lean','formal/A.lean','formal/.lake/packages/Dep.lean',
               'formal/build/Generated.lean','formal/lakefile.lean','formal2/Leak.lean','other/guide.lean']
        owned={'papers/current/'+p:dict(work='paper-i') for p in paths}
        owned['papers/current/formal/Foreign.lean']=dict(work='other')
        self.assertEqual(list(selected_paths(c,owned)),['papers/current/formal/A.lean','papers/current/formal/Main.lean'])
        c['resources'][0]['path']='../unsafe/'
        with self.assertRaises(ValueError):list(selected_paths(c,owned))

    def fixture(self, output):
        root=Path(__file__).resolve().parents[1]
        text='-- preserved source <&>\ntheorem result : True := by\n  trivial\n'
        raw=text.encode();path='papers/paper-i/current/formal/Main.lean'
        record=dict(repository_path=path,work='paper-i',url='read/paper-i/main.html',file_url='documents/files/Main.lean',
                    sha256=hashlib.sha256(raw).hexdigest(),size=len(raw))
        site=SimpleNamespace(root=root,output=output,revision='a'*40,search=[],
                components={'paper-i':dict(title='Paper I <test>',destination='papers/paper-i/current')},
                assessments={'paper-i':dict(lean='partial')},
                status=dict(labels=dict(lean=dict(partial=['Selected results recorded','Scope remains limited.']))))
        import posixpath
        site.rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
        def write(path,text):
            target=output/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
        site.write=write;site.page=lambda path,title,body:write(path,body);site.read_source=lambda record:raw
        reader=SimpleNamespace(site=site,lean_works={'paper-i':[record]})
        return reader,record,text

    def test_publication_preserves_bytes_line_links_escaping_and_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp);reader,record,text=self.fixture(output)
            report=build(reader)
            self.assertEqual(report,dict(works=1,files=1,new_lean_execution=False))
            page=output/record['url'];page.parent.mkdir(parents=True)
            page.write_text(source_controls(reader,record,text,record['url'])+code_view(text),encoding='utf-8')
            raw=output/record['file_url'];raw.parent.mkdir(parents=True);raw.write_bytes(text.encode())
            body=page.read_text(encoding='utf-8')
            self.assertIn('href="#L2"',body);self.assertIn('Selected results recorded',body)
            directory=(output/'lean/paper-i/index.html').read_text(encoding='utf-8')
            self.assertIn('Paper I &lt;test&gt;',directory)
            self.assertIn('data-lean-search="formal/Main.lean theorem result"',directory)
            self.assertEqual(verify(output,dict(files=[record]))['files'],1)
            tampered=body.replace('>trivial</span>','>sorry</span>')
            self.assertNotEqual(tampered,body)
            page.write_text(tampered,encoding='utf-8')
            with self.assertRaises(AssertionError):verify(output,dict(files=[record]))

    def test_highlighting_preserves_unicode_indentation_and_escapes_active_html(self):
        from html.parser import HTMLParser
        class Text(HTMLParser):
            def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
            def handle_data(self,data):self.parts.append(data)
        text = ('/- outer <script>\n/- nested theorem -/ still comment -/\n'
                'def message := "a\\\" -- text & <tag>"\n'
                'def letter := \'"\'\n'
                'lemma quoted\' : True := by\n  exact True.intro\n'
                'def «a--b» := 12\n\n'
                'theorem τεστ (n : ℕ) : n = n := by\n  rfl -- unchanged\n')
        highlighted=highlight_lines(text)
        self.assertEqual(len(highlighted),len(text.splitlines()))
        for original,markup in zip(text.splitlines(),highlighted):
            parser=Text();parser.feed(markup);self.assertEqual(''.join(parser.parts),original)
        self.assertIn('lean-token-comment',highlighted[1])
        self.assertIn('lean-token-string',highlighted[2]);self.assertIn('lean-token-string',highlighted[3])
        self.assertIn('lean-token-keyword',highlighted[4]);self.assertIn('lean-token-tactic',highlighted[5])
        self.assertNotIn('lean-token-comment',highlighted[6])
        self.assertNotIn('<script>', ''.join(highlighted))
        with self.assertRaises(ValueError):source_lines('one\ntwo',rendered_lines=['one'])

    def test_prepare_does_not_add_works_without_a_reading_edition(self):
        reader=SimpleNamespace(site=SimpleNamespace(registry=dict(components=[
            dict(id='not-a-reading-edition',destination='outside',resources=[dict(kind='lean',path='main.lean')])])),
            owned={'outside/main.lean':dict(work='not-a-reading-edition')},
            add=lambda path:self.fail('Source should not be registered'))
        prepare(reader)
        self.assertEqual(reader.lean_works,{})

    def test_reading_edition_without_lean_selection_has_no_inspector(self):
        reader=SimpleNamespace(site=SimpleNamespace(registry=dict(components=[
            dict(id='komorebi-methodology',destination='methodology',
                 resources=[dict(kind='text',path='essay.tex')])])),
            owned={'methodology/unselected.lean':dict(work='komorebi-methodology')},
            add=lambda path:self.fail('Unselected source should not be registered'))
        prepare(reader)
        self.assertEqual(reader.lean_works,{})

    def test_reading_editions_with_lean_selections_have_receipt_bound_sources(self):
        from readable_chapters import BOOKS
        root=Path(__file__).resolve().parents[1]
        registry=json.loads((root/'manifests/browse-resources.json').read_bytes())
        works={};expected=set();registered=set()
        for c in registry['components']:
            if c['id'] not in BOOKS:continue
            registered.add(c['id'])
            receipt=json.loads((root/('manifests/source-imports/'+c['id']+'.json')).read_bytes())
            owned={c['destination']+'/'+f['path']:{**f,'work':c['id']} for f in receipt['files']}
            paths=list(selected_paths(c,owned))
            if any(r['kind']=='lean' for r in c['resources']):
                expected.add(c['id'])
                self.assertTrue(paths,c['id']);works[c['id']]=paths
            else:
                self.assertEqual(paths,[],c['id'])
        self.assertEqual(registered,set(BOOKS))
        self.assertEqual(set(works),expected)


if __name__=='__main__':unittest.main()
