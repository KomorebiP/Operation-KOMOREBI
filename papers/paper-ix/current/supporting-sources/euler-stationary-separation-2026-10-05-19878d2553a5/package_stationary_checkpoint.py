#!/usr/bin/env python3
"""Save current stationary-separation evidence with immutable ancestry."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parent
NAME='Euler_Stationary_Separation_2026-10-05'
DEST=ROOT/NAME
PARENT='Euler_Bernoulli_Structure_2026-10-05.zip'
PARENT_SHA='b1dd12d9e0904b7d9a0b999e961fd1b12b4e3afde71995da4064d7849cdfacf7'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    assert sha(ROOT/PARENT)==PARENT_SHA
    evidence=json.loads((ROOT/'stationary_separation/CURRENT_EVIDENCE.json').read_text())
    assert evidence['parent_sha256']==PARENT_SHA
    if DEST.exists():
        raise SystemExit('Refusing to overwrite a checkpoint.')
    DEST.mkdir()
    ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store')
    for directory in ['stationary_separation','bernoulli_closure','audit_helpers',
                      'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04',
                      'shifted_obstruction','next/unit_identity']:
        shutil.copytree(ROOT/directory,DEST/directory,ignore=ignore)
    shutil.copy2(ROOT/PARENT,DEST/PARENT)
    shutil.copy2(Path(__file__),DEST/'package_stationary_checkpoint.py')
    records=[]
    for run in evidence['current_runs']:
        result=subprocess.run([sys.executable,str(DEST/'audit_helpers/validate_manifest.py'),
            str(DEST/run['manifest']),'--root',str(DEST/run['execution_root'])],
            capture_output=True,text=True)
        records.append({'manifest':run['manifest'],'execution_root':run['execution_root'],
                        'returncode':result.returncode,'output':(result.stdout+result.stderr).strip()})
        if result.returncode:
            raise SystemExit(json.dumps(records[-1],indent=2))
    for group in ['proofs','reviews']:
        for relative,expected in evidence[group].items():
            assert sha(DEST/relative)==expected,relative
    (DEST/'PACKAGE_CHECK.json').write_text(json.dumps({'status':'passed','checks':records},indent=2)+'\n')
    (DEST/'README.txt').write_text('Euler stationary separation checkpoint, 2026-10-05\n\n'
        'The original Euler simplicity goal remains open.\n'
        'Read stationary_separation/README.md and SYNTHESIS.md first.\n'
        'The full immutable parent archive is included. Current computation dependencies\n'
        'are also extracted. Superseded runs are explicitly excluded from current evidence.\n'
        'Run python3 verify_checkpoint.py from this extracted directory.\n')
    reproduce=['# Reproduce the stationary-separation checkpoint\n',
        'Python 3.12 and standard-library arithmetic suffice. Run from the extracted root.\n',
        'Verify all saved bytes and current manifests with `python3 verify_checkpoint.py`.\n',
        'Current runs are listed in `stationary_separation/CURRENT_EVIDENCE.json`.\n',
        'The commands below write fresh replay files. They do not overwrite saved evidence.\n']
    for index,run in enumerate(evidence['current_runs'],1):
        data=json.loads((DEST/run['manifest']).read_text())
        command=data['command'][:];command[0]='python3';command[2]=f'replay_{index:02d}.json'
        reproduce+=['Working directory: `'+run['execution_root']+'`.',
                    '```bash\n'+' '.join(command)+'\n```\n']
    reproduce+=['Inherited proofs and historical runs retain their original status. The parent\n'
        'ZIP is included unchanged and can be extracted separately for its full context.\n'
        'The new actual convergence theorem and quadratic reduction do not establish\n'
        'the remaining nonvanishing assertion.\n']
    (DEST/'REPRODUCE.md').write_text('\n'.join(reproduce))
    verifier='''#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parent
hashes=json.loads((root/'SOURCE_HASHES.json').read_text())
for relative,expected in hashes.items():
    with (root/relative).open('rb') as stream:
        actual=hashlib.file_digest(stream,'sha256').hexdigest()
    if actual!=expected: raise SystemExit('Hash mismatch: '+relative)
evidence=json.loads((root/'stationary_separation/CURRENT_EVIDENCE.json').read_text())
for run in evidence['current_runs']:
    result=subprocess.run([sys.executable,str(root/'audit_helpers/validate_manifest.py'),
       str(root/run['manifest']),'--root',str(root/run['execution_root'])],
       capture_output=True,text=True)
    if result.returncode: raise SystemExit(result.stdout+result.stderr)
print(str(len(hashes))+' files and '+str(len(evidence['current_runs']))+' current manifests verified.')
'''
    (DEST/'verify_checkpoint.py').write_text(verifier)
    hashes={str(path.relative_to(DEST)):sha(path) for path in sorted(DEST.rglob('*')) if path.is_file()}
    (DEST/'SOURCE_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n')
    result=subprocess.run([sys.executable,str(DEST/'verify_checkpoint.py')],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    archive=ROOT/(NAME+'.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for path in sorted(DEST.rglob('*')):
            if path.is_file():bundle.write(path,str(path.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        members=len(bundle.namelist())
    payload={'checkpoint':evidence['checkpoint'],'path':str(archive),'sha256':sha(archive),
             'bytes':archive.stat().st_size,'files':members,'validation':result.stdout.strip(),
             'original_goal_status':'open'}
    (ROOT/'STATIONARY_FINAL_ARTIFACT.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2))

if __name__=='__main__':main()
