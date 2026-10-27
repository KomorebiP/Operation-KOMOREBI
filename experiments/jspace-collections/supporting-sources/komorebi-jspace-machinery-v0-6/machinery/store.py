"""Revisioned workspaces, previews, change traces, atomic guarded saves. Komorebi P."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import numpy as np
from .values import Value, Fault, canonical, digest, change
from .runtime import Runner, named


def compare_runs(before,after):
    result = {}
    for field in ['outputs','values']:
        changed = {}
        for name in sorted(set(before[field]) | set(after[field])):
            a,b = before[field].get(name),after[field].get(name)
            detail = change(Value.unpack(a) if a is not None else None,Value.unpack(b) if b is not None else None)
            if detail['status'] != 'unchanged': changed[name] = detail
        result[field] = changed
    return result


class Store:
    SCHEMA = 'komorebi_workspace_machinery_v0.6'

    def __init__(self,registry):
        self.registry = registry; self.registry_identity = digest(registry.manifest())
        self.runner = Runner(registry); self.revisions = {}; self.branches = {}
        self._path = None; self._disk_hash = None

    def _meaning(self):
        if digest(self.registry.manifest()) != self.registry_identity:
            raise Fault('identity','Registry changed. Create an explicit new bank or migrate its meanings.')

    def _revision(self,name):
        if name not in self.branches: raise Fault('binding',f'Unknown workspace: {name}')
        return self.revisions[self.branches[name]]

    def snapshot(self,name): return copy.deepcopy(self._revision(name)['snapshot'])

    def run(self,name):
        self._meaning(); snapshot = self.snapshot(name)
        return self.runner.run(snapshot['program'],{k:Value.unpack(v) for k,v in snapshot['inputs'].items()})

    def _commit(self,name,snapshot,result,parent,label):
        if result['status'] != 'ok': return {'status':'rejected','run':result}
        ident = 'r'+str(len(self.revisions)).zfill(6)
        self.revisions[ident] = {'id':ident,'parent':parent,'label':label,'snapshot':copy.deepcopy(snapshot),
                                'snapshot_identity':digest(snapshot),'outputs':copy.deepcopy(result['outputs']),
                                'output_identity':digest(result['outputs'])}
        self.branches[name] = ident
        return {'status':'committed','workspace':name,'revision':ident,'run':result}

    def create(self,name,program,inputs):
        self._meaning()
        if not named(name) or name in self.branches: raise Fault('binding','Choose a new workspace name.')
        snapshot = {'program':copy.deepcopy(program),'inputs':{k:v.pack() for k,v in inputs.items()}}
        result = self.runner.run(program,inputs)
        return self._commit(name,snapshot,result,None,'create')

    def fork(self,source,name):
        self._meaning(); self._revision(source)
        if not named(name) or name in self.branches: raise Fault('binding','Choose a new workspace name.')
        self.branches[name] = self.branches[source]
        return {'status':'forked','workspace':name,'revision':self.branches[name]}

    def preview(self,name,updates=None,program=None,expected_revision=None):
        self._meaning(); current = self.branches.get(name)
        if expected_revision is not None and expected_revision != current: raise Fault('conflict','The workspace revision changed.')
        snapshot = self.snapshot(name)
        for key,value in (updates or {}).items():
            if key not in snapshot['inputs']: raise Fault('binding',f'Unknown input: {key}')
            snapshot['inputs'][key] = value.pack()
        if program is not None: snapshot['program'] = copy.deepcopy(program)
        before = self.run(name)
        after = self.runner.run(snapshot['program'],{k:Value.unpack(v) for k,v in snapshot['inputs'].items()})
        return {'status':'ready' if after['status']=='ok' else 'rejected','base_revision':current,
                'snapshot':snapshot,'run':after,'changes':compare_runs(before,after) if after['status']=='ok' else None}

    def edit(self,name,updates=None,program=None,expected_revision=None,label='edit'):
        preview = self.preview(name,updates,program,expected_revision)
        if preview['status'] != 'ready': return preview
        result = self._commit(name,preview['snapshot'],preview['run'],preview['base_revision'],label)
        result['changes'] = preview['changes']
        return result

    def undo(self,name):
        self._meaning(); revision = self._revision(name)
        if revision['parent'] is None: return {'status':'at_root','revision':revision['id']}
        self.branches[name] = revision['parent']
        return {'status':'restored','revision':revision['parent']}

    def checkout(self,name,revision):
        self._meaning(); self._revision(name)
        if revision not in self.revisions: raise Fault('binding','Unknown revision.')
        self.branches[name] = revision
        return {'status':'restored','revision':revision}

    def compare(self,a,b): return compare_runs(self.run(a),self.run(b))

    def define_function(self,name,parameters,body,origin='authored_function'):
        """Extend the library under a new name without changing old meanings."""
        self._meaning(); candidate = copy.deepcopy(self.registry)
        candidate.define(name,parameters,body,origin)
        original = self.registry.manifest(); extended = candidate.manifest()
        if any(extended.get(key)!=value for key,value in original.items()):
            raise Fault('identity','A library extension must preserve all existing operations.')
        self.registry = candidate; self.registry_identity = digest(candidate.manifest())
        self.runner = Runner(candidate)
        return {'status':'registered','operation':name,'identity':candidate.get(name).identity}

    def pack(self):
        self._meaning()
        return {'schema':self.SCHEMA,'author':'Komorebi P.','registry':self.registry.manifest(),
                'registry_identity':self.registry_identity,'functions':self.registry.definitions(),
                'revisions':copy.deepcopy(self.revisions),'branches':dict(self.branches)}

    def save(self,path):
        path = Path(path).resolve(); path.parent.mkdir(parents=True,exist_ok=True)
        payload = canonical(self.pack()).encode(); lock = path.with_name(path.name+'.lock')
        try: descriptor = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError as exc: raise Fault('conflict','Another writer holds the bank lock.') from exc
        temp = None
        try:
            os.close(descriptor)
            if path.exists():
                current = hashlib.sha256(path.read_bytes()).hexdigest()
                if self._path != path or current != self._disk_hash:
                    raise Fault('conflict','Bank changed on disk or destination already exists.')
            elif self._path == path and self._disk_hash is not None:
                raise Fault('conflict','The loaded bank was removed from disk.')
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix=path.name+'.',suffix='.tmp',delete=False) as handle:
                temp = Path(handle.name); handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            os.replace(temp,path); temp = None
            self._path = path; self._disk_hash = hashlib.sha256(payload).hexdigest()
        finally:
            if temp is not None: temp.unlink(missing_ok=True)
            lock.unlink(missing_ok=True)

    @classmethod
    def load(cls,path,base_registry,replay_atol=1e-9):
        path = Path(path).resolve(); raw = path.read_bytes(); obj = json.loads(raw)
        if obj.get('schema') != cls.SCHEMA: raise Fault('schema','Unknown workspace bank format.')
        if base_registry.definitions(): raise Fault('registry','Load requires a registry containing native operations only.')
        for definition in obj['functions']: base_registry.define(**definition)
        bank = cls(base_registry)
        if obj['registry_identity'] != bank.registry_identity or obj['registry'] != base_registry.manifest():
            raise Fault('identity','Saved operations do not match the current implementations or checkpoints.')
        for i,(name,revision) in enumerate(obj['revisions'].items()):
            if name != 'r'+str(i).zfill(6) or name != revision['id'] or (revision['parent'] is not None and revision['parent'] not in bank.revisions):
                raise Fault('history','Invalid revision ancestry.')
            snapshot = revision['snapshot']
            if digest(snapshot) != revision['snapshot_identity']: raise Fault('integrity','Stored snapshot changed.')
            result = bank.runner.run(snapshot['program'],{k:Value.unpack(v) for k,v in snapshot['inputs'].items()})
            if digest(revision['outputs']) != revision['output_identity']:
                raise Fault('integrity','Stored output record changed.')
            matches = result['status']=='ok' and set(result['outputs'])==set(revision['outputs'])
            for key,saved in revision['outputs'].items():
                if not matches: break
                a,b = Value.unpack(saved),Value.unpack(result['outputs'][key])
                matches = a.kind==b.kind and (abs(a.data-b.data)<=replay_atol if a.kind=='scalar' else np.array_equal(a.data,b.data))
            if not matches:
                raise Fault('replay','Saved outputs no longer reproduce.')
            bank.revisions[name] = revision
        for name,head in obj['branches'].items():
            if not named(name) or head not in bank.revisions: raise Fault('history','Invalid workspace head.')
        bank.branches = obj['branches']; bank._path = path; bank._disk_hash = hashlib.sha256(raw).hexdigest()
        return bank
