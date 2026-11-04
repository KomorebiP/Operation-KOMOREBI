"""Browser import plans over the reader's existing receipt-bound source bundle.

An available import route is a preflight result, not a proof verification.
"""
import hashlib
import json
import re
from pathlib import PurePosixPath
import zipfile

from lean_runner import Collection, EXTERNAL_ROOTS, safe_path
from lean_workspaces import COMPAT_SOURCE
from prepare_lean_wasm import MATHLIB, MATHLIB_SOURCE_SHA256, validate_source_library


def tactic_umbrella(available):
    modules=sorted(n for n in available if n.startswith('Mathlib.Tactic.') and n.count('.')==2)
    return ('-- Browser compatibility module, not retained Mathlib.Tactic source.\n'
            '-- Imports only the tactic modules shipped with this pinned browser runtime.\n'
            '-- Missing tactics remain errors. No declarations or assumptions are added.\n'+
            ''.join('import '+name+'\n' for name in modules))


def validate_order(entry):
    """Every checked source appears once; the selected retained file stays last."""
    files=entry['files'];library=entry['library'];order=entry['order']
    if (not isinstance(files,list) or not files or not isinstance(library,list) or
            any(not isinstance(module,str) for module in library) or
            len(library)!=len(set(library)) or not isinstance(order,list)):
        raise ValueError('Invalid browser source order')
    file_done=set();library_done=set()
    for step in order:
        if not isinstance(step,dict) or len(step)!=1:
            raise ValueError('Invalid browser source order step')
        if 'file' in step:
            index=step['file']
            if type(index) is not int or not 0<=index<len(files) or index in file_done:
                raise ValueError('Invalid or repeated browser source order file')
            file_done.add(index)
        elif 'library' in step:
            module=step['library']
            if not isinstance(module,str) or module not in library or module in library_done:
                raise ValueError('Invalid or repeated browser source order library')
            library_done.add(module)
        else:raise ValueError('Invalid browser source order step')
    if (len(file_done)!=len(files) or len(library_done)!=len(library) or
            not order or order[-1]!={'file':len(files)-1}):
        raise ValueError('Incomplete browser source order or selected file is not last')


def plans(catalog,read,available,library_sources=None):
    library_sources=library_sources or {}
    validate_source_library(library_sources,available)
    collection=Collection(catalog,read)
    entries=[];needed=set()
    for source in catalog['sources']:
        ordered=[];done={};active=set();modules={};issues=set();needs_tactics=False;needs_legacy=False
        library=[];library_done=set();order=[]
        def library_visit(module):
            if module in library_done:return
            for dependency in library_sources[module]['imports']:
                if dependency in library_sources:library_visit(dependency)
            library_done.add(module);library.append(module);order.append(dict(library=module))
        def visit(path,module):
            nonlocal needs_tactics,needs_legacy
            if path in active:
                issues.add('Local import cycle: '+module);return
            if path in done:
                if done[path]!=module:issues.add('One source requested under two module names: '+module)
                return
            active.add(path)
            try:
                names=collection.module_imports(path)
                needs_legacy|=bool(re.search(r'\bdite_eq_left\b',collection.read(path).decode('utf-8-sig')))
            except ValueError as error:
                issues.add(str(error));names=[]
            for name in names:
                root=name.split('.')[0]
                if name=='Mathlib.Tactic':needs_tactics=True;continue
                if root in EXTERNAL_ROOTS:
                    if name in library_sources:library_visit(name)
                    elif root not in {'Init','Std','Lean','Batteries'} and name not in available:
                        issues.add('Unavailable browser import: '+name)
                    continue
                try:
                    dependency=collection.resolve(name,path)
                    if name in modules and modules[name]!=dependency:
                        raise ValueError('Two source editions requested for module '+name)
                    modules[name]=dependency;visit(dependency,name)
                except ValueError as error:issues.add(str(error))
            active.remove(path);done[path]=module;needed.add(path)
            order.append(dict(file=len(ordered)))
            ordered.append(dict(module=module,path=path))
        # The selected file is checked as source; only dependencies need an export name.
        visit(source['path'],PurePosixPath(source['path']).stem)
        entry=dict(id=source['id'],path=source['path'],work=source['work'],
                            label=source['label'],inspect=source['url'],files=ordered,
                            library=library,order=order,
                            tactics=needs_tactics,legacy=needs_legacy,issues=sorted(issues))
        validate_order(entry);entries.append(entry)
    return entries,{p:{k:catalog['inputs'][p][k] for k in ('sha256','size','work')} for p in sorted(needed)}


