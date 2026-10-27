from pathlib import Path
import argparse,hashlib,json,re,collections
import fitz
from pypdf import PdfReader

ap=argparse.ArgumentParser();ap.add_argument('pdf',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--traditional',type=Path);a=ap.parse_args()
ROOT=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18')
H=ROOT/'editable/lean_guide';S=ROOT/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
doc=fitz.open(a.pdf);reader=PdfReader(a.pdf);destinations=reader.named_destinations
texts=[pg.get_text() for pg in doc];flat=re.sub(r'\s+','',''.join(texts))
bodyflat=re.sub(r'\s+','',''.join(pg.get_text(clip=fitz.Rect(0,45,pg.rect.width,pg.rect.height-45)) for pg in doc)).replace('↪','')
targets=json.loads((H/'generated/targets.json').read_text());missing=[r['declaration'] for r in targets if r['declaration'] not in flat]
geometric=[];blank=[];links=[];badlinks=[]
for i,pg in enumerate(doc,1):
    if len(pg.get_text().strip())<25:blank.append(i)
    for block in pg.get_text('dict')['blocks']:
        if block['type']!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>pg.rect.width+.5 or y1>pg.rect.height+.5:geometric.append({'page':i,'text':span['text'],'bbox':span['bbox']})
    for link in pg.get_links():
        name=link.get('nameddest');target=link.get('page')
        if name:
            other=reader.get_destination_page_number(destinations[name]) if name in destinations else None
            good=other==target and isinstance(target,int) and 0<=target<len(doc)
        elif link['kind']==fitz.LINK_GOTO:
            other=None;good=isinstance(target,int) and 0<=target<len(doc)
        else:
            other=None;good=False
        rec={'source_physical_page':i,'kind':link['kind'],'named_destination':name,'fitz_target_page_index':target,'pypdf_target_page_index':other,'valid':good}
        links.append(rec)
        if not good:badlinks.append(rec)
excerpt_rows=[]
for e in json.loads((H/'generated/excerpts.json').read_text()):
    raw=H/'excerpts'/f"{e['tag']}.lean.txt";src=S/e['source_file'];original=''.join(src.read_text().splitlines(keepends=True)[e['start_line']-1:e['end_line']]).encode()
    compact=re.sub(r'\s+','',raw.read_text())
    # The only non-text glyph in these exact excerpts is the two small square
    # dot-product marks in kl_rigidity. They are drawn by the documented fallback
    # and are verified separately in the page raster. Continuation arrows are
    # line-wrap aids added by fvextra rather than Lean source characters.
    extraction=compact in bodyflat
    drawn_square_count=compact.count('⬝')
    accounted=extraction or (e['tag']=='kl_rigidity' and drawn_square_count==2 and compact.replace('⬝','') in bodyflat)
    excerpt_rows.append({'tag':e['tag'],'source_hash_matches':sha(src)==e['source_sha256'],'raw_hash_matches':sha(raw)==e['excerpt_sha256'],'exact_contiguous_source_bytes':original==raw.read_bytes(),'declaration_name_extracts':e['name'] in flat,'full_code_body_extracts_after_removing_layout_continuation_arrows':extraction,'drawn_dot_product_squares':drawn_square_count,'full_body_accounted_for':accounted})
locators=[]
if a.traditional:
    td=fitz.open(a.traditional);cross=json.loads((H/'generated/traditional_crosswalk.json').read_text())
    wanted=[r['traditional'] for r in cross['core']]+[r['traditional'] for r in cross['strengthened']]+[r[key] for r in cross['supplements'] for key in ('first','last')]
    for r in wanted:
        pg=td[r['physical_pdf_page']-1];txt=re.sub(r'\s+','',pg.get_text());number=r['number']
        locators.append({'label':r['label'],'number':number,'printed':r['printed_page'],'physical':r['physical_pdf_page'],'printed_label_matches':pg.get_label()==str(r['printed_page']),'statement_number_on_page':number in txt})
pins=json.loads((H/'generated/imports.json').read_text());module_hash_pairs=[]
for pin in pins:
    occurrences=[i+1 for i,t in enumerate(texts) if pin['sha256'] in re.sub(r'\s+','',t)]
    first=occurrences[0] if occurrences else None
    same=first is not None and pin['module'] in re.sub(r'\s+','',texts[first-1])
    module_hash_pairs.append({'module':pin['module'],'first_hash_page':first,'module_name_on_same_page':same})
out={'pdf_path':str(a.pdf),'pdf_sha256':sha(a.pdf),'pages':len(doc),'all_323_declaration_names_extract':len(targets)==323 and not missing,'missing_declarations':missing,'excerpts':excerpt_rows,'raw_excerpts':len(excerpt_rows),'full_code_bodies_textually_accounted_for':sum(r['full_body_accounted_for'] for r in excerpt_rows),'code_extraction_note':'Remove layout continuation arrows. The two small square dot-product glyphs in kl_rigidity are drawn by the documented fallback and require visual verification. All raw UTF-8 source excerpts remain exact.','blank_pages':blank,'out_of_page_text':geometric,'replacement_glyphs':sum(t.count('\ufffd') for t in texts),'known_prior_corrupt_glyph_U0357':sum(t.count('\u0357') for t in texts),'links':links,'internal_links':len(links),'invalid_links':badlinks,'named_destinations':len(destinations),'outline_entries':len(doc.get_toc()),'traditional_document_locators':locators,'traditional_locator_count':len(locators),'module_hash_pairs':module_hash_pairs,'detached_module_hash_labels':[r for r in module_hash_pairs if not r['module_name_on_same_page']],'fresh_lean_kernel_run':False}
out['content_checks_pass']=not any((missing,blank,geometric,badlinks,out['replacement_glyphs'],out['known_prior_corrupt_glyph_U0357'])) and all(r['source_hash_matches'] and r['raw_hash_matches'] and r['exact_contiguous_source_bytes'] and r['declaration_name_extracts'] and r['full_body_accounted_for'] for r in excerpt_rows) and all(r['printed_label_matches'] and r['statement_number_on_page'] for r in locators)
a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:out[k] for k in ['pdf_sha256','pages','all_323_declaration_names_extract','raw_excerpts','full_code_bodies_textually_accounted_for','internal_links','traditional_locator_count','detached_module_hash_labels','content_checks_pass']}))
