"""Physical controls of the written one-L/one-C minimum-sign theorem.
Author: Komorebi P. These are finite controls, not its universal proof.
"""
from fractions import Fraction as F
from exact_phasor import C,response


def checks():
    rows=[]
    for j in range(12):
        L=F(j+1,3);omega=F(j+2,4);cap=1/(omega*omega*L)
        r1=F(j+2,5);r2=F(7,j+3)
        edges=[('R',1,2,r1),('R',0,3,r2),('C',1,3,cap),('C',0,2,cap),('L',2,3,L)]
        for swapped in (False,True):
            graph=[('C' if k=='L' else 'L' if k=='C' else 'R',u,v,1/value if k!='R' else value)
                   for k,u,v,value in edges] if swapped else edges
            w=1/omega if swapped else omega;solution=response(graph,C(0,w))
            z=C(0,omega*L if swapped else -omega*L)
            assert solution['gamma']==(z-1)/(z+1)
            assert all(not current for (k,_,_,_),current in zip(graph,solution['currents']) if k=='R')
            rows.append({'control':j,'class':'one-C' if swapped else 'one-L','omega':str(w),
              'impedance_imaginary_part':str(z.im),
              'DC':str(r1*r2/(r1+r2) if swapped else r1+r2),
              'infinity':str(r1+r2 if swapped else r1*r2/(r1+r2))})
    return {'status':'PASS','physical_minimum_controls':len(rows),'resistor_zero_current_checks':2*len(rows),
            'controls':rows,'scope':'Only the twenty-four declared graphs. The arbitrary capacitor/resistor-count theorem is a separately written graph argument with a finite phasor-solution hypothesis.'}