def runtime_library(root,runtime):
    sources=runtime.get('mathlib_source_modules',{})
    available=set(runtime['mathlib_modules'])|set(runtime.get('core_modules',[]))
    validate_source_library(sources,available)
    if sources:
        if runtime['mathlib']!=MATHLIB or runtime.get('mathlib_source_sha256')!=MATHLIB_SOURCE_SHA256:
            raise ValueError('Unpinned Mathlib fallback source archive')
        for module,record in sources.items():
            asset=safe_path(record['asset']);raw=(root/asset).read_bytes()
            identity=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            if raw!=record['source'].encode('utf-8') or runtime['files'].get(asset)!=identity:
                raise ValueError('Mathlib fallback source asset mismatch: '+module)
    return sources,available


def build(site,runtime):
    record=json.loads((site.output/'lean/run.json').read_bytes())
    bundle=site.output/'downloads/komorebi-lean-runner.zip';raw=bundle.read_bytes()
    if len(raw)!=record['bundle_bytes'] or hashlib.sha256(raw).hexdigest()!=record['bundle_sha256']:
        raise ValueError('Browser source bundle identity failed')
    library_sources,available=runtime_library(site.output/'lean/browser/engine',runtime)
    with zipfile.ZipFile(bundle) as archive:
        catalog=json.loads(archive.read('CATALOG.json'))
        entries,inputs=plans(catalog,lambda p:archive.read('inputs/'+safe_path(p)),available,library_sources)
    page='lean/browser/index.html'
    paths=list(inputs);indices={p:i for i,p in enumerate(paths)}
    for entry in entries:
        entry['inspect']=site.rel(entry['inspect'],page)
        for file in entry['files']:file['input']=indices[file.pop('path')]
    # Source fallbacks must be opt-in through the selected file's imports.
    compatibility=tactic_umbrella(set(runtime['mathlib_modules']))
    legacy='import Std\n'+COMPAT_SOURCE
    data=dict(schema=1,revision=site.revision,entries=entries,mathlibRevision=runtime['mathlib'],librarySources=library_sources,
              inputs=[dict(path=p,**inputs[p]) for p in paths],
              bundle=dict(url=site.rel('downloads/komorebi-lean-runner.zip',page),
                          size=len(raw),sha256=record['bundle_sha256']),
              compatibility=dict(module='Mathlib.Tactic',source=compatibility,
                                 sha256=hashlib.sha256(compatibility.encode()).hexdigest()),
              legacy=dict(module='KomorebiBrowser.Compatibility',source=legacy,
                          sha256=hashlib.sha256(legacy.encode()).hexdigest()))
    site.write('lean/browser/catalog.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    site.write('lean/browser/tactic-compatibility.lean',compatibility)
    site.write('lean/browser/version-compatibility.lean',legacy)
    return dict(sources=len(entries),available_import_routes=sum(not e['issues'] for e in entries))


def verify(root,documents):
    data=json.loads((root/'lean/browser/catalog.json').read_bytes())
    engine=root/'lean/browser/engine';runtime=json.loads((engine/'SOURCE.json').read_bytes())
    library_sources,available=runtime_library(engine,runtime)
    assert data['mathlibRevision']==runtime['mathlib'] and data['librarySources']==library_sources
    owned={r['repository_path']:r for r in documents['files']}
    bundle=root/'downloads/komorebi-lean-runner.zip';raw=bundle.read_bytes()
    assert len(raw)==data['bundle']['size'] and hashlib.sha256(raw).hexdigest()==data['bundle']['sha256']
    with zipfile.ZipFile(bundle) as archive:
        source=json.loads(archive.read('CATALOG.json'))
        expected,_=plans(source,lambda p:archive.read('inputs/'+safe_path(p)),available,library_sources)
        expected={entry['path']:entry for entry in expected}
        assert {e['path'] for e in data['entries']}=={s['path'] for s in source['sources']}
        for entry in data['entries']:
            assert entry['path'] in owned
            original=next(s for s in source['sources'] if s['path']==entry['path'])
            assert entry['id']==original['id'] and entry['work']==original['work']
            assert entry['library']==expected[entry['path']]['library']
            validate_order(entry)
            assert entry['order']==expected[entry['path']]['order']
            assert [(file['module'],data['inputs'][file['input']]['path']) for file in entry['files']]==[
                (file['module'],file['path']) for file in expected[entry['path']]['files']]
            selected=data['inputs'][entry['files'][-1]['input']]
            assert selected['path']==entry['path'] and selected['sha256']==owned[entry['path']]['sha256']
            for file in entry['files']:
                record=data['inputs'][file['input']];path=safe_path(record['path'])
                assert record['work']==entry['work']
                assert record['sha256']==source['inputs'][path]['sha256']
                assert hashlib.sha256(archive.read('inputs/'+path)).hexdigest()==record['sha256']
    assert (root/'lean/browser/tactic-compatibility.lean').read_text(encoding='utf8')==data['compatibility']['source']
    assert (root/'lean/browser/version-compatibility.lean').read_text(encoding='utf8')==data['legacy']['source']
    return dict(sources=len(data['entries']),available_import_routes=sum(not e['issues'] for e in data['entries']))
