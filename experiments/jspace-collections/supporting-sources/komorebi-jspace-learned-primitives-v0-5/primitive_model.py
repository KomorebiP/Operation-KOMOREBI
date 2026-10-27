"""Small trainable operation kernels. Author: Komorebi P.

There is no operation name, product feature, or x*y branch here. The square
activation is an explicit polynomial prior. Matrix arithmetic is supplied.
"""
import hashlib,json
from pathlib import Path
import numpy as np

class Kernels:
    def __init__(self,channels,seed=0,width=12,activation='tanh'):
        if activation not in ['tanh','square']:raise ValueError('Unknown activation.')
        self.channels=list(channels);self.activation=activation;self.width=width;self.seed=seed
        rng=np.random.default_rng(seed);n=len(channels)
        self.p={'W':rng.normal(0,.4,(n,2,width)),'b':rng.normal(0,.4,(n,width)),
                'v':rng.normal(0,.1,(n,width)),'skip':np.zeros((n,2)),'c':np.zeros(n)}

    def hidden(self,xy):
        x=np.asarray(xy,float)/2
        h=np.einsum('bi,kij->kbj',x,self.p['W'])+self.p['b'][:,None,:]
        a=np.tanh(h) if self.activation=='tanh' else np.square(h)
        return x,h,a

    def predict(self,xy):
        x,h,a=self.hidden(xy)
        return 4*(np.einsum('kbj,kj->kb',a,self.p['v'])+self.p['skip']@x.T+self.p['c'][:,None])

    def call(self,channel,a,b):
        i=self.channels.index(channel);a,b=np.broadcast_arrays(a,b)
        x=np.column_stack([a.ravel(),b.ravel()])/2
        h=x@self.p['W'][i]+self.p['b'][i]
        hidden=np.tanh(h) if self.activation=='tanh' else np.square(h)
        y=4*(hidden@self.p['v'][i]+x@self.p['skip'][i]+self.p['c'][i])
        return y.reshape(a.shape)

    def loss_grad(self,xy,targets):
        x,h,a=self.hidden(xy)
        pred=np.einsum('kbj,kj->kb',a,self.p['v'])+self.p['skip']@x.T+self.p['c'][:,None]
        error=pred-np.asarray(targets)/4;d=2*error/error.size
        da=d[:,:,None]*self.p['v'][:,None,:]
        dh=da*(1-a*a if self.activation=='tanh' else 2*h)
        grad={'W':np.einsum('bi,kbj->kij',x,dh),'b':dh.sum(axis=1),
              'v':np.einsum('kb,kbj->kj',d,a),'skip':d@x,'c':d.sum(axis=1)}
        return float(np.mean(error**2)),grad

    def train(self,xy,targets,steps=6000,batch=256,seed=501,lr=.003):
        rng=np.random.default_rng(seed);first={k:np.zeros_like(v) for k,v in self.p.items()};second={k:np.zeros_like(v) for k,v in self.p.items()};trace=[]
        for step in range(1,steps+1):
            ids=rng.integers(0,len(xy),batch);loss,grad=self.loss_grad(xy[ids],targets[:,ids])
            norm=np.sqrt(sum(np.sum(g*g) for g in grad.values()));scale=min(1.,5/max(norm,1e-12))
            for k in self.p:
                g=grad[k]*scale;first[k]=.9*first[k]+.1*g;second[k]=.999*second[k]+.001*g*g
                self.p[k]-=lr*(first[k]/(1-.9**step))/(np.sqrt(second[k]/(1-.999**step))+1e-8)
            if step==1 or step%500==0:trace.append({'step':step,'normalized_training_loss':loss})
        return trace

    def refit_readout(self,xy,targets):
        """Same final linear readout fit for both activation families."""
        x,h,a=self.hidden(xy);ranks=[]
        for i in range(len(self.channels)):
            design=np.column_stack([a[i],x,np.ones(len(x))])
            weights,_,rank,_=np.linalg.lstsq(design,targets[i]/4,rcond=1e-10)
            self.p['v'][i]=weights[:self.width];self.p['skip'][i]=weights[self.width:self.width+2];self.p['c'][i]=weights[-1]
            ranks.append(int(rank))
        return ranks

    def identity(self):
        meta={'channels':self.channels,'activation':self.activation,'width':self.width,'p':{k:v.tolist() for k,v in self.p.items()}}
        return hashlib.sha256(json.dumps(meta,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def save(self,path):
        np.savez_compressed(path,**self.p,metadata=json.dumps({'author':'Komorebi P.','channels':self.channels,
                   'activation':self.activation,'width':self.width,'seed':self.seed,'parameters':sum(p.size for p in self.p.values())}))

    @classmethod
    def load(cls,path):
        with np.load(path,allow_pickle=False) as z:
            info=json.loads(str(z['metadata']));model=cls(info['channels'],info['seed'],info['width'],info['activation'])
            model.p={k:z[k].copy() for k in model.p}
        return model

class Catalog:
    """Evidence-based acceptance for use by the executable language."""
    def __init__(self,kernels,accepted,receipt):
        self.kernels=kernels;self.accepted=list(accepted);self.receipt=receipt

    @classmethod
    def validate(cls,kernels,xy,outputs,tolerance=1e-6):
        errors=np.max(abs(kernels.predict(xy)-outputs),axis=1)
        accepted=[c for c,e in zip(kernels.channels,errors) if e<=tolerance]
        return cls(kernels,accepted,{'heldout_max_errors':dict(zip(kernels.channels,errors.tolist())),
                                    'tolerance':tolerance,'status':'empirically_validated','kernel_identity':kernels.identity()})

    def call(self,channel,a,b):
        if channel not in self.accepted:raise ValueError('Primitive has not passed validation.')
        return self.kernels.call(channel,a,b)

    def to_dict(self):return {'schema':'komorebi_primitive_catalog_v0.5','author':'Komorebi P.',
                              'accepted':self.accepted,'receipt':self.receipt}
