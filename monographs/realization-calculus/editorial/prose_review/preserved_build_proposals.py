from pathlib import Path
import fitz, json, re, hashlib, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from preserved_pdf_proofread import block_text, plain, all_spans, ismath
FOLDER=ROOT/'editorial/prose_review/preserved_inputs'
FILES={'IV_visual':'Paper_IV_Visual_Guide_Final.pdf','XI_research_progress':'Paper_XI_Conjecture66_Progress_v0.4.0.pdf','XI_research_atlas':'Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf'}
DOCS={cid:fitz.open(FOLDER/name) for cid,name in FILES.items()}
EDITS=[]
def block(cid,pn,needle):
    bs=[b for b in DOCS[cid][pn-1].get_text('dict')['blocks'] if b.get('type')==0 and needle in plain(block_text(b))]
    assert len(bs)==1,(cid,pn,needle,len(bs))
    return bs[0]
def add(cid,pn,b,new,reason,kind='replace_paragraph',**extra):
    e={'component_id':cid,'page_1based':pn,'old_text_exact':block_text(b),'new_text':new,'kind':kind,'reason':reason,'bbox_optional':list(b['bbox'])}
    e.update(extra);EDITS.append(e)
def replace(cid,pn,needle,pairs,reason,**extra):
    b=block(cid,pn,needle);new=plain(block_text(b))
    for a,z in pairs:
        assert a in new,(a,new)
        new=new.replace(a,z)
    if any(ismath(s) for s in all_spans(b)):
        extra.update(math_spans_present=True,text_substitutions=pairs)
    add(cid,pn,b,new,reason,**extra)
def exact_occurrence(cid,pn,old,new,bbox,reason,proposal_id=None):
    hits=DOCS[cid][pn-1].search_for(old,clip=fitz.Rect(bbox)+(-.2,-.2,.2,.2))
    assert len(hits)==1,(cid,pn,old,bbox,len(hits))
    bs=[b for b in DOCS[cid][pn-1].get_text('dict')['blocks'] if b.get('type')==0 and fitz.Rect(b['bbox']).contains(hits[0])]
    assert len(bs)==1
    add(cid,pn,bs[0],new,reason,kind='replace_exact_occurrence',target_substring=old,target_bbox=list(hits[0]),external_proposal_id=proposal_id)
def additional_edits():
    later=json.loads((ROOT/'editorial/prose_review/xi_progress_later_findings.json').read_text())
    for e in later['proposals']:
        if ' ' in e['old_substring']:
            pn=e['physical_page'];oldspan=e['overlapping_source_spans'][0]['text']
            b=block('XI_research_progress',pn,plain(e['old_block_text']))
            add('XI_research_progress',pn,b,e['new_substring'],e['reason'],kind='replace_prose_spans',span_substitutions=[[oldspan,oldspan.replace(e['old_substring'],e['new_substring'])]],external_proposal_id=e['id'])
        else:
            exact_occurrence('XI_research_progress',e['physical_page'],e['old_substring'],e['new_substring'],e['bbox'],e['reason'],e['id'])
    cid='XI_research_atlas'
    replace(cid,14,'unramified self twist',[('unramified self twist','unramified self-twist')],'Use the established technical spelling self-twist.')
    for pn in [18,35]:
        for hit in DOCS[cid][pn-1].search_for('fibre'):
            if pn==18 and hit.y0>570:continue  # combined with the paragraph correction below
            exact_occurrence(cid,pn,'fibre','fiber',hit,'Use American spelling in ordinary title, subtitle, figure label or prose; retain neighboring symbols.')
    replace(cid,18,'rank-three continuation113 fixed-center ambiguity',[('rank-three continuation113 fixed-center ambiguity','rank-three fixed-center ambiguity'),('fibre','fiber')],'Remove an obsolete source-workflow identifier and use American spelling in the same ordinary-prose paragraph.')
    b=block(cid,20,'In continuation113,')
    s=b['lines'][0]['spans'][0]
    add(cid,20,b,'In the descent study, the original','Use a readable study reference while keeping theta and its index fixed.',kind='replace_prose_spans',span_substitutions=[[s['text'],s['text'].replace('In continuation113,','In the descent study,')]])
    b=block(cid,20,'The new atlas recomputes');s=b['lines'][0]['spans'][0]
    add(cid,20,b,'The atlas records the exact scalar exponents.','Describe the preserved calculation without claiming a fresh execution.',kind='replace_prose_spans',span_substitutions=[[s['text'],s['text'].replace('The new atlas recomputes the exact scalar exponents.','The atlas records the exact scalar exponents.')]])
    # Parent withdrew the optional p19 nominal-noun expansion as unnecessary.
    replace(cid,32,'Question marks are not zeroes',[('zeroes','zeros')],'Use consistent American spelling.')
    replace(cid,33,'example in continuation113',[('example in continuation113','example in the descent study')],'Replace an obsolete source-workflow identifier with a readable study reference.')
    b=block(cid,34,'The progress record now has');s=b['lines'][0]['spans'][0]
    add(cid,34,b,s['text'].replace('The progress record now has','The progress record has'),'Remove a revision-relative cue.',kind='replace_prose_spans',span_substitutions=[[s['text'],s['text'].replace('The progress record now has','The progress record has')]])
    replace(cid,36,'What is freshly executable',[('What is freshly executable','Executable checks and scope')],'Use a timeless heading for the recorded executable evidence.',kind='replace_label')
    replace(cid,36,'The delivered replay also runs',[('The delivered replay also runs','The recorded replay also covers')],'Describe the inherited replay without implying a new execution.')
    b=block(cid,36,'The versioned ledger and CONTINUE_HERE.md')
    add(cid,36,b,'The evidence ledger and CONTINUE_HERE.md record the remaining research tasks.','Replace checkpoint workflow prose while leaving literal filenames and their glyph positions untouched.',kind='replace_prose_spans',span_substitutions=[['. The versioned ledger and','. The evidence ledger and'],['specify the next checkpoint.','record the remaining research tasks.']])
