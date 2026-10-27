"""Versioned edits of learned rule memories. Author: Komorebi P.
The editor, exact addressing and history operations are supplied algorithms.
Neural weights remain frozen. No general solver discovery is claimed.
"""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
import numpy as np
from workspace import Workspace, features, make_episode


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def point(x,z):
    return {'reader':0,'terms':[{'xy':[float(x),float(z)],'weight':1.}]}


def observable(spec):
    reader=int(spec.get('reader',0))
    if reader not in (0,1,2):raise ValueError('Invalid reader.')
    raw=spec.get('terms')
    if raw is None and 'xy' in spec:raw=[{'xy':spec['xy'],'weight':1.}]
    if not raw:raise ValueError('An observable needs a weighted point.')
    merged={}
    for t in raw:
        xy=tuple(float(v) for v in t['xy']);w=float(t.get('weight',1.))
        if len(xy)!=2 or not np.all(np.isfinite([*xy,w])):raise ValueError('Invalid point.')
        merged[xy]=merged.get(xy,0.)+w
    terms=[{'xy':list(xy),'weight':w} for xy,w in sorted(merged.items()) if w!=0]
    if not terms:raise ValueError('Zero observable.')
    return {'reader':reader,'terms':terms}


def obs_key(x):return digest(observable(x))


def fit_edit_coordinates(model):
    o,_,_,_=make_episode(np.random.default_rng(20400),n=256,queries=8)
    h=model.infer(o,16)
    _,s,v=np.linalg.svd(h,full_matrices=False)
    rank=int(np.searchsorted(np.cumsum(s*s)/sum(s*s),.999)+1)
    transform=v[:rank].T*(s[:rank]/np.sqrt(len(h)))
    return transform,{'rank':rank,'development_seed':20400,'energy_fraction':.999,
                      'singular_values':s.tolist(),'coefficient_labels_used':False}


