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


def tactic_umbrella(available):
    modules=sorted(n for n in available if n.startswith('Mathlib.Tactic.') and n.count('.')==2)
    return ('-- Browser compatibility module, not retained Mathlib.Tactic source.\n'
            '-- Imports only the tactic modules shipped with this pinned browser runtime.\n'
            '-- Missing tactics remain errors. No declarations or assumptions are added.\n'+
            ''.join('import '+name+'\n' for name in modules))


def plans(catalog,read,available):
    collection=Collection(catalog,read)
    entries=[];needed=set()
    for source in catalog['sources']:
        ordered=[];done={};active=set();modules={};issues=set();needs_tactics=False;needs_legacy=False
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
                    if root not in {'Init','Std','Lean','Batteries'} and name not in available:
                        issues.add('Unavailable browser import: '+name)
                    continue
                try:
                    dependency=collection.resolve(name,path)
                    if name in modules and modules[name]!=dependency:
                        raise ValueError('Two source editions requested for module '+name)
                    modules[name]=dependency;visit(dependency,name)
                except ValueError as error:issues.add(str(error))
            active.remove(path);done[path]=module;needed.add(path)
            ordered.append(dict(module=module,path=path))
        # The selected file is checked as source; only dependencies need an export name.
        visit(source['path'],PurePosixPath(source['path']).stem)
        entries.append(dict(id=source['id'],path=source['path'],work=source['work'],
                            label=source['label'],inspect=source['url'],files=ordered,
                            tactics=needs_tactics,legacy=needs_legacy,issues=sorted(issues)))
    return entries,{p:{k:catalog['inputs'][p][k] for k in ('sha256','size','work')} for p in sorted(needed)}


def build(site,runtime):
    record=json.loads((site.output/'lean/run.json').read_bytes())
    bundle=site.output/'downloads/komorebi-lean-runner.zip';raw=bundle.read_bytes()
    if len(raw)!=record['bundle_bytes'] or hashlib.sha256(raw).hexdigest()!=record['bundle_sha256']:
        raise ValueError('Browser source bundle identity failed')
    available=set(runtime['mathlib_modules'])
    with zipfile.ZipFile(bundle) as archive:
        catalog=json.loads(archive.read('CATALOG.json'))
        entries,inputs=plans(catalog,lambda p:archive.read('inputs/'+safe_path(p)),available)
    page='lean/browser/index.html'
    paths=list(inputs);indices={p:i for i,p in enumerate(paths)}
    for entry in entries:
        entry['inspect']=site.rel(entry['inspect'],page)
        for file in entry['files']:file['input']=indices[file.pop('path')]
    compatibility=tactic_umbrella(available)
    legacy='import Std\n'+COMPAT_SOURCE
    data=dict(schema=1,revision=site.revision,entries=entries,
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
    owned={r['repository_path']:r for r in documents['files']}
    bundle=root/'downloads/komorebi-lean-runner.zip';raw=bundle.read_bytes()
    assert len(raw)==data['bundle']['size'] and hashlib.sha256(raw).hexdigest()==data['bundle']['sha256']
    with zipfile.ZipFile(bundle) as archive:
        source=json.loads(archive.read('CATALOG.json'))
        assert {e['path'] for e in data['entries']}=={s['path'] for s in source['sources']}
        for entry in data['entries']:
            assert entry['path'] in owned
            original=next(s for s in source['sources'] if s['path']==entry['path'])
            assert entry['id']==original['id'] and entry['work']==original['work']
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
