#!/usr/bin/env python3
"""Test a candidate arithmetic exclusion, not universal simplicity.

Construct an ordinary admissible Euler index whose depleted stationary value
has ODD valuation91 and normalized leading unit15 modulo32. This tests whether
either feature is forbidden by the actual Bernoulli coefficients independently
of the crucial relation N=2r-25. The latter relation is NOT tested or asserted.
"""
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Euler_Coupled_Stationarity_2026-10-05'

def ev(poly, x, modulus):
    out = 0
    for a in reversed(poly):
        out = (out * x + a) % modulus
    return out

def main():
    output = Path(sys.argv[1])
    model = json.loads((BASE / 'coupled/parameter_geometry/model_coefficients.json').read_text())
    h0, h1 = ([int(a) for a in model[k]] for k in ('H0', 'H1'))
    q0, q1 = ([i * a // 2 for i, a in enumerate(h) if i] for h in (h0, h1))
    assert all((i*a) % 2 == 0 for h in (h0,h1) for i,a in enumerate(h))
    N, bits, unit = 91, 96, 15
    target = unit << N
    T = Z = 0
    for b in range(1, bits + 1):
        step, mod = 1 << (b-1), 1 << b
        candidates = []
        for t in (T, T+step):
            B = 17659 + (t << 18)
            for z in (Z, Z+step):
                if (ev(h0,z,mod) + t*ev(h1,z,mod) - B*target) % mod == 0 and (ev(q0,z,mod) + t*ev(q1,z,mod)) % mod == 0:
                    candidates.append((t,z))
        assert len(candidates) == 1, (b, candidates)
        T,Z = candidates[0]
    # Reconstruct all actual packets from the ordinary index, independently of
    # the model equation used to choose T. Reuse the audited direct packet path.
    engine_path = BASE / 'coupled/packet_balance/build_ledger.py'
    spec = importlib.util.spec_from_file_location('actual_packet_ledger', engine_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    rec, poly = engine.run(T, 'odd_valuation_leading_unit_15')
    value = rec['groups']['total']['value']
    assert value['normalized_valuation'] == N
    assert value['unit_mod65536'] % 32 == unit
    assert (int(rec['stationary_Z']) - Z) % (1 << bits) == 0
    r = int(rec['r'])
    E = 2*r-25
    # Undepletion changes the critical value only at E, so actual and depleted
    # agree throughout the142 certified normalized bits.
    assert E > rec['normalized_value_bits']
    out = {
        'status':'passed',
        'base_checkpoint':'Euler-coupled-stationarity-20261005',
        'candidate_lemma_refuted':'Actual Euler critical values cannot have odd valuation and normalized leading unit15mod32',
        'T':str(T), 'B':rec['B'], 'r':rec['r'],
        'actual_terminal':161, 'mu':-154,
        'target_valuation':N, 'target_unit_mod32':unit,
        'stationary_Z_mod2_96':str(Z),
        'actual_stationary_Z_mod2_141':rec['stationary_Z'],
        'actual_value_record':value,
        'actual_global_precision':rec['precision'],
        'actual_packet_max':rec['computed_packet_max'],
        'actual_nonzero_packets':rec['retained_nonzero_local_packets'],
        'actual_second_derivative':rec['groups']['total']['second_derivative'],
        'actual_parameter_exponent_E':str(E),
        'nonclaim':'This is NOT a singular Euler index. N=91 is vastly smaller than E=2r-25. It does not satisfy the necessary equality v2(Phi_r(0))=E.',
        'proof_of_depleted_agreement':'Inherited fixed-r critical-value correction has exact valuation E, above142 normalized bits.'
    }
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','T','target_valuation','target_unit_mod32','actual_global_precision')}))

if __name__ == '__main__':
    main()
