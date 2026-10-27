#!/usr/bin/env python3
"""Export the complete guide, preserving custom captions and source anchors."""
from pathlib import Path
import re, subprocess, tempfile
ROOT=Path(__file__).resolve().parent
text=(ROOT/'Stratified_Universality_Visual_Guide.tex').read_text()
body=text[text.index('\\section{Reading this guide}'):text.index('\\end{document}')]
def arguments(source,start,n):
    args=[]; p=start
    for _ in range(n):
        while p<len(source) and source[p].isspace(): p+=1
        assert source[p]=='{'; depth=1; q=p+1; begin=q
        while depth:
            if source[q]=='{':depth+=1
            elif source[q]=='}':depth-=1
            q+=1
        args.append(source[begin:q-1]);p=q
    return args,p
def replace_macro(source,name,n,fn):
    while '\\'+name+'{' in source:
        p=source.index('\\'+name+'{'); args,q=arguments(source,p+len(name)+1,n)
        source=source[:p]+fn(args)+source[q:]
    return source
body=replace_macro(body,'guidefig',3,lambda a:'\n\\includegraphics{figures/'+a[0]+'.png}\n\n'+a[2]+'\n')
body=replace_macro(body,'src',1,lambda a:'\n\\textbf{Manuscript anchors:} '+', '.join('\\texttt{'+s.strip()+'}' for s in a[0].split(';'))+'.\n')
body=body.replace('\\nextpage','').replace('\\quad',' ')
# \path deliberately survives in the PDF as breakable monospace; Markdown uses code spans.
body=replace_macro(body,'path',1,lambda a:'\\texttt{'+a[0].replace('_','\\_')+'}')
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'guide.tex';p.write_text(body)
    result=subprocess.run(['pandoc','--from=latex','--to=gfm','--wrap=none',str(p)],check=True,capture_output=True,text=True)
md=result.stdout.replace('<div class="center">\n\n','').replace('\n</div>','')
md=re.sub(r'<img src="([^"]+)"[^>]*>',r'![Exact guide figure](\1)',md)
md=re.sub(r'<embed src="([^"]+)"[^>]*/>',r'![Exact guide figure](\1)',md)
md=re.sub(r'!\[image\]\(figures/([^)]*)\.png\)',lambda m:'!['+m.group(1).replace('_',' ').capitalize()+'](figures/'+m.group(1)+'.png)',md)
md=re.sub(r'\$\$(.*?)\$\$',lambda m:'\n\n$$\n'+m.group(1).strip()+'\n$$\n\n',md,flags=re.S)
header='# Stratified Universality: Visual Guide\n\n**Komorebi P. · Final companion edition · 6 October 2026**\n\nProfiled lane transport, semantic quotients, carrier change, and certified descent.\n\nThis is the complete Markdown companion to the PDF. Vector PDF figures and the exact example generator are included alongside the PNG previews.\n\n'
md=header+md
(ROOT/'Stratified_Universality_Visual_Guide.md').write_text(md)
anchors=sum(md.count('`'+s.strip()+'`') for block in re.findall(r'\\src\{([^}]+)\}',text) for s in block.split(';'))
print('Markdown export complete:',len(md.split()),'whitespace-delimited words;',md.count('Manuscript anchors:'),'anchor blocks;',len(re.findall(r'!\[[^\]]*\]\(',md)),'figures.')
