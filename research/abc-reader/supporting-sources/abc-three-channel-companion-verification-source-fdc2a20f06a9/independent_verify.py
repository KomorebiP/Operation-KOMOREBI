from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import fitz
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

ROOT=Path(__file__).resolve().parent


def rad(n:int)->int:
    r=1
    for p in sp.factorint(abs(n)): r*=int(p)
    return r


def check_row(row:dict[str,str])->None:
    a=int(row['a']);b=int(row['b']);c=int(row['c']);A=int(row['A']);L=int(row['L'])
    assert c==a+b
    assert A==a*a+a*b+b*b
    assert L==(a-b)*(a+2*b)*(2*a+b)
    C=sp.Matrix([[a*c,b*c,-a*b],[-a*b,a*c,b*c],[b*c,-a*b,a*c]])
    assert C*C.T==A*A*sp.eye(3)
    S=smith_normal_form(C,domain=ZZ)
    diag=[abs(int(S[i,i])) for i in range(3)]
    assert diag==[1,A,A*A]
    assert math.gcd(A,a*b*c)==1
    assert math.gcd(abs(L),a*b*c)==2
    assert math.gcd(A,abs(L)) in (1,3)
    assert L*L+27*a*a*b*b*c*c==4*A**3


def main()->None:
    groups={}
    for name in ['worked_examples.csv','random_audit.csv']:
        path=ROOT/'tables'/name
        count=0
        with path.open(newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                check_row(row);count+=1
        groups[name]=count

    # Figure pairing.
    pdfs={p.stem for p in (ROOT/'figures').glob('*.pdf')}
    pngs={p.stem for p in (ROOT/'figures').glob('*.png')}
    assert pdfs==pngs and len(pdfs)==8
    groups['figure_pairs']=len(pdfs)

    # PDF integrity and page-density check.
    doc=fitz.open(ROOT/'ABC_Three_Channel_Companion_Verification.pdf')
    assert len(doc)==30
    low=[]
    for i,page in enumerate(doc):
        words=page.get_text('words')
        if len(words)<25: low.append(i+1)
    assert not low
    groups['pdf_pages']=len(doc)
    groups['pages_below_25_words']=low

    # Result ledger agreement.
    result=json.loads((ROOT/'results'/'verification_results.json').read_text())
    assert result['all_random_checks_passed']
    assert result['all_worked_checks_passed']
    assert result['record']['A_is_prime']
    groups['record_A']=result['record']['A']

    output={'status':'all_independent_checks_passed','groups':groups}
    (ROOT/'results'/'independent_verification.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__': main()
