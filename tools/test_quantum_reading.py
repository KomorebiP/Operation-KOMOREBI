"""Check arithmetic transcription, authored proof routes and original figures."""
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import readable_chapters as reading
from quantum_reading import BOOK,CHAPTERS,DATA,WORK,normalize,source_specs
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
    def test_selection_is_complete_for_both_opening_chapters_and_fails_closed(self):
        load=lambda path:(ROOT/path).read_bytes().decode('utf-8-sig')
        self.assertEqual(source_specs(load),CHAPTERS)
        self.assertEqual(len(CHAPTERS),42)
        for source in DATA['selected_sources']:
            text=load(source)
            self.assertEqual(text.count('\n'),normalize(text).count('\n'))
            self.assertEqual(reading.original_math(text),reading.original_math(normalize(text)))
        with self.assertRaisesRegex(ValueError,'Review changed Quantum arithmetic source'):
            source_specs(lambda path:load(path)+'\nUnreviewed source change.')
        self.assertTrue(BOOK['partial'])
        self.assertIn('remaining book',BOOK['reading_introduction'])
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            reading.Chapter('',{}).inline(normalize(r'\unreviewedcommand{lost prose}'))

    def test_published_math_proofs_tables_figures_and_source_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            documents=dict(files=list(reader.records.values()))
            with patch.object(reading,'BOOKS',{WORK:BOOK}),patch.object(reading,'CHAPTERS',CHAPTERS):
                total=check_readable_chapter(output,documents,pages)
            self.assertEqual(total,638)
            nodes=[n for _,_,chapter in reader.readable_books[WORK]['chapters'] for n in chapter.nodes]
            statements=[n for n in nodes if n['kind']=='theorem']
            proofs=[n for n in nodes if n['kind']=='proof']
            self.assertEqual([n['number'] for n in statements],['QA'+str(i).zfill(2) for i in range(1,21)])
            self.assertEqual(len(proofs),20)
            self.assertTrue(all(r'\(\square\)' in n['body'] for n in proofs))
            raw=(ROOT/DATA['selected_sources'][0]).read_text(encoding='utf-8')
            expected=[raw.count('\n',0,m.start())+1 for m in re.finditer(r'\\subsection\*\{Theorem QA\d\d\. ',raw)]
            self.assertEqual([n['line'] for n in statements],expected)
            self.assertEqual(sum(n['kind']=='figure' for n in nodes),20)
            self.assertEqual(len(reader.images),20)
            self.assertEqual(sum(n['kind'] in {'longtable','tabular'} for n in nodes),4)
            directory=reading.statement_directory_url(BOOK)
            self.assertIn('in this HTML selection',(output/directory).read_text(encoding='utf-8'))
            chapters=[(s['url'],(output/s['url']).read_text(encoding='utf-8')) for s in CHAPTERS]
            result=check_directory((output/directory).read_text(encoding='utf-8'),chapters,directory)
            self.assertEqual(result['proof_links'],20)
            for spec in CHAPTERS:
                markup=(output/spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size',markup)
                self.assertIn('Switch work',markup)
                self.assertIn('Original TeX with line links',markup)
            for record in reader.images.values():
                self.assertIn(record['file_url'],{p.relative_to(output).as_posix() for p in output.rglob('*.png')})


if __name__=='__main__':unittest.main()
