"""A bounded nonlinear-rule induction workspace. Author: Komorebi P.

Supplied: six quadratic features, residual update form, two observation channels,
24-dimensional available memory, three query descriptor types, exact addressing.
Learned from final query answers: writers, feedback readers, input-dependent
write gains and output readers. No latent-coordinate or rule-coefficient targets.
This is not unrestricted solver emergence, a transformer, or an ARC solver.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import numpy as np

SCALE = 10.0
FEATURES = 6


def features(x):
    x = np.asarray(x, dtype=float)
    a, b = x[..., 0], x[..., 1]
    return np.stack([np.ones_like(a), a / np.sqrt(2), b / np.sqrt(2),
                     a * b / 2, (a*a-2)/np.sqrt(2.8),
                     (b*b-2)/np.sqrt(2.8)], axis=-1)


def truth(coeff, xy):
    """Independent raw-coordinate oracle, used by the environment and scorer."""
    a, b = xy[..., 0], xy[..., 1]
    raw = np.stack([np.ones_like(a), a, b, a*b, a*a, b*b], axis=-1)
    return np.sum(raw * coeff, axis=-1) / SCALE


def coefficients(rng, n, family='train'):
    c = rng.integers(-2, 3, size=(n, 6)).astype(float)
    if family in ('train', 'iid'):
        # Each training rule has at most one square term. All other terms vary.
        c[np.arange(n), rng.integers(4, 6, n)] = 0
    elif family == 'both_squares':
        c[:, 4:6] = rng.choice([-2., -1., 1., 2.], (n, 2))
    elif family == 'coefficient_ood':
        c = rng.choice([-4., -3., 3., 4.], (n, 6))
        c[np.arange(n), rng.integers(4, 6, n)] = 0
    else:
        raise ValueError(family)
    return c


def make_episode(rng, n=64, support=16, family='train', query_range=2,
                 coeff=None, queries=6):
    c = coefficients(rng, n, family) if coeff is None else np.array(coeff, float)
    n = len(c)
    xy = rng.integers(-2, 3, (n, support, 2)).astype(float)
    # The noiseless task must be identifiable. Only support inputs are inspected.
    for i in range(n):
        tries = 0
        while np.linalg.matrix_rank(features(xy[i])) < FEATURES:
            xy[i] = rng.integers(-2, 3, (support, 2))
            tries += 1
            if tries > 1000:
                raise RuntimeError('Unable to sample full-rank support inputs')
    y = truth(c[:, None, :], xy)
    channel = rng.integers(0, 2, (n, support))
    q1 = rng.integers(-query_range, query_range+1, (n, queries, 2)).astype(float)
    q2 = rng.integers(-query_range, query_range+1, (n, queries, 2)).astype(float)
    p1, p2 = features(q1), features(q2)
    t1, t2 = truth(c[:, None, :], q1), truth(c[:, None, :], q2)
    descriptors = np.stack([p1, p1-p2, p1+p2], axis=1)
    target = np.stack([t1, t1-t2, t1+t2], axis=1)
    observation = {'xy': xy, 'y': y, 'channel': channel}
    query = {'descriptor': descriptors, 'q1': q1, 'q2': q2}
    return observation, query, target, c


def sigmoid(x):
    return 1/(1+np.exp(-np.clip(x, -40, 40)))


class Workspace:
    def __init__(self, seed=0, width=24, architecture='free'):
        self.width = width
        self.seed = seed
        self.architecture = architecture
        rng = np.random.default_rng(seed)
        self.sensor_basis = np.stack([np.linalg.qr(rng.normal(size=(6, 6)))[0]
                                      for _ in range(2)])
        self.sensor_scale = np.array([1., -0.7])
        self.p = {
            'write': rng.normal(0, .16, (2, 6, width)),
            'feedback': rng.normal(0, .16, (2, 6, width)),
            'read': rng.normal(0, .16, (3, 6, width)),
            'gain': np.zeros((2, 6)),
            'bias': np.zeros(2),
        }
        if architecture == 'stable':
            del self.p['feedback']
        elif architecture != 'free':
            raise ValueError(architecture)

    @property
    def parameter_count(self):
        return sum(p.size for p in self.p.values())

    def step(self, h, phi, y, channel, cache=False):
        u = np.einsum('bi,bij->bj', phi, self.sensor_basis[channel])
        v = np.einsum('bi,bij->bj', u, self.p['write'][channel])
        q = v if self.architecture == 'stable' else np.einsum('bi,bij->bj', u, self.p['feedback'][channel])
        err = self.sensor_scale[channel]*y - np.sum(h*q, axis=1)
        gg = sigmoid(np.sum(u*u*self.p['gain'][channel], axis=1)
                     + self.p['bias'][channel])
        den = 1 + np.sum((q if self.architecture == 'stable' else u)**2, axis=1)
        rate = (2 if self.architecture == 'stable' else 1)*gg/den
        new = h + (rate*err)[:, None]*v
        if cache:
            return new, (h, u, v, q, err, gg, den, channel)
        return new

    def infer(self, observation, passes=4, mode='normal', cache=False):
        # Inference API accepts no coefficient or query-output argument.
        phi = features(observation['xy'])
        yy = observation['y']
        ch = observation['channel']
        n, s = yy.shape
        h = np.zeros((n, self.width))
        trace = []
        for cycle in range(passes):
            # Deterministic support replay. Every solver control uses this order.
            order = range(s) if cycle % 2 == 0 else range(s-1, -1, -1)
            for t in order:
                if mode == 'reset_every_write':
                    h = np.zeros_like(h)
                if cache:
                    h, item = self.step(h, phi[:, t], yy[:, t], ch[:, t], True)
                    trace.append(item)
                else:
                    h = self.step(h, phi[:, t], yy[:, t], ch[:, t])
        if mode == 'ablate':
            h[:] = 0
        return (h, trace) if cache else h

    def predict(self, h, descriptor):
        return np.einsum('bh,bkqi,kih->bkq', h, descriptor, self.p['read'])

    def value(self, h, xy, head=0):
        return np.einsum('bh,bh->b', h, features(xy) @ self.p['read'][head])

    def loss_grad(self, observation, descriptor, target, passes=4):
        h, trace = self.infer(observation, passes, cache=True)
        pred = self.predict(h, descriptor)
        diff = pred - target
        loss = np.mean(diff*diff)
        grad = {k: np.zeros_like(v) for k, v in self.p.items()}
        dout = 2*diff/diff.size
        grad['read'] = np.einsum('bkq,bkqi,bh->kih', dout, descriptor, h)
        dh = np.einsum('bkq,bkqi,kih->bh', dout, descriptor, self.p['read'])
        for before, u, v, q, err, gg, den, ch in reversed(trace):
            factor = 2 if self.architecture == 'stable' else 1
            rate = factor*gg/den
            dot = np.sum(dh*v, axis=1)
            dv = dh*(rate*err)[:, None]
            de = dot*rate
            dg = dot*err/den*gg*(1-gg)*factor
            dq = -de[:, None]*before
            if self.architecture == 'stable':
                dq += dv - (2*dot*err*rate/den)[:,None]*q
            for src in range(2):
                ids = ch == src
                if self.architecture == 'stable':
                    grad['write'][src] += u[ids].T @ dq[ids]
                else:
                    grad['write'][src] += u[ids].T @ dv[ids]
                    grad['feedback'][src] += u[ids].T @ dq[ids]
                grad['gain'][src] += (u[ids]*u[ids]).T @ dg[ids]
                grad['bias'][src] += np.sum(dg[ids])
            dh = dh - de[:, None]*q
        return float(loss), grad

    def save(self, path, extra=None):
        np.savez_compressed(path, **self.p, sensor_basis=self.sensor_basis,
                            sensor_scale=self.sensor_scale,
                            metadata=json.dumps({'seed':self.seed,'width':self.width,
                                                 'architecture':self.architecture,
                                                 'extra':extra or {}}))

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as z:
            m = json.loads(str(z['metadata']))
            out = cls(m['seed'], m['width'], m.get('architecture','free'))
            out.p = {k: z[k].copy() for k in out.p}
            out.sensor_basis = z['sensor_basis'].copy()
            out.sensor_scale = z['sensor_scale'].copy()
        return out


class Adam:
    def __init__(self, model, lr=.003):
        self.lr, self.t = lr, 0
        self.m = {k: np.zeros_like(v) for k,v in model.p.items()}
        self.v = copy.deepcopy(self.m)

    def step(self, model, grad):
        self.t += 1
        norm = np.sqrt(sum(np.sum(v*v) for v in grad.values()))
        scale = min(1., 2./max(norm, 1e-12))
        for k,p in model.p.items():
            g = grad[k]*scale
            self.m[k] = .9*self.m[k]+.1*g
            self.v[k] = .999*self.v[k]+.001*g*g
            p -= self.lr*(self.m[k]/(1-.9**self.t))/(np.sqrt(self.v[k]/(1-.999**self.t))+1e-8)
        return float(norm)


def score(pred, target):
    err = (pred-target)*SCALE
    correct = np.rint(pred*SCALE) == np.rint(target*SCALE)
    sse = np.sum(err*err)
    total = np.sum((target*SCALE-np.mean(target*SCALE))**2)
    return {'queries':int(correct.size), 'rounded_correct':int(correct.sum()),
            'rounded_accuracy':float(correct.mean()),
            'all_queries_correct_episodes':int(np.all(correct,axis=(1,2)).sum()),
            'episodes':int(len(correct)), 'mae':float(np.mean(np.abs(err))),
            'rmse':float(np.sqrt(np.mean(err*err))),
            'r2':float(1-sse/max(total,1e-12)),
            'by_reader_accuracy':[float(correct[:,i].mean()) for i in range(3)]}


def symbolic_predict(observation, descriptor):
    phi = features(observation['xy'])
    theta = np.stack([np.linalg.lstsq(x,y,rcond=None)[0]
                      for x,y in zip(phi, observation['y'])])
    return np.einsum('bi,bkqi->bkq', theta, descriptor)


def nlms_predict(observation, descriptor, passes=4, lr=1.):
    phi = features(observation['xy'])
    theta = np.zeros((len(phi),6))
    for cycle in range(passes):
        order = range(phi.shape[1]) if cycle%2 == 0 else range(phi.shape[1]-1,-1,-1)
        for i in order:
            p=phi[:,i]
            e=observation['y'][:,i]-np.sum(theta*p,axis=1)
            theta += (lr*e/(1+np.sum(p*p,axis=1)))[:,None]*p
    return np.einsum('bi,bkqi->bkq', theta, descriptor)