class MemoryBank:
    def __init__(self,model,transform=None):
        self.model=model
        if transform is None:self.transform,self.coordinate_info=fit_edit_coordinates(model)
        else:
            self.transform=np.array(transform,float)
            self.coordinate_info={'rank':self.transform.shape[1],'source':'supplied_or_loaded'}
        if self.transform.shape[0]!=model.width or not np.all(np.isfinite(self.transform)):
            raise ValueError('Invalid edit coordinates.')
        self.slots={};self.cache={}
        self.model_hash=digest({k:v.tolist() for k,v in model.p.items()}|
                              {'sensor_basis':model.sensor_basis.tolist(),
                               'sensor_scale':model.sensor_scale.tolist()})

    def revision(self,name):
        s=self.slots[name]
        return s['versions'][s['current']]

    def state(self,name):
        return np.array(self.revision(name)['state'],float)

    def add(self,name,h,evidence=None,origin=None):
        if not name or name in self.slots:raise ValueError('Workspace name must be new.')
        h=np.asarray(h,float)
        if h.shape!=(self.model.width,) or not np.all(np.isfinite(h)):raise ValueError('Invalid state.')
        v={'id':0,'parent':None,'state':h.tolist(),'locks':{},'event':'create',
           'evidence':copy.deepcopy(evidence),'origin':copy.deepcopy(origin)}
        self.slots[name]={'current':0,'versions':[v]}

    def learn(self,name,o,passes=16):
        if len(o['y'])!=1:raise ValueError('One rule per named workspace.')
        self.add(name,self.model.infer(o,passes)[0],
                 evidence={k:np.asarray(v).tolist() for k,v in o.items()})

    def row(self,spec):
        s=observable(spec)
        phi=sum((t['weight']*features(np.array(t['xy'])) for t in s['terms']),np.zeros(6))
        row=10*phi@self.model.p['read'][s['reader']]
        if not np.all(np.isfinite(row)):raise ValueError('Observable exceeds numeric range.')
        return row

    def read(self,name,spec):
        return float(self.row(spec)@self.state(name))

    def _conflict(self,name,request,reason):
        return {'workspace':name,'status':'conflict','request':copy.deepcopy(request),
                'report':{'reason':reason}}

    def _solve(self,name,locks,request,tolerance=1e-7):
        if not np.isfinite(tolerance) or tolerance<=0:raise ValueError('Invalid tolerance.')
        if not locks:raise ValueError('At least one constraint is required.')
        h=self.state(name);v=self.revision(name)
        l=np.stack([self.row(s) for s in locks.values()])
        target=np.array([s['target'] for s in locks.values()],float)
        if not np.all(np.isfinite(target)):raise ValueError('Invalid target.')
        a=l@self.transform
        z,_,rank,s=np.linalg.lstsq(a,target-l@h,rcond=1e-10)
        changed=h+self.transform@z
        errors=l@changed-target
        worst=float(np.max(np.abs(errors)))
        good=np.all(np.isfinite(changed)) and worst<=tolerance
        return {'workspace':name,'base_revision':v['id'],'base_state_hash':digest(v['state']),
                'status':'feasible' if good else 'conflict',
                'state':changed.tolist() if good else None,'locks':copy.deepcopy(locks),
                'request':copy.deepcopy(request),
                'report':{'constraints':len(locks),'constraint_rank':int(rank),
                    'editable_dimensions':self.transform.shape[1],
                    'unconstrained_dimensions':int(self.transform.shape[1]-rank),
                    'identified_within_edit_space':bool(rank==self.transform.shape[1]),
                    'selection_assumption':'minimum development-whitened coordinate change',
                    'max_constraint_error':worst,'tolerance':float(tolerance),
                    'edit_coordinate_norm':float(np.linalg.norm(z)),
                    'latent_delta_norm':float(np.linalg.norm(changed-h)),
                    'singular_values':s.tolist(),
                    'conflicting_constraint_indices':np.flatnonzero(abs(errors)>tolerance).tolist()}}

    def propose(self,name,request):
        locks={} if request.get('clear_locks',False) else copy.deepcopy(self.revision(name)['locks'])
        tol=float(request.get('tolerance',1e-7));requested={}
        for item in request.get('set',[]):
            s=observable(item)
            if ('target' in item)==('delta' in item):raise ValueError('Specify target or delta, exclusively.')
            target=float(item['target']) if 'target' in item else self.read(name,s)+float(item['delta'])
            key=obs_key(s)
            if key in requested and abs(requested[key]-target)>tol:
                return self._conflict(name,request,'Conflicting values for one observable.')
            requested[key]=target;locks[key]=s|{'target':target,'kind':'set'}
        for item in request.get('preserve',[]):
            s=observable(item);key=obs_key(s);target=self.read(name,s)
            if key in requested and abs(requested[key]-target)>tol:
                return self._conflict(name,request,'Requested change conflicts with preservation.')
            locks[key]=s|{'target':target,'kind':'preserve'}
        return self._solve(name,locks,request,tol)

    def commit(self,p):
        if p['status']!='feasible':return {'status':p['status'],'report':p['report']}
        v=self.revision(p['workspace'])
        if v['id']!=p['base_revision'] or digest(v['state'])!=p['base_state_hash']:
            return {'status':'stale_proposal','current_revision':v['id']}
        h=np.array(p['state'],float);tol=float(p['report']['tolerance'])
        if h.shape!=(self.model.width,) or not np.all(np.isfinite(h)) or not np.isfinite(tol) or tol<=0:
            raise ValueError('Invalid proposal.')
        delta=h-self.state(p['workspace'])
        projected=self.transform@np.linalg.lstsq(self.transform,delta,rcond=1e-10)[0]
        if np.max(abs(delta-projected))>1e-7:raise ValueError('Edit leaves declared state subspace.')
        if max(abs(self.row(s)@h-s['target']) for s in p['locks'].values())>tol:
            raise ValueError('Edit no longer meets constraints.')
        slot=self.slots[p['workspace']];idx=len(slot['versions'])
        slot['versions'].append({'id':idx,'parent':v['id'],'state':h.tolist(),
            'locks':copy.deepcopy(p['locks']),'event':'edit',
            'request':copy.deepcopy(p['request']),'report':copy.deepcopy(p['report'])})
        slot['current']=idx
        return {'status':'committed','workspace':p['workspace'],'revision':idx,'report':p['report']}

    def edit(self,name,request):return self.commit(self.propose(name,request))

    def edit_many(self,requests):
        scratch=copy.deepcopy(self);receipts=[]
        for name,request in requests:
            r=scratch.edit(name,request);receipts.append(r)
            if r['status']!='committed':return {'status':'conflict','committed':False,'receipts':receipts}
        self.slots=scratch.slots
        return {'status':'committed','committed':True,'receipts':receipts}

    def undo(self,name):
        p=self.revision(name)['parent']
        if p is None:return False
        self.slots[name]['current']=p;return True

    def checkout(self,name,revision):
        if not 0<=revision<len(self.slots[name]['versions']):raise ValueError('Unknown revision.')
        self.slots[name]['current']=revision

    def fork(self,source,new_name):
        v=self.revision(source)
        self.add(new_name,self.state(source),origin={'workspace':source,'revision':v['id'],
                                                     'base_locks':copy.deepcopy(v['locks'])})
        self.revision(new_name)['locks']=copy.deepcopy(v['locks'])

    @staticmethod
    def _same_lock(a,b,tol=1e-7):
        if a is None or b is None:return a is b
        return obs_key(a)==obs_key(b) and abs(a['target']-b['target'])<=tol

    def merge(self,branch,target):
        origin=self.slots[branch]['versions'][0].get('origin')
        if not origin or origin['workspace']!=target:raise ValueError('A direct fork is required.')
        base=origin['base_locks'];src=self.revision(branch)['locks'];dst=self.revision(target)['locks']
        combined=copy.deepcopy(dst)
        for k in set(base)|set(src):
            b,s,d=base.get(k),src.get(k),dst.get(k)
            if self._same_lock(s,b):continue
            if not self._same_lock(d,b) and not self._same_lock(d,s):
                return {'status':'conflict','report':{'reason':'Both branches changed one observable.'}}
            if s is None:combined.pop(k,None)
            else:combined[k]=copy.deepcopy(s)
        if not combined:return {'status':'no_constraints'}
        p=self._solve(target,combined,{'merge_from':branch,'branch_revision':self.revision(branch)['id']})
        r=self.commit(p)
        if r['status']=='committed':self.revision(target)['event']='merge'
        return r

    def locate(self,examples,tolerance=.5):
        if not examples:raise ValueError('Lookup needs before-edit examples.')
        scores=[]
        for name in sorted(self.slots):
            errors=[self.read(name,s)-float(s['target']) for s in examples]
            scores.append({'workspace':name,'rmse':float(np.sqrt(np.mean(np.square(errors))))})
        scores.sort(key=lambda x:x['rmse'])
        candidates=[s['workspace'] for s in scores if s['rmse']<=tolerance]
        return {'status':'unique' if len(candidates)==1 else ('ambiguous' if candidates else 'no_match'),
                'candidates':candidates,'scores':scores,'tolerance':tolerance}

    def execute(self,steps,x,z):
        versions=[(name,self.revision(name)['id']) for name in steps]
        key=digest({'versions':versions,'x':float(x),'z':float(z)})
        if key in self.cache:return {'value':self.cache[key],'cache_hit':True,'versions':versions}
        val=float(x)
        for name in steps:val=self.read(name,point(val,z))/10
        self.cache[key]=val
        return {'value':val,'cache_hit':False,'versions':versions}

    def replay(self,name,o,passes=4,enforce_locks=True):
        if len(o['y'])!=1:raise ValueError('Replay one workspace at a time.')
        h=self.state(name)[None,:];phi=features(o['xy']);locks=self.revision(name)['locks']
        if locks:
            rows=np.stack([self.row(v) for v in locks.values()])
            targets=np.array([v['target'] for v in locks.values()])
            pinv=np.linalg.pinv(rows@self.transform,rcond=1e-10)
        for cycle in range(passes):
            order=range(phi.shape[1]) if cycle%2==0 else range(phi.shape[1]-1,-1,-1)
            for t in order:
                h=self.model.step(h,phi[:,t],o['y'][:,t],o['channel'][:,t])
                if enforce_locks and locks:h[0]+=self.transform@(pinv@(targets-rows@h[0]))
        return h[0]

    def refine(self,name,o,passes=4,tolerance=1e-7):
        if len(o['y'])!=1:raise ValueError('Refine one workspace at a time.')
        v=self.revision(name);locks=copy.deepcopy(v['locks']);constraints=copy.deepcopy(locks)
        for xy,y in zip(o['xy'][0],o['y'][0]*10):
            s=point(*xy);k=obs_key(s)
            if k in constraints and abs(constraints[k]['target']-float(y))>tolerance:
                return {'status':'conflict','report':{'reason':'New evidence contradicts a retained requirement.'}}
            constraints[k]=s|{'target':float(y),'kind':'evidence'}
        check=self._solve(name,constraints,{'event':'new_evidence_check'},tolerance)
        if check['status']!='feasible':return {'status':'conflict','report':check['report']}
        h=self.replay(name,o,passes,True)
        error=max([abs(self.row(s)@h-s['target']) for s in locks.values()]+[0.])
        if not np.all(np.isfinite(h)) or error>tolerance:raise ValueError('Retained constraints violated.')
        slot=self.slots[name];idx=len(slot['versions'])
        data_error=np.array([self.row(point(*xy))@h for xy in o['xy'][0]])-o['y'][0]*10
        r={'status':'committed','workspace':name,'revision':idx,'max_retained_error':float(error),
           'new_evidence_rmse':float(np.sqrt(np.mean(data_error**2))),'passes':passes}
        slot['versions'].append({'id':idx,'parent':v['id'],'state':h.tolist(),'locks':locks,
            'event':'native_refinement_with_constraints','report':r,
            'evidence':{k:np.asarray(a).tolist() for k,a in o.items()}})
        slot['current']=idx
        return r

    def to_dict(self):
        return {'schema':'komorebi_editable_workspace_v0.2','author':'Komorebi P.',
                'model_seed':self.model.seed,'model_hash':self.model_hash,
                'edit_coordinates':self.transform.tolist(),'coordinate_info':self.coordinate_info,
                'slots':copy.deepcopy(self.slots)}

    def save(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_name(path.name+'.tmp')
        temp.write_text(json.dumps(self.to_dict(),indent=2,allow_nan=False));temp.replace(path)

    @classmethod
    def load(cls,path,model):
        obj=json.loads(Path(path).read_text())
        if obj.get('schema')!='komorebi_editable_workspace_v0.2':raise ValueError('Unknown schema.')
        b=cls(model,obj['edit_coordinates'])
        if b.model_hash!=obj['model_hash']:raise ValueError('Bank/checkpoint mismatch.')
        b.coordinate_info=obj['coordinate_info'];b.slots=obj['slots']
        for name,slot in b.slots.items():
            if not 0<=slot['current']<len(slot['versions']):raise ValueError('Invalid revision.')
            for i,v in enumerate(slot['versions']):
                h=np.array(v['state'],float)
                if v['id']!=i or h.shape!=(model.width,) or not np.all(np.isfinite(h)):
                    raise ValueError('Invalid saved state.')
                if v['parent'] is not None and not 0<=v['parent']<i:raise ValueError('Invalid parent.')
        return b
