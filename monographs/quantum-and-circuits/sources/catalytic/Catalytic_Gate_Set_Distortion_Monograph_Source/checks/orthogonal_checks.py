#!/usr/bin/env python3
"""Exact bounded independent invariants for the packaged catalytic atlas.

Contract: verify every elementary symplectic generator at n=1,2,3 by
independent dense arithmetic; compare 0-1 BFS with heap Dijkstra on n=2
Clifford and n=3 reversible groups; verify exported witness symplectic
endpoints; verify no-ancilla parity at four bits. These are finite checks,
not a proof for larger n. Run with PYTHONPATH pointing at component/code.
"""
import json, subprocess, hashlib, time, sys, platform, os
from pathlib import Path
from catalytic_gate_atlas import exact_clifford_census
from catalytic_gate_atlas.clifford import ambient_generators, parabolic_generators
from catalytic_gate_atlas.reversible import toffoli_generators
from catalytic_gate_atlas.algebra import gf2_identity, gf2_mul, perm_identity, perm_compose
from catalytic_gate_atlas.search import zero_one_distances, dijkstra_distances

def dense_mul(A,B):
 return [[sum(A[i][k]*B[k][j] for k in range(len(B)))%2 for j in range(len(B[0]))] for i in range(len(A))]
def transpose(A): return [list(r) for r in zip(*A)]
def dense(bits):return [[(r>>j)&1 for j in range(len(bits))] for r in bits]
def parity(p):return sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))%2
checks=[]
for n in (1,2,3):
 J=[[int((i+n)%(2*n)==j) for j in range(2*n)] for i in range(2*n)]
 gens=ambient_generators(n,include_swap=True)
 for g in gens:
  A=dense(g.element)
  assert dense_mul(dense_mul(transpose(A),J),A)==J
 checks.append({'name':'independent_dense_symplectic_generators','n':n,'generators':len(gens),'status':'PASS'})
for family in ('clifford2','reversible3'):
 if family=='clifford2':
  e=gf2_identity(4);gs=ambient_generators(2,entangling_cost=True);mul=gf2_mul
 else:e=perm_identity(8);gs=toffoli_generators(3,entangling_cost=True);mul=perm_compose
 a=zero_one_distances(e,gs,mul);b=dijkstra_distances(e,gs,mul)
 assert a==b
 checks.append({'name':'all_distances_01bfs_equal_dijkstra','family':family,'states':len(a),'status':'PASS'})
for n in (1,2):
 for metric in ('total','entangling'):
  py=exact_clifford_census(n,entangling_cost=metric=='entangling',with_witness=False)
  cpp=json.loads(subprocess.check_output([os.environ['CATALYTIC_CENSUS_BINARY'],'--n',str(n),'--metric',metric],text=True))
  assert py==cpp
  checks.append({'name':'independent_python_cpp_census','n':n,'metric':metric,'states':py['ambient_group_size'],'status':'PASS'})
words=[(2,['CX01','S1','CX10','CX01'],['H1','CX10','CX01','H0','S1','S0']), (3,['CX02','CZ12','CX20','CX02','CX01','CX10','CX01'],['H1','CX12','CX21','CX20','CX02','H0'])]
for n,r,a in words:
 gs={g.name:g.element for g in ambient_generators(n)}
 def evaluate(w):
  A=gf2_identity(2*n)
  for x in w:A=gf2_mul(gs[x],A)
  return A
 assert evaluate(r)==evaluate(a)
 checks.append({'name':'displayed_witness_endpoint_equality','n':n,'status':'PASS','equality':'binary symplectic action only'})
gs=toffoli_generators(4)
assert all(parity(g.element)==0 for g in gs)
checks.append({'name':'four_bit_gate_parity','generators':len(gs),'status':'PASS','parity':'even'})
# Verify the four-member analytic family against the full two-qubit maps.
gs=ambient_generators(2,entangling_cost=True)
ambient=zero_one_distances(gf2_identity(4),gs,gf2_mul)
restricted=zero_one_distances(gf2_identity(4),parabolic_generators(2,entangling_cost=True),gf2_mul)
family=set()
for d0 in (0,1):
 for d1 in (0,1):
  M=(2,1,1+2*d0+8,2+d1+4)
  family.add(M)
  assert restricted[M]==3 and ambient[M]==2
assert family=={M for M in restricted if restricted[M]>ambient[M]}
checks.append({'name':'analytic_four_target_family_equals_census','family_size':4,'status':'PASS'})
result={'assertion_tested':__doc__,'checks':checks,'python':platform.python_version(),'status':'PASS'}
print(json.dumps(result,indent=2))
