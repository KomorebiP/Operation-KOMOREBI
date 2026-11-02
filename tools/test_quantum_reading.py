"""Check the twenty-one main chapters against the retained manuscript."""
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import readable_chapters as reading
from quantum_reading import BOOK,CHAPTERS,DATA,WORK,normalize,source_specs,source_math
from quantum_symmetry import SOURCE as SYMMETRY,MACROS,FIGURES,normalize as normalize_symmetry
from quantum_catalytic import SOURCE as CATALYTIC,MACROS as CATALYTIC_MACROS,normalize as normalize_catalytic
from quantum_circuits import SOURCE as CIRCUITS,VISUAL,MACROS as CIRCUIT_MACROS,normalize as normalize_circuits,normalize_visual,source_macros as circuit_macros
from build_reader_site import Site
from check_reader_site import Page,check_readable_chapter
from reader_documents import ReadingDocuments,source_lines
from statement_navigation import check_directory

ROOT=Path(__file__).resolve().parents[1]


def publish_fixture(output):
    site=SimpleNamespace(root=ROOT,output=output,revision='quantum-reading-test',search=[],cache=None,
        assessments={},editorial_editions={})
    for name in ('rel','write','page','read_source'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader=ReadingDocuments.__new__(ReadingDocuments);reader.site=site
    reader.owned={};reader.records={};reader.images={};reader.inclusions={}
    reader.learning={'learning_topics':[]};reader.claims_by_module={};reader.claims_by_source={}
    reader.manuscript_roots={WORK:BOOK['main']}
    receipt=json.loads((ROOT/f'manifests/source-imports/{WORK}.json').read_bytes())
    for entry in receipt['files']:
        path=receipt['destination']+'/'+entry['path']
        reader.owned[path]=dict(entry,repository_path=path,work=WORK)
    reader.add('monographs/quantum-and-circuits/volume/output/Realization_Calculus_Quantum_and_Circuits.pdf','Read PDF')
    with patch.object(reading,'BOOKS',{WORK:BOOK}):
        reading.prepare(reader);reading.render(reader)
    for record in reader.records.values():
        raw=site.read_source(record);target=output/record['file_url']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        if record['format']=='source':site.page(record['url'],record['title'],'<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class QuantumReadingTests(unittest.TestCase):
    def test_selection_covers_chapters_one_through_twenty_one_and_fails_closed(self):
        load=lambda path:(ROOT/path).read_bytes().decode('utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        self.assertEqual(len(CHAPTERS),148)
        for source in DATA['selected_sources']:
            text=load(source)
            translated={SYMMETRY:normalize_symmetry,CATALYTIC:normalize_catalytic,CIRCUITS:normalize_circuits,VISUAL:normalize_visual}.get(source,normalize)(text)
            self.assertEqual(text.count('\n'),translated.count('\n'))
            if source in DATA['selected_sources'][:2]:self.assertEqual(reading.original_math(text),reading.original_math(translated))
        with self.assertRaisesRegex(ValueError,'Review changed Quantum source'):
            source_specs(lambda path:load(path)+'\nUnreviewed source change.')
        self.assertTrue(BOOK['partial'])
        self.assertIn('appendices remain available',BOOK['reading_introduction'])
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            reading.Chapter('',{}).inline(normalize(r'\unreviewedcommand{lost prose}'))

    def test_symmetry_math_includes_numbered_equations_and_omits_only_duplicate_print_headers(self):
        raw=(ROOT/SYMMETRY).read_bytes().decode('utf-8-sig')
        # Independent extraction also recognizes numbered equation environments.
        # Only the two identical longtable continuation headers are print copies.
        def strip_header(match):
            first=match[1];repeated=match[2]
            self.assertEqual(first.strip(),repeated.strip())
            return first
        semantic=re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}',
            lambda block:re.sub(r'(\\toprule.*?\\midrule\s*)\\endfirsthead\s*(\\toprule.*?\\midrule\s*)\\endhead',strip_header,block[0],flags=re.S),raw,flags=re.S)
        pattern=re.compile(reading.MATH_PATTERN.pattern+r'|\\begin\{equation\}(.*?)\\end\{equation\}',re.S)
        expected=[next(value for value in m.groups() if value is not None) for m in pattern.finditer(semantic)]
        actual=[value for spec in CHAPTERS if spec['source']==SYMMETRY for value in source_math(raw,spec)]
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),567)
        self.assertEqual(len(re.findall(r'\\begin\{equation\}',raw)),21)
        with self.assertRaisesRegex(ValueError,'continuation header'):
            normalize_symmetry(raw.replace('full dim. & packet dim.','altered dim. & packet dim.',1))

    def test_catalytic_formula_sequence_including_the_six_numbered_gate_rows(self):
        raw=(ROOT/CATALYTIC).read_bytes().decode('utf-8-sig')
        # Extract source displays independently; numbered align rows represent
        # six separately numbered equations and lose only their layout column.
        def strip_header(match):
            self.assertEqual(match[1].strip(),match[2].strip());return match[1]
        semantic=re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}',
            lambda block:re.sub(r'(\\toprule.*?\\midrule\s*)\\endfirsthead\s*(\\toprule.*?\\midrule\s*)\\endhead',strip_header,block[0],flags=re.S),raw,flags=re.S)
        semantic=re.sub(r'\\begin\{(lstlisting|verbatim)\}(?:\[[^\]]*\])?.*?\\end\{\1\}','',reading.clean_tex(semantic),flags=re.S)
        pattern=re.compile(reading.MATH_PATTERN.pattern+r'|\\begin\{equation\}(.*?)\\end\{equation\}|\\begin\{align\}(.*?)\\end\{align\}',re.S)
        expected=[]
        for match in pattern.finditer(semantic):
            if match[6] is None:expected.append(next(v for v in match.groups() if v is not None))
            else:expected.extend(row.replace('&','').strip('\n') for row in reading.split_cells(match[6],r'\\') if row.strip())
        actual=[value for spec in CHAPTERS if spec['source']==CATALYTIC for value in source_math(raw,spec)]
        self.assertEqual(actual,expected);self.assertEqual(len(actual),1906)
        with self.assertRaisesRegex(ValueError,'gate alignment'):
            normalize_catalytic(raw.replace('g:gate:a6','g:gate:changed'))

    def test_circuit_formula_sequence_and_local_field_conventions(self):
        pattern=re.compile(reading.MATH_PATTERN.pattern+r'|\\begin\{equation\}(.*?)\\end\{equation\}',re.S)
        for source,count in [(CIRCUITS,447),(VISUAL,328)]:
            raw=(ROOT/source).read_bytes().decode('utf-8-sig')
            expected=[next(v for v in m.groups() if v is not None) for m in pattern.finditer(reading.clean_tex(raw))]
            actual=[v for spec in CHAPTERS if spec['source']==source for v in source_math(raw,spec)]
            self.assertEqual(actual,expected);self.assertEqual(len(actual),count)
        load=lambda path:(ROOT/path).read_bytes().decode('utf-8-sig')
        self.assertEqual(circuit_macros(load)['F'],r'\mathbb F_2')
        self.assertEqual(circuit_macros(load,visual=True)['F'],r'\mathbb F')
        self.assertEqual(circuit_macros(load)['B'],r'\{0,1\}')
        with self.assertRaisesRegex(ValueError,'field and Boolean conventions'):
            circuit_macros(lambda path:load(path).replace(r'\mathbb F_2',r'\mathbb F_3'))

    def test_published_math_proofs_tables_figures_and_source_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()))
            with patch.object(reading,'BOOKS',{WORK:BOOK}),patch.object(reading,'CHAPTERS',CHAPTERS):
                total=check_readable_chapter(output,documents,pages)
            self.assertEqual(total,3886)
            nodes=[n for _,_,chapter in reader.readable_books[WORK]['chapters'] for n in chapter.nodes]
            arithmetic=[n for spec,_,chapter in reader.readable_books[WORK]['chapters'] if spec['source'] in DATA['selected_sources'][:2] for n in chapter.nodes]
            statements=[n for n in arithmetic if n['kind']=='theorem']
            proofs=[n for n in nodes if n['kind']=='proof']
            self.assertEqual([n['number'] for n in statements],['QA'+str(i).zfill(2) for i in range(1,21)])
            self.assertEqual(len(proofs),120)
            self.assertTrue(all(r'\(\square\)' in n['body'] for n in arithmetic if n['kind']=='proof'))
            raw=(ROOT/DATA['selected_sources'][0]).read_text(encoding='utf-8')
            expected=[raw.count('\n',0,m.start())+1 for m in re.finditer(r'\\subsection\*\{Theorem QA\d\d\. ',raw)]
            self.assertEqual([n['line'] for n in statements],expected)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),85)
            self.assertEqual(len(reader.images),82)
            nested=[n for _,_,c in reader.readable_books[WORK]['chapters'] for n in c.nested_tables]
            self.assertEqual(sum(n['kind'] in {'table','longtable','tabular'} for n in nodes)+len(nested),31)
            self.assertEqual(sum(n['kind']=='question' for n in nodes),44)
            self.assertEqual(sum(n['kind']=='interpretation' for n in nodes),54)
            # Reconstruct the chapter-wide statement counters from raw source,
            # independently of the reader's section-based parser and renumbering.
            source=(ROOT/SYMMETRY).read_bytes().decode('utf-8-sig');chapter_number=2;counter=0;expected=[]
            pattern=r'\\chapter\{|\\begin\{('+ '|'.join(sorted(reading.NUMBERED))+r')\}'
            for match in re.finditer(pattern,source):
                if match[1] is None:chapter_number+=1;counter=0
                else:
                    counter+=1;expected.append((match[1],str(chapter_number)+'.'+str(counter),source.count('\n',0,match.start())+1))
            symmetry_chapters=[c for c in reader.readable_books[WORK]['chapters'] if c[0]['source']==SYMMETRY]
            actual=[(n['kind'],n['number'],n['line']) for _,_,chapter in symmetry_chapters for n in chapter.nodes if n['kind'] in reading.NUMBERED]
            self.assertEqual(actual,expected);self.assertEqual(len(actual),49)
            equations=symmetry_chapters[0][2].equation_numbers
            self.assertEqual(equations['s:eq:residue-projector'],'3.1')
            self.assertEqual(equations['s:eq:commutant-output'],'4.6')
            expected_equations={};chapter_number=2;counter=0
            for match in re.finditer(r'\\chapter\{|\\begin\{equation\}(.*?)\\end\{equation\}',source,re.S):
                if match[1] is None:chapter_number+=1;counter=0
                else:
                    counter+=1
                    for label in re.findall(r'\\label\{([^{}]+)\}',match[1]):expected_equations[label]=str(chapter_number)+'.'+str(counter)
            self.assertEqual({k:v for k,v in equations.items() if k.startswith('s:')},expected_equations)
            proof_page=next(s['url'] for s,_,_ in symmetry_chapters if s['title']=='Permutation-invariant mixed states and commutant compression')
            proof_markup=(output/proof_page).read_text(encoding='utf-8')
            self.assertIn('>Equation (4.8)</a>',proof_markup)
            self.assertIn('>Theorem 6.1</a>',proof_markup)
            self.assertTrue(all(chapter.macro_source==MACROS for _,_,chapter in symmetry_chapters))
            # A figure repeated in the book must match its recorded use count.
            from reader_figure_assets import prepare
            compiler=next(chapter for _,_,chapter in symmetry_chapters if any('s_compiler_pipeline.pdf' in n['body'] for n in chapter.nodes))
            figure=next(n for n in compiler.nodes if n['kind']=='figure' and 's_compiler_pipeline.pdf' in n['body'])
            compiler.nodes.append(figure)
            with self.assertRaisesRegex(ValueError,'recorded number of times'):
                prepare(reader,dict(BOOK,figure_receipts=FIGURES),symmetry_chapters)
            compiler.nodes.pop()
            directory=reading.statement_directory_url(BOOK)
            self.assertIn('in this HTML selection',(output/directory).read_text(encoding='utf-8'))
            chapters=[(s['url'],(output/s['url']).read_text(encoding='utf-8')) for s in CHAPTERS]
            result=check_directory((output/directory).read_text(encoding='utf-8'),chapters,directory)
            self.assertEqual(result['proof_links'],120)
            self.assertEqual(result['statements'],233)
            references=(output/BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('Życzkowski',references)
            self.assertIn('[17] s:TransferRecords',references)
            self.assertIn('[45] g:WeedbrookEtAl2012',references)
            catalytic=[c for c in reader.readable_books[WORK]['chapters'] if c[0]['source']==CATALYTIC]
            self.assertTrue(all(c.macro_source==CATALYTIC_MACROS for _,_,c in catalytic))
            source=(ROOT/CATALYTIC).read_bytes().decode('utf-8-sig');number=7;counter=0;expected=[]
            for match in re.finditer(r'\\chapter\{|\\begin\{('+ '|'.join(sorted(reading.NUMBERED))+r')\}',source):
                if match[1] is None:number+=1;counter=0
                else:
                    counter+=1;expected.append((match[1],str(number)+'.'+str(counter),source.count('\n',0,match.start())+1))
            actual=[(n['kind'],n['number'],n['line']) for _,_,c in catalytic for n in c.nodes if n['kind'] in reading.NUMBERED]
            self.assertEqual(actual,expected);self.assertEqual(len(actual),134)
            # Every cross-page proof link follows an explicitly named source
            # title; check the destination and return independently of the binder.
            import posixpath
            named=list(re.finditer(r'\\begin\{proof\}\[Proof of \\cref\{([^{}]+)\}\]',source))
            self.assertEqual(len(named),8)
            for match in named:
                line=source.count('\n',0,match.start())+1
                proof_spec=next(s for s,_,_ in catalytic if s['start_line']<=line<=s['end_line'])
                statement_spec,statement=next((s,n) for s,_,c in catalytic for n in c.nodes if match[1] in n['labels'])
                proof_href=posixpath.relpath(proof_spec['url'],posixpath.dirname(statement_spec['url']))+'#L'+str(line)
                statement_href=posixpath.relpath(statement_spec['url'],posixpath.dirname(proof_spec['url']))+'#'+statement['id']
                self.assertIn('href="'+proof_href+'">Read proof</a>',(output/statement_spec['url']).read_text(encoding='utf-8'))
                self.assertIn('href="'+statement_href+'">Back to statement</a>',(output/proof_spec['url']).read_text(encoding='utf-8'))
                search=next(entry for entry in reader.site.search if entry['url']==proof_spec['url']+'#L'+str(line))
                expected_title='Proof of '+reading.KIND_NAMES.get(statement['kind'],statement['kind'].capitalize())+' '+statement['number']
                self.assertEqual(search['title'],BOOK['label']+' / '+expected_title)
            # Reconstruct every equation counter from original source order.
            number=7;counter=0;expected={}
            for match in re.finditer(r'\\chapter\{|\\begin\{(equation|align)\}(.*?)\\end\{\1\}',source,re.S):
                if match[1] is None:number+=1;counter=0
                else:
                    rows=[match[2]] if match[1]=='equation' else [r for r in reading.split_cells(match[2],r'\\') if r.strip()]
                    for row in rows:
                        counter+=1
                        for label in re.findall(r'\\label\{([^{}]+)\}',row):expected[label]=str(number)+'.'+str(counter)
            equations=catalytic[0][2].equation_numbers
            self.assertEqual({k:v for k,v in equations.items() if k.startswith('g:')},expected)
            gate_page=next(s['url'] for s,_,_ in catalytic if s['title']=='The universal six-row atom')
            gate_markup=(output/gate_page).read_text(encoding='utf-8')
            for i in range(1,7):self.assertIn('Equation ('+expected['g:gate:a'+str(i)]+')',gate_markup)
            # Code is a retained listing, not executed as part of publication.
            from html.parser import HTMLParser
            class Listings(HTMLParser):
                def __init__(self):super().__init__();self.active=False;self.items=[]
                def handle_starttag(self,tag,attrs):
                    if tag=='pre':self.active=True;self.items.append('')
                def handle_endtag(self,tag):
                    if tag=='pre':self.active=False
                def handle_data(self,data):
                    if self.active:self.items[-1]+=data
            listing=Listings()
            for spec,_,_ in catalytic:listing.feed((output/spec['url']).read_text(encoding='utf-8'))
            expected=[m[2].strip('\n') for m in re.finditer(r'\\begin\{(lstlisting|verbatim)\}(?:\[[^\]]*\])?(.*?)\\end\{\1\}',source,re.S)]
            self.assertEqual(listing.items,expected);self.assertEqual(len(expected),6)
            self.assertEqual(sum(n['kind']=='algorithm' for n in nodes),3)
            self.assertEqual(sum(n['kind']=='protocol' for n in nodes),2)
            circuits=[c for c in reader.readable_books[WORK]['chapters'] if c[0]['source']==CIRCUITS]
            visual=[c for c in reader.readable_books[WORK]['chapters'] if c[0]['source']==VISUAL]
            self.assertEqual((len(circuits),len(visual)),(23,25))
            self.assertTrue(all(c.macro_source==CIRCUIT_MACROS for _,_,c in circuits+visual))
            self.assertTrue(all(c.macros['F']==r'\mathbb F_2' for _,_,c in circuits))
            self.assertTrue(all(c.macros['F']==r'\mathbb F' for _,_,c in visual))
            # Independently recover the printed chapter-shared statements and
            # equation counters directly from the unmodified circuit source.
            source=(ROOT/CIRCUITS).read_bytes().decode('utf-8-sig');number=12;counter=0;expected=[]
            for match in re.finditer(r'\\chapter\{|\\begin\{('+ '|'.join(sorted(reading.NUMBERED))+r')\}',source):
                if match[1] is None:number+=1;counter=0
                else:
                    counter+=1;expected.append((match[1],str(number)+'.'+str(counter),source.count('\n',0,match.start())+1))
            actual=[(n['kind'],n['number'],n['line']) for _,_,c in circuits for n in c.nodes if n['kind'] in reading.NUMBERED]
            self.assertEqual(actual,expected);self.assertEqual(len(actual),30)
            self.assertEqual(sum(len(c.proof_pairs) for _,_,c in circuits),30)
            number=12;counter=0;expected={}
            for match in re.finditer(r'\\chapter\{|\\begin\{equation\}(.*?)\\end\{equation\}',source,re.S):
                if match[1] is None:number+=1;counter=0
                else:
                    counter+=1
                    for label in re.findall(r'\\label\{([^{}]+)\}',match[1]):expected[label]=str(number)+'.'+str(counter)
            self.assertEqual({k:v for k,v in circuits[0][2].equation_numbers.items() if k.startswith('c:')},expected)
            self.assertEqual(len(expected),6)
            for title in re.findall(r'\\begin\{circuitscopebox\}\{([^{}]+)\}',source):
                self.assertTrue(any(title in (output/s['url']).read_text(encoding='utf-8') for s,_,_ in circuits))
            guide=(ROOT/VISUAL).read_bytes().decode('utf-8-sig')
            figures=[n for _,_,c in visual for n in c.nodes if n['kind']=='figure']
            self.assertEqual(len(figures),12);self.assertTrue(all(not n['number'] for n in figures))
            guide_listing=Listings()
            for spec,_,_ in visual:guide_listing.feed((output/spec['url']).read_text(encoding='utf-8'))
            self.assertEqual(guide_listing.items,[m[1].strip('\n') for m in re.finditer(r'\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}',guide,re.S)])
            self.assertEqual(len(guide_listing.items),2)
            appendix=next(r for r in reader.records.values() if r['repository_path'].endswith('c_supplement.tex'))
            citation_page=next(s['url'] for s,_,_ in circuits if s['title']=='What the comparison does and does not require')
            self.assertIn(appendix['url'].split('/')[-1]+'#L85',(output/citation_page).read_text(encoding='utf-8'))
            self.assertIn('id="L85"',(output/appendix['url']).read_text(encoding='utf-8'))
            self.assertIn('[54] c:beckli',references)
            self.assertIn('<code>docs/FOUNDATIONS.md</code>',references)
            for spec in CHAPTERS:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size',markup)
                self.assertIn('Switch work',markup)
                self.assertIn('Original TeX with line links',markup)
            for record in reader.images.values():
                self.assertIn(record['file_url'],{p.relative_to(output).as_posix() for p in output.rglob('*.png')})


if __name__=='__main__':unittest.main()
