#!/usr/bin/env python3
"""Export this guide's controlled page macros to editable Markdown.

Not a general LaTeX converter. Exact math blocks are preserved verbatim.
"""
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent

def group(s,start):
    assert s[start]=='{'
    depth=1;i=start+1
    while depth:
        if s[i]=='{' and (i==0 or s[i-1]!='\\'):depth+=1
        elif s[i]=='}' and (i==0 or s[i-1]!='\\'):depth-=1
        i+=1
    return s[start+1:i-1],i

def macros(s,name,count,render):
    key='\\'+name
    at=0
    while True:
        idx=s.find(key,at)
        if idx<0:break
        end=idx+len(key);args=[]
        for _ in range(count):
            while s[end].isspace():end+=1
            arg,end=group(s,end);args.append(arg)
        repl=render(*args);s=s[:idx]+repl+s[end:];at=idx+len(repl)
    return s

def main():
    s=(HERE/'Quantum_Arithmetic_Visual_Body.tex').read_text()
    tables=[
      '| Arithmetic | Signal | Quantum model |\n|---|---|---|\n| Coprime labels | Fourier support | Frequency-basis amplitudes |\n| Rational cyclic projector | Exact convolution filter | Projective measurement |\n| Cyclotomic phase sum | Integer samples | Signed coherent amplitudes |',
      '| Sample | Relevant divisor contribution | Exact result |\n|---|---|---|\n| $n=0$ | $2\\mu(6)+4\\mu(3)+6\\mu(2)+12\\mu(1)$ | $4$ |\n| $n=2$ | $\\mu(12)+2\\mu(6)$ | $2$ |\n| $n=4$ | $\\mu(12)+2\\mu(6)+4\\mu(3)$ | $-2$ |\n| $n=6$ | $\\mu(12)+2\\mu(6)+3\\mu(4)+6\\mu(2)$ | $-4$ |',
      '| Passage | Preserves | Additional requirement or loss |\n|---|---|---|\n| Selector $D$ to $P=FDF^\\dagger$ | Rank, idempotence, orthogonality | A specified unitary Fourier basis |\n| Vector $x$ to $F^\\dagger x$ | Full vector, inner product, norm | Retain all complex coefficients |\n| Vector $x$ to $Px$ | Selected component | Complementary component removed |\n| Vector to all polyphase lanes | All sample values | Every lane and its address retained |\n| Amplitudes to probabilities | Outcome probabilities in one basis | Relative phase discarded |\n| Projective measurement | Born probabilities and conditional state | One outcome per run, conditional branch |'
    ]
    iterator=iter(tables)
    s=re.sub(r'\\begin\{center\}.*?\\end\{center\}',lambda m:'\n'+next(iterator)+'\n',s,flags=re.S)
    s=macros(s,'vpage',3,lambda num,category,title:f'\n\n## {num}. {title}\n\n*{category.title()}*\n')
    s=macros(s,'lead',1,lambda a:'\n**'+a+'**\n')
    s=macros(s,'note',1,lambda a:'\n> '+a.replace('\n',' ')+'\n')
    s=macros(s,'fig',3,lambda name,width,cap:f'\n![{cap}](../figures/{name}.png)\n\n*{cap}*\n')
    s=macros(s,'textbf',1,lambda a:'**'+a+'**')
    s=macros(s,'texttt',1,lambda a:'`'+a.replace('\\_','_')+'`')
    s=s.replace('\\[','\n$$\n').replace('\\]','\n$$\n').replace('M\\\"obius','Möbius').replace('L\\\"uders','Lüders').replace('``','“').replace("''",'”')
    s=re.sub(r'\n{3,}','\n\n',s)
    title='# Quantum–Arithmetic Bridge\n\n## Visual Guide: Projectors, Fourier Packets, and Unitary Realization\n\nKomorebi P. · Operation Komorebi · Realization Calculus\n\nThis editable body accompanies the release PDF, twenty reproducible scientific figures, the traditional paper, and the Lean guide.\n'
    (HERE/'Quantum_Arithmetic_Visual_Guide.md').write_text(title+s+'\n')

if __name__=='__main__':main()
