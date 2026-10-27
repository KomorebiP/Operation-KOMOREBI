from __future__ import annotations
import copy, itertools, json, os, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from semantic_interface import (FiniteMachine, d4_fixture, labels, horizon_partition, minimal_partition,
    make_certificate, verify_certificate, checkpoint, restore, quotient_step, emit_osl, digest)

class InterfaceTests(unittest.TestCase):
    def test_nonempty_total_machine(self):
        with self.assertRaises(ValueError):FiniteMachine((),('a',),((),),())
        with self.assertRaises(ValueError):FiniteMachine(('s',),('a',),((True,),),('y',))
        with self.assertRaises(ValueError):FiniteMachine(('s',),('a',),((1,),),('y',))

    def test_minimal_exact_d4_quotient(self):
        m=d4_fixture();q=minimal_partition(m)
        self.assertEqual(len(set(q)),8)
        for a in range(8):self.assertEqual(q[2*a],q[2*a+1])
        self.assertTrue(verify_certificate(m,make_certificate(m)))

    def test_current_answer_not_enough_for_continuation(self):
        m=FiniteMachine(('00','01','10','11'),('swap',),((0,2,1,3),),('0','0','1','1'))
        self.assertEqual(len(set(horizon_partition(m,0))),2)
        self.assertEqual(len(set(horizon_partition(m,1))),4)
        self.assertEqual(minimal_partition(m),(0,1,2,3))

    def test_independent_checker_rejects_unsound_partition(self):
        m=d4_fixture();c=make_certificate(m)
        c['partition']=[0]*16;c['observations']=['0,0'];c['transitions']=[[0],[0],[0]]
        c['certificate_digest']=digest({k:v for k,v in c.items() if k!='certificate_digest'})
        self.assertFalse(verify_certificate(m,c))

    def test_finer_valid_partition_is_sound_not_claimed_minimal(self):
        m=d4_fixture();c=make_certificate(m)
        c.update(partition=list(range(16)),observations=list(m.observations),transitions=[list(t) for t in m.transitions])
        c['certificate_digest']=digest({k:v for k,v in c.items() if k!='certificate_digest'})
        self.assertTrue(verify_certificate(m,c))

    def test_stale_machine_rejected(self):
        m=d4_fixture();c=make_certificate(m)
        other=FiniteMachine(m.states,m.alphabet,m.transitions,tuple('other' for _ in m.states))
        self.assertFalse(verify_certificate(other,c))

    def test_invalid_scopes_never_admitted(self):
        m=d4_fixture();c=make_certificate(m);c['scope']='all_neural_networks'
        c['certificate_digest']=digest({k:v for k,v in c.items() if k!='certificate_digest'})
        self.assertFalse(verify_certificate(m,c));self.assertNotIn('\nadmit ',emit_osl(m,c,0))

    def test_json_and_shape_validation(self):
        m=d4_fixture();c=make_certificate(m)
        for item in [None, [], {'schema':'x'}, {**c,'surplus':0}]:self.assertFalse(verify_certificate(m,item))
        for v in [True,-1,16,1.5,'0']:
            bad=copy.deepcopy(c);bad['partition'][0]=v
            bad['certificate_digest']=digest({k:v for k,v in bad.items() if k!='certificate_digest'})
            self.assertFalse(verify_certificate(m,bad))

    def test_roundtrip_checkpoint_and_private_erasure(self):
        m=d4_fixture();c=make_certificate(m)
        self.assertEqual(checkpoint(m,c,0),checkpoint(m,c,1))
        p=json.loads(json.dumps(checkpoint(m,c,7)))
        self.assertEqual(restore(m,c,p),c['partition'][7])

    def test_checkpoint_scope_and_digest_binding(self):
        m=d4_fixture();c=make_certificate(m);p=checkpoint(m,c,0)
        for field,val in [('scope','universal'),('class',True),('machine_digest','0'*64),('certificate_digest','1'*64)]:
            bad={**p,field:val};bad['checkpoint_digest']=digest({k:v for k,v in bad.items() if k!='checkpoint_digest'})
            with self.assertRaises(ValueError):restore(m,c,bad)

    def test_total_future_commutation(self):
        m=d4_fixture();c=make_certificate(m)
        for word in itertools.product(m.alphabet,repeat=5):
            for s in range(16):
                z=s;q=c['partition'][s]
                for a in word:z=m.step(z,a);q=quotient_step(m,c,q,a)
                self.assertEqual(m.observations[z],c['observations'][q])

    def test_d4_relations_on_quotient(self):
        m=d4_fixture();c=make_certificate(m)
        for word in [('r',)*4,('f','f'),('f','r','f','r')]:
            for q in range(8):
                z=q
                for a in word:z=quotient_step(m,c,z,a)
                self.assertEqual(q,z)

    def test_fresh_process_restoration(self):
        m=d4_fixture();c=make_certificate(m);p=checkpoint(m,c,11)
        code='from semantic_interface import *; import json,sys; x=json.load(sys.stdin); print(restore(d4_fixture(),x["c"],x["p"]))'
        done=subprocess.run([sys.executable,'-B','-c',code],cwd=ROOT,input=json.dumps({'c':c,'p':p}),text=True,capture_output=True,check=True)
        self.assertEqual(int(done.stdout),c['partition'][11])

    def test_finite_exhaustive_three_state_machines(self):
        # 216 exact single-action machines; no learned or sampled population claim.
        for t in itertools.product(range(3),repeat=3):
            for obs in itertools.product(('0','1'),repeat=3):
                m=FiniteMachine(('x','y','z'),('a',),(t,),obs);c=make_certificate(m)
                self.assertTrue(verify_certificate(m,c))
                self.assertEqual(tuple(c['partition']),horizon_partition(m,3))
                for i in range(3):
                    for j in range(3):
                        a,b=i,j;eq=True
                        for _ in range(4):
                            eq=eq and m.observations[a]==m.observations[b];a=t[a];b=t[b]
                        self.assertEqual(c['partition'][i]==c['partition'][j],eq)

    def test_source_is_explicit_about_trust_root(self):
        m=d4_fixture();c=make_certificate(m);s=emit_osl(m,c,0)
        self.assertIn('attest origin',s);self.assertIn('verify_receipts',s)
        self.assertNotIn('write_memory',s)

if __name__=='__main__':unittest.main()
