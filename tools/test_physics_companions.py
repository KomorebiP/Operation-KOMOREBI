"""Coverage and publication controls for Physics verification reading editions."""
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from check_reader_site import Page
from physics_companions import metadata,source_specs,scope_pages,verify,REPORT,INDEX,SCOPE,article_identity
from test_physics_reading import ROOT,publish_fixture


class PhysicsCompanionTests(unittest.TestCase):
    def test_table_spacing_preserves_mathematical_arrays(self):
        from physics_companions import presentation_table
        raw=r'A & value\\[3pt] B & \(M=\begin{pmatrix}1&0\\[3pt]0&1\end{pmatrix}\)'
        rendered=presentation_table(dict(body=raw))['body']
        self.assertEqual(rendered.count('[3pt]'),1)
        self.assertIn(r'1&0\\[3pt]0&1',rendered)
        self.assertIn(r'A & value\\ B',rendered)

    def test_complete_inclusion_order_and_rejected_source_changes(self):
        data=metadata();load=lambda p:(ROOT/p).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load),data)
        self.assertEqual(len(data['pages']),70)
        for path in data['inputs']:
            with self.assertRaisesRegex(ValueError,'changed Physics companion source'):
                source_specs(lambda p:load(p)+('changed' if p==path else ''))
        altered=copy.deepcopy(data);altered['pages'][1]['start_line']+=1
        with patch('physics_companions.metadata',return_value=altered),self.assertRaisesRegex(ValueError,'gap or overlap'):
            source_specs(load)
        main=data['companions'][0]['main'];raw=load(main).replace(r'\end{document}','Unselected prose.\n'+r'\end{document}')
        altered=copy.deepcopy(data);altered['inputs'][main]=hashlib.sha256(raw.encode()).hexdigest()
        with patch('physics_companions.metadata',return_value=altered),self.assertRaisesRegex(ValueError,'Unselected Physics companion'):
            source_specs(lambda p:raw if p==main else load(p))
        # Keep the centered appendix before the Dirac companion's final sections.
        altered=copy.deepcopy(data);fragments=altered['companions'][1]['fragments'];fragments[1],fragments[2]=fragments[2],fragments[1]
        with patch('physics_companions.metadata',return_value=altered),self.assertRaisesRegex(ValueError,'inclusion coverage'):
            source_specs(load)

    def test_pdf_transcription_and_reading_controls(self):
        data=metadata();raw=(ROOT/SCOPE).read_bytes()
        self.assertEqual(len(scope_pages(raw,data)),3)
        self.assertIn('2.63 × 10²⁰',data['scope_pages'][2]['sections'][0]['text'])
        altered=copy.deepcopy(data);altered['scope_pages'][2]['sections'][0]['text']=altered['scope_pages'][2]['sections'][0]['text'].replace('2.63','2.64')
        with self.assertRaisesRegex(ValueError,'scope transcription'):scope_pages(raw,altered)
        with self.assertRaisesRegex(ValueError,'scope PDF'):scope_pages(raw+b'changed',data)
        from reader_display import edition
        self.assertEqual(len(edition(INDEX)['chapters']),73)
        self.assertIsNone(edition('read/monographs-physics/verification/unknown.html'))
        for page in data['scope_pages']+data['pages']:self.assertEqual(edition(page['url'])['index'],INDEX)

    def test_publication_math_prose_commands_and_evidence_boundaries(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=publish_fixture(output)
            documents=dict(files=list(reader.records.values()),source_revision=reader.site.revision)
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            result=verify(output,documents,pages)
            self.assertEqual((result['companions'],result['pages'],result['scope_pages']),(5,73,3))
            report=json.loads((output/REPORT).read_bytes())
            self.assertEqual(len([n for row in report['html_pages'] for n in row['nodes'] if n['kind'] in {'longtable','tabular'}]),16)
            for row in report['html_pages']:
                markup=(output/row['url']).read_text(encoding='utf-8')
                self.assertNotIn('\\mbox',markup)
                self.assertNotIn('[3pt]',markup)
                self.assertNotIn('[2pt]',markup)
                self.assertIn('reading-text-size',markup)
            first=output/report['html_pages'][0]['url'];original=first.read_text(encoding='utf-8')
            changed=original.replace('not a fresh kernel run','a fresh kernel run',1)
            self.assertNotEqual(changed,original);first.write_text(changed,encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Changed Physics companion article'):verify(output,documents,pages)
            first.write_text(original,encoding='utf-8')
            # A changed expression must fail even if the article receipt is replaced.
            row=next(row for row in report['html_pages'] if row['math_expressions'])
            path=output/row['url'];original=path.read_text(encoding='utf-8')
            changed=re.sub(r'(<span class="arithmatex">\\\()','\\g<1>1+',original,count=1)
            self.assertNotEqual(changed,original);path.write_text(changed,encoding='utf-8')
            saved=row['article_sha256'];row['article_sha256']=article_identity(changed)
            (output/REPORT).write_text(json.dumps(report),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Changed Physics companion math'):verify(output,documents,pages)
            row['article_sha256']=saved;path.write_text(original,encoding='utf-8')
            (output/REPORT).write_text(json.dumps(report),encoding='utf-8')
            contents=(output/'read/monographs-physics/index.html').read_text(encoding='utf-8')
            self.assertEqual(contents.count('Read verification material in HTML'),6)
            self.assertIn('verification/index.html',contents)
            self.assertEqual(len(json.loads((output/'documents/readable-chapters.json').read_bytes())),160)
            scope=(output/metadata()['scope_pages'][2]['url']).read_text(encoding='utf-8')
            self.assertIn('10<sup>20</sup>',scope)
            subheading=(output/'read/monographs-physics/verification/foundations-01.html').read_text(encoding='utf-8')
            self.assertRegex(subheading,r'<h3 id="L[0-9]+">Three kinds of statement</h3>')


if __name__=='__main__':unittest.main()
