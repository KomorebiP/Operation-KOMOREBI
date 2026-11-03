"""Independent exact replay of the finite LSM browser comparison domain."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = 'monographs/large-signal-model/Visual_Companion/figures/exact_example.json'


def check(node):
    retained = json.loads((ROOT/RECEIPT).read_bytes())
    matrix = [[Q(x) for x in row] for row in retained['matrix']]
    assert matrix==[[Q(1,2),Q(1)],[Q(1,4),Q(1,3)]]
    browser_raw = subprocess.check_output([node,'tools/dump_large_signal_explorer.cjs'],cwd=ROOT)
    actual = json.loads(browser_raw)
    def trace(initial,last):
        rows = [list(map(Q,initial))]
        for _ in range(last):
            rows.append([sum((matrix[i][j]*rows[-1][j] for j in range(2)),Q(0)) for i in range(2)])
        return rows
    encode = lambda row:[str(x) for x in row]
    source = trace(retained['initial_state'],12)
    assert [encode(row) for row in source]==retained['trajectory']==actual['original']
    assert retained['probability_data'] is False
    population = {(h,t) for h in range(-2,3) for t in range(9)}
    visited = [(r['h'],r['t']) for r in actual['cases']]
    assert actual['max_step']==8 and len(visited)==45 and set(visited)==population and len(set(visited))==45
    forecasts = 0
    for case in actual['cases']:
        h,t = case['h'],case['t'];a,b=trace([0,0],t+1),trace([0,h],t+1)
        assert case['states']==[encode(a[t]),encode(b[t])]
        assert case['outputs']==[str(a[t][0]),str(b[t][0])]
        assert case['next']==[str(a[t+1][0]),str(b[t+1][0])]
        assert case['observed']==[[str(a[i][0]),str(b[i][0])] for i in range(t+1)]
        if t:
            assert case['histories']==[[str(a[t-1][0]),str(a[t][0])],[str(b[t-1][0]),str(b[t][0])]]
            expected=[Q(1,12)*rows[t-1][0]+Q(5,6)*rows[t][0] for rows in (a,b)]
            assert case['delayed']==[str(x) for x in expected]
            assert expected==[a[t+1][0],b[t+1][0]]
            forecasts+=2
        else:
            assert case['histories'] is None and case['delayed'] is None
    y=[row[0] for row in source]
    for t in range(1,12):assert y[t+1]==Q(5,6)*y[t]+Q(1,12)*y[t-1]
    for t in range(12):
        memory=Q(1,2)*y[t]+sum((Q(1,4)*Q(1,3)**j*y[t-1-j] for j in range(t)),Q(0))
        assert memory==y[t+1]
    return dict(schema=1,status='PASS',assertion_tested='Exact browser state, history, forecast, and observed-output values on the complete declared finite UI domain; retained rational trajectory and its finite delay/memory identities.',
        coefficient_domain='Q',hidden_coordinates=list(range(-2,3)),observed_steps=[0,8],next_output_steps=[1,9],
        compared_cases=45,delay_forecasts=forecasts,retained_trajectory_states=13,retained_delay_steps=11,retained_memory_steps=12,
        receipt=RECEIPT,receipt_sha256=hashlib.sha256((ROOT/RECEIPT).read_bytes()).hexdigest(),
        browser_output_sha256=hashlib.sha256(browser_raw).hexdigest(),case_records=actual['cases'],original_trace=actual['original'],
        software=dict(python=sys.version.split()[0],node=subprocess.check_output([node,'--version'],text=True).strip()),
        non_claims=['No universal theorem follows from the finite replay.','No learned model, statistical performance, or probability data.','No new Lean execution or original PDF rebuild.','Floating chart positions are not the exact arithmetic record.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',default='node');parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=check(args.node)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'case_records','original_trace'}}))
