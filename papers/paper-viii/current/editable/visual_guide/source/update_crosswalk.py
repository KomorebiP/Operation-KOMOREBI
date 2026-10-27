#!/usr/bin/env python3
"""Refresh all guide source lines from the final traditional aux/PDF pair.

Named PDF destinations establish physical pages independently of printed page
numbers. This edits explanatory source lines only, never mathematical spans.
The resulting register is copied into this standalone companion for rebuilds.
"""
from pathlib import Path
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
MAP={
1:['sec:ir','sec:cost','supp6:section:001'],
2:['def:packet_layout','def:packet_ir','def:output_contract','sec:precision','sec:compiler','sec:benchmark_protocol'],
3:['thm:exact_evaluation','thm:bdlr_counts'],
4:['thm:packet_counts','cor:equal_blocks','thm:bdlr_counts','cor:capacity','prop:block_banded_count'],
5:['thm:circulant'],6:['cor:toeplitz_embedding'],
7:['thm:kronecker_apply','cor:tensor_modewise'],8:['thm:walsh_hadamard'],
9:['thm:bdlr_product','cor:rank_growth'],10:['thm:woodbury','cor:inverse_norm'],
11:['thm:small_core_recompression','supp6:subsection:001'],
12:['thm:small_core_recompression','supp6:subsection:002','supp6:subsection:003','supp6:subsection:004'],
13:['thm:product_chain_error','cor:recompression_chain'],
14:['thm:block_composition','thm:path_support','cor:acyclic_nilpotence'],
15:['thm:level_schedule','cor:sequential_depth','thm:dag_depth'],
16:['thm:inverse_support','prop:schur_fill'],
17:['prop:krylov_invariant','thm:approx_krylov'],
18:['thm:block_jacobi','cor:certified_pcg','fact:cg'],
19:['thm:packet_error','prop:block_discovery_certificate'],
20:['thm:continuous_precision','thm:clipped_precision'],
21:['thm:discrete_precision','rem:dtype_boundary'],
22:['thm:tree_compiler','cor:supported_pareto','thm:budget_compiler'],
23:['thm:compiler_stability','thm:local_recompilation'],
24:['prop:streaming_bytes','thm:roofline','prop:shape_launch'],
25:['thm:amortization','cor:graph_threshold','cor:materialization_threshold'],
26:['prop:contract_conversion','sec:benchmark_protocol','sec:measured'],
27:['thm:exact_evaluation','thm:bdlr_counts','thm:bdlr_product'],
28:['sec:implementation','sec:boundaries','supp6:subsection:006','supp6:subsection:007'],
29:['thm:small_core_recompression','supp6:subsection:001','supp6:subsection:002'],
30:['thm:inverse_support','thm:path_support','cor:acyclic_nilpotence'],
31:['cor:shared_compiler','thm:tree_compiler'],
32:['thm:discrete_precision','thm:budget_compiler','cor:budget_complexity']}
KINDS={'theorem':'Theorem','corollary':'Corollary','proposition':'Proposition','definition':'Definition','standardfact':'Classical input','section':'Section','subsection':'Section','appendix':'Appendix','remark':'Remark'}
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
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    import fitz
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aux',type=Path,required=True)
    parser.add_argument('--pdf',type=Path,required=True)
    parser.add_argument('--map',type=Path,required=True)
    parser.add_argument('--visual-pdf',type=Path,default=ROOT/'Paper_VIII_Visual_Guide_Final.pdf')
    args=parser.parse_args()
    page_map=json.loads(args.map.read_text())
    if page_map['pdf_sha256']!=sha(args.pdf):raise RuntimeError('Traditional map/PDF identity mismatch.')
    doc=fitz.open(args.pdf);names=doc.resolve_names();records={}
    for line in args.aux.read_text().splitlines():
        if not line.startswith(r'\newlabel{'):continue
        g=groups(line)
        if len(g)!=2 or '@cref' in g[0]:continue
        fields=groups(g[1])
        if len(fields)<4:continue
        num,aux_printed,title,dest=fields[:4];r=names.get(dest)
        if not r or not isinstance(r.get('page'),int):continue
        physical=r['page']+1;printed=doc[physical-1].get_label()
        if aux_printed!=printed:raise RuntimeError('Printed-page disagreement at '+g[0])
        kind=KINDS.get(dest.split('.')[0],'Result')
        records[g[0]]={'label':g[0],'number':num,'title':title,'kind':kind,'printed_page':printed,'physical_page':physical,'pdf_destination':dest}
    for n,keys in MAP.items():
        for label in keys:
            if label not in records:raise RuntimeError('Missing final traditional label '+label)
            current=page_map['labels'].get(label)
            if not current:raise RuntimeError('Missing map label '+label)
            if current['physical_page']!=records[label]['physical_page'] or current['printed_page']!=records[label]['printed_page']:
                raise RuntimeError('Map label disagrees with actual PDF '+label)
    reg={'pdf_sha256':sha(args.pdf),'pdf_pages':len(doc),'aux_sha256':sha(args.aux),'map_sha256':sha(args.map),'method':'LaTeX label identity, current final page map, named PDF destinations, and actual printed PDF page labels. No cover offset inferred.','labels':records};doc.close()
    rows=[]
    for name in ('pages.tex','extended_pages.tex'):
        file=ROOT/'source'/name;s=file.read_text()
        old=ROOT/'historical_assembly/source'/name
        original_lines={int(m[1]):m[4] for m in re.finditer(r'\\vpage\{(\d+)\}\{([^{}]*)\}\{([^{}]*)\}\{([^\n]*)\}',old.read_text())}
        def sub(m):
            n=int(m[1]);targets=[dict(records[k]) for k in MAP[n]]
            refs=[t['kind']+' '+t['number'] for t in targets]
            pages=sorted({t['printed_page'] for t in targets},key=lambda x:int(x) if x.isdigit() else -1)
            line='Traditional p'+('p' if len(pages)>1 else '')+'. '+', '.join(pages)+' / '+', '.join(refs)+'.'
            rows.append({'visual_page':n,'title':m[2],'source_line_original':original_lines[n],'source_line':line,'targets':targets,'current_targets_verified':True})
            return r'\vpage{'+m[1]+'}{'+m[2]+'}{'+m[3]+'}{'+line+'}'
        s=re.sub(r'\\vpage\{(\d+)\}\{([^{}]*)\}\{([^{}]*)\}\{[^\n]*\}',sub,s);file.write_text(s)
    if sorted(r['visual_page'] for r in rows)!=list(range(1,33)):raise RuntimeError('Incomplete guide crosswalk.')
    rows.sort(key=lambda r:r['visual_page'])
    (ROOT/'provenance/FINAL_TRADITIONAL_REGISTER.json').write_text(json.dumps(reg,indent=2)+'\n')
    (ROOT/'SOURCE_CROSSWALK.json').write_text(json.dumps(rows,indent=2)+'\n')
    md=['# Paper VIII visual guide source crosswalk','','All 32 guide source lines cite printed pages in the current traditional edition. The register separately records physical PDF pages resolved from named destinations and actual page labels. Reading references retain the stated formal scope.','','| Guide page | Worked page | Traditional sources |','|---|---|---|']
    for row in rows:md.append(f"| V{row['visual_page']} | {row['title']} | {row['source_line']} |")
    (ROOT/'SOURCE_CROSSWALK.md').write_text('\n'.join(md)+'\n')
    # The guide may be rebuilt after these source changes. Re-run once after its final build to pin it.
    visual=fitz.open(args.visual_pdf);vnames=visual.resolve_names();cross=[]
    for row in rows:
        destination=vnames.get('plate'+str(row['visual_page'])+'.1') or vnames.get('vpage'+str(row['visual_page']))
        if not destination:raise RuntimeError('Missing guide worked-page destination '+str(row['visual_page']))
        index=destination['page'];page=visual[index]
        if page.get_label()!=str(row['visual_page']):raise RuntimeError('Guide page-label mismatch '+str(row['visual_page']))
        cross.append({'visual_page':row['visual_page'],'visual_physical_pdf_page':index+1,'visual_printed_page':page.get_label(),'title':row['title'],'source_line_original':row['source_line_original'],'source_line_current':row['source_line'],'traditional_targets':[{'final_label':target['label'],'number':target['number'],'printed_page':target['printed_page'],'physical_pdf_page':target['physical_page'],'title_tex':target['title'],'kind':target['kind']} for target in row['targets']]})
    source=ROOT.parent/'traditional/Paper_VIII_Traditional_Final.tex'
    crosswalk={'status':'PASS','traditional_map_sha256':sha(args.map),'traditional_pdf_sha256':sha(args.pdf),'traditional_aux_sha256':sha(args.aux),'traditional_source_sha256':sha(source),'visual_pdf_sha256':sha(args.visual_pdf),'scope':'32 exact declared reading rows. Targets verified against current map, named destinations, and actual printed and physical PDF page labels. The integrated atlas omits PDF locators. Reading references do not expand formal scope.','pages':cross}
    visual.close();(ROOT/'VISUAL_TO_TRADITIONAL_CROSSWALK.json').write_text(json.dumps(crosswalk,indent=2)+'\n')
    print('Updated 32 current traditional source crosswalk rows.')
if __name__=='__main__':main()
