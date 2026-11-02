"""Repack pinned browser Lean assets into static, checksum-bound library bundles.

Inputs come from the reader workflow's pinned upstream checkout. Mathlib imports
are followed in the exact source revision recorded by its artifact manifest.
This packages existing artifacts; it does not compile or certify paper proofs.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import urllib.request

from lean_runner import imports, safe_path

UPSTREAM = 'a8aed095534e67061e2626b94e8e69193099091d'
LEAN = '62b6a2291302d4bbeace37642a066b7510d0145c'
MATHLIB = 'de3a9cf33016bbb6d15880d7680643f7ca2d25ba'
SEEDS = ['Mathlib.Data.Set.Function']
LIMIT = 8 * 1024 * 1024


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def pack(entries, output, prefix, identity):
    """Keep offsets and bytes explicit; no archive extraction occurs in browsers."""
    output.mkdir(parents=True, exist_ok=True)
    packs=[]; files=[]; raw=bytearray(); members=[]
    def flush():
        if not members:return
        name=f'{prefix}-{len(packs):03d}.pack'
        compressed=gzip.compress(raw, mtime=0)
        (output/name).write_bytes(compressed)
        packs.append(dict(file=name, bytes=len(raw), sha256=sha(compressed),
                          compressedBytes=len(compressed), entries=list(members)))
        raw.clear(); members.clear()
    for name, data in entries:
        safe_path(name)
        if raw and len(raw)+len(data)>LIMIT:flush()
        members.append(dict(path=name, offset=len(raw), bytes=len(data)))
        files.append(name); raw.extend(data)
    flush()
    return dict(**identity, files=files, packs=packs)


def mathlib_closure(archive):
    with tarfile.open(archive) as source:
        members={m.name.split('/',1)[-1]:m for m in source if m.isfile()}
        pending=list(SEEDS); found=set()
        while pending:
            name=pending.pop()
            if name in found:continue
            found.add(name)
            if not name.startswith('Mathlib.'):continue
            path=name.replace('.','/')+'.lean'
            if path not in members:raise ValueError('Missing Mathlib source: '+path)
            pending.extend(imports(source.extractfile(members[path]).read().decode('utf-8')))
    return found


def prepare(source, output, mathlib_archive):
    source=source/'public'
    output.mkdir(parents=True, exist_ok=True)
    upstream=json.loads((source/'lean-mathlib/real-analysis-layer.json').read_bytes())
    core=json.loads((source/'lean-wasm/core-layer.json').read_bytes())
    if upstream['leanCommit']!=LEAN or core['leanCommit']!=LEAN or upstream['mathlibCommit']!=MATHLIB:
        raise ValueError('Browser compiler and library build identities disagree')
    inventory={}
    def record(path):
        data=(source/path).read_bytes()
        inventory[path]=dict(size=len(data),sha256=sha(data))
        return data
    for p in sorted((source/'lean-wasm').rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(source).as_posix()
        target=output/rel;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(record(rel))
    for root in ('Std','Lean','Batteries'):
        paths=sorted((source/'lean-lib'/root).rglob('*'))
        paths=[p for p in paths if p.is_file() and p.name.endswith('.gz')]
        base=source/'lean-lib'/(root+'.olean.gz')
        if base.exists():paths.append(base)
        for ext in ('.ir.gz','.ir.sig.gz'):
            p=source/'lean-lib'/(root+ext)
            if p.exists():paths.append(p)
        def entries():
            for p in sorted(set(paths)):
                rel=p.relative_to(source).as_posix()
                yield p.relative_to(source/'lean-lib').as_posix()[:-3], gzip.decompress(record(rel))
        layer=pack(entries(),output/'lean-lib',root.lower(),dict(leanCommit=LEAN))
        if not layer['files']:raise ValueError('Empty library: '+root)
        write_json(output/'lean-lib'/(root+'-layer.json'),layer)
    selected=mathlib_closure(mathlib_archive)
    def entries():
        for item in upstream['packs']:
            blob=gzip.decompress(record('lean-mathlib/'+item['file']))
            if len(blob)!=item['bytes']:raise ValueError('Invalid upstream Mathlib pack')
            for entry in item['entries']:
                path=entry['path']
                name=path.removesuffix('.sig').removesuffix('.olean').removesuffix('.ir').replace('/','.')
                # The upstream Mathlib layer duplicates core, Lean, Std and Batteries.
                # Supply those once through the ordinary library packs instead.
                external=name.split('.')[0] not in {'Init','Lean','Std','Batteries','Mathlib'}
                if external or name in selected and name.startswith('Mathlib.'):
                    yield path,blob[entry['offset']:entry['offset']+entry['bytes']]
    layer=pack(entries(),output/'lean-mathlib','paper-imports',
               dict(leanCommit=LEAN,mathlibCommit=MATHLIB,version='komorebi-browser-pilot-1'))
    available={p[:-6].replace('/','.') for p in layer['files'] if p.endswith('.olean')}
    missing={n for n in selected if n.startswith('Mathlib.')}-available
    if missing:raise ValueError('Mathlib artifacts not in upstream layer: '+', '.join(sorted(missing)))
    write_json(output/'lean-mathlib/real-analysis-layer.json',layer)
    # A build input record also binds all generated bytes, so packaging is auditable.
    files={p.relative_to(output).as_posix():dict(size=p.stat().st_size,sha256=sha(p.read_bytes()))
           for p in sorted(output.rglob('*')) if p.is_file() and p.name!='SOURCE.json'}
    source_record=dict(schema=1,upstream=UPSTREAM,lean=LEAN,mathlib=MATHLIB,
                       mathlib_source_sha256=sha(mathlib_archive.read_bytes()),
                       mathlib_seeds=SEEDS,mathlib_modules=sorted(available),
                       inputs=inventory,files=files,bytes=sum(p['size'] for p in files.values()))
    write_json(output/'SOURCE.json',source_record)
    return source_record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mathlib-source',type=Path)
    args=parser.parse_args()
    archive=args.mathlib_source or args.output.parent/'mathlib-browser-source.tar.gz'
    if not archive.exists():
        archive.parent.mkdir(parents=True,exist_ok=True)
        urllib.request.urlretrieve('https://codeload.github.com/leanprover-community/mathlib4/tar.gz/'+MATHLIB,archive)
    result=prepare(args.source,args.output,archive)
    print(json.dumps(dict(bytes=result['bytes'],files=len(result['files']),mathlib_modules=len(result['mathlib_modules']))))


if __name__=='__main__':main()
