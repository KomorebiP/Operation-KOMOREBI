#!/usr/bin/env python3
"""Independent checks of stored coefficient records, not Euler reconstruction."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def ev(a, x, m):
    y = 0
    for c in reversed(a):
        y = (y*x + int(c)) % m
    return y


def val(a, bits):
    a %= 1 << bits
    return (a & -a).bit_length()-1 if a else bits


def affine(a, s, k, bits):
    m = 1 << bits
    step = 1 << k
    degree = min(len(a)-1, (bits-1)//k) if k else len(a)-1
    out = [0]*(degree+1)
    for c in reversed(a):
        for i in range(degree, 0, -1):
            out[i] = (s*out[i] + step*out[i-1]) % m
        out[0] = (s*out[0] + int(c)) % m
    while len(out)>1 and not out[-1]:
        out.pop()
    return out


def reduction(a, s, k, content):
    shifted = affine(a, s, k, content+1)
    assert all(c % (1 << content) == 0 for c in shifted)
    out = [c >> content for c in shifted]
    while len(out)>1 and not out[-1]:
        out.pop()
    return out


def cover(leaves):
    assert sum((Fraction(1, 1 << x['k']) for x in leaves), Fraction()) == 1
    for i, x in enumerate(leaves):
        assert 0 <= x['s'] < 1 << x['k']
        for y in leaves[:i]:
            assert (x['s']-y['s']) % (1 << min(x['k'],y['k']))


def check_phases():
    out = []
    for L in (639,641):
        path = ROOT/'next/critical_phases'/f'phase_{L}.json'
        data = json.loads(path.read_text())
        template = data['template']; P=template['precision']; m=1 << P
        low, high = template['low'], template['high']
        certs=data['certificates']
        assert len(certs)==1
        cert=certs[0]
        assert (cert['parameter_residue'],cert['parameter_exponent'])==(1,1)
        size=max(len(low),len(high))
        f0=[((low[i] if i<len(low) else 0)+(high[i] if i<len(high) else 0))%m
            for i in range(size)]
        f1=[(2*c)%m for c in low]
        cover(cert['atlas'])
        roots=0
        for leaf in cert['atlas']:
            c=leaf['value'] if leaf['kind']=='constant' else leaf['content']
            assert c<P
            a=reduction(f0,leaf['s'],leaf['k'],c)
            b=reduction(f1,leaf['s'],leaf['k'],c)
            assert [a,b]==[leaf['red0'],leaf['red1']]
            if leaf['kind']=='constant':
                assert [a,b]==[[1],[0]]
            else:
                assert leaf['kind']=='simple_root'
                assert len(a)==2 and a[1]==1 and len(b)==1
                roots+=1
        assert roots==cert['root_count']
        out.append({'L':L,'leaves':len(cert['atlas']),'roots':roots,
                    'coefficient_reductions':'passed','partition':'passed'})
    return out


def check_epsilon():
    path=ROOT/'next/unit_identity/run_272/results.json'
    data=json.loads(path.read_text()); out=[]
    for rec in data['records']:
        jets=[[int(c) for c in row] for row in rec['jet']]
        bits=rec['local_coefficient_bits']; N=rec['joint_lift_bits']; M=1 << N
        assert N==bits-1==93
        assert rec['omitted_eta_power_valuation_lower_bound']>=bits
        qjets=[]
        for row in jets:
            assert all(i*c%2==0 for i,c in enumerate(row))
            qjets.append([i*row[i]//2 for i in range(1,len(row))])
        def at(js,e,z,m):
            return ev([ev(row,z,m) for row in js],e,m)
        eta=z=0
        for k in range(N):
            step=1 << k; m=step*2
            successors=[(eta+u*step,z+v*step) for u in (0,1) for v in (0,1)
                        if at(jets,eta+u*step,z+v*step,m)==0
                        and at(qjets,eta+u*step,z+v*step,m)==0]
            assert len(successors)==1
            eta,z=successors[0]
        assert eta==int(rec['eta_star_residue']) and z==int(rec['critical_Z_residue'])
        c=0
        for k in range(N):
            m=1 << (k+1)
            candidates=[u for u in (c,c+(1 << k)) if ev(qjets[0],u,m)==0]
            assert len(candidates)==1
            c=candidates[0]
        phi0=ev(jets[0],c,M)
        assert phi0==int(rec['depleted_critical_value_residue'])
        assert val(phi0,N)==val(eta,N)==rec['eta_star_valuation_or_bound']
        # Check the exact isometry statement only on these finite sample pairs.
        test_etas=[0,1,2,3,5,eta]
        phis=[]
        for e in test_etas:
            c=0
            for k in range(N):
                m=1 << (k+1)
                candidates=[u for u in (c,c+(1 << k)) if at(qjets,e,u,m)==0]
                assert len(candidates)==1
                c=candidates[0]
            phis.append(at(jets,e,c,M))
        pairs=0
        for i,e in enumerate(test_etas):
            for j,f in enumerate(test_etas[:i]):
                assert val(phis[i]-phis[j],N)==val(e-f,N)
                pairs+=1
        out.append({'T':rec['integer_T'],'joint_bits':N,'successors_checked':4*N,
                    'eta_valuation':val(eta,N),'sample_isometry_pairs':pairs})
    return out


def check_middle_and_composition():
    data=json.loads((ROOT/'next/critical_phases/phase_640.json').read_text())
    A,C,W=data['low_local'],data['high_local'],data['wronskian']
    P=64; M=1 << P
    # Recompute the polynomial elimination before inspecting its two leaves.
    wc=[0]*max(1,len(A)+len(C)-2)
    for i,a in enumerate(A):
        for j,c in enumerate(C):
            if i+j:
                wc[i+j-1]=(wc[i+j-1]+(j-i)*a*c)%M
    while len(wc)>1 and not wc[-1]:
        wc.pop()
    assert wc==W
    leaves=data['wronskian_atlas']; cover(leaves)
    for leaf in leaves:
        c=leaf['value'] if leaf['kind']=='constant' else leaf['content']
        assert reduction(W,leaf['s'],leaf['k'],c)==leaf['reduction']
    assert leaves[0]['reduction']==[1] and leaves[1]['reduction']==[1,1]
    normalized=[x>>4 for x in affine(W,1,1,64)]
    z=0
    for k in range(60):
        m=1 << (k+1)
        candidates=[x for x in (z,z+(1 << k)) if ev(normalized,x,m)==0]
        assert len(candidates)==1
        z=candidates[0]
    y=1+2*z; m=1 << 61
    assert ev(A,y,m)%2
    b=(-ev(C,y,m)*pow(ev(A,y,m),-1,m))%m
    assert y==data['candidate_Y'] and b==data['candidate_B']
    recpath=ROOT/'local_parameter/recenter_1096.json'
    rec=json.loads(recpath.read_text())
    joined=json.loads((ROOT/'next/critical_phases/combined_frontier.json').read_text())
    B=17659+(1 << 18)*int(rec['candidate_T_residue'])
    X=10202+(1 << 15)*int(rec['candidate_Z_residue'])
    assert B==int(joined['candidate_B']) and X==int(joined['candidate_X'])
    assert 0<B<(1 << 935) and 0<X<(1 << 932)
    assert B.bit_length()==933
    assert B%m==b and ((X-90)//128)%m==y
    assert hashlib.sha256(recpath.read_bytes()).hexdigest()==joined['inherited_sha256']
    return {'W_coefficient_reconstruction':'passed','W_leaves':len(leaves),
            'Y_bits':61,'B_bits':61,'composed_B_bits':935,
            'composed_X_bits':932,'canonical_B_bitlength':B.bit_length()}


def check_hashes():
    manifests=[ROOT/'next/unit_identity/run_272/manifest.json',
               ROOT/'next/higher_address/certified_run/manifest.json']
    checked=0
    for path in manifests:
        manifest=json.loads(path.read_text())
        for record in manifest['input_artifacts']+manifest['outputs']:
            p=Path(record['path']); p=p if p.is_absolute() else ROOT/p
            assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],p
            checked+=1
    return checked


def main():
    result={'scope':'Independent modular verification of stored coefficient records and manifests; no original Euler coefficient reconstruction and no universal proof.',
            'phase_atlases':check_phases(),'epsilon_jets':check_epsilon(),
            'middle_phase_and_composition':check_middle_and_composition(),
            'manifest_hashes_checked':check_hashes(),'status':'PASS'}
    path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'STORED_OUTPUT_CHECKS.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
