#!/usr/bin/env python3
"""Create one explicitly requested draft from verified versioned assets.
Default behavior prints the command. No credentials or arbitrary shell commands
are accepted; execution requires --execute and an existing GitHub CLI session.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
VERSION='1.0.0'
TAG='v1.0.0'

def validate_assets(directory: Path) -> list[Path]:
    directory=directory.resolve();manifest=json.loads((directory/'assets.json').read_text())
    if manifest.get('version')!=VERSION:raise ValueError('Asset version must be exactly 1.0.0.')
    names=manifest.get('files')
    if not isinstance(names,list) or not names or len(names)!=len(set(names)):raise ValueError('Invalid asset filename list.')
    paths=[]
    for name in names:
        if not isinstance(name,str) or Path(name).name!=name or '/' in name or chr(92) in name:
            raise ValueError('Release assets must be simple filenames under the asset directory.')
        path=(directory/name).resolve()
        if not path.is_relative_to(directory) or not path.is_file():raise ValueError(f'Missing or external release asset: {name}')
        paths.append(path)
    if 'SHA256SUMS.txt' not in names or not any(path.suffix=='.zip' for path in paths):
        raise ValueError('A versioned ZIP and SHA256SUMS.txt are required.')
    declared={}
    for line in (directory/'SHA256SUMS.txt').read_text().splitlines():
        if not line.strip():continue
        h,name=line.split(maxsplit=1);name=name.lstrip('*').strip()
        if not re.fullmatch(r'[0-9a-f]{64}',h) or name in declared:raise ValueError('Invalid checksum record.')
        declared[name]=h
    for path in paths:
        if path.name=='SHA256SUMS.txt':continue
        if declared.get(path.name)!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError(f'Asset checksum mismatch: {path.name}')
    return paths

def draft_command(repo: str,commit: str,paths: list[Path],notes: Path) -> list[str]:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Invalid owner/repository name.')
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})',commit):raise ValueError('A full verified Git commit is required.')
    return ['gh','release','create',TAG,*map(str,paths),'--repo',repo,'--target',commit,
            '--draft','--title','Large Signal Model 1.0.0','--notes-file',str(notes)]

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=Path('.'))
    ap.add_argument('--assets-dir',type=Path,required=True)
    ap.add_argument('--execute',action='store_true')
    args=ap.parse_args();source=args.source.resolve();assets=args.assets_dir.resolve()
    counts=json.loads((source/'Lean/RELEASE_COUNTS.json').read_text())
    if counts.get('release')!=VERSION:raise ValueError('Lean release metadata must be exactly 1.0.0.')
    repo=os.environ.get('GITHUB_REPOSITORY','');commit=os.environ.get('GITHUB_SHA','')
    paths=validate_assets(assets)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    if head!=commit:raise ValueError('The packaging checkout differs from the verified workflow commit.')
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=source,text=True)
    if dirty:raise ValueError('The release source tree is dirty; no draft was created.')
    tag=subprocess.run(['git','rev-parse','--verify',f'refs/tags/{TAG}^{{commit}}'],cwd=source,capture_output=True,text=True)
    exists=subprocess.run(['git','show-ref','--verify','--quiet',f'refs/tags/{TAG}'],cwd=source).returncode
    if exists not in (0,1):raise ValueError('Unable to inspect the existing release tag.')
    if exists==0 and (tag.returncode!=0 or tag.stdout.strip()!=commit):raise ValueError('Existing v1.0.0 tag does not resolve to the verified commit; it will not be moved.')
    notes=assets/'DRAFT_NOTES.md'
    text=(source/'RELEASE_NOTES.md').read_text() if (source/'RELEASE_NOTES.md').is_file() else 'Large Signal Model 1.0.0. See the bundled source, monograph and verification receipts.\n'
    server=os.environ.get('GITHUB_SERVER_URL','https://github.com');run_id=os.environ.get('GITHUB_RUN_ID','')
    if server=='https://github.com' and re.fullmatch(r'\d+',run_id):
        text+=f'\nFresh verification for this source commit: {server}/{repo}/actions/runs/{run_id}\n'
    notes.write_text(text)
    command=draft_command(repo,commit,paths,notes)
    if not args.execute:
        print(json.dumps({'execute':False,'command':command},indent=2));return 0
    # gh fails if a release already exists. No asset-clobber or tag-update path is provided.
    return subprocess.run(command,cwd=source).returncode
if __name__=='__main__':raise SystemExit(main())
