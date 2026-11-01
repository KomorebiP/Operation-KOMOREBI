"""Publication gates reject stale sources and invalid accepted-run records."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from euler_case import RECORD, PREFIX, READER, checked_path, publish, verify_site
from build_reader_site import Site
from euler_navigation import PARTS, TAP_SECTION, decorate, headings


class EulerPublicationTests(unittest.TestCase):
    def fixture(self, folder, *, status='completed', wrong_input=False):
        root=Path(folder)/'source'
        output=Path(folder)/'site'
        root.mkdir(); output.mkdir()
        raw=b"print('Euler')\n"
        contents={
            'examples/euler_packets.py':raw,
            'docs/demonstrations/EULER_PACKETS.md':b'# Euler\n',
            'verification/euler-packets/run-007/fibonacci-transfer.csv':b'transform,row,column,value\nconnection,0,0,1\n',
            'verification/euler-packets/run-007/fibonacci-precision.csv':b'step,depth,modulus\n12,1,8\n',
            'verification/euler-packets/run-007/polynomial-calculus.csv':b'operator,row,column,value\nD,0,0,0\n',
            'verification/euler-packets/run-007/quartic-addresses.csv':b'address,index,value\n0,0,1\n',
            'verification/euler-packets/run-007/dyadic-inverse.csv':b'bits,index,residue\n0,0,0\n',
            'verification/euler-packets/run-007/euler-coordinate-atlas.csv':b'degree,euler,logarithmic\n0,1,1\n',
            'verification/euler-packets/run-007/dyadic-edge-tails.csv':b'r,N,tail_valuation\n1,1,3\n',
            'verification/euler-packets/run-007/results.json':b'{}\n',
            'verification/euler-packets/run-007/congruence-ladders.csv':b'chart,depth,modulus,residue\n3,0,9,8\n',
            'verification/euler-packets/run-007/coefficient-matrices.csv':b'transform,row,column,value\nlocal,0,0,1\n',
            'verification/euler-packets/run-007/local-reconstruction.csv':b'chart,depth,error\n2,4,0\n',
            'verification/euler-packets/run-007/euler-coefficients.csv':b'n,s\n0,1\n',
            'verification/euler-packets/run-007/power-polynomials.csv':b'n,r\n0,1\n',
            'verification/euler-packets/cross-check-007/results.json':b'{}\n',
        }
        digest=hashlib.sha256(raw).hexdigest()
        run=dict(run=dict(status=status,exit_status=0),input_artifacts=[
            dict(path='examples/euler_packets.py',sha256='0'*64 if wrong_input else digest,
                 sha256_after=digest)],outputs=[])
        for name in ('run-007','cross-check-007'):
            contents['verification/euler-packets/'+name+'/manifest.json']=json.dumps(run).encode()
        for path,content in contents.items():
            target=root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(content)
        record=dict(title='Euler example',work_ids=['paper-iv'],scope='Test fixture',
            accepted_runs=['verification/euler-packets/'+n+'/manifest.json' for n in ('run-007','cross-check-007')],
            files=[dict(path=p,sha256=hashlib.sha256(b).hexdigest()) for p,b in contents.items()])
        (root/RECORD).parent.mkdir(parents=True,exist_ok=True)
        (root/RECORD).write_text(json.dumps(record))
        (root/'LICENSE.md').write_text('Test license')
        pages={}
        def write(path,text):
            target=output/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        def page(path,title,body,source):
            pages[path]=body;write(path,body)
        binding=dict(record=RECORD,sha256=hashlib.sha256((root/RECORD).read_bytes()).hexdigest())
        site=SimpleNamespace(root=root,output=output,revision='a'*40,search=[],write=write,page=page,
            assessments={'euler-signal-bridge':{'worked_example':binding}})
        pages['collection/demonstrations/EULER_PACKETS.html']='Euler'
        return site,pages

    def test_bound_download_and_archive_then_tampered_download(self):
        with tempfile.TemporaryDirectory() as folder:
            site,pages=self.fixture(folder)
            publish(site)
            self.assertEqual(verify_site(site.output,pages),1)
            self.assertIn(READER,pages)
            (site.output/(PREFIX+'euler_packets.py')).write_bytes(b'changed')
            with self.assertRaises(AssertionError):verify_site(site.output,pages)

    def test_changed_source_cannot_publish(self):
        with tempfile.TemporaryDirectory() as folder:
            site,_=self.fixture(folder)
            (site.root/'examples/euler_packets.py').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'differs from its publication record'):publish(site)

    def test_noncompleted_run_cannot_publish(self):
        with tempfile.TemporaryDirectory() as folder:
            site,_=self.fixture(folder,status='timeout')
            with self.assertRaisesRegex(ValueError,'did not complete'):publish(site)

    def test_run_input_digest_must_match_actual_source(self):
        with tempfile.TemporaryDirectory() as folder:
            site,_=self.fixture(folder,wrong_input=True)
            with self.assertRaisesRegex(ValueError,'run input differs'):publish(site)

    def test_source_paths_stay_relative_and_canonical(self):
        for path in ('../escape','C:/escape','C:escape','/absolute','a\\b','a/../b','a/./b','.'):
            with self.subTest(path=path),self.assertRaises(ValueError):checked_path(path)

    def test_own_site_hostname_case_is_ignored_and_query_is_retained(self):
        site=Site.__new__(Site)
        site.repos={}
        self.assertEqual(site.resolve('collection','docs/demonstrations/EULER_PACKETS.md',
            'collection/demonstrations/EULER_PACKETS.html',
            'https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/results.json?v=1#data'),
            '../../downloads/euler-packets/results.json?v=1#data')

    def test_optional_tap_program_and_results_are_bound_and_published(self):
        with tempfile.TemporaryDirectory() as folder:
            site,pages=self.fixture(folder)
            record=json.loads((site.root/RECORD).read_bytes())
            program='examples/euler_polyphase_taps.py'
            result='verification/euler-packets/polyphase-taps-001/results.json'
            for path,raw in ((program,b"print('tap split')\n"),(result,b'{"status":"PASS"}\n')):
                target=site.root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                record['files'].append(dict(path=path,sha256=hashlib.sha256(raw).hexdigest()))
            record['tap_example']=dict(program=program,results=result)
            (site.root/RECORD).write_text(json.dumps(record))
            site.assessments['euler-signal-bridge']['worked_example']['sha256']=hashlib.sha256((site.root/RECORD).read_bytes()).hexdigest()
            publish(site)
            self.assertEqual(verify_site(site.output,pages),1)
            self.assertIn('read/euler-polyphase-taps.html',pages)
            self.assertIn('#split-an-fir-filter-into-polyphase-taps',pages['read/euler-polyphase-taps.html'])
            self.assertEqual((site.output/(PREFIX+'euler_polyphase_taps.py')).read_bytes(),b"print('tap split')\n")
            (site.output/(PREFIX+'polyphase-taps.json')).write_bytes(b'changed')
            with self.assertRaises(AssertionError):verify_site(site.output,pages)


class EulerNavigationTests(unittest.TestCase):
    def manuscript(self):
        sections=''.join('<h2 id="'+start+'">'+title+'</h2><p>Original text.</p>' for title,start in PARTS)
        return '<h1>Euler</h1><p><strong>Date</strong></p>'+sections.replace(
            '<h2 id="'+PARTS[4][1]+'">','<h2 id="'+TAP_SECTION+'">Tap split</h2><p>\\[x+y\\]</p><h2 id="'+PARTS[4][1]+'">')

    def test_guide_is_complete_closed_and_preserves_all_section_anchors(self):
        source=self.manuscript();result=decorate(source)
        self.assertEqual(headings(result),headings(source))
        self.assertEqual(result.count('Original text.'),len(PARTS))
        self.assertEqual(result.count('\\[x+y\\]'),1)
        self.assertEqual(result.count('class="euler-part-menu"'),7)
        self.assertEqual(result.count('class="euler-part-navigation"'),7)
        self.assertNotIn(' open',result)
        self.assertNotIn('<script',result)
        self.assertLess(result.index('<strong>Date</strong>'),result.index('id="euler-reading-guide"'))
        self.assertLess(result.index('id="euler-reading-guide"'),result.index('id="'+PARTS[0][1]+'"'))

    def test_missing_duplicate_and_reordered_section_anchors_fail_closed(self):
        source=self.manuscript()
        cases=(source.replace(PARTS[0][1],'missing'),source.replace(TAP_SECTION,'missing'),
               source+'<h2 id="'+PARTS[0][1]+'">Duplicate</h2>',
               source.replace(PARTS[0][1],'TEMP').replace(PARTS[1][1],PARTS[0][1]).replace('TEMP',PARTS[1][1]))
        for case in cases:
            with self.subTest(case=case[:80]),self.assertRaises(ValueError):decorate(case)

    def test_guide_links_have_real_destinations_and_titles_are_escaped(self):
        from check_reader_site import Page
        source=self.manuscript().replace('Original text.','Retained &amp; safe.')
        source=source.replace('Tap split</h2>','Tap &amp; split &lt;check&gt;</h2>')
        result=decorate(source);page=Page(result)
        self.assertIn('Tap &amp; split &lt;check&gt;',result)
        for link in page.links:
            self.assertTrue(link.startswith('#'))
            self.assertIn(link[1:],page.ids)


if __name__=='__main__':unittest.main()
