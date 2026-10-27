#!/usr/bin/env python3
"""Map immutable modular records to actual final PDF destinations and page labels."""
from pathlib import Path
import collections,csv,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
KINDS=('theorem','proposition','lemma','corollary','definition','example','remark','boundary','certificate','conjecture','standardfact','classical','construction','statement')
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
    m=json.loads((E/'ASSEMBLY_MANIFEST.json').read_text());pdf=ROOT/'Paper_VII_Traditional_Final.pdf';doc=fitz.open(pdf);names=doc.resolve_names();labels={}
    body_start=max(x['startpage'] for x in doc.get_page_labels() if x.get('style')=='D' and x.get('firstpagenum')==1)
    printed_to_physical={}
    for index,page in enumerate(doc,1):
        if index-1>=body_start:printed_to_physical.setdefault(page.get_label(),[]).append(index)
    for line in (ROOT/'Paper_VII_Traditional_Final.aux').read_text().splitlines():
        if not line.startswith(r'\newlabel'):continue
        g=groups(line[len(r'\newlabel'):])
        if len(g)!=2 or '@cref' in g[0]:continue
        f=groups(g[1]);key=g[0]
        if len(f)<4:continue
        dest=names.get(f[3],{});destination_physical=dest.get('page',-1)+1
        matches=printed_to_physical.get(f[1],[])
        if len(matches)!=1:raise SystemExit('Printed label is not unique in actual PDF body region '+key)
        physical=matches[0]
        if doc[physical-1].get_label()!=f[1]:raise SystemExit('Actual PDF page label mismatch '+key)
        labels[key]={'number':f[0],'printed_page':f[1],'physical_pdf_page':physical,'physical_page':physical,'page':f[1],'title_tex':f[2],'title':f[2],'destination':f[3],'named_destination_physical_page':destination_physical,'final_label':key,'type':'label'}
    rows=[];proofs=[];sourceparts=[];pattern=r'\\begin\{('+'|'.join(KINDS)+r')\}(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}'
    originals={x['label']:x for x in m['result_records']};origproofs={x['label']:x for x in m['proof_records']}
    for filename in re.findall(r'\\input\{parts/([^}]+)\}',(ROOT/'Paper_VII_Traditional_Final.tex').read_text()):
        p=ROOT/'parts'/filename;s=p.read_text();sourceparts.append({'path':'parts/'+filename,'sha256':sha(p)})
        for match in re.finditer(pattern,s):
            labs=re.findall(r'\\label\{([^}]+)\}',match.group());label=labs[0];original=originals[label];loc=labels[label]
            row={**original,**loc,'kind':match[1],'environment':match[1],'is_numbered':match[1]!='statement','title_tex':match[2] or original['title'],'source_part':'parts/'+filename,'source_part_line':s[:match.start()].count('\n')+1,'all_labels':labs,'final_record_sha256':hashlib.sha256(match.group().encode()).hexdigest(),'formal_scope':'nineteen-item-released-core' if original['part']=='core' and match[1] in ['theorem','corollary','classical'] else 'outside-nineteen-item-contract'}
            if match[1]=='statement':
                row['counter_context_number']=row['number'];row['number']=''
            rows.append(row)
            for lab in labs:
                labels[lab].update({'type':match[1],'title_tex':row['title_tex'],'part':original['part'],'environment':match[1]})
                if match[1]=='statement':labels[lab].update({'number':'','counter_context_number':row['counter_context_number']})
        for match in re.finditer(r'\\begin\{proof\}(?:\[[^\]]*\])?([\s\S]*?)\\end\{proof\}',s):
            labs=re.findall(r'\\label\{([^}]+)\}',match.group());label=labs[0];original=origproofs[label];end=original['end_label']
            row={**original,'ordinal':len(proofs)+1,'source_part':'parts/'+filename,'source_part_line':s[:match.start()].count('\n')+1,'start_page':labels[label]['physical_pdf_page'],'end_page':labels[end]['physical_pdf_page'],'printed_start_page':labels[label]['printed_page'],'printed_end_page':labels[end]['printed_page'],'physical_pdf_page':labels[label]['physical_pdf_page'],'printed_page':labels[label]['printed_page'],'final_proof_sha256':hashlib.sha256(match.group().encode()).hexdigest()};proofs.append(row)
            labels[label].update({'type':'proof','end_label':end,'end_physical_pdf_page':row['end_page']})
    assert len(rows)==147 and sum(x['is_numbered'] for x in rows)==142 and len(proofs)==107
    excluded_historical_metadata_labels=[x['label'] for x in m['section_records'] if x['label'] not in labels]
    m['section_records']=[x for x in m['section_records'] if x['label'] in labels]
    for row in m['section_records']:
        row.update(labels[row['label']]);row['page']=row['physical_pdf_page'];labels[row['label']].update({'type':'section','title_tex':row['title'],'part':row['part']})
    for row in m['result_records']:
        new=next(x for x in rows if x['label']==row['label']);row.update(new);row['page']=row['physical_pdf_page']
    m['proof_records']=proofs
    finite=[]
    for row in rows:
        if row['part']=='core' and row['environment'] in ['theorem','corollary','classical']:
            proof=next(x for x in proofs if x['result_label']==row['label'])
            finite.append({'item':row['number'].removeprefix('I.'),'environment':row['environment'],'title':row['title_tex'],'number':row['number'],'label':row['label'],'page':row['physical_pdf_page'],'physical_pdf_page':row['physical_pdf_page'],'printed_page':row['printed_page'],'proof_start_page':proof['start_page'],'proof_end_page':proof['end_page']})
    assert len(finite)==19
    body_start=max(x['startpage'] for x in doc.get_page_labels() if x.get('style')=='D' and x.get('firstpagenum')==1)
    result={'schema':'komorebi.paper_vii.final_page_map.v2','pdf':pdf.name,'pdf_pages':len(doc),'pdf_sha256':sha(pdf),'final_tex_sha256':sha(ROOT/'Paper_VII_Traditional_Final.tex'),'physical_page_method':'Unique actual PDF Arabic page-label region matched to TeX shipout printed labels. Historical hyperref named destinations are retained separately and do not determine physical record pages.','printed_body_page_offset':body_start,'labels':labels,'records':m['result_records'],'sections':m['section_records'],'proofs':proofs,'finite_items':finite,'supplement_crosswalk':m['supplement_crosswalk'],'excluded_historical_metadata_labels':excluded_historical_metadata_labels}
    source={'schema':'komorebi.paper_vii.current_source_records.v1','traditional_pdf_sha256':sha(pdf),'traditional_source_sha256':sha(ROOT/'Paper_VII_Traditional_Final.tex'),'source_parts':sourceparts,'statement_records':rows,'proof_records':proofs,'scope':'147 protected environments:142 numbered plus5 unnumbered supplementary statements,107 proof environments,including overlapping source branches. No distinct-new-result or additional formal-coverage count.'}
    for path,value in [(ROOT/'canonical_label_to_final.json',labels),(ROOT/'current_source_records.json',source),(E/'FINAL_PAGE_MAP.json',result)]:path.write_text(json.dumps(value,indent=2)+'\n')
    with (E/'FINAL_THEOREM_MAP.csv').open('w',newline='') as f:
        fields=['part','environment','number','title','label','page','printed_page','source','source_line'];writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(m['result_records'])
    md=['# Paper VII monograph statement and proof crosswalk','','The locators below come from actual final PDF destinations and printed page labels.','','| Released finite item | Result | Printed page | Physical page | Proof physical pages |','|---|---|---:|---:|---|']
    for x in finite:md.append(f"| {x['item']} | {x['number']} {x['title']} | {x['printed_page']} | {x['page']} | {x['proof_start_page']}-{x['proof_end_page']} |")
    md+=['','## Complete strengthened proof inventory','','| Result | Title | Printed page | Physical page | Proof physical pages |','|---|---|---:|---:|---|']
    for row in rows:
        if row['part']=='strong' and row['environment'] in ['theorem','proposition','lemma','corollary']:
            pf=next(x for x in proofs if x['result_label']==row['label']);md.append(f"| {row['environment'].title()} {row['number']} | {row['title_tex']} | {row['printed_page']} | {row['physical_pdf_page']} | {pf['start_page']}-{pf['end_page']} |")
    md+=['','## Supplement sections','','| Branch | Section | Title | Printed page | Physical page |','|---|---|---|---:|---:|']
    for row in m['section_records']:
        if row['part'] not in ['core','strong']:md.append(f"| {row['part']} | {row['number']} | {row['title']} | {row['printed_page']} | {row['physical_pdf_page']} |")
    (E/'FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({'pdf_pages':len(doc),'labels':len(labels),'protected_environments':len(rows),'numbered_records':sum(x['is_numbered'] for x in rows),'proofs':len(proofs),'released_finite_items':len(finite),'source_records_sha256':sha(ROOT/'current_source_records.json'),'canonical_map_sha256':sha(ROOT/'canonical_label_to_final.json')},indent=2))
if __name__=='__main__':main()
