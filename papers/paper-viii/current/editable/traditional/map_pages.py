#!/usr/bin/env python3
"""Map preserved Paper VIII records to final printed and physical PDF pages.

Actual page labels resolve the unique body location. Named destinations are
retained independently so a premature anchor cannot silently change a locator.
"""
from pathlib import Path
import collections,csv,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
KINDS=('theorem','proposition','lemma','corollary','definition','example','remark','standardfact')
def groups(s):
    out=[];level=0;start=None
    for i,c in enumerate(s):
        if c=='{':
            if level==0:start=i+1
            level+=1
        elif c=='}':
            level-=1
            if level==0:out.append(s[start:i])
    return out

def main():
    manifest=json.loads((E/'ASSEMBLY_MANIFEST.json').read_text());pdf=ROOT/'Paper_VIII_Traditional_Final.pdf';doc=fitz.open(pdf);names=doc.resolve_names();labels={}
    body_start=max(x['startpage'] for x in doc.get_page_labels() if x.get('style')=='D' and x.get('firstpagenum')==1)
    printed_to_physical={}
    for index,page in enumerate(doc,1):
        if index-1>=body_start:printed_to_physical.setdefault(page.get_label(),[]).append(index)
    for line in (ROOT/'Paper_VIII_Traditional_Final.aux').read_text().splitlines():
        if not line.startswith(r'\newlabel'):continue
        g=groups(line[len(r'\newlabel'):])
        if len(g)!=2 or '@cref' in g[0]:continue
        f=groups(g[1]);key=g[0]
        if len(f)<4:continue
        dest=names.get(f[3],{});destination_physical=dest.get('page',-1)+1;matches=printed_to_physical.get(f[1],[])
        if len(matches)!=1:raise SystemExit('Printed label not unique in actual PDF body '+key)
        physical=matches[0]
        if doc[physical-1].get_label()!=f[1]:raise SystemExit('Actual PDF page label mismatch '+key)
        labels[key]={'number':f[0],'printed_page':f[1],'physical_pdf_page':physical,'physical_page':physical,'page':f[1],'title_tex':f[2],'title':f[2],'destination':f[3],'named_destination_physical_page':destination_physical,'final_label':key,'type':'label'}
    originals={x['label']:x for x in manifest['result_records']};original_proofs={x['label']:x for x in manifest['proof_records']}
    rows=[];proofs=[];parts=[];pattern=r'\\begin\{('+'|'.join(KINDS)+r')\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
    for filename in re.findall(r'\\input\{parts/([^}]+)\}',(ROOT/'Paper_VIII_Traditional_Final.tex').read_text()):
        p=ROOT/'parts'/filename;s=p.read_text();parts.append({'path':'parts/'+filename,'sha256':sha(p)})
        for match in re.finditer(pattern,s):
            labs=re.findall(r'\\label\{([^}]+)\}',match.group());label=labs[0];original=originals[label];loc=labels[label]
            row={**original,**loc,'kind':match[1],'environment':match[1],'is_numbered':True,'title_tex':match[2] or original['title'],'source_part':'parts/'+filename,'source_part_line':s[:match.start()].count('\n')+1,'all_labels':labs,'final_record_sha256':hashlib.sha256(match.group().encode()).hexdigest(),'formal_scope':'56-item-released-finite-contract' if original['proof_required'] else 'classical-input' if match[1]=='standardfact' else 'finite-definition-example-or-remark'}
            rows.append(row)
            for lab in labs:labels[lab].update({'type':match[1],'kind':match[1],'title_tex':row['title_tex'],'title':row['title_tex'],'part':original['part'],'environment':match[1]})
        for match in re.finditer(r'\\begin\{proof\}(?:\[[^\]]*\])?([\s\S]*?)\\end\{proof\}',s):
            labs=re.findall(r'\\label\{([^}]+)\}',match.group());label=labs[0];original=original_proofs[label];end=original['end_label']
            row={**original,'ordinal':len(proofs)+1,'source_part':'parts/'+filename,'source_part_line':s[:match.start()].count('\n')+1,'start_page':labels[label]['physical_pdf_page'],'end_page':labels[end]['physical_pdf_page'],'printed_start_page':labels[label]['printed_page'],'printed_end_page':labels[end]['printed_page'],'physical_pdf_page':labels[label]['physical_pdf_page'],'printed_page':labels[label]['printed_page'],'final_proof_sha256':hashlib.sha256(match.group().encode()).hexdigest()};proofs.append(row);labels[label].update({'type':'proof','end_label':end,'end_physical_pdf_page':row['end_page']})
    assert len(rows)==85 and len(proofs)==56 and len(parts)==7
    sections=[]
    for row in manifest['section_records']:
        row={**row,**labels[row['label']]};row['page']=row['physical_pdf_page'];sections.append(row);labels[row['label']].update({'type':'section','kind':row['kind'],'title_tex':row['title'],'part':row['part']})
    finite=[]
    for row in rows:
        if row['proof_required']:
            proof=next(x for x in proofs if x['result_label']==row['label'])
            finite.append({'item':row['number'],'environment':row['environment'],'title':row['title_tex'],'number':row['number'],'label':row['original_labels'][0],'canonical_label':row['label'],'page':row['physical_pdf_page'],'physical_pdf_page':row['physical_pdf_page'],'printed_page':row['printed_page'],'proof_start_page':proof['start_page'],'proof_end_page':proof['end_page']})
    assert len(finite)==56
    result={'schema':'komorebi.paper_viii.final_page_map.v2','pdf':pdf.name,'pdf_pages':len(doc),'pdf_sha256':sha(pdf),'final_tex_sha256':sha(ROOT/'Paper_VIII_Traditional_Final.tex'),'physical_page_method':'Unique actual PDF Arabic page-label region matched to TeX shipout printed labels. Named destinations retained independently.','printed_body_page_offset':body_start,'labels':labels,'records':rows,'sections':sections,'proofs':proofs,'finite_items':finite,'supplement_crosswalk':manifest['supplement_crosswalk']}
    source={'schema':'komorebi.paper_viii.current_source_records.v1','traditional_pdf_sha256':sha(pdf),'traditional_source_sha256':sha(ROOT/'Paper_VIII_Traditional_Final.tex'),'source_parts':parts,'statement_records':rows,'proof_records':proofs,'scope':'85 preserved main numbered records and56 explicit proof environments;complete six supplementary mathematical bodies preserved separately. These units are not distinct discoveries or theorem-declaration counts.'}
    for path,value in [(ROOT/'canonical_label_to_final.json',labels),(ROOT/'current_source_records.json',source),(E/'FINAL_PAGE_MAP.json',result)]:path.write_text(json.dumps(value,indent=2)+'\n')
    with (E/'FINAL_THEOREM_MAP.csv').open('w',newline='') as f:
        fields=['part','environment','number','title','label','page','printed_page','source','source_line'];writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    md=['# Paper VIII monograph statement and proof crosswalk','','Printed pages and physical PDF pages are separate, verified against actual PDF page labels.','','| Finite item | Result | Printed page | Physical page | Proof physical pages |','|---|---|---:|---:|---|']
    for x in finite:md.append(f"| {x['item']} | {x['environment'].title()} {x['number']} {x['title']} | {x['printed_page']} | {x['page']} | {x['proof_start_page']}-{x['proof_end_page']} |")
    md+=['','## Supplement sections','','| Branch | Section | Title | Printed page | Physical page |','|---|---|---|---:|---:|']
    for row in sections:
        if row['part']!='main':md.append(f"| {row['part']} | {row['number']} | {row['title']} | {row['printed_page']} | {row['physical_pdf_page']} |")
    (E/'FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md').write_text('\n'.join(md)+'\n')
    badlinks=[];offpage=[];replacement=[]
    for i,page in enumerate(doc,1):
        if '\ufffd' in page.get_text():replacement.append(i)
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0<-1 or y0<-1 or x1>page.rect.width+1 or y1>page.rect.height+1:offpage.append({'page':i,'text':span['text'],'bbox':span['bbox']})
        for link in page.get_links():
            if link['kind']==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(doc):badlinks.append({'page':i,'link':link})
            if link['kind']==fitz.LINK_NAMED and not 0<=names.get(link.get('nameddest',''),{}).get('page',-1)<len(doc):badlinks.append({'page':i,'link':link})
    diagnostics=[line for line in (ROOT/'Paper_VIII_Traditional_Final.log').read_text(errors='replace').splitlines() if any(marker in line for marker in ('Warning:','Overfull','Underfull','undefined','multiply defined'))]
    anchor_mismatches=[{'label':key,'printed':val['printed_page'],'physical':val['physical_pdf_page'],'destination_physical':val['named_destination_physical_page']} for key,val in labels.items() if val['physical_pdf_page']!=val['named_destination_physical_page']]
    preflight={'status':'PASS' if not badlinks+offpage+replacement else 'FAIL','pdf_pages':len(doc),'pdf_sha256':sha(pdf),'page_labels':doc.get_page_labels(),'off_page_text':offpage,'replacement_character_pages':replacement,'invalid_internal_links':badlinks,'anchor_mismatches':anchor_mismatches,'log_diagnostics':diagnostics,'result_counts':dict(collections.Counter(x['environment'] for x in rows)),'proof_count':56,'supplement_body_count':6}
    (E/'PDF_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n');(E/'FINAL_DIAGNOSTICS.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
    print(json.dumps({'pdf_pages':len(doc),'labels':len(labels),'protected_environments':85,'proofs':56,'released_finite_items':56,'source_records_sha256':sha(ROOT/'current_source_records.json'),'canonical_map_sha256':sha(ROOT/'canonical_label_to_final.json'),'off_page_text':len(offpage),'anchor_mismatches':anchor_mismatches},indent=2))
    if badlinks or offpage or replacement:raise SystemExit('PDF preflight failed')
if __name__=='__main__':main()
