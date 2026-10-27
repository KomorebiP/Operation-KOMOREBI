#!/usr/bin/env python3
"""Generate deterministic native_decide vectors for Block 12."""
from __future__ import annotations
import json, math
from pathlib import Path
from verify_final_fiber_boundary import concrete_boundary

GENERAL_FILES=8
GENERAL_PER_FILE=120
COMPILER_FILES=2
COMPILER_PER_FILE=60
PRIMES=(2,3,5,7,11,13)

def ndiv(a:int,b:int)->int: return 0 if b==0 else a//b
def nsub(a:int,b:int)->int: return max(a-b,0)
def coarse_k(r:int,h:int)->int: return ndiv(nsub(r,1),h+1)
def qbound(p:int,r:int,h:int)->int: return ndiv(coarse_k(r,h),nsub(p,1))+1
def depth(p:int,r:int,h:int)->int: return ndiv(coarse_k(r,h),p*nsub(p,1))
def core(p:int,K:int)->int:
 d=ndiv(K,p*nsub(p,1))
 return 2*(ndiv(K,nsub(p,1))+1)+p+(p*d*(d+1))//2
def parameter_bound(p:int,r:int,h:int)->int: return core(p,coarse_k(r,h))
def raw_bound(p:int,r:int)->int: return core(p,nsub(r,1))
def prime_bound(p:int,r:int,h:int)->int:
 B=qbound(p,r,h); d=ndiv(nsub(B,1),p)
 return 2*B+p+(p*d*(d+1))//2

def main()->None:
 root=Path(__file__).resolve().parents[1]
 outdir=root/'verification'
 # deterministic, broad totalized cases including p=0 and p=1
 candidates=[]
 rvals=list(range(0,81))+[97,127,128,255,256,511,1024,4097]
 hvals=list(range(0,11))+[13,17,31]
 for p in range(0,33):
  for r in rvals:
   for h in hvals:
    if (17*p+11*r+7*h)%23 in (0,1,2): candidates.append((p,r,h))
 general=candidates[:GENERAL_FILES*GENERAL_PER_FILE]
 assert len(general)==GENERAL_FILES*GENERAL_PER_FILE
 files=[]; count=0
 for idx in range(GENERAL_FILES):
  cases=general[idx*GENERAL_PER_FILE:(idx+1)*GENERAL_PER_FILE]
  lines=['import KomorebiPadic','','namespace KomorebiPadic','']
  for p,r,h in cases:
   K=coarse_k(r,h); B=qbound(p,r,h); d=depth(p,r,h); pb=parameter_bound(p,r,h); rb=raw_bound(p,r)
   lines += [
    f'example : coarseK {r} {h} = {K} ∧',
    f'    quotientSearchBound {p} {r} {h} = {B} ∧',
    f'    coarseRadixDepth {p} {r} {h} = {d} ∧',
    f'    lastRadixBlockQuotient {p} (quotientSearchBound {p} {r} {h}) = {d} ∧',
    f'    maximumLayerCompilerPrimeEnvelopeBound {p} {r} {h} = {pb} ∧',
    f'    maximumLayerCompilerParameterEnvelopeBound {p} {r} {h} = {pb} ∧',
    f'    maximumLayerCompilerRawPrecisionBound {p} {r} = {rb} ∧',
    f'    maximumLayerCompilerParameterEnvelopeBound {p} {r} {h} ≤ maximumLayerCompilerRawPrecisionBound {p} {r} := by',
    '  native_decide',''
   ]; count+=1
  lines += ['end KomorebiPadic','']
  path=outdir/f'LeanParameterEnvelopeVector_{idx+1:02d}.lean'; path.write_text('\n'.join(lines)); files.append(path.name)
 # concrete compiler cases, including retained larger-but-bounded lanes
 cc=[]
 for p in PRIMES:
  for r in range(1,101):
   for h in range(0,7):
    if (13*p+5*r+3*h)%19==0: cc.append((p,r,h))
 cc=cc[:COMPILER_FILES*COMPILER_PER_FILE]
 assert len(cc)==COMPILER_FILES*COMPILER_PER_FILE
 for j in range(COMPILER_FILES):
  cases=cc[j*COMPILER_PER_FILE:(j+1)*COMPILER_PER_FILE]
  lines=['import KomorebiPadic','','namespace KomorebiPadic','']
  for p,r,h in cases:
   out=concrete_boundary(p,r,h)
   total=out['quotient']+out['boundary_tests']+out['representative_tests']
   pb=parameter_bound(p,r,h); rb=raw_bound(p,r)
   lines += [
    f'example : maximumLayerCompilerTotalTests {p} {r} {h} = {total} ∧',
    f'    maximumLayerCompilerTotalTests {p} {r} {h} ≤ maximumLayerCompilerParameterEnvelopeBound {p} {r} {h} ∧',
    f'    maximumLayerCompilerParameterEnvelopeBound {p} {r} {h} = {pb} ∧',
    f'    maximumLayerCompilerTotalTests {p} {r} {h} ≤ maximumLayerCompilerRawPrecisionBound {p} {r} ∧',
    f'    maximumLayerCompilerRawPrecisionBound {p} {r} = {rb} := by',
    '  native_decide',''
   ]; count+=1
  lines += ['end KomorebiPadic','']
  path=outdir/f'LeanParameterCompilerVector_{j+1:02d}.lean'; path.write_text('\n'.join(lines)); files.append(path.name)
 report={'schema':'komorebi-padic-block12-vector-generation-v1','status':'PASS','general_cases':len(general),'compiler_cases':len(cc),'example_count':count,'file_count':len(files),'files':files}
 (root/'results'/'parameter_envelope_vector_generation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__': main()
