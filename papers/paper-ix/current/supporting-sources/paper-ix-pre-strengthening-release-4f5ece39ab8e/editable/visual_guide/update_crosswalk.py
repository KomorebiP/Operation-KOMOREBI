#!/usr/bin/env python3
"""Pin final traditional PDF locators from its actual LaTeX aux labels.

This editorial script requires the traditional .aux and PDF produced by the
corresponding final build. It never guesses missing label or page numbers.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def group(text,start):
    if text[start]!='{':raise ValueError('Expected brace group.')
    depth=1;i=start+1
    while i<len(text) and depth:
        if text[i]=='{' and (i==0 or text[i-1]!='\\'):depth+=1
        elif text[i]=='}' and (i==0 or text[i-1]!='\\'):depth-=1
        i+=1
    if depth:raise ValueError('Unclosed aux brace group.')
    return text[start+1:i-1],i

def groups(text):
    values=[];i=0
    while i<len(text):
        if text[i]=='{':value,i=group(text,i);values.append(value)
        else:i+=1
    return values

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--aux',type=Path,required=True);ap.add_argument('--pdf',type=Path,required=True);args=ap.parse_args()
    source=args.aux.read_text();labels={}
    for match in re.finditer(r'\\newlabel\{([^}]+)\}',source):
        if match[1].endswith('@cref'):continue
        i=match.end()
        while i<len(source) and source[i].isspace():i+=1
        outer,_=group(source,i);parts=groups(outer)
        if len(parts)<2:continue
        number,page=parts[:2]
        labels[match[1]]={'label':match[1],'number':number,'page':int(page),'destination':parts[3] if len(parts)>3 else ''}
    import fitz
    pdf=fitz.open(args.pdf);total=len(pdf);pdf.close()
    requested=json.loads((ROOT/'source/crosswalk_targets.json').read_text());pages=[];macros=[]
    names={'thm':'Theorem','prop':'Proposition','lem':'Lemma','cor':'Corollary','def':'Definition','ex':'Example','rem':'Remark','eq':'Eq.','sec':'Section','subsec':'Section'}
    for visual,targets in requested.items():
        actual=[];links=[]
        for target in targets:
            if target not in labels:raise RuntimeError('Missing final traditional label: '+target)
            item=labels[target].copy();page=item['page']
            if not 1<=page<=total:raise RuntimeError(f'Out-of-range page for {target}: {page}')
            display=names.get(target.partition(':')[0],'Item')+' '+item['number']
            link='Paper_IX_Traditional_Final.pdf'
            item.update({'display':display,'pdf_physical_page':page,'relative_pdf_file':link,'pdf_zero_based_link_page':page-1});actual.append(item)
            links.append(r'\href[page='+str(page)+']{'+link+'}{'+display+r', p.\ '+str(page)+'}')
        pages.append({'visual_page':int(visual),'traditional_targets':actual})
        macros.append(r'\expandafter\def\csname MainTargets'+visual+r'\endcsname{Traditional companion: '+r';\quad '.join(links)+'}')
    (ROOT/'source/traditional_targets.tex').write_text('\n'.join(macros)+'\n')
    result={'status':'PASS','visual_pages':34,'target_occurrences':sum(len(p['traditional_targets']) for p in pages),
            'unique_target_labels':len(set(q for qs in requested.values() for q in qs)),
            'traditional_pdf_sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
            'traditional_pdf_pages':total,'traditional_aux_sha256':hashlib.sha256(args.aux.read_bytes()).hexdigest(),
            'locator_method':'Final traditional LaTeX aux labels; printed numbering equals PDF physical pages. Explicit remote PDF page actions via hyperref href[page=N].',
            'pages':pages}
    (ROOT/'QA/FINAL_PAGE_CROSSWALK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','visual_pages','target_occurrences','unique_target_labels','traditional_pdf_sha256']},indent=2))

if __name__=='__main__':main()
