import re
def active_text(text):
    out=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;out.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif string:
            if text[i]=='\\':out.extend('  ');i+=2
            elif text[i]=='"':string=False;out.append(' ');i+=1
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;out.extend('  ');i+=2
        elif text.startswith('--',i):
            e=text.find('\n',i);e=len(text) if e<0 else e;out.extend(' '*(e-i));i=e
        elif text[i]=='"':string=True;out.append(' ');i+=1
        else:out.append(text[i]);i+=1
    return ''.join(out)
def esc(s):
    d={'^':r'\textasciicircum{}','~':r'\textasciitilde{}','\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}'}
    return ''.join(d.get(c,c) for c in s)
def prose(s):return ''.join(r'\code{'+p[1:-1]+'}' if p.startswith('`') else esc(p) for p in re.split(r'(`[^`]*`)',s))
