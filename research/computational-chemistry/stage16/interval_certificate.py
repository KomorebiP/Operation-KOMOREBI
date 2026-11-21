"""Exact continuous-energy enclosures from endpoint resolvent disks.

Only standard-library rational arithmetic is used. Endpoint disks are inputs;
this module neither establishes their provenance nor upgrades their assumptions.
"""
from fractions import Fraction as F
from math import isqrt

def sqrt_upper(value,digits=30):
    value=F(value)
    if value<0:raise ValueError('Negative squared norm')
    a,b=isqrt(value.numerator),isqrt(value.denominator)
    if a*a==value.numerator and b*b==value.denominator:return F(a,b)
    scale=10**digits;k=isqrt(value.numerator*scale*scale//value.denominator)
    return F(k if k*k*value.denominator==value.numerator*scale*scale else k+1,scale)

def endpoint(energy,eta,center,radius):
    energy,eta,radius=F(energy),F(eta),F(radius)
    re,im=F(center['real']),F(center['imaginary'])
    if eta<=0 or radius<0:raise ValueError('Positive broadening and nonnegative radius required')
    strength=-im+radius
    if strength<0:raise ValueError('Endpoint disk contradicts nonnegative resolvent strength')
    return dict(energy=energy,eta=eta,re=re,im=im,radius=radius,strength_upper=strength)

def cell(left,right):
    if left['eta']!=right['eta'] or left['energy']>=right['energy']:raise ValueError('Ordered distinct energies and equal broadening required')
    h=right['energy']-left['energy'];eta=left['eta']
    coefficient=h*h/eta**2*sqrt_upper(left['strength_upper']*right['strength_upper'])
    uniform=max(left['radius'],right['radius'])+coefficient/4
    return dict(left=left,right=right,interpolation_coefficient=coefficient,uniform_radius_upper=uniform)

def evaluate(segment,t):
    t=F(t)
    if not 0<=t<=1:raise ValueError('Interpolation fraction must lie in [0,1]')
    a,b=segment['left'],segment['right'];u=1-t
    return dict(energy=u*a['energy']+t*b['energy'],eta=a['eta'],
        center=dict(real=str(u*a['re']+t*b['re']),imaginary=str(u*a['im']+t*b['im'])),
        radius=str(u*a['radius']+t*b['radius']+t*u*segment['interpolation_coefficient']))

def serialize(segment):
    a,b=segment['left'],segment['right']
    return dict(left_energy=str(a['energy']),right_energy=str(b['energy']),eta=str(a['eta']),
        coefficient=str(segment['interpolation_coefficient']),uniform_radius=str(segment['uniform_radius_upper']))

def signed_gap(full,reduced):
    if any(full[side]['energy']!=reduced[side]['energy'] or full[side]['eta']!=reduced[side]['eta'] for side in ['left','right']):raise ValueError('Comparison cells differ')
    lower=[];upper=[]
    for side in ['left','right']:
        f,r=full[side],reduced[side];difference=-f['im']+r['im'];radius=f['radius']+r['radius']
        lower.append(difference-radius);upper.append(difference+radius)
    bulge=(full['interpolation_coefficient']+reduced['interpolation_coefficient'])/4
    lo,hi=min(lower)-bulge,max(upper)+bulge
    return dict(signed_lower=str(lo),signed_upper=str(hi),absolute_lower=str(max(F(0),lo,-hi)))
