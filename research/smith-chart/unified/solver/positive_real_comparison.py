"""Rational budgets from the written positive-real Rayleigh comparison.
Author: Komorebi P. Not an imaginary-frequency or measured-tolerance theorem.
"""
from fractions import Fraction as F
import hashlib,json
from resonant_mode_face import checked_edges,port_component,certificate as mode_certificate,rational,serialized
from pure_type_margins import gamma


def relative_bound(epsilon):
    epsilon=rational(epsilon)
    if not 0<=epsilon<1:raise ValueError('Relative error must be in[0,1)')
    return epsilon/(2*(1-epsilon))


def near_mode_certificate(edges,ideal_reactive_values,mode,opened_R=(),epsilon=F(1,100),requested_margin=None):
    edges=checked_edges(edges);epsilon=rational(epsilon);tol=relative_bound(epsilon)
    ids=[j for j,e in enumerate(edges) if e[0]!='R'];ideal=list(map(rational,ideal_reactive_values))
    if len(ideal)!=len(ids) or any(x<=0 for x in ideal):raise ValueError('One positive ideal value for each retained reactive branch required')
    adjusted=list(edges)
    for j,target in zip(ids,ideal):
        k,u,v,x=edges[j]
        if not (1-epsilon)*target<=x<=(1+epsilon)*target:raise ValueError('Actual value outside declared relative box')
        adjusted[j]=(k,u,v,target)
    opened_R=list(opened_R)
    if any(type(j)!=int for j in opened_R) or len(opened_R)!=len(set(opened_R)) or any(j<0 or j>=len(edges) or edges[j][0]!='R' for j in opened_R):raise ValueError('Distinct actual resistor indices required')
    cut=2*sum((1/edges[j][3] for j in opened_R),F(0))
    face=[e for j,e in enumerate(adjusted) if j not in opened_R];face,reached=port_component(face)
    if 0 not in reached:
        baseline={'kind':'inversion-symmetric','mechanism':'open port'};base=abs(gamma(F(2))-gamma(F(1,2)))/2
    elif sum(k!='R' for k,u,v,x in face)<=3:
        baseline={'kind':'lower-budget','mechanism':'smaller port component'};base=F(1,10**13)
    else:
        if not isinstance(mode,dict) or any(v not in mode and str(v) not in mode for v in reached):raise ValueError('Mode data missing a retained vertex')
        w={v:mode[v] if v in mode else mode[str(v)] for v in reached}
        baseline=mode_certificate(face,w)
        base=F(baseline['two_sample_weak_margin']) if baseline['kind']=='inversion-symmetric' else F(baseline['strict_margin'])
    slack=base-tol-cut
    if slack<=0:raise ValueError('No positive margin: budget is inconclusive')
    margin=slack/2 if requested_margin is None else rational(requested_margin)
    if not 0<margin<slack:raise ValueError('Requested strict margin must be below proved slack')
    return {'format':'komorebi-balanced-near-mode-v1','status':'PASS',
      'input_sha256':hashlib.sha256(json.dumps(serialized(edges),separators=(',',':')).encode()).hexdigest(),
      'ideal_reactive_values':list(map(str,ideal)),'relative_error':str(epsilon),'relative_response_bound':str(tol),
      'opened_R_indices':sorted(opened_R),'opening_response_bound':str(cut),'face_certificate':baseline,
      'face_margin':str(base),'remaining_slack':str(slack),'strict_margin':str(margin),
      'scope':'Same positive-real Laplace samples, ordinary passive graph, supplied relative reactive box and resistor opening budget. Allowed resistor values and count are unrestricted. No whole balanced-class, imaginary-frequency or hardware claim.'}


def verify(edges,ideal,mode,opened_R,epsilon,record):
    expected=near_mode_certificate(edges,ideal,mode,opened_R,epsilon,record.get('strict_margin'))
    if record!=expected:raise ValueError('Near-mode certificate binding differs')
    return {'status':'PASS','strict_margin':record['strict_margin']}


def main():
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description='Exact positive-real near-mode margin producer/consumer.')
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.source.stat().st_size>262144:raise ValueError('Input exceeds consumer byte cap')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('Duplicate JSON field')
            out[key]=value
        return out
    data=json.loads(args.source.read_bytes(),object_pairs_hook=unique);spec=data['input'] if args.verify else data
    if not isinstance(spec,dict) or set(spec)-{'edges','ideal_reactive_values','mode','opened_R_indices','relative_error','requested_margin'}:raise ValueError('Unexpected specification fields')
    call=(spec['edges'],spec['ideal_reactive_values'],spec['mode'],spec.get('opened_R_indices',()),spec['relative_error'])
    if args.verify:
        if set(data)!={'input','certificate'}:raise ValueError('Producer result requires input and certificate only')
        if spec.get('requested_margin') is not None and rational(spec['requested_margin'])!=rational(data['certificate']['strict_margin']):raise ValueError('Requested margin binding differs')
        result=verify(*call,data['certificate'])
    else:result={'input':spec,'certificate':near_mode_certificate(*call,spec.get('requested_margin'))}
    raw=json.dumps(result,indent=2)+'\n'
    if args.output:
        if args.output.resolve()==args.source.resolve():raise ValueError('Choose an output different from the input')
        args.output.write_text(raw,encoding='utf-8')
    else:print(raw,end='')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
