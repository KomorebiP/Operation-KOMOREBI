"""Exact physical-state consumer and scope controls. Author: Komorebi P."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json,subprocess,sys,tempfile
import backbone_transfer as bt
from exact_phasor import C,response
from pure_type_margins import SAMPLES,gamma
from natural_graph_polynomials import determinant

def run():
    here=Path(__file__).resolve().parent
    spec=json.loads((here/'physical_transfer_example.json').read_bytes())
    cert=bt.certificate(spec);assert cert['status']=='PASS'
    assert bt.verify(spec,cert)=={'status':'PASS','strict_margin':'1/400'}
    actual=[(k,u,v,F(x)) for k,u,v,x in spec['actual']]
    err=max(abs(response(actual,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
    assert err>F(cert['remaining_strict_error_floor'])>F(1,400)
    corruptions=0
    for mutate in (lambda r:r.update(strict_margin='1'),lambda r:r.update(remaining_strict_error_floor='1'),
      lambda r:r['witness']['potential'].__setitem__(1,'2'),lambda r:r['witness']['corrected'][4].__setitem__(3,'2')):
        bad=deepcopy(cert);mutate(bad)
        try:bt.verify(spec,bad)
        except ValueError:corruptions+=1
        else:raise AssertionError('Corrupt state certificate accepted')
    changed=deepcopy(spec);changed['requested_margin']='1/399'
    try:bt.verify(changed,cert)
    except ValueError:corruptions+=1
    else:raise AssertionError('Changed request was not bound')
    no_slack=deepcopy(spec);no_slack['requested_margin']='1'
    assert bt.certificate(no_slack)['status']=='INCONCLUSIVE'
    outside=deepcopy(spec);outside['actual'][4][3]='2'
    assert bt.certificate(outside)['status']=='INCONCLUSIVE'
    e=F(1,10**16)
    mode={'actual':[['L',2,3,str(1+e)],['C',2,3,str(1-e)],['L',1,0,'2'],['C',1,0,'3'],['R',1,0,'1'],['R',3,0,'2']],
      'mode':True,'potential':['0',str(e),str(1+e),str(-e)],'large':'1/1000','small':'1/100000000','requested_margin':'1/100000000000000'}
    m=bt.certificate(mode);assert m['status']=='PASS' and bt.verify(mode,m)['status']=='PASS'
    errors=max(abs(response([(k,u,v,F(x)) for k,u,v,x in mode['actual']],C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
    assert errors>F(m['remaining_strict_error_floor'])>F(mode['requested_margin'])
    invalid=0
    mutations=(lambda s:s.update(mode=1),lambda s:s.update(small='-1'),lambda s:s.update(large='0'),
      lambda s:s.update(requested_margin='0'),lambda s:s.update(opened_R_indices=[0]),
      lambda s:s.update(opened_R_indices=[6,6]),lambda s:s.update(shorted_R_indices=[6]),
      lambda s:s['actual'][0].__setitem__(3,True),lambda s:s['actual'][0].__setitem__(3,0.5),
      lambda s:s['actual'][0].__setitem__(3,'-1'),lambda s:s['actual'][0].__setitem__(3,str(2**257)),
      lambda s:s['actual'][0].__setitem__(1,10),lambda s:s.update(potential=[0]*11))
    for mutate in mutations:
        bad=deepcopy(spec);mutate(bad)
        try:bt.certificate(bad)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid domain/resource input accepted')
    # Monic sample recovery is invertible for a genuine coprime degree-three
    # target, and singular for a degree-two target padded to degree three.
    target=json.loads((here/'frozen_targets.json').read_bytes())['targets'][0]['target']
    def matrix(P,Q):
        rows=[]
        for s in SAMPLES:
            z=sum(F(x)*s**j for j,x in enumerate(P))/sum(F(x)*s**j for j,x in enumerate(Q))
            rows.append([s**j for j in range(4)]+[-z*s**j for j in range(3)])
        return rows
    assert determinant(matrix(target['P'],target['Q']))
    assert not determinant(matrix([4,3,6],[9,2,6]))
    with tempfile.TemporaryDirectory(prefix='physical-transfer-') as folder:
        dest=Path(folder);source=dest/'input.json';output=dest/'certificate.json'
        source.write_text(json.dumps(spec),encoding='utf-8')
        cmd=[sys.executable,'-B',str(here/'backbone_transfer.py')]
        subprocess.run(cmd+[str(source),'--output',str(output)],capture_output=True,text=True,check=True,timeout=30)
        v=subprocess.run(cmd+[str(output),'--verify'],capture_output=True,text=True,check=True,timeout=30)
        assert json.loads(v.stdout)=={'status':'PASS','strict_margin':'1/400'}
        source.write_text('{"actual":[],"actual":[]}',encoding='utf-8')
        assert subprocess.run(cmd+[str(source)],capture_output=True,text=True,timeout=30).returncode
        source.write_bytes(b' '* (bt.MAX_BYTES+1))
        assert subprocess.run(cmd+[str(source)],capture_output=True,text=True,timeout=30).returncode
    return {'status':'PASS','driven_certificate_strict_margin':'1/400',
      'mode_certificate_strict_margin':mode['requested_margin'],'consumer_corruptions_rejected':corruptions,
      'invalid_domain_resource_controls':invalid,'inconclusive_controls':2,'CLI_roundtrip':True,
      'CLI_duplicate_and_byte_cap_controls':2,'generic_interpolation_rank_controls':2,
      'global_arithmetic':bt.global_arithmetic_certificate(),
      'scope':'Physical finite certificate/implementation controls. Genericity is not a pointwise rational-target minimum certificate.'}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(run(),indent=2))
