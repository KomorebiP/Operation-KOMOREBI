"""Prepare small manifests for pinned, checksum-bound public browser Lean assets.

Inputs come from the reader workflow's pinned upstream checkout. Mathlib imports
are followed in the exact source revision recorded by its artifact manifest.
Large artifacts stay at their immutable public GitHub URLs. This prepares their
import manifests; it does not compile or certify paper proofs.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
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
    if output.exists() and any(output.iterdir()):raise ValueError('Use an empty browser runtime output directory')
    output.mkdir(parents=True, exist_ok=True)
    upstream=json.loads((source/'lean-mathlib/real-analysis-layer.json').read_bytes())
    core=json.loads((source/'lean-wasm/core-layer.json').read_bytes())
    if upstream['leanCommit']!=LEAN or core['leanCommit']!=LEAN or upstream['mathlibCommit']!=MATHLIB:
        raise ValueError('Browser compiler and library build identities disagree')
    inventory={};remote={}
    origin='https://raw.githubusercontent.com/live-codes/browser-lean/'+UPSTREAM+'/public/'
    def record(path):
        data=(source/path).read_bytes()
        if path.endswith(('.js','.json','.txt')):data=data.replace(b'\r\n',b'\n')
        inventory[path]=dict(size=len(data),sha256=sha(data))
        return data
    def remote_file(virtual,path,data=None):
        data=record(path) if data is None else data
        remote[virtual]=dict(size=len(data),sha256=sha(data),url=origin+path)
        return remote[virtual]
    record('lean-mathlib/real-analysis-layer.json')
    for p in sorted((source/'lean-wasm').rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(source).as_posix()
        data=record(rel)
        if p.name=='core-layer.json':
            target=output/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        else:remote_file(rel,rel,data)
    roots={};expected={}
    for root in ('Std','Lean','Batteries'):
        paths=sorted((source/'lean-lib'/root).rglob('*'))
        paths=[p for p in paths if p.is_file() and p.name.endswith('.gz')]
        base=source/'lean-lib'/(root+'.olean.gz')
        if base.exists():paths.append(base)
        for ext in ('.ir.gz','.ir.sig.gz'):
            p=source/'lean-lib'/(root+ext)
            if p.exists():paths.append(p)
        names=[]
        for p in sorted(set(paths)):
            path=p.relative_to(source/'lean-lib').as_posix()[:-3]
            rel=p.relative_to(source).as_posix();compressed=record(rel);raw=gzip.decompress(compressed)
            expected[path]=dict(root=root,source=rel,sha256=sha(raw),bytes=len(raw))
            names.append(path)
        roots[root]=dict(leanCommit=LEAN,files=names,packs=[],loose=[])
    selected=mathlib_closure(mathlib_archive)
    layer=dict(leanCommit=LEAN,mathlibCommit=MATHLIB,version='komorebi-browser-pilot-2',files=[],packs=[])
    covered=set()
    for item in upstream['packs']:
        source_path='lean-mathlib/'+item['file'];compressed=record(source_path);blob=gzip.decompress(compressed)
        if len(blob)!=item['bytes']:raise ValueError('Invalid upstream Mathlib pack')
        groups={root:[] for root in roots};groups['Mathlib']=[]
        for entry in item['entries']:
            path=entry['path'];wanted=expected.get(path)
            if wanted and sha(blob[entry['offset']:entry['offset']+entry['bytes']])==wanted['sha256']:
                groups[wanted['root']].append(entry);covered.add(path)
            name=path.removesuffix('.sig').removesuffix('.olean').removesuffix('.ir').replace('/','.')
            external=name.split('.')[0] not in {'Init','Lean','Std','Batteries','Mathlib'}
            if external or name in selected and name.startswith('Mathlib.'):
                groups['Mathlib'].append(entry);layer['files'].append(path)
        if not any(groups.values()):continue
        receipt=remote_file('shared/'+item['file'],source_path,compressed)
        for root,entries in groups.items():
            if entries:
                target=layer if root=='Mathlib' else roots[root]
                target['packs'].append(dict(file='../shared/'+item['file'],bytes=item['bytes'],
                                            compressedBytes=len(compressed),sha256=receipt['sha256'],entries=entries))
    for path,wanted in expected.items():
        if path in covered:continue
        virtual='loose/'+path+'.gz';receipt=remote_file(virtual,wanted['source'])
        roots[wanted['root']]['loose'].append(dict(path=path,file='../'+virtual,
                                                 sha256=receipt['sha256'],bytes=wanted['bytes']))
    for root,manifest in roots.items():write_json(output/'lean-lib'/(root+'-layer.json'),manifest)
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
                       inputs=inventory,files=files,remote_files=remote,
                       bytes=sum(p['size'] for p in files.values())+sum(p['size'] for p in remote.values()),
                       local_bytes=sum(p['size'] for p in files.values()),
                       loose_files=sum(len(m['loose']) for m in roots.values()))
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
