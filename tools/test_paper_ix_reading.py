"""Source-preservation checks for the opening Paper IX reading edition."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import readable_chapters as reading
from claim_navigation import statements
from paper_ix_reading import CHAPTERS, MAIN, source_references
from reader_documents import page_path

ROOT=Path(__file__).resolve().parents[1]


class PaperIXReadingTests(unittest.TestCase):
    def reader(self):
        records={}
        def add(path,label=None):
            if not (ROOT/path).is_file(): return None
            raw=(ROOT/path).read_bytes()
            import hashlib
            records[path]=dict(url=page_path('paper-ix',path),format='source',work='paper-ix',
                title=label or path,file_url='files/'+path,sha256=hashlib.sha256(raw).hexdigest(),path=path)
            return records[path]
        site=SimpleNamespace(root=ROOT,read_source=lambda record:(ROOT/record['path']).read_bytes())
        reader=SimpleNamespace(add=add,records=records,site=site,primary_pdf=lambda work:dict(url='paper.pdf'),claims_by_source={})
        add(MAIN)
        for spec in CHAPTERS:
            record=add(spec['source'])
            reader.claims_by_source[spec['source']]=statements(
                site.read_source(record).decode('utf-8-sig'),spec['source'],'paper-ix',record['sha256'])
        return reader

    def test_opening_chapters_preserve_math_proofs_and_lean_names(self):
        reader=self.reader()
        with patch.dict(reading.BOOKS,{'paper-ix':reading.BOOKS['paper-ix']},clear=True):
            reading.prepare(reader)
        book=reader.readable_books['paper-ix']
        total_proofs=0
        for spec,raw,chapter in book['chapters']:
            rendered=''
            for node in chapter.nodes:
                rendered+=chapter.inline(node['title'])+chapter.paragraphs(node['body'])
                total_proofs+=node['kind']=='proof'
            self.assertEqual(chapter.math,reading.original_math(raw.decode('utf-8-sig')))
            self.assertNotIn('\\lean{',rendered)
            if '10_foundations' in spec['source']:
                self.assertIn('<code>ResiduePackets.packet_reconstruction</code>',rendered)
                self.assertIn('Historical material and interface work (source)',rendered)
        self.assertGreater(total_proofs,8)
        # Every indexed statement and adjacent proof has its original line anchor.
        for spec,raw,chapter in book['chapters']:
            nodes={node['line']:node for node in chapter.nodes}
            for row in reader.claims_by_source[spec['source']]:
                self.assertIn(row['statement_line'],nodes)
                if row['proof_line']: self.assertEqual(nodes[row['proof_line']]['kind'],'proof')

    def test_forward_links_reject_changed_source_headings(self):
        reader=self.reader(); config=reading.BOOKS['paper-ix']
        refs=source_references(reader,config)
        for key,path,kind,title in config['source_references']:
            line=int(refs[key]['id'][1:])
            self.assertIn('\\'+kind+'{'+title+'}',(ROOT/path).read_text(encoding='utf-8-sig').splitlines()[line-1])
        read=reader.site.read_source
        reader.site.read_source=lambda record:read(record).replace(b'Analytic regularity of the local solution map',b'Changed heading')
        with self.assertRaisesRegex(ValueError,'forward reference: sec:regularity'):
            source_references(reader,config)

    def test_new_syntax_still_requires_explicit_support(self):
        with self.assertRaisesRegex(ValueError,'Unsupported prose command'):
            reading.Chapter('',{}).paragraphs(r'Kept text. \unknowncommand{must not disappear}')


if __name__=='__main__': unittest.main()
