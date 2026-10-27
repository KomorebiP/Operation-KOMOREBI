"""Editable states bound to learned primitive checkpoints. Komorebi P."""
import copy,json
from pathlib import Path
import numpy as np
from workspace import features
from behavior_bank import BehaviorBank

class PrimitiveWorkspace:
    def __init__(self,model,geometry,executor,reader_adapter):
        binding=BehaviorBank(model,geometry)
        self.model=model;self.geometry=geometry;self.executor=executor
        self.core_identity=binding.model_hash;self.primitive_identity=executor.catalog.kernels.identity()
        self.adapter=np.asarray(reader_adapter,float);self.slots={}

    def add(self,name,h,expression=None,amplitude=0.):
        if not name or name in self.slots:raise ValueError('Choose a new name.')
        if expression is not None:self.executor.evaluate(expression,np.array([[0.,0.]]))
        state={'core':np.asarray(h,float).tolist(),'expression':copy.deepcopy(expression),'amplitude':float(amplitude)}
        self.validate(state)
        self.slots[name]={'current':0,'versions':[{'id':0,'parent':None,'state':state,'event':'create'}]}

    def validate(self,state):
        h=np.asarray(state['core'])
        if h.shape!=(24,) or not np.all(np.isfinite(h)) or not np.isfinite(state['amplitude']):raise ValueError('Invalid state.')

    def state(self,name):
        slot=self.slots[name];return copy.deepcopy(slot['versions'][slot['current']]['state'])

    def install(self,name,expression,xy,outputs,tolerance=1e-6):
        xy=np.asarray(xy,float);outputs=np.asarray(outputs,float)
        extra=self.executor.evaluate(expression,xy)
        design=np.column_stack([features(xy),extra])
        weights,_,rank,_=np.linalg.lstsq(design,outputs,rcond=1e-10)
        error=float(np.max(abs(design@weights-outputs)))
        if rank!=7 or error>tolerance:return {'status':'incompatible','rank':int(rank),'error':error}
        # Fit the base behavior into the existing calibrated core. No neural
        # core weight update is made, and coefficient labels are not supplied.
        anchors=np.array([[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1]],float)
        target=features(anchors)@weights[:6]
        h=self.geometry.transform@np.linalg.solve(self.geometry.primary@self.geometry.transform,target)
        self.add(name,h,expression,float(weights[-1]))
        return {'status':'committed','rank':int(rank),'demonstration_error':error}

    def read_state(self,state,q1,q2=None):
        q1=np.atleast_2d(np.asarray(q1,float));q2=np.zeros_like(q1) if q2 is None else np.broadcast_to(q2,q1.shape)
        p1,p2=features(q1),features(q2)
        desc=np.stack([p1,p1-p2,p1+p2])[None,:,:,:]
        value=10*self.model.predict(np.array(state['core'])[None,:],desc)[0]
        if state['expression'] is not None:
            a=self.executor.evaluate(state['expression'],q1);b=self.executor.evaluate(state['expression'],q2)
            value+=state['amplitude']*(self.adapter[:,0,None]*a+self.adapter[:,1,None]*b)
        return value

    def read(self,name,q1,q2=None):return self.read_state(self.state(name),q1,q2)

    def fork(self,name,new_name):
        s=self.state(name);self.add(new_name,s['core'],s['expression'],s['amplitude'])

    def edit_amplitude(self,name,delta):
        s=self.state(name)
        if s['expression'] is None:raise ValueError('No primitive expression is installed.')
        s['amplitude']+=float(delta);self.validate(s)
        slot=self.slots[name];idx=len(slot['versions'])
        slot['versions'].append({'id':idx,'parent':slot['current'],'state':s,'event':'edit_signal_amplitude','delta':float(delta)})
        slot['current']=idx
        return {'status':'committed','workspace':name,'revision':idx,'amplitude':s['amplitude']}

    def undo(self,name):
        slot=self.slots[name];parent=slot['versions'][slot['current']]['parent']
        if parent is None:return False
        slot['current']=parent;return True

    def to_dict(self):
        return {'schema':'komorebi_primitive_workspace_v0.5','author':'Komorebi P.',
                'core_identity':self.core_identity,'primitive_identity':self.primitive_identity,
                'reader_adapter':self.adapter.tolist(),'slots':copy.deepcopy(self.slots)}

    def save(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp')
        tmp.write_text(json.dumps(self.to_dict(),indent=2,allow_nan=False));tmp.replace(path)

    @classmethod
    def load(cls,path,model,geometry,executor):
        obj=json.loads(Path(path).read_text())
        if obj['schema']!='komorebi_primitive_workspace_v0.5':raise ValueError('Unknown workspace.')
        bank=cls(model,geometry,executor,obj['reader_adapter'])
        if bank.core_identity!=obj['core_identity'] or bank.primitive_identity!=obj['primitive_identity']:
            raise ValueError('Checkpoint meaning changed. Explicit migration and validation are required.')
        bank.slots=obj['slots']
        for slot in bank.slots.values():
            if not 0<=slot['current']<len(slot['versions']):raise ValueError('Invalid revision.')
            for i,revision in enumerate(slot['versions']):
                if revision['id']!=i or (revision['parent'] is not None and not 0<=revision['parent']<i):raise ValueError('Invalid parent.')
                bank.validate(revision['state'])
                if revision['state']['expression'] is not None:executor.evaluate(revision['state']['expression'],np.array([[0.,0.]]))
        return bank
