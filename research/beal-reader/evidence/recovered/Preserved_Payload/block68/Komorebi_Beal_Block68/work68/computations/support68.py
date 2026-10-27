#!/usr/bin/env python3
"""Extract exact bounded-support consequences, retaining every surviving tuple."""
import argparse,json,collections,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sieve',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
d=json.loads(a.sieve.read_text());s=d['expanded28']['survivors'];assert len(s)==d['expanded28']['count'] and s
supports=[tuple(q for q,x in zip(t['columns'],t['inertia']) if x) for t in s]
patterns=collections.Counter(tuple(q for q in ss if q in (307,797,1483)) for ss in supports)
lengths=collections.Counter(map(len,supports));ratios=collections.Counter(t['alpha'][1] for t in s)
assert min(map(len,supports))==7 and min(map(len,patterns))==2
small=[t for t,ss in zip(s,supports) if len(ss)==7]
assert len(small)==2
stage={str(ell):sum(z['counts'][rec['tests'].index(ell)] for rec in d['expanded28']['stages'] for z in rec['records']) for ell in (1051,701,911,1009)}
out={'schema':'beal.block68.support.v1','status':'PASS_BOUNDED_SUPPORT_AUDIT','scope':'Actual depth one; complete beta ramification at rational primes <=2000; all inherited hypotheses','final_count':len(s),'stages':stage,'minimum_rational_support':7,'minimum_new_support':2,'new_support_patterns':[{'primes':list(k),'count':v} for k,v in sorted(patterns.items())],'support_size_counts':dict(sorted(lengths.items())),'ratio_counts':dict(sorted(ratios.items())),'minimal_support_survivors':small,'no_globally_mandatory_single_prime':not set.intersection(*map(set,supports)),'nonclaims':['Not an exclusion of all conductors <=2000','No global prime-support lower bound without the <=2000 scope','No Frey realization of any candidate','No single one of3077971483 is forced by this finite system']}
a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],len(s),stage)
