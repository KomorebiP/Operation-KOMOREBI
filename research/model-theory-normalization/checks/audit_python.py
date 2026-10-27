from pathlib import Path
import sys,json,time,random,hashlib,itertools
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'baseline')]
from binary_backend import *
import costed_echelon as old

def main():
 start=time.time(); rng=random.Random(2026092110); counts=Counter()
 def check(condition,label):
  if not condition:raise AssertionError(label)
  counts[label]+=1
 for a,b in itertools.product(range(64),repeat=2):
  x,y=encode(a),encode(b);B=max(len(x),len(y))
  for carry in (0,1):
   s,c=add_eval(x,y,carry)
   check(decode(s)==a+b+carry,'unsigned_add')
   check(c==10*B+1 and len(s)==B+1,'adder_cost_length')
   xx,yy=pad(x,B),pad(y,B);(z,borrow),sc=sub_eval(xx,yy,carry)
   check(decode(z)+b+carry==a+(1<<B)*borrow,'subtractor_borrow_identity')
   check(sc==12*B+1 and len(z)==B,'subtractor_cost_length')
  p,c=mul_eval(x,y)
  check(decode(p)==a*b,'unsigned_multiply')
  check(c<=32*(B+1)**2,'multiply_quadratic_budget')
 for a in range(256):
  for b in range(1,32):
   x,y=encode(a),encode(b);(q,r),c=div_eval(x,y);B=max(len(x),len(y))
   check((decode(q),decode(r))==divmod(a,b),'unsigned_divmod')
   check(c<=32*(B+1)**2,'division_quadratic_budget')
 for a,b in itertools.product(range(-32,33),repeat=2):
  x,y=Signed.of_int(a),Signed.of_int(b)
  check(signed_add_eval(x,y)[0].value()==a+b,'signed_add')
  B=max(len(x.magnitude),len(y.magnitude))
  check(signed_add_eval(x,y)[1]<=64*(B+1)**2,'signed_add_budget')
  check(signed_mul_eval(x,y)[1]<=64*(B+1)**2,'signed_multiply_budget')
  check(signed_sub_eval(x,y)[1]<=256*(B+1)**2,'signed_subtract_budget')
  check(signed_sub_eval(x,y)[0].value()==a-b,'signed_subtract')
  check(signed_mul_eval(x,y)[0].value()==a*b,'signed_multiply')
 for a in range(-128,129):
  for b in range(1,33):
   (q,r),c=signed_div_eval(Signed.of_int(a),encode(b))
   check((q.value(),decode(r))==divmod(a,b),'signed_euclidean_divmod')
   B=max(abs(a).bit_length(),b.bit_length())
   check(c<=64*(B+1)**2,'signed_division_budget')
 for m in range(1,25):
  for a in range(m):
   for b in range(m):
    x,y,z=encode(a),encode(b),encode(m);B=max(len(x),len(y),len(z))
    out,c=residue_mul_eval(x,y,z)
    check(decode(out)==a*b%m,'residue_multiply')
    check(c<=256*(B+1)**2,'residue_wide_product_budget')
    out,c=residue_add_eval(x,y,z);check(decode(out)==(a+b)%m,'residue_add')
    check(c<=256*(B+1)**2,'residue_add_budget')
 for _ in range(160):
  B=rng.choice([16,32,64,128,256]);a=rng.getrandbits(B);b=rng.getrandbits(B) or 1
  x=encode(a)+(0,)*rng.randrange(4);y=encode(b)+(0,)*rng.randrange(4)
  z,c=mul_eval(x,y);check(decode(z)==a*b,'wide_padded_multiply')
  (q,r),c=div_eval(x,y);check((decode(q),decode(r))==divmod(a,b),'wide_padded_divide')
  (q,r),c=signed_div_eval(Signed(True,x),y);check((q.value(),decode(r))==divmod(-a,b),'wide_signed_divide')
 for w in [(),(0,),(0,0,0,0)]:
  try:div_eval((1,),w)
  except ZeroDivisionError:counts['zero_divisor_rejected']+=1
  else:raise AssertionError('zero divisor accepted')
 for w in [(2,),(-1,),(True,),('0',)]:
  try:validate(w)
  except ValueError:counts['malformed_word_rejected']+=1
  else:raise AssertionError('bad bit accepted')
 # Regression input is separate from the answers. The native implementation is frozen.
 cases=json.loads((ROOT/'baseline/COSTED_CASES.json').read_text());reports=[]
 old_meter=old.Meter
 for case in cases:
  source=json.loads((ROOT/'baseline'/case['source']).read_text())
  native,ns=old.discover_costed(source)
  check(native==case['result'] and ns['units']==case['units'],'frozen_parent_result_count')
  meter=BitMeter()
  old.Meter=lambda:meter
  try:answer,stats=old.discover_costed(source)
  finally:old.Meter=old_meter
  check(answer==native,'bit_backend_discovery_answer')
  check(stats['final_basis']==ns['final_basis'],'bit_backend_canonical_basis')
  check(stats['unit_counts']==ns['unit_counts'],'same_arithmetic_opcode_counts')
  check(stats['units']==ns['units'],'same_arithmetic_total')
  rec={'index':case['index'],'source':case['source'],**meter.report()}
  reports.append(rec)
 out={'status':'PASS','started_unix':start,'runtime_seconds':time.time()-start,
      'seed':2026092110,'counts':dict(counts),'cases':reports,
      'total_arithmetic_events':sum(r['arithmetic_events'] for r in reports),
      'total_gate_cell_units':sum(r['gate_cell_units'] for r in reports),
      'maximum_operand_bits':max(r['maximum_operand_bits'] for r in reports),
      'maximum_output_storage_bits':max(r['maximum_output_storage_bits'] for r in reports),
      'non_claims':['Python is a tested port, not verified extraction',
          'Whole discovery lowering, conversion costs and runtime overhead are not universal Lean cost theorems',
          'Gate/cell costs exclude encoding, decoding, address arithmetic, list allocation, queue control, and native runtime',
          'No held-out discovery or performance comparison']}
 (ROOT/'results/PYTHON_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
 for r in reports[-2:]:print(r['source'],r['arithmetic_events'],r['gate_cell_units'],r['maximum_operand_bits'])
if __name__=='__main__':main()
