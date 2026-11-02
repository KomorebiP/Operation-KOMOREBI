"""Check arithmetic and symmetry transcription against the retained manuscript."""
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
    def test_selection_covers_chapters_one_through_seven_and_fails_closed(self):
        load=lambda path:(ROOT/path).read_bytes().decode('utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        self.assertEqual(len(CHAPTERS),72)
        for source in DATA['selected_sources']:
            text=load(source)
            translated=(normalize_symmetry if source==SYMMETRY else normalize)(text)
            self.assertEqual(text.count('\n'),translated.count('\n'))
            if source!=SYMMETRY:self.assertEqual(reading.original_math(text),reading.original_math(translated))
        with self.assertRaisesRegex(ValueError,'Review changed Quantum source'):
            source_specs(lambda path:load(path)+'\nUnreviewed source change.')
        self.assertTrue(BOOK['partial'])
        self.assertIn('remaining book',BOOK['reading_introduction'])
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
        semantic=re.sub(r'(\\toprule.*?\\midrule\s*)\\endfirsthead\s*(\\toprule.*?\\midrule\s*)\\endhead',strip_header,raw,flags=re.S)
        pattern=re.compile(reading.MATH_PATTERN.pattern+r'|\\begin\{equation\}(.*?)\\end\{equation\}',re.S)
        expected=[next(value for value in m.groups() if value is not None) for m in pattern.finditer(semantic)]
        actual=[value for spec in CHAPTERS if spec['source']==SYMMETRY for value in source_math(raw,spec)]
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),567)
        self.assertEqual(len(re.findall(r'\\begin\{equation\}',raw)),21)
        with self.assertRaisesRegex(ValueError,'continuation header'):
            normalize_symmetry(raw.replace('full dim. & packet dim.','altered dim. & packet dim.',1))

    def test_published_math_proofs_tables_figures_and_source_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()))
            with patch.object(reading,'BOOKS',{WORK:BOOK}),patch.object(reading,'CHAPTERS',CHAPTERS):
                total=check_readable_chapter(output,documents,pages)
            self.assertEqual(total,1205)
            nodes=[n for _,_,chapter in reader.readable_books[WORK]['chapters'] for n in chapter.nodes]
            arithmetic=[n for spec,_,chapter in reader.readable_books[WORK]['chapters'] if spec['source']!=SYMMETRY for n in chapter.nodes]
            statements=[n for n in arithmetic if n['kind']=='theorem']
            proofs=[n for n in nodes if n['kind']=='proof']
            self.assertEqual([n['number'] for n in statements],['QA'+str(i).zfill(2) for i in range(1,21)])
            self.assertEqual(len(proofs),39)
            self.assertTrue(all(r'\(\square\)' in n['body'] for n in arithmetic if n['kind']=='proof'))
            raw=(ROOT/DATA['selected_sources'][0]).read_text(encoding='utf-8')
            expected=[raw.count('\n',0,m.start())+1 for m in re.finditer(r'\\subsection\*\{Theorem QA\d\d\. ',raw)]
            self.assertEqual([n['line'] for n in statements],expected)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),39)
            self.assertEqual(len(reader.images),38)
            self.assertEqual(sum(n['kind'] in {'longtable','tabular'} for n in nodes),6)
            self.assertEqual(sum(n['kind']=='question' for n in nodes),12)
            self.assertEqual(sum(n['kind']=='interpretation' for n in nodes),21)
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
            self.assertEqual(equations,expected_equations)
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
            self.assertEqual(result['proof_links'],39)
            self.assertEqual(result['statements'],69)
            references=(output/BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('Życzkowski',references)
            self.assertIn('[17] s:TransferRecords',references)
            for spec in CHAPTERS:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size',markup)
                self.assertIn('Switch work',markup)
                self.assertIn('Original TeX with line links',markup)
            for record in reader.images.values():
                self.assertIn(record['file_url'],{p.relative_to(output).as_posix() for p in output.rglob('*.png')})


if __name__=='__main__':unittest.main()
