"""Independent rechecks of fresh confirmation, sequential recall, and codec."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from audit_results import audit_bank,world_from_events
ROOT=Path(__file__).resolve().parents[1]
def run():
    conf=ROOT/'runs/confirmation';r=json.loads((conf/'result.json').read_text());entries=0;nb=0
    for model,rows in r.items():
        for key,row in rows.items():entries+=audit_bank(conf/f'{model}__{key}.npz',row);nb+=1
    seq=ROOT/'runs/sequential';s=json.loads((seq/'result.json').read_text());sn=0;se=0
    for model,rows in s.items():
        for name,row in rows.items():
            with np.load(seq/f'{model}__{name}.npz') as d:
                world=world_from_events(d['events']);assert np.array_equal(world,d['world'])
                ys=[]
                for t in range(8):
                    pair=d['pairs'][:,t%4];bits=world[np.arange(len(world))[:,None],pair];ys.append(bits[:,0]+2*bits[:,1])
                target=np.stack(ys,1);assert np.array_equal(target,d['target'])
                cor=d['pred']==target[:,:,None];pr=d['private_pred']==d['roles'][:,None,:]
                assert np.allclose(cor.mean((0,2)),row['stage_accuracy'],rtol=0,atol=1e-12)
                assert np.allclose(pr.mean((0,2)),row['stage_private'],rtol=0,atol=1e-12)
                assert abs(cor[:,:4].all(1).mean()-row['first_pass_all_eight'])<1e-12
                assert abs(cor[:,4:].all(1).mean()-row['second_pass_all_eight'])<1e-12
                assert row['state_reset_between_cues'] is False
                se+=d['pred'].size+d['private_pred'].size;sn+=1
    dc=ROOT/'runs/distributed_control';r=json.loads((dc/'result.json').read_text());ncodec=0;maxerr=0
    for lin in 'AB':
        with np.load(dc/f'{lin}.npz') as d:
            W=d['W'];bias=d['bias'];Wn=d['W_shuffled'];bn=d['bias_shuffled']
            for name,row in r[lin].items():
                x=d[name+'_x'];truth=d[name+'_y'];expected=x@W+bias
                assert np.array_equal(expected,d[name+'_central'])
                ma=d[name+'_message_A'];mb=d[name+'_message_B']
                a=x[:,:64]@W[:64]+bias/2+mb/(1-np.abs(mb))
                b=x[:,64:]@W[64:]+bias/2+ma/(1-np.abs(ma))
                assert np.array_equal(a,d[name+'_A']) and np.array_equal(b,d[name+'_B'])
                assert np.array_equal(a>0,expected>0) and np.array_equal(b>0,expected>0)
                for logits,key in [(expected,'central'),(x@Wn+bn,'shuffled_labels')]:
                    c=(logits>0)==truth;assert abs(float(c.all(1).mean())-row[key]['all_eight'])<1e-12
                    assert abs(float(c.mean())-row[key]['bit_accuracy'])<1e-12
                maxerr=max(maxerr,float(abs(a-expected).max()),float(abs(b-expected).max()));ncodec+=1
    result={'status':'PASS','confirmation_banks':nb,'confirmation_output_entries_rechecked':entries,
            'sequential_banks':sn,'sequential_output_entries_rechecked':se,'distributed_codec_conditions':ncodec,'maximum_float64_codec_error':maxerr,
            'warning':'output entries reuse histories and are not independent experiments'}
    (ROOT/'checks/additional_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
