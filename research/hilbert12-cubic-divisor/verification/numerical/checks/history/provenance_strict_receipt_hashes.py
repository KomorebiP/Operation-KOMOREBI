"""Read-only archived manifest, receipt and extracted-chain integrity checks."""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, subprocess, sys, zipfile

ap = argparse.ArgumentParser()
ap.add_argument("--release", type=Path, required=True)
ap.add_argument("--result", type=Path, required=True)
args = ap.parse_args()
release = args.release.resolve()
workspace = Path.cwd()
validator = Path(__file__).resolve().parents[1] / 'runner/validate_manifest.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(root, name):
    p = (root / name).resolve()
    if not p.is_relative_to(root.resolve()): raise AssertionError(f'escaping recorded path {name}')
    return p
manifest_rows, receipt_rows, zip_rows, pinned_rows = [], [], [], []
for p in sorted((release/'sources').rglob('*.json')):
    j = json.loads(p.read_text())
    if p.name.lower() == 'manifest.json' or p.name in {'exact_manifest.json', 'numerical_manifest.json'}:
        root = p.parent.parent if p.parent.name=='evidence' else p.parent
        entries = j.get('outputs', j.get('files', []))
        for e in entries:
            f = resolve(root, e['path'])
            assert f.is_file() and sha(f) == e['sha256'], (str(p), e['path'])
            if 'bytes' in e: assert f.stat().st_size == e['bytes']
        validate = None
        if j.get('schema_version') == 1:
            run = subprocess.run([sys.executable, str(validator), str(p), '--root', str(root)], capture_output=True, text=True, timeout=30)
            assert run.returncode == 0, (str(p), run.stdout, run.stderr)
            validate = run.stdout.strip()
        input_count = 0
        for e in j.get('mathematics', {}).get('inputs', []) + j.get('input_artifacts', []):
            if isinstance(e, dict) and 'path' in e and 'sha256' in e:
                f = resolve(root, e['path']); assert f.is_file() and sha(f) == e['sha256']
                if 'sha256_after' in e: assert sha(f) == e['sha256_after']
                input_count += 1
        manifest_rows.append({'path':str(p.relative_to(release)), 'manifest_sha256':sha(p), 'output_records_verified':len(entries), 'pinned_inputs_verified':input_count, 'schema':j.get('schema_version',j.get('format')), 'validator_message':validate, 'result':'PASS'})
    if p.name in {'replay_receipt.json', 'extraction_replay.json'}:
        root = p.parent.parent
        count = 0; verified=[]; fallbacks=[]
        for key in ['files','source_hashes','output_hashes','outputs']:
            files=j.get(key,{})
            if isinstance(files,dict):
                for name,digest in files.items():
                    if isinstance(digest,str) and len(digest)==64:
                        f=resolve(root,name)
                        if not f.is_file() and key=='output_hashes' and '/' not in name:
                            matches=list(root.rglob(name));assert len(matches)==1,(str(p),name,matches)
                            f=matches[0];fallbacks.append({'recorded':name,'resolved':str(f.relative_to(root)),'reason':'Unique bare-name output in legacy receipt'})
                        assert sha(f)==digest
                        count+=1;verified.append(name)
        for key in ['checks','source_hashes_unchanged']:
            entries=j.get(key,[])
            if isinstance(entries,list):
                for e in entries:
                    if isinstance(e,dict) and 'sha256' in e:
                        name=e.get('path',e.get('file'))
                        if 'path' in e:f=resolve(root,name)
                        else:
                            matches=list(root.rglob(name));assert len(matches)==1,(str(p),name,matches)
                            f=matches[0]
                        assert sha(f)==e['sha256'];count+=1;verified.append(str(f.relative_to(root)))
        receipt_rows.append({'path':str(p.relative_to(release)), 'sha256':sha(p), 'mapped_file_hashes_verified':count,'verified_paths':verified,'resolution_fallbacks':fallbacks,'historical_execution_claims_not_freshly_authenticated':True,'full_inherited_replay':j.get('full_inherited_replay'),'result':'PASS'})
intake = json.loads((release/'provenance/ARCHIVE_INTAKE.json').read_text())
for row in intake['original_downloads']:
    p = release/'provenance'/row['file']
    assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
    with zipfile.ZipFile(p) as z: assert z.testzip() is None
    pinned_rows.append({'file':str(p.relative_to(release)),'sha256':sha(p),'bytes':p.stat().st_size,'result':'PASS'})
for index,row in enumerate(intake['source_chain'],1):
    p = workspace/row['archive']; assert sha(p)==row['sha256']
    targets = list((release/'sources/continuation_chain'/f'{index:02}').iterdir()); assert len(targets)==1
    target = targets[0]
    count=0
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        for entry in z.infolist():
            if entry.is_dir(): continue
            parts=PurePosixPath(entry.filename).parts
            assert '..' not in parts and len(parts)>1
            local = target.joinpath(*parts[1:])
            assert local.is_file() and local.read_bytes()==z.read(entry), (index,entry.filename)
            count+=1
    zip_rows.append({'chain_index':index,'archive_sha256':row['sha256'],'crc_test':'PASS','extracted_file_payloads_verified':count,'target':str(target.relative_to(release)),'result':'PASS'})
out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS','source_manifests':manifest_rows,'historical_receipts':receipt_rows,'intake_archives':pinned_rows,'continuation_archives':zip_rows,'limits':['Legacy v1 hashes and current files are verified; old runtime/command claims are historical records, not execution attestation.','No historical mathematical theorem or arithmetic equality follows from a hash match.','Old Lean replay is not reexecuted by this Python provenance check.']}
args.result.write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(manifest_rows),'source/evidence manifests;',sum(r['output_records_verified'] for r in manifest_rows),'output hashes;',len(receipt_rows),'receipts;',len(zip_rows),'chain archives')
