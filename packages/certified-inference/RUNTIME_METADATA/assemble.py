#!/usr/bin/env python3
"""Reassemble the compact offline Lean ZIP parts, checking every byte by SHA-256."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, zipfile

def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parts',type=Path,default=Path.cwd(),help='Folder containing all compact ZIP parts')
    parser.add_argument('--extract',action='store_true',help='Also extract using tar and the appropriate decompressor (Linux/WSL)')
    parser.add_argument('--verify-only',action='store_true',help='Check all part contents without creating another large file')
    args=parser.parse_args()
    manifest=json.loads(Path(__file__).with_name('parts.json').read_text())
    folder=args.parts.resolve()
    # Preflight every input before writing output.
    for part in manifest['parts']:
        if not (folder/part['zip']).is_file():raise RuntimeError('Missing part: '+part['zip'])
    output=folder/manifest['archive']
    temporary=output.with_suffix(output.suffix+'.assembling')
    if not args.verify_only and output.exists():
        raise RuntimeError('Output already exists. Move it aside or use --verify-only: '+str(output))
    if not args.verify_only and temporary.exists():
        raise RuntimeError('An earlier partial output exists. Move it aside before retrying: '+str(temporary))
    target=None
    try:
        if not args.verify_only:target=temporary.open('xb')
        combined=hashlib.sha256();total=0
        for part in manifest['parts']:
            h=hashlib.sha256();size=0
            with zipfile.ZipFile(folder/part['zip']) as archive:
                with archive.open(part['member']) as stream:
                    for block in iter(lambda:stream.read(4*1024*1024),b''):
                        combined.update(block);h.update(block);size+=len(block);total+=len(block)
                        if target:target.write(block)
            if size!=part['bytes'] or h.hexdigest()!=part['sha256']:
                raise RuntimeError('Corrupt part: '+part['zip'])
            print('PASS '+part['zip'],flush=True)
        if total!=manifest['bytes'] or combined.hexdigest()!=manifest['sha256']:
            raise RuntimeError('Combined archive integrity check failed')
        if target:
            target.close();target=None
            os.replace(temporary,output)
        print('PASS Complete archive SHA-256: '+combined.hexdigest(),flush=True)
    finally:
        if target:target.close()
    if args.extract:
        if args.verify_only:raise RuntimeError('--extract cannot be combined with --verify-only')
        destination=folder/manifest['root_folder']
        if destination.exists():raise RuntimeError('Extraction folder already exists; refusing to overwrite it: '+str(destination))
        subprocess.run(['tar','-xf',str(output),'-C',str(folder)],check=True)
        print('Ready. In '+str(destination)+', run: bash run.sh verify')

if __name__=='__main__':
    try:main()
    except Exception as error:
        print('FAILED: '+str(error),file=sys.stderr)
        sys.exit(1)
