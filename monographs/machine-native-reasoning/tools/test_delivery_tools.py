#!/usr/bin/env python3
"""Small positive and rejection fixtures for delivery mechanics, not proof truth."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zipfile
sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, BASE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

vp, rr = load('verify_package'), load('restore_runtime')

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'x.txt').write_bytes(b'original\n')
        self.data = {'schema': vp.SCHEMA, 'files': [
            {'path':'x.txt', 'bytes':9, 'sha256':hashlib.sha256(b'original\n').hexdigest()}]}
        self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):(self.root / 'MANIFEST.json').write_text(json.dumps(self.data))
    def bad(self):
        self.save()
        with self.assertRaises((ValueError, OSError)):vp.verify(self.root)
    def test_valid(self):self.assertEqual(vp.verify(self.root)['payload_files'], 1)
    def test_changed_bytes(self):(self.root/'x.txt').write_bytes(b'altered!\n');self.bad()
    def test_missing_file(self):(self.root/'x.txt').unlink();self.bad()
    def test_extra_file(self):(self.root/'extra').write_bytes(b'x');self.bad()
    def test_duplicate_row(self):self.data['files'].append(dict(self.data['files'][0]));self.bad()
    def test_wrong_size(self):self.data['files'][0]['bytes']=8;self.bad()
    def test_boolean_size(self):self.data['files'][0]['bytes']=True;self.bad()
    def test_negative_size(self):self.data['files'][0]['bytes']=-1;self.bad()
    def test_bad_hash(self):self.data['files'][0]['sha256']='z'*64;self.bad()
    def test_wrong_schema(self):self.data['schema']='other';self.bad()
    def test_empty_inventory(self):self.data['files']=[];self.bad()
    def test_extra_entry_key(self):self.data['files'][0]['ignored']=True;self.bad()
    def test_traversal(self):self.data['files'][0]['path']='../x.txt';self.bad()
    def test_absolute(self):self.data['files'][0]['path']='/x.txt';self.bad()
    def test_backslash(self):self.data['files'][0]['path']='a\\x.txt';self.bad()
    def test_dot_component(self):self.data['files'][0]['path']='./x.txt';self.bad()
    def test_double_slash(self):self.data['files'][0]['path']='a//x.txt';self.bad()
    def test_colon(self):self.data['files'][0]['path']='C:x.txt';self.bad()
    def test_self_reference(self):self.data['files'][0]['path']='MANIFEST.json';self.bad()
    def test_symlink(self):
        (self.root/'x.txt').rename(self.root/'other')
        (self.root/'x.txt').symlink_to(self.root/'other');self.bad()

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.payload=b'fixture chunk';self.sha=hashlib.sha256(self.payload).hexdigest()
        self.parts=self.root/'parts';self.parts.mkdir();self.output=self.root/'combined.xz'
        self.make()
    def tearDown(self):self.tmp.cleanup()
    def make(self,name='lean-compact-01.chunk',extra=False):
        with zipfile.ZipFile(self.parts/'Lean_Compact_01.zip','w') as z:
            z.writestr(name,self.payload)
            if extra:z.writestr('other',b'x')
    def run_fixture(self,**kw):
        args={'chunks':[(len(self.payload),self.sha)],'total_bytes':len(self.payload),'total_sha':self.sha}
        args.update(kw)
        return rr.assemble(self.parts,self.output,**args)
    def test_valid(self):self.assertEqual(self.run_fixture()['status'],'PASS')
    def test_wrong_member(self):
        self.make('wrong')
        with self.assertRaises(ValueError):self.run_fixture()
    def test_extra_member(self):
        self.make(extra=True)
        with self.assertRaises(ValueError):self.run_fixture()
    def test_bad_chunk_hash(self):
        with self.assertRaises(ValueError):self.run_fixture(chunks=[(len(self.payload),'0'*64)])
    def test_bad_combined_hash(self):
        with self.assertRaises(ValueError):self.run_fixture(total_sha='0'*64)
    def test_bad_combined_length(self):
        with self.assertRaises(ValueError):self.run_fixture(total_bytes=1)
    def test_no_overwrite(self):
        self.output.write_bytes(b'kept')
        with self.assertRaises(FileExistsError):self.run_fixture()
        self.assertEqual(self.output.read_bytes(),b'kept')
    def test_extraction_traversal(self):
        archive=self.root/'bad.tar.xz'
        with tarfile.open(archive,'w:xz') as t:
            member=tarfile.TarInfo('../outside');member.size=1;t.addfile(member,io.BytesIO(b'x'))
        with self.assertRaises(ValueError):rr.extract(archive,self.root/'unpack')

if __name__=='__main__':unittest.main(verbosity=2)
