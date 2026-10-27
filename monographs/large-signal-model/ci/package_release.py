#!/usr/bin/env python3
"""Package only verified distribution files, including the .github directory."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(source: Path) -> tuple[str, dict]:
    manifest_path=source/'DISTRIBUTION_MANIFEST.json'
    manifest=json.loads(manifest_path.read_text())
    version=manifest['version']
    counts=json.loads((source/'Lean/RELEASE_COUNTS.json').read_text())
    if version!=counts['release'] or version!='1.0.0':
        raise ValueError('Release version does not match the checked Lean source')
    for name,record in manifest['files'].items():
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts or '.git' in rel.parts:
            raise ValueError('Invalid distribution path: '+name)
        p=source/rel
        if not p.is_file() or p.is_symlink() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:
            raise ValueError('Missing or changed distribution file: '+name)
    for name,record in json.loads((source/'Lean/MANIFEST.json').read_text())['files'].items():
        p=source/'Lean'/name
        if not p.is_file() or sha(p)!=record['sha256'] or p.stat().st_size!=record['bytes']:
            raise ValueError('Checked Lean payload changed: '+name)
    report=json.loads((source/'Lean/verification/current/report.json').read_text())
    status=json.loads((source/'Lean/CURRENT_STATUS.json').read_text())
    coverage=json.loads((source/'Lean/COVERAGE.json').read_text())
    if not (report['passed'] and report['complete'] and status['verification_passed'] and status['goal_reached']):
        raise ValueError('Mathematical execution is not accepted')
    if status['verification_report_sha256']!=sha(source/'Lean/verification/current/report.json'):
        raise ValueError('Execution receipt identity changed')
    if coverage['complete']!=list(range(1,88)) or coverage['partial'] or coverage['not_formalized_count']:
        raise ValueError('Incomplete proposition coverage')
    for name,h in report['source_snapshot'].items():
        if sha(source/'Lean'/name)!=h:
            raise ValueError('Accepted proof or verifier input changed: '+name)
    if not any(n.startswith('.github/workflows/') for n in manifest['files']):
        raise ValueError('GitHub workflows are missing from the distribution')
    return version,manifest

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();source=args.source.resolve();out=args.out.resolve()
    version,manifest=verify(source)
    out.mkdir(parents=True,exist_ok=True)
    filename=f'Large_Signal_Model_Final_GitHub_Release_{version}.zip'
    target=out/filename
    # A fixed member time and mode make the same checked payload reproducible.
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted([*manifest['files'],'DISTRIBUTION_MANIFEST.json']):
            p=source/name
            info=zipfile.ZipInfo('Large_Signal_Model/'+name,date_time=(1980,1,1,0,0,0))
            info.create_system=3
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=((0o100755 if p.suffix=='.sh' else 0o100644)<<16)
            archive.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise ValueError('ZIP integrity check failed')
        expected={'Large_Signal_Model/'+n for n in manifest['files']}|{'Large_Signal_Model/DISTRIBUTION_MANIFEST.json'}
        if set(archive.namelist())!=expected or len(archive.namelist())!=len(expected):
            raise ValueError('ZIP inventory does not match the distribution')
        if not any('/.github/workflows/' in n for n in archive.namelist()):
            raise ValueError('Hidden GitHub directory was omitted')
    (out/'SHA256SUMS.txt').write_text(sha(target)+'  '+filename+'\n')
    assets={'version':version,'files':[filename,'SHA256SUMS.txt']}
    (out/'assets.json').write_text(json.dumps(assets,indent=2)+'\n')
    print(json.dumps({'passed':True,'archive':str(target),'sha256':sha(target),'bytes':target.stat().st_size,'members':len(expected),'github_directory_included':True}))

if __name__=='__main__':main()
