from collections import defaultdict
from math import gcd
from pathlib import Path
import json
import sys
from packet_core import shell,weight,tau_from_product

t=tau_from_product(121)
groups=defaultdict(int)
for v in shell(121):groups[gcd(*v)]+=weight(v)
assert t[11]==534612
assert t[121]==t[11]**2-11**11==498319933
assert dict(groups)=={1:-25439104668,11:25937424601}
assert groups[11]==11**10 and sum(groups.values())==t[121]
out={'status':'PASS','n':121,'tau_11':t[11],'tau_121':t[121],
     'content_masses':dict(groups),'independent_formulas':['Direct defining product','Hecke recurrence','Direct content shell enumeration']}
Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
