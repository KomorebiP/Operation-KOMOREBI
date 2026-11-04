"""Bind later reader sources to dated publication manifests without changing imports."""
import hashlib
import json
from pathlib import Path

CONFIG='manifests/reader-source-additions.json'


def extend_owned(root, registry, owned):
    from build_reader_site import safe_path
    root=Path(root).resolve()
    if not (root/CONFIG).is_file():return {}
    config=json.loads((root/CONFIG).read_bytes())
    if config.get('schema')!=1:raise ValueError('Unsupported reader source additions')
    components={c['id']:c for c in registry['components']}
    additions={};seen=set()
    def read(path):
        target=root/safe_path(path)
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('Reader source escapes its repository: '+path)
        return target.read_bytes()
    def entry(path, work, raw, record, record_hash):
        return dict(repository_path=path,work=work,path=path.removeprefix(components[work]['destination']+'/'),
                    size=len(raw),mode='100644',sha256=hashlib.sha256(raw).hexdigest(),
                    git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                    source_record=record,source_record_sha256=record_hash)
    for source in config['sources']:
        work=source['work']
        if work not in components:continue
        if work in seen:raise ValueError('Duplicate reader source work: '+work)
        seen.add(work)
        prefix=safe_path(components[work]['destination'])+'/'
        record=prefix+safe_path(source['record']);raw=read(record)
        record_hash=hashlib.sha256(raw).hexdigest()
        if record_hash!=source['record_sha256']:raise ValueError('Reader publication record changed: '+record)
        publication=json.loads(raw)
        if publication.get('schema')!=1:raise ValueError('Unsupported reader publication record')
        bindings={r['path']:r for r in publication['files']}
        if len(bindings)!=len(publication['files']):raise ValueError('Duplicate publication source binding')
        paths=source['paths']
        if len(paths)!=len(set(paths)):raise ValueError('Duplicate reader source selection')
        additions[record]=entry(record,work,raw,record,record_hash)
        for relative in paths:
            path=prefix+safe_path(relative)
            binding=bindings.get(path)
            if binding is None:raise ValueError('Reader source is not bound by its publication: '+path)
            raw=read(path)
            if len(raw)!=binding['bytes'] or hashlib.sha256(raw).hexdigest()!=binding['sha256']:
                raise ValueError('Reader publication source changed: '+path)
            additions[path]=entry(path,work,raw,record,record_hash)
    for path,record in additions.items():
        if path in owned:
            fields=('work','size','mode','sha256','git_blob_sha1')
            if any(owned[path][key]!=record[key] for key in fields):
                raise ValueError('Reader source conflicts with its original import: '+path)
    for path,record in additions.items():owned.setdefault(path,record)
    return additions
