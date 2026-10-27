from pathlib import Path
import re

def active_text(text):
    """Erase comments/strings while preserving offsets and every newline."""
    out=list(text); i=0; depth=0
    while i<len(text):
        if text.startswith('/-',i):
            depth+=1; out[i:i+2]='  '; i+=2
        elif depth and text.startswith('-/',i):
            depth-=1; out[i:i+2]='  '; i+=2
        elif depth:
            if text[i]!='\n':out[i]=' '
            i+=1
        elif text.startswith('--',i):
            while i<len(text) and text[i]!='\n':out[i]=' ';i+=1
        elif text[i]=='"':
            out[i]=' ';i+=1
            while i<len(text):
                c=text[i]
                if c!='\n':out[i]=' '
                i+=1
                if c=='\\' and i<len(text):out[i]=' ';i+=1
                elif c=='"':break
        else:i+=1
    if depth:raise ValueError('Unterminated block comment')
    return ''.join(out)

def esc(s):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))

def inventory(p):
    text=p.read_text(); active=active_text(text); stack=[]; rows=[]
    for number,line in enumerate(active.splitlines(),1):
        ns=re.match(r'^namespace\s+(\S+)',line)
        sec=re.match(r'^(?:noncomputable\s+)?section(?:\s+(\S+))?\s*$',line)
        end=re.match(r'^end(?:\s+(\S+))?\s*$',line)
        if ns:stack.append(('namespace',ns.group(1)))
        elif sec:stack.append(('section',sec.group(1)))
        elif end:
            if not stack:raise ValueError(f'Unexpected end {p}:{number}')
            stack.pop()
        m=re.match(r'^\s*(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?theorem\s+([^\s(:]+)',line)
        if m:
            name=m.group(1); namespace='.'.join(v for k,v in stack if k=='namespace')
            full=namespace+'.'+name if namespace else name
            rows.append({'declaration':full,'name':name,'line':number,'module':p.stem,'file':'formalization/'+p.name})
    return rows

def excerpt(p,name):
    text=p.read_text(); active=active_text(text)
    pat=r'(?m)^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:noncomputable[ \t]+)?(?:theorem|def|abbrev|structure|inductive)[ \t]+'+re.escape(name)+r'(?=[\s(:])'
    found=list(re.finditer(pat,active))
    if len(found)!=1:raise ValueError(f'{p.name}:{name}: {len(found)} matches')
    start=found[0].start()
    # Strip regex whitespace preceding the actual declaration line.
    while text[start]=='\n':start+=1
    command=re.compile(r'(?m)^(?:@\[[^\]\n]*\]\s*)?(?:(?:noncomputable\s+)?(?:theorem|def|abbrev|structure|inductive)|namespace|end|section|variable|omit|include|#print)\b|^/--|^/-!')
    after=command.search(text,found[0].end())
    stop=after.start() if after else len(text)
    # Remove only separating blank lines, retaining complete proof and source newline.
    raw=text[start:stop].rstrip('\n')+'\n'
    return raw,text[:start].count('\n')+1
