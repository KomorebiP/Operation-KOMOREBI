"""Rebind final editorial sources to the unchanged mathematical environments."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'records/final_math_preservation.json'
d=json.loads(p.read_text())
shutil.copy2(p,ROOT/'records/final_math_preservation_pre_final04.json')
env=re.compile(r'\\begin\{(theorem|lemma|proposition|corollary|definition|proof|example|remark|claim)\}[\s\S]*?\\end\{\1\}')
display=re.compile(r'(?<!\\)\\\[[\s\S]*?(?<!\\)\\\]')
count=displays=0
with zipfile.ZipFile(d['parent_archive']) as z:
    for row in d['checked_files']:
        raw=(ROOT/'publication'/row['file']).read_bytes()
        s=raw.decode()
        old=z.read('Komorebi_Space_Publication_v1.14.0/'+row['file']).decode()
        a=[m.group(0) for m in env.finditer(s)]
        b=[m.group(0) for m in env.finditer(old)]
        assert a==b
        ds,do=display.findall(s),display.findall(old)
        assert ds==do
        assert len(a)==row['current_environment_count']
        assert len(ds)==row['display_count']
        row['current_sha256']=hashlib.sha256(raw).hexdigest()
        row['file_changed']=row['current_sha256']!=row['parent_sha256']
        count+=len(a);displays+=len(ds)
assert (count,displays)==(192,512)
d['recorded_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
d['stage']='Final_04 sources after all typesetting corrections'
d['previous_record']='records/final_math_preservation_pre_final04.json'
p.write_text(json.dumps(d,indent=2)+'\n')
print('PASS: 192 mathematical environments and 512 displays preserved.')
