#!/usr/bin/env python3
"""Check frozen archives, historical source hashes, and the extracted sources.

This is an integrity and lexical audit. It does not compile Lean, inspect a
kernel environment, or reproduce an imported axiom dependency audit.
"""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
import hashlib, json, re, shutil
from build_concordance import strip_comments
ROOT=Path(__file__).resolve().parents[1]
FONTS={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.ttc'}

def sha(data: bytes) -> str:return hashlib.sha256(data).hexdigest()

def main() -> None:
    records=json.loads((ROOT/'audit/source_archives.json').read_text())
    archives=[]
    for rec in records:
        p=ROOT/'evidence/archives'/rec['name']
        actual=sha(p.read_bytes())
        if actual!=rec['sha256']:raise RuntimeError(f'Archive hash mismatch: {p.name}')
        with ZipFile(p) as z:
            bad=z.testzip()
            fonts=[n for n in z.namelist() if Path(n).suffix.lower() in FONTS]
            if bad or fonts:raise RuntimeError(f'Archive integrity/font failure: {p.name}: {bad}, {fonts}')
            archives.append({'name':p.name,'sha256':actual,'bytes':p.stat().st_size,'entries':len(z.infolist()),'crc_pass':True,'font_files':fonts})
    trees=[]
    for tree,archive,replay in [
        ('foundations_v020','Komorebi_Space_Lean_v0.20.0.zip','Komorebi_Space_Lean_v0.20.0_REPLAY_EVIDENCE.zip'),
        ('moving_v032','Komorebi_Moving_Exact_Spaces_v0.32.0.zip','Komorebi_Moving_Exact_Spaces_v0.32.0_REPLAY_EVIDENCE.zip')]:
        root=ROOT/'evidence'/tree
        with ZipFile(ROOT/'evidence/archives'/archive) as z:
            src={n.split('/',1)[1]:z.read(n) for n in z.namelist() if (n.endswith('.lean') and (n.split('/',1)[1].startswith('KomorebiSpace/') or n.split('/',1)[1]=='KomorebiSpace.lean'))}
        with ZipFile(ROOT/'evidence/archives'/replay) as z:
            cmp=json.loads(z.read(next(n for n in z.namelist() if n.endswith('COMPARISON.json'))))
        # These independent replay records identify the historical exact source bytes.
        hashes=cmp.get('source_sha256',{})
        if not hashes:
            # The focused comparison keeps per-file values in its comparison list/map.
            for k,v in cmp.items():
                if k=='source_hashes' and isinstance(v,dict): hashes=v
        verified=0;forbidden=[];missing_imports=[]
        for rel,data in src.items():
            p=root/rel
            if not p.is_file() or p.read_bytes()!=data:raise RuntimeError(f'Extracted source differs: {tree}/{rel}')
            if rel in hashes:
                if hashes[rel]!=sha(data):raise RuntimeError(f'Historical replay hash mismatch: {rel}')
                verified+=1
            code=strip_comments(data.decode())
            # Strings are excluded from lexical declaration scans.
            code=re.sub(r'"(?:\\.|[^"\\])*"','""',code)
            for m in re.finditer(r'\b(?:sorry|admit|native_decide)\b|^\s*(?:axiom|unsafe)\b',code,re.M):
                forbidden.append({'file':rel,'line':code.count('\n',0,m.start())+1,'token':m.group(0).strip()})
            for imp in re.findall(r'^import\s+(KomorebiSpace(?:\.[\w]+)*)',code,re.M):
                target=imp.replace('.','/')+'.lean'
                if target not in src:missing_imports.append({'file':rel,'import':imp})
        if forbidden or missing_imports:raise RuntimeError(f'Source scan failed: {tree}: {forbidden}, {missing_imports}')
        trees.append({'tree':tree,'production_modules':len(src)-1,'sources_including_root':len(src),
                      'all_sources_match_frozen_archive':True,'direct_historical_replay_hash_matches':verified,
                      'local_import_closure_complete':True,'lexical_forbidden_hits':forbidden,
                      'historical_comparison_status':cmp.get('status'),
                      'historical_record_is_not_a_current_execution':True})
    selected=ROOT/'evidence/selected/HilbertHolonomyRepair.lean'
    result={'status':'PASS','executed_utc':datetime.now(timezone.utc).isoformat(),'archives':archives,'trees':trees,
            'separate_source':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected.read_bytes()),'compilation_scope':'Recorded separately in audit/formal/release.json'},
            'lean_in_path':shutil.which('lean'),'fresh_lean_compilation':'NOT RUN BY THIS INTEGRITY SCRIPT',
            'limits':['A lexical scan is not an axiom dependency audit.','Imported mathlib and compiler are not rebuilt here.','Canonical compilation and imported axiom auditing are separate records, not results of this integrity check.']}
    (ROOT/'audit/source_integrity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
