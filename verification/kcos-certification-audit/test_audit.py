"""Local regression controls for the independent reference and proposed cap repair."""
import json, sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import pytest
import sympy as sp
ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/'engine' if (ROOT/'engine').is_dir() else ROOT.parents[1]/'monographs/cos-method/engine'
sys.path.insert(0,str(ENGINE))
from independent_reference import Box, exact_law_tail, density_partial_fractions
from directed_accuracy import interval_endpoint_strings, directed_relative_accuracy
from repair_candidate import load_candidate

@pytest.mark.parametrize('spectrum',[
 ['1']*8,['1','1','2','2'],['1','1','1','1','2','2','3','3'],
 ['0.999999','0.999999','1','1','1.000001','1.000001'],
 ['0.000001','0.000001','0.01','0.01','1','1','100','100']])
def test_partial_fraction_identity_as_rational_function(spectrum):
    s=sp.Symbol('s');terms=density_partial_fractions(spectrum)
    found=sum(sp.Rational(c.numerator,c.denominator)/(s+sp.Rational(r.numerator,r.denominator))**k for r,k,c in terms)
    from collections import Counter
    expected=sp.prod((1+2*sp.Rational(x)*s)**(-n//2) for x,n in Counter(spectrum).items())
    assert sp.cancel(found-expected)==0

@pytest.mark.parametrize('value',[Fraction(1,3),Fraction(-2,7),Fraction(10**90+1,10**91-3),Fraction(1,10**5000)])
def test_rational_box_contains_exact_value(value):
    box=Box.rational(value,90)
    assert Fraction(box.lo)<=value<=Fraction(box.hi)

@pytest.mark.parametrize('left,right',[(Fraction(-2,7),Fraction(3,11)),(Fraction(2,3),Fraction(9,13)),(Fraction(-7,2),Fraction(-13,9))])
def test_interval_rational_operations(left,right):
    a,b=Box.rational(left,80),Box.rational(right,80)
    c=a+b;d=a*b
    assert Fraction(c.lo)<=left+right<=Fraction(c.hi)
    assert Fraction(d.lo)<=left*right<=Fraction(d.hi)

def test_reference_running_law():
    ref=exact_law_tail('40',['1','1','2','2'],digits=160)
    exact=Box.rational(-10,200).exp()*2+Box.rational(-20,200).exp()*(-1)
    assert Decimal(ref['probability'][0])<=exact.lo<=exact.hi<=Decimal(ref['probability'][1])

def test_zero_and_scale_invariance():
    ref=exact_law_tail('40',['1','1','2','2'])
    scaled=exact_law_tail('0.000040',['0.000001','0.000001','0.000002','0.000002'])
    assert ref['probability']==scaled['probability']
    assert exact_law_tail('0',['1','1'])['probability']==['1','1']

def test_rank_deficient_factor_exact_zero_mode_elimination():
    A=sp.Matrix([[1,1,1,1,1,1],[1,-1,1,-1,1,-1],[1,1,-1,-1,-1,-1],[1,-1,-1,1,-1,1],[0,0,0,0,0,0]])/2
    assert (A*A.T).eigenvals()=={sp.Integer(0):1,sp.Integer(1):2,sp.Integer(2):2}
    assert A.rank()==4
    assert exact_law_tail('40',['1','1','2','2'])['log10'][0].startswith('-4.041924')

@pytest.mark.parametrize('changes',[{'initial_K':128,'max_K':32},{'initial_interval_dps':60,'max_interval_dps':30},
 {'initial_L':'10','max_L':8},{'max_K':0},{'initial_K':1.5},{'max_L':'Infinity'}])
def test_candidate_rejects_invalid_resource_contract(changes):
    module=load_candidate()
    kw=dict(initial_K=32,max_K=32,initial_L='8',max_L=8,initial_interval_dps=30,max_interval_dps=30,working_dps=100)
    kw.update(changes)
    with pytest.raises(ValueError):module.certified_positive_logsf('100',['1']*8,relative_accuracy='1e-40',**kw)

def test_candidate_clamps_odd_support_cap():
    module=load_candidate()
    result=module.certified_positive_logsf('100',['1']*8,relative_accuracy='1e-40',initial_K=32,max_K=32,
        initial_L='8',max_L=9,initial_interval_dps=30,max_interval_dps=30,working_dps=100)
    assert not result.certified and result.L=='9' and result.K==32 and result.interval_dps==30

@pytest.mark.parametrize('depth',[100,1000,5000])
def test_candidate_preserves_deep_containment(depth):
    module=load_candidate();saved=json.loads((ROOT/'results'/f'deep-{depth}.json').read_text())
    result=module.certified_positive_logsf(saved['input']['q'],['0.02']*80,relative_accuracy='1e-12',
        initial_K=32,max_K=512,initial_L='8',max_L=16,initial_interval_dps=60,max_interval_dps=90,working_dps=220)
    lo,hi=map(Decimal,interval_endpoint_strings(result.log10_interval));rlo,rhi=map(Decimal,saved['independent_reference']['log10'])
    assert result.certified and lo<=rlo<=rhi<=hi
    assert directed_relative_accuracy(result.log10_interval,'1e-12',dps=220).accepted
    assert result.K<=512 and int(result.L)<=16 and result.interval_dps<=90
