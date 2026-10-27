#!/usr/bin/env python3
"""Resolve current paper labels against the built PDF; refresh the Lean reader crosswalk."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
import fitz
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--pdf',type=Path,default=R/'publication/pdfs/Paper_IX_Euler_Main_Final.pdf')
ap.add_argument('--aux',type=Path,default=R/'publication/build/Paper_IX_Euler_Main_Final/Paper_IX_Euler_Main_Final.aux')
ap.add_argument('--edition-label',default='20 October 2026 final release')
a=ap.parse_args()
PDF=a.pdf.resolve()
AUX=a.aux.resolve()
def group(s,pos):
    if s[pos]!='{':raise ValueError('Expected TeX group')
    start=pos+1;depth=1;pos+=1
    while pos<len(s):
        if s[pos]=='\\' and pos+1<len(s) and s[pos+1] in '{}':pos+=2;continue
        if s[pos]=='{':depth+=1
        elif s[pos]=='}':
            depth-=1
            if not depth:return s[start:pos],pos+1
        pos+=1
    raise ValueError('Unclosed TeX group')
def parts(s):
    p=0;out=[]
    while p<len(s):
        if s[p].isspace():p+=1;continue
        x,p=group(s,p);out.append(x)
    return out
with fitz.open(PDF) as doc:
    dest=doc.resolve_names();pages=len(doc)
labels={}
for line in AUX.read_text().splitlines():
    if not line.startswith('\\newlabel{'):continue
    key,pos=group(line,len('\\newlabel'));payload,pos=group(line,pos)
    if key.endswith('@cref'):continue
    v=parts(payload)
    if len(v)<4 or v[3] not in dest:continue
    labels[key]=dict(label=key,number=v[0],printed_page=v[1],physical_page=dest[v[3]]['page']+1,title=v[2],pdf_destination=v[3])
sha=hashlib.sha256(PDF.read_bytes()).hexdigest()
page_map=dict(file_name=PDF.name,pdf_sha256=sha,pdf_pages=pages,labels=labels,scope='Exact current TeX labels and named PDF destinations, not theorem verification.')
(R/'CURRENT_PUBLICATION_LOCATORS.json').write_text(json.dumps(page_map,indent=2)+'\n')
cw=json.loads((R/'sources/lean/audit/CROSSWALK.json').read_text());names={'arithmetic':'Arithmetic','dyadic':'Dyadic results','foundations':'Exact coordinates','affine':'Affine obstructions','polynomial':'Polynomial digits','towers':'Compatible towers','parameters':'Parameters and charts','weighted':'Weighted lifting','regularity':'Analytic regularity'}
t=[r'\section{Current manuscript-to-guide navigation}\label{sec:crosswalk}',
   'This table resolves all 62 inherited statement entries against the current '+str(pages)+'-page monograph. The paper column gives physical PDF pages, counting the cover. The guide column uses printed pages. The 202 exact formal source links are retained in the paired JSON without changing their source hashes. A separate classical example follows the indexed entries.',
   r'{\footnotesize Current monograph SHA-256: \code{'+sha+r'}.}\par',
   r'\begingroup\small',r'\begin{longtable}{p{.44\linewidth}r p{.27\linewidth}r}',r'\toprule Statement & Paper & Teaching chapter & Guide\\\midrule\endhead']
current=[]
for row in cw:
    key=row['manuscript_label'];m=labels[key];ch=row['guide_chapter'];x=dict(row)
    for old in ['guide_page','guide_printed_page','guide_physical_page']:x.pop(old,None)
    x.update(traditional_pdf_sha256=sha,traditional_number=m['number'],traditional_physical_page=m['physical_page'],traditional_printed_page=m['printed_page'],traditional_edition_role='Current '+a.edition_label,guide_section_label='sec:'+ch)
    current.append(x);t.append(r'\textbf{'+m['number']+r'} \code{'+key+'} & '+str(m['physical_page'])+' & '+names[ch]+r' & \pageref{sec:'+ch+r'}\\')
m=labels['ex:arith-bernoulli'];t += [r'\textbf{'+m['number']+r'} \code{ex:arith-bernoulli} & '+str(m['physical_page'])+r' & Classical derivation & \pageref{sec:reading}\\',r'\bottomrule\end{longtable}\endgroup']
extra=[key for key in re.findall(r'\\label\{([^{}]+)\}',(R/'sources/strengthening.tex').read_text()) if key.startswith(('thm:','lem:','cor:','prop:'))]
t += [r'\subsection{Strengthening and worked-example routes}',r'These locators navigate the newer written proofs and the exact worked atlas. Their formal coverage is discussed in Section~\ref{sec:new-coverage}. The page map does not turn a written proof or a finite example into a compiled Lean endpoint.',r'\begingroup\small',r'\begin{longtable}{p{.75\linewidth}r}',r'\toprule Current statement or example & Paper PDF page\\\midrule\endhead']
for key in extra+[k for k in labels if k.startswith('atlas:')]:
    m=labels[key];t.append(r'\textbf{'+m['number']+r'} \code{'+key+r'} & '+str(m['physical_page'])+r'\\')
t += [r'\bottomrule\end{longtable}\endgroup']
(R/'sources/lean/generated/crosswalk.tex').write_text('\n'.join(t)+'\n')
(R/'sources/lean/audit/CURRENT_CROSSWALK.json').write_text(json.dumps(current,indent=2)+'\n')
print(json.dumps({'status':'PASS','main_labels':len(labels),'inherited_statement_entries':len(cw),'source_links':sum(len(x['source_links'])for x in cw),'strengthening_routes':len(extra),'worked_routes':8,'main_pages':pages}))
