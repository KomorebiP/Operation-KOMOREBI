#!/usr/bin/env python3
"""Exhaustive first-digit determinant identity in O/49 with w^2=5.
This checks finite algebra, not existence of global Frey representations.
"""
from __future__ import annotations
import argparse,json
from fractions import Fraction
from pathlib import Path

def need(x,msg):
    if not x:raise AssertionError(msg)
def add(x,y,m):return ((x[0]+y[0])%m,(x[1]+y[1])%m)
def neg(x,m):return (-x[0]%m,-x[1]%m)
def mul(x,y,m):return ((x[0]*y[0]+5*x[1]*y[1])%m,(x[0]*y[1]+x[1]*y[0])%m)
def scale(c,x,m):return (c*x[0]%m,c*x[1]%m)
def run():
    residues=[(a,b) for b in range(7) for a in range(7)]
    total=0;nonrational=0;Q=29
    for D in residues:
        d=add((1,0),scale(7,D,49),49);di=add((1,0),scale(-7,D,49),49)
        need(mul(d,di,49)==(1,0),'Principal-unit inverse')
        for b in residues:
            for c in residues:
                bc=mul(b,c,49)
                a=mul(add((Q,0),scale(7,bc,49),49),di,49)
                determinant=add(mul(a,d,49),scale(-7,bc,49),49)
                need(determinant==(Q,0),'Constructed determinant')
                defect=add(add(a,d,49),(-Q-1,0),49)
                need(all(t%7==0 for t in defect),'Trace not scalar mod7')
                need(tuple(t//7 for t in defect)==mul(b,c,7),'Trace product identity')
                total+=1;nonrational+=bool(D[1] or b[1] or c[1])
    # This exact matrix has determinant29 and an admissible rank-two Weil trace -5.
    F=[[-6,1],[-35,1]]
    need(F[0][0]*F[1][1]-F[0][1]*F[1][0]==29,'Good-matrix control determinant')
    tau=F[0][0]+F[1][1];need(tau==-5 and tau*tau<4*29,'Good-matrix control trace')
    need((tau-30)//7%7==2 and (F[0][1]*(F[1][0]//7))%7==2,'Good-matrix control product')
    # Q=1 mod7 is essential, not optional: this matrix has exact determinant3.
    a=Fraction(5,4);d=Fraction(8);b=Fraction(1);c=Fraction(1)
    need(a*d-7*b*c==3,'Nonseparated norm control')
    t=(a+d-4)/7
    reduce=lambda x:x.numerator*pow(x.denominator,-1,7)%7
    need(reduce(t)==6 and reduce(b*c)==1,'Q!=1 control did not falsify strengthening')
    return {'schema':'beal.block62.matrix.v1','status':'PASS_FINITE_MATRIX_IDENTITY',
       'modulus':49,'coefficient_relation':'w^2=5','Q':Q,
       'exhaustive_D_b_c_residual_triples':total,'triples_with_nonrational_input':nonrational,
       'good_case_control':{'matrix':F,'determinant':29,'rank_two_trace':tau,'defect_product_mod7':2,
          'meaning':'Unramified beta may be nonzero at a good place; do not impose the bad toric trace.'},
       'Q_not_one_control':{'matrix':[['5/4',1],[7,8]],'determinant':3,'defect_mod7':6,'bc_mod7':1},
       'nonclaims':['Finite matrix identity is not a global representation','No Lean proof']}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=run();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'triples':d['exhaustive_D_b_c_residual_triples']}))
if __name__=='__main__':main()
