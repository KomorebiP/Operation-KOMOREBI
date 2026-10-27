from pathlib import Path
import json, math, collections

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "Fermat_Hodge_Global_Closure_Audit.json"
OUT = ROOT / "Fermat_Hodge_CRT_Kummer_Polyphase_VERIFICATION.json"

def units(n):
    return [u for u in range(1,n) if math.gcd(u,n)==1]

def lpr(x,n):
    r=x%n
    return n if r==0 else r

def balanced(packet,n):
    return all(sum(lpr(u*a,n) for a in packet)==len(packet)//2*n for u in units(n))

def phase_profile(packet):
    c=[0]*5
    for a in packet:
        c[a%5]+=1
    return tuple(c)

def canonical_phase_profile(profile):
    images=[]
    for u in (1,2,3,4):
        p=[0]*5
        for r,c in enumerate(profile):
            p[(u*r)%5]=c
        images.append(tuple(p))
    return min(images)

def reduce_four_phase(packet,m):
    q=m//5
    if math.gcd(q,5)!=1:
        return None
    nz=[a for a in packet if a%5]
    z=[a for a in packet if not a%5]
    if len(nz)!=4 or len(z)!=2:
        return None
    bases=[a%q or q for a in nz]
    if len(set(bases))!=1:
        return None
    b=bases[0]%q
    c,d=(z[0]//5)%q,(z[1]//5)%q
    e=(-pow(5,-1,q)*b)%q or q
    lower=tuple(sorted((b,c or q,d or q,e)))
    return lower

data=json.loads(AUDIT.read_text())
res=data["finite_audit"]["no_sat_certificate_orbits"]
profiles=collections.Counter()
records=[]
for ms,packets in res.items():
    m=int(ms)
    if m%5:
        continue
    for packet in packets:
        profiles[canonical_phase_profile(phase_profile(packet))]+=1
        lower=reduce_four_phase(packet,m)
        if lower is not None:
            records.append({
                "degree":m,
                "packet":packet,
                "lower":list(lower),
                "upper_balanced":balanced(packet,m),
                "lower_balanced":balanced(lower,m//5),
            })
out={
    "profile_counts":{str(k):v for k,v in profiles.items()},
    "four_phase_record_count":len(records),
    "all_checks_passed":all(r["upper_balanced"] and r["lower_balanced"] for r in records),
    "records":records,
}
OUT.write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
