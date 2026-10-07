"""Strict parsers and source stripping for retained proof-evidence checks."""
import re

def parse_declared(text):
    out={}
    matches=[]
    for m in re.finditer(r"'([^\n]+?)'\s+depends on axioms:\s*\[(.*?)\]",text,re.S):
        matches.append((m.start(),m.group(1),set(x.strip() for x in m.group(2).split(',') if x.strip())))
    for m in re.finditer(r"'([^\n]+?)'\s+does not depend on any axioms",text):
        matches.append((m.start(),m.group(1),set()))
    for _,name,axs in sorted(matches):
        if name in out:raise ValueError('Duplicate declared axiom result: '+name)
        out[name]=axs
    return out

def parse_environment(text):
    out={}
    for line in text.splitlines():
        if not line.startswith('PROJECT_AXIOMS|'):continue
        pieces=line.split('|')
        if len(pieces)!=4:raise ValueError('Malformed environment axiom record.')
        _,name,module,axs=pieces
        if name in out:raise ValueError('Duplicate environment constant: '+name)
        out[name]=(module,set(filter(None,axs.split(','))))
    return out

def strip_comments(text):
    out=[];i=0;depth=0
    while i<len(text):
        if text.startswith('/-',i):depth+=1;i+=2;continue
        if depth and text.startswith('-/',i):depth-=1;i+=2;continue
        if depth:i+=1;continue
        if text.startswith('--',i):
            end=text.find('\n',i);i=len(text) if end<0 else end;continue
        out.append(text[i]);i+=1
    if depth:raise ValueError('Unterminated source comment.')
    return ''.join(out)

def selftest():
    x=parse_declared("'A.a' does not depend on any axioms\n'A.b' depends on axioms: []\n'A.c' depends on axioms:\n[propext,\n Quot.sound]\n'A.d\'' depends on axioms: [Classical.choice]\n")
    assert x=={'A.a':set(),'A.b':set(),'A.c':{'propext','Quot.sound'},"A.d'":{'Classical.choice'}}
    assert strip_comments('a /- b /- c -/ d -/ e --x\nf')=='a  e \nf'
if __name__=='__main__':selftest();print('Evidence parser regression controls PASS')
