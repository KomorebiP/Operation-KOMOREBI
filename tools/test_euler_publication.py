"""Publication gates reject stale sources and invalid accepted-run records."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from euler_case import RECORD, PREFIX, READER, checked_path, publish, verify_site
from build_reader_site import Site


class EulerPublicationTests(unittest.TestCase):
    def fixture(self, folder, *, status='completed', wrong_input=False):
        root=Path(folder)/'source'
        output=Path(folder)/'site'
        root.mkdir(); output.mkdir()
        raw=b"print('Euler')\n"
        contents={
            'examples/euler_packets.py':raw,
            'docs/demonstrations/EULER_PACKETS.md':b'# Euler\n',
            'verification/euler-packets/run-003/results.json':b'{}\n',
            'verification/euler-packets/run-003/congruence-ladders.csv':b'chart,depth,modulus,residue\n3,0,9,8\n',
            'verification/euler-packets/run-003/coefficient-matrices.csv':b'transform,row,column,value\nlocal,0,0,1\n',
            'verification/euler-packets/run-003/local-reconstruction.csv':b'chart,depth,error\n2,4,0\n',
            'verification/euler-packets/run-003/euler-coefficients.csv':b'n,s\n0,1\n',
            'verification/euler-packets/run-003/power-polynomials.csv':b'n,r\n0,1\n',
            'verification/euler-packets/cross-check-003/results.json':b'{}\n',
        }
        digest=hashlib.sha256(raw).hexdigest()
        run=dict(run=dict(status=status,exit_status=0),input_artifacts=[
            dict(path='examples/euler_packets.py',sha256='0'*64 if wrong_input else digest,
                 sha256_after=digest)],outputs=[])
        for name in ('run-003','cross-check-003'):
            contents['verification/euler-packets/'+name+'/manifest.json']=json.dumps(run).encode()
        for path,content in contents.items():
            target=root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(content)
        record=dict(title='Euler example',work_ids=['paper-iv'],scope='Test fixture',
            accepted_runs=['verification/euler-packets/'+n+'/manifest.json' for n in ('run-003','cross-check-003')],
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


if __name__=='__main__':unittest.main()
