from pathlib import Path
import hashlib,json,re,shutil,sys
import fitz
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import preserved_pdf_proofread as H
BASE=ROOT/'editorial/rhythm_review'
SPEC=json.loads((ROOT/'book/build_spec.json').read_text())
IDS=('IV_visual','XI_research_progress','XI_research_atlas')
DOCS={};BASIS=[];EDITS=[]
for cid in IDS:
    c=next(c for p in SPEC['parts'] for c in p['components'] if c['id']==cid)
    src=ROOT/c['path'];dst=BASE/'preserved_inputs'/(cid+'.pdf');dst.parent.mkdir(exist_ok=True)
    if not dst.exists():shutil.copy2(src,dst)
    DOCS[cid]=fitz.open(dst)
    BASIS.append({'component_id':cid,'path':str(dst.relative_to(ROOT)),'sha256':H.sha(dst),'pages':len(DOCS[cid])})

def change(cid,pn,needle,pairs,reason='Replace optional clause punctuation with natural sentences while preserving meaning.'):
    blocks=[b for b in DOCS[cid][pn-1].get_text('dict')['blocks'] if b.get('type')==0 and needle in H.plain(H.block_text(b))]
    assert len(blocks)==1,(cid,pn,needle,len(blocks))
    b=blocks[0];subs=[]
    for old,new in pairs:
        spans=[s for s in H.all_spans(b) if old in s['text']]
        assert len(spans)==1,(cid,pn,old,[s['text'] for s in spans])
        s=spans[0];assert not H.ismath(s),(cid,pn,old,s['font'])
        subs.append([s['text'],s['text'].replace(old,new)])
    assert len({a for a,b in subs})==len(subs)
    EDITS.append({'component_id':cid,'page_1based':pn,'old_text_exact':H.block_text(b),'new_text':' | '.join(z for a,z in subs),'bbox_optional':list(b['bbox']),'kind':'replace_prose_spans','span_substitutions':subs,'reason':reason})

change('IV_visual',24,'five finite contributions',[('; higher moments','. Higher moments')])
change('IV_visual',28,'Twenty-three match',[('; Plate IV.13','. Plate IV.13')])
change('XI_research_progress',4,'These are separate kinds',[('; none','. None')])
change('XI_research_progress',4,'Sections 14–21;',[('; conductor','. Conductor')])
change('XI_research_progress',7,'Its base inventory',[('; it also','. It also')])
change('XI_research_progress',9,'Both pairs',[('; in','. In')])
change('XI_research_progress',32,'Displayed numerical specializations',[('; this','. This')])
change('XI_research_progress',32,'These statuses remain distinct',[('; they','. They')])
change('XI_research_progress',34,'These developments preserve',[('; they','. They')])
change('XI_research_progress',37,'Source provenance.',[('; its complete','. Its complete')])
change('XI_research_progress',41,'The production source was recovered',[('; it also','. It also')])
change('XI_research_progress',53,'The occurrence question remains',[('; it is','. It is')])
change('XI_research_progress',64,'The three necessary invariants',[('invariants—standard','invariants (standard'),('conductor—cannot','conductor) cannot')],'Use parentheses for the explanatory list, keeping the stated three invariants and formula unchanged.')
change('XI_research_atlas',5,'Orthogonal factors commute;',[('; the actual','. The actual')])
change('XI_research_atlas',16,'The critical-four candidate passes',[('; it is','. It is')])
change('XI_research_atlas',26,'Source dimension is 6;',[('; the embedding','. The embedding')])
change('XI_research_atlas',27,'0 and e stay fixed;',[('; f and','. f and')],'Use a full stop between caption statements; the mathematical variable f retains its case.')
change('XI_research_atlas',30,'C2 acts trivially;',[('; the cocycle','. The cocycle')])
change('XI_research_atlas',32,'not only six squares',[('section products','section products,'),('—not only six squares','not only six squares')],'Replace a parenthetic dash with a comma across the existing three-line diagram label.')
change('XI_research_atlas',34,'proved conditionally; exact models',[('proved conditionally; exact models','conditional proofs, exact models')],'Use a concise comma-separated diagram status label.')

plan={'schema':'realization-calculus.preserved-prose-edits/1','source_basis':BASIS,'edits':EDITS,'scope':'Contextual prose punctuation and diagram-caption wording only. Equations, variables, technical compounds, citations, code and historical counts remain unchanged.','coverage':'Root reviewed all40 candidate paragraphs extracted from141 preserved pages and the technical-compound inventory. Mathematical semicolons, compact legend separators and bibliographic source delimiters were retained.'}
(BASE/'preserved_proposals.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
print('Prepared',len(EDITS),'bounded contextual proposals.')
