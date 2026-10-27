"""Regression controls for exact support and numerical packet API validation."""
import json
import numpy as np
from symmetry_packets import PacketPlan, apply_local_gate_full, circuit_leakage_bound, hamiltonian_leakage_bound, random_packet_state


def main():
    assertions=0
    def rejected(f):
        nonlocal assertions
        try:f()
        except ValueError:assertions+=1
        else:raise AssertionError('invalid input was accepted')
    p=PacketPlan.fixed_weight(2,1)
    for qubits in [(0,0),(2,),(-1,)]:
        gate=np.eye(1<<len(qubits))
        rejected(lambda:p.restrict_gate(gate,qubits))
        rejected(lambda:apply_local_gate_full(np.array([0.,1.,0.,0.]),gate,qubits,2))
    rejected(lambda:PacketPlan(2,(1,1)))
    rejected(lambda:PacketPlan(2,(4,)))
    rejected(lambda:PacketPlan(-1,()))
    rejected(lambda:random_packet_state(PacketPlan(2,())))
    for invalid in [-0.1,float('nan'),float('inf')]:
        rejected(lambda:circuit_leakage_bound([invalid]))
        rejected(lambda:hamiltonian_leakage_bound(1,invalid))
    rejected(lambda:p.restrict_gate(np.full((2,2),np.nan),(0,)))
    rejected(lambda:apply_local_gate_full(np.ones(4),np.full((2,2),np.nan),(0,),2))
    # The old implementation silently accepted this off-packet coefficient:
    # its squared leakage falls below the old 1e-12 threshold.
    for epsilon in [1e-7,1e-200]:
        gate=np.array([[np.sqrt(1-epsilon**2),-epsilon],[epsilon,np.sqrt(1-epsilon**2)]])
        rejected(lambda:p.restrict_gate(gate,(0,)))
    # A real input vector must accept a complex gate without losing imaginary parts.
    state=np.array([1.,0.])
    got=apply_local_gate_full(state,np.array([[1j,0],[0,-1j]]),(0,),1)
    assert np.array_equal(got,np.array([1j,0]));assertions+=1
    print(json.dumps({'status':'PASS','assertions':assertions,'non_claims':['No symbolic exactness claim for floating matrices.']}))

if __name__=='__main__':main()
