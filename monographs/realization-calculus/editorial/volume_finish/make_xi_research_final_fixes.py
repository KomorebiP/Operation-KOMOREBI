from pathlib import Path
import json,zipfile,fitz,hashlib,sys,re,unicodedata
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');O=R/'editorial/volume_finish';sys.path.insert(0,str(R));from preserved_pdf_proofread import ismath,block_text,all_spans,prepare_region,targeted_region
S=json.loads((O/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']};Z=zipfile.ZipFile('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip');D={};ops=[]
def doc(cid):
 if cid not in D:
  q=Z.read('Realization_Calculus_Publication_Package/'+C[cid]['path']);assert hashlib.sha256(q).hexdigest()==C[cid]['sha256'];D[cid]=fitz.open(stream=q,filetype='pdf')
 return D[cid]
def add(cid,pn,old,new,kind,bbox,reason):
 row={'component_id':cid,'source_page_1based':pn,'kind':kind,'action':kind,'old':old.rstrip('\n'),'new':new,'bbox':list(bbox),'reason':reason,'category':'publication_prose','baseline_source':C[cid]['path']};ops.append(row);return row
def omit(cid,pn,inds,reason):
 p=doc(cid)[pn-1];bs=p.get_text('blocks');box=fitz.Rect(bs[inds[0]][:4])
 for i in inds[1:]:box|=fitz.Rect(bs[i][:4])
 box+=(-.15,-.15,.15,.15)
 bad=[s['text'] for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if ismath(s) and fitz.Rect(s['bbox']).intersects(box) and s['text'].strip()];assert not bad,(cid,pn,bad)
 row=add(cid,pn,p.get_text(clip=box),'','omit_region',box,reason);row['source_block_indices']=inds;row['exact_bounded_region']=True;row['math_spans_present']=False
 return row
def fragment(cid,pn,old,new,reason):
 p=doc(cid)[pn-1];hs=p.search_for(' '.join(old.split()));assert hs,(cid,pn,old);b=fitz.Rect(hs[0])
 for h in hs[1:]:b|=h
 return add(cid,pn,old,new,'replace_phrase',b,reason)
def replaceblock(cid,pn,ind,new,reason):
 b=doc(cid)[pn-1].get_text('blocks')[ind];return add(cid,pn,b[4],new,'replace_block',b[:4],reason)
omit('XI_research_progress',41,[17,2,18,20,19],'Pure source recovery/log/receipt section. The preceding paragraph retains that the finite-group arguments are ordinary proofs independent of an unverified compilation claim. No arithmetic descent or realization assertion is removed.')
fragment('XI_research_progress',44,'The correct historical flow is therefore:','The argument therefore separates:','Retain the full mathematical distinction between genuine source multiplicities, one-quotient obstruction and an enlarged carrier. Remove only chronological framing.')
fragment('XI_research_progress',53,'A historical formal receipt records a past','A formal receipt records a','Retain the evidence-class distinction and exact compiler-evidence boundary without historical framing.')
omit('XI_research_progress',53,[7],'Pure replay-driver program list, temporary directory behavior and orchestration failure history. The following bounded-test scope and its arithmetic limitations remain untouched.')
omit('XI_research_progress',53,[4,8],'Pure source-recovery subsection heading and archive availability paragraph. No mathematical assertion occurs in the region.')
replaceblock('XI_research_progress',53,9,'The corrected-character occurrence question remains','Remove documentary source/receipt distinctions while keeping the mathematical occurrence obligation and the unchanged following sentence continuation.')
omit('XI_research_progress',76,[7,8],'Repeated source-replay suite accounting, archive recovery and compiler nonexecution notes. The 23-method conductor/marking finite-check scope above remains, as do the explicit required native-certificate fields in30.2 and the following open-conjecture statement.')
replaceblock('XI_research_atlas',36,20,'The atlas suite contains 28 test methods. It checks the displayed finite data and deliberate false controls, including the 72-target corner, conductor translations, cocycle products, all 64 vectors in each display of dimension six, and explicit correction formulas. These finite tests do not measure theorem completion. The native certificate remains uncomputed.','Keep all stated finite-test subjects and explicitly preserve the uncomputed native-certificate boundary. Remove only source Block1/3/4 replay accounting.')
omit('XI_research_atlas',36,[18,21],'Pure command/build/continuation-file production note, with its duplicated uncomputed-certificate boundary retained explicitly in the preceding rewritten scope paragraph. The two interleaved blocks must be omitted as one region to avoid fragments.')
# Optional source-only census from the introductory study, with all formal/claim coverage retained elsewhere.
omit('XI_research_progress',7,[15,16,17],'Pure module/source-byte census and source-layer identifiers. The separate conjecture/conditional-comparison logic on this page and the exact formal catalogue in the formal companion remain untouched.')
# p35 is subsequently adapted by the book-route normalizer. Request a renderer-owned replacement instead of adding a baseline op.
p=doc('XI_research_atlas')[34];b=p.get_text('blocks')[19]
request={'owner':'atlas_book_routes.py','component_id':'XI_research_atlas','source_page_1based':35,'baseline_block_index':19,'bbox':list(b[:4]),'old':b[4].rstrip('\n'),'proposed_text':'The concordance links each plate to its argument in the arithmetic studies. Hypotheses, arithmetic inputs and verification scope remain those of the cited statements.','reason':'This scope paragraph still says preserved checkpoint. Modify it in the renderer that owns the final concordance, not with a post-normalizer baseline operation.','no_baseline_edit_added':True}
# Read-only local fit test.
def canon(t):return re.sub(r'\s+',' ',re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])','',unicodedata.normalize('NFKC',t))).strip()
errs=[];passed=[]
for i,x in enumerate(ops):
 if x['kind']=='omit_region':passed.append(i);continue
 p=doc(x['component_id'])[x['source_page_1based']-1];bs=[b for b in p.get_text('dict')['blocks'] if b.get('type')==0];matches=[b for b in bs if canon(x['old']) in canon(block_text(b))]
 try:
  assert len(matches)==1,len(matches);b=matches[0]
  if any(ismath(s) for s in all_spans(b)):targeted_region(p,b,x['old'],x['new'])
  else:prepare_region(p,b['bbox'],canon(block_text(b)).replace(canon(x['old']),canon(x['new'])),all_spans(b),b['lines'])
  passed.append(i)
 except Exception as e:errs.append({'index':i,'failure':str(e),'component':x['component_id'],'page':x['source_page_1based']})
result={'status':'FROZEN' if not errs else 'FIT_REVIEW_REQUIRED','changes':ops,'renderer_owned_requests':[request],'native_fit':{'status':'PASS' if not errs else 'REVIEW_REQUIRED','passed':len(passed),'errors':errs},'classifications':[
 {'location':'XI research progress6','decision':'Retain named H1–H4 and Conjecture66/source-assertion correspondence. These identify the mathematical contract, not publication versions.'},
 {'location':'XI research progress44','decision':'Retain every mathematical distinction in the paragraph; replace only historical-flow framing.'},
 {'location':'XI research progress53','decision':'Retain four evidence classes and the corrected-character occurrence obligation. Remove only program/workspace/recovery diary.'},
 {'location':'XI research progress60','decision':'Retain v9 = −v. This is a mathematical exponent relation, not a version.'},
 {'location':'XI research atlas34','decision':'Retain distinction between ordinary proofs, classical inputs and formal compiler evidence. It limits the claim rather than describing a publication release.'},
 {'location':'Back references','decision':'Retain publication years and arXiv version identifiers as bibliographic identity.'}], 'preservation':['p33 final matrix-check sentence and p34 opening continuation untouched.','Conjecture66 general arithmetic realization remains open; same-candidate H5 and formal existence-input boundaries unchanged.','No PDF, source or parent/master plan mutation performed.']}
(O/'xi_research_final_fixes.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'status':result['status'],'ops':len(ops),'native_fit':result['native_fit'],'renderer_request':request},indent=2))