def build():
    cid='IV_visual';pn=2
    replace(cid,pn,'The labels V1 through V26',[(plain(block_text(block(cid,pn,'The labels V1 through V26'))),'Plates IV.1–IV.26 identify worked pages independently of PDF pagination. Each page names the corresponding statements in Chapter IV. The formal companion records the separate formal contract.')],'Use chapter and plate references and correct the awkward edition wording.')
    for n in range(1,27):
        bs=[b for b in DOCS[cid][pn-1].get_text('dict')['blocks'] if b.get('type')==0 and block_text(b).startswith(f'V{n} ')]
        assert len(bs)==1
        b=bs[0];old=plain(block_text(b))
        add(cid,pn,b,old.replace(f'V{n} ',f'IV.{n} ',1),'Normalize the directory label to the book plate identifier.',kind='replace_label')
    replace(cid,pn,'Algebra first: V3 to V16',[(plain(block_text(block(cid,pn,'Algebra first: V3 to V16'))),'Algebra first: Plates IV.3–IV.16. Zeros first: Plates IV.17–IV.24. Full calculation: Plate IV.25. Evidence: Plate IV.26.')],'Use explicit book plate references in all reading routes.')
    for pn in range(3,29):
        b=block(cid,pn,'Traditional monograph:');old=plain(block_text(b));new=re.sub(r'\s*\(p\.\s*\d+\)','',old).replace('Traditional monograph:','Chapter IV:',1)
        add(cid,pn,b,new,'Use the chapter locator and retain named sections, definitions and theorems while removing obsolete local page locators.',kind='replace_label')
    replace(cid,3,'READER·S GUIDE',[('READER·S GUIDE',"READER'S GUIDE")],'Correct the apostrophe in the plate kicker.',kind='replace_label')
    b=block(cid,3,'V3 to V16: how do selection')
    add(cid,3,b,'','Use explicit book plate references in the reading-route table; keep the mathematical 69 glyphs at their original position. The replacement prefix fills the original prose width at native size.',kind='replace_table_cells',cell_substitutions=[['V3 to V16: how do selection, signs, reciprocals, and finite differential operators work?','Plates IV.3–IV.16: selection, signs, reciprocals, and finite differential operators.'],['V17 to V24: where can cancellation happen, and how does it determine coefficients?','Plates IV.17–IV.24: cancellation and its consequences for coefficients.'],['V25: derive the same number,','Plate IV.25: derive the integer']])
    add(cid,3,b,'','Remove the prose comma after the unchanged mathematical 69; extend only into adjacent blank space to contain its antialiasing pixels.',kind='remove_punctuation',anchor=', from denominator coefficients and from zero moments.',target_substring=',',pad_right_points=1.0,pad_vertical_points=.4)
    replace(cid,26,'therefore has half-plane',[('therefore has half-plane of absolute convergence','therefore has a half-plane of absolute convergence')],'Supply the missing article without moving the adjacent mathematical spans.',kind='replace_prose_spans',span_substitutions=[['. Their absolute zero-zeta series therefore has half-plane of absolute convergence','. Their absolute zero-zeta series therefore has a half-plane of absolute convergence']])
    cid='XI_research_progress'
    replace(cid,4,'This paper collects',[('This paper collects the mathematical progress toward the arithmetic realization endpoint of Paper XI.','This study collects the mathematical progress toward the arithmetic realization endpoint of Chapter XI.')],'Use a chapter reference and timeless study wording.')
    replace(cid,4,'The purpose of a separate paper',[('The purpose of a separate paper is to develop','The purpose of these studies is to develop')],'Remove obsolete separate-paper workflow wording.')
    replace(cid,6,'Paper XI separates',[('Paper XI separates','Chapter XI separates')],'Use Chapter XI for the internal reference.')
    replace(cid,6,'conventions of Paper XI',[('conventions of Paper XI','conventions of Chapter XI')],'Use Chapter XI for the internal reference while retaining the mathematical span positions.',kind='replace_prose_spans',span_substitutions=[['Fix the reciprocity, additive-character, local-factor and phase conventions of Paper XI. Let','Fix the reciprocity, additive-character, local-factor and phase conventions of Chapter XI. Let']])
    replace(cid,12,'char- acterization',[('char- acterization','characterization')],'Remove the artificial intra-word hyphen and space.')
    for needle in ['supplied, labelled','a labelled symplectic']:
        replace(cid,18,needle,[('labelled','labeled')],'Use American spelling in ordinary prose; retain mathematical spans.')
    b=block(cid,29,'The new paper should');lines=b['lines'][1:]
    oldtail=' '.join(''.join(s['text'] for s in l['spans']) for l in lines)
    oldsent='The new paper should make both facts easy to see without reducing all progress to either “finished” or “unfinished.”'
    newtail=oldtail.replace(oldsent,'These distinctions keep the restricted results separate from the general realization and comparison obligations.');assert oldtail!=newtail
    add(cid,29,b,newtail,'Replace workflow language with the mathematical distinction while retaining the preceding general-conjecture and same-candidate H5 sentences.',kind='replace_pure_lines',line_indexes=[1,2],old_lines_exact=[''.join(s['text'] for s in l['spans']) for l in lines])
    cid='XI_research_atlas'
    replace(cid,2,'This atlas accompanies',[('This atlas accompanies Toward Arithmetic Packet Realization, the 77-page cumulative research paper v0.4.0.','This atlas accompanies the arithmetic realization studies following Chapter XI.'),('Each plate combines one spacious mathematical graphic','Each plate combines a mathematical graphic'),('and a route back to that paper.','and a route back to those studies.')],'Remove obsolete version/page-count framing, keep direct mathematical prose, and retain a matching antecedent.')
    replace(cid,2,'Ordinary general proofs remain in the companion paper.',[('Ordinary general proofs remain in the companion paper.','Ordinary general proofs remain in the companion study.')],'Keep the study terminology consistent in the evidence note.',math_spans_present=True,text_substitutions=[['Ordinary general proofs remain in the companion paper.','Ordinary general proofs remain in the companion study.']])
    replace(cid,2,'The source line on every plate',[(plain(block_text(block(cid,2,'The source line on every plate'))),'The source line on each plate links to its argument in this book. The final concordance lists the corresponding book pages.')],'Describe the current internal book routes and concordance.')
    replace(cid,5,'every fibre',[('fibre','fiber')],'Use American spelling in ordinary prose.')
    additional_edits()
    basis=[{'component_id':cid,'path':str((FOLDER/name).relative_to(ROOT)),'sha256':hashlib.sha256((FOLDER/name).read_bytes()).hexdigest(),'pages':len(DOCS[cid])} for cid,name in FILES.items()]
    j={'schema':'realization-calculus.preserved-prose-edits/1','scope':'Minimal grammar, style, chapter and plate-reference repairs to current preserved PDF input copies; source attachments are read-only. No formula, proof, code or historical technical record changes.','source_basis':basis,'edits':EDITS,'root_approval':'Parent approved the base plan and supplied additional contextual prose corrections on this turn.','coverage':'Root is continuously reading all 141 pages; this module acts on exact root-supplied local findings and targeted locator/label normalization. It does not claim independent whole-document reading.'}
    p=ROOT/'editorial/prose_review/preserved_final_proposals.json';p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
    print('Wrote',p,'with',len(EDITS),'exact proposals.')
if __name__=='__main__':build()
