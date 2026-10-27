from pathlib import Path
import json,re,zipfile,fitz,collections,hashlib
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');O=R/'editorial/volume_finish'
S=json.loads((O/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']}
Z=zipfile.ZipFile('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip')
D={cid:fitz.open(stream=Z.read('Realization_Calculus_Publication_Package/'+C[cid]['path']),filetype='pdf') for cid in ['IX_traditional','IX_lean','IX_visual']}
MATH=re.compile(r'Math|^CM(?:MI|SY|EX|R|SS|TI)|^MS[AB]|Symbol|rsfs|stmary|msbm',re.I)
A=[];supersede=[];page_omit=[174,181,188,194,200,206,224]
def bbox_math(cid,pn,box):
 return [s['text'] for b in D[cid][pn-1].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if MATH.search(s['font']) and fitz.Rect(s['bbox']).intersects(box) and s['text'].strip()]
def region(cid,pn,box,label,why,table=False):
 box=fitz.Rect(box);bad=bbox_math(cid,pn,box);assert not bad,(cid,pn,label,bad)
 p=D[cid][pn-1];A.append({'component_id':cid,'source_page_1based':pn,'kind':'omit_region','action':'omit_region','old':p.get_textbox(box).rstrip('\n'),'new':'','bbox':list(box),'context':label,'reason':why,'category':'production_metadata','exact_bounded_region':True,'math_spans_present':False,'nonmathematical_table_rules_in_region':[{'type':d['type'],'bbox':list(d['rect'])} for d in p.get_drawings() if fitz.Rect(d['rect']).intersects(box)] if table else []})
def block_region(cid,pn,ids,label,why):
 blocks=D[cid][pn-1].get_text('blocks');box=fitz.Rect(blocks[ids[0]][:4])
 for i in ids[1:]:box|=fitz.Rect(blocks[i][:4])
 region(cid,pn,box,label,why)
def replace(cid,pn,anchor,new,kind='replace_block',label='Final-volume prose',reason='Remove production chronology while retaining mathematical and formal-coverage boundaries.'):
 bs=[b for b in D[cid][pn-1].get_text('blocks') if anchor in b[4]];assert len(bs)==1,(cid,pn,anchor,len(bs));b=bs[0]
 old=b[4].rstrip('\n') if kind=='replace_block' else anchor
 A.append({'component_id':cid,'source_page_1based':pn,'kind':kind,'action':kind,'old':old,'new':new,'bbox':list(b[:4]),'context':label,'reason':reason,'category':'publication_prose'})
# Source catalogue fields, including all line-wrapped path continuations. Keep headings, namespace,
# SHA identity, declaration names/kinds and every actual code excerpt unchanged.
flat=[]
for pn in range(61,len(D['IX_lean'])+1):
 for bi,b in enumerate(D['IX_lean'][pn-1].get_text('blocks')):flat.append((pn,bi,b))
fields=0;i=0
while i<len(flat):
 pn,bi,b=flat[i]
 if not b[4].startswith('Source:'):i+=1;continue
 selected=[(pn,bi,b)];k=i
 while not selected[-1][2][4].strip().endswith('.lean.'):
  k+=1;assert k<len(flat)
  np,nb,n=flat[k];assert not n[4].startswith(('SHA-256:','Namespace:','Source:')),(pn,bi,n[4])
  selected.append((np,nb,n));assert len(selected)<6
 bypage=collections.defaultdict(list)
 for pno,bno,bb in selected:bypage[pno].append(bb)
 for pno,bb in bypage.items():
  box=fitz.Rect(bb[0][:4])
  for e in bb[1:]:box|=fitz.Rect(e[:4])
  region('IX_lean',pno,box,'Source-catalogue path field','Remove only the archive/file locator and its wrapped continuation. Module heading, namespace, source hash, declaration identifiers and logical content remain; exact paths remain in the accompanying source records.')
 fields+=1;i=k+1
assert fields==199,fields
# Pure catalogue metadata nomenclature, not any formal declaration identifier.
source_file_rows=0
for pn in [96,106]:
 for b in D['IX_lean'][pn-1].get_text('dict')['blocks']:
  for l in b.get('lines',[]):
   t=''.join(s['text'] for s in l['spans'])
   if '2 source versions' in t:
    A.append({'component_id':'IX_lean','source_page_1based':pn,'kind':'exact_lines','action':'replace_line','old':t,'new':t.replace('2 source versions','2 source files'),'bbox':list(l['bbox']),'context':'Generated declaration-catalogue metadata field','reason':'Use source-file identity language without a publication-version label. Declaration name, kind, role and count remain exact.','category':'source_metadata'});source_file_rows+=1
assert source_file_rows==26
# Remove only the retrospective prefix word from appendix D result labels AND prose cross-references.
# Numerical labels and all statement/proof text stay in exactly the same native glyph positions.
historical_tokens=0
for pn in range(114,161):
 words=D['IX_traditional'][pn-1].get_text('words')
 for wi,w in enumerate(words):
  if w[4] not in ['Historical','historical']:continue
  nxt=words[wi+1][4] if wi+1<len(words) else ''
  if not re.match(r'(?:defin|propos|theor|coroll|lemm|examp|remar|stand)',nxt,re.I):continue
  region('IX_traditional',pn,w[:4],'Appendix D result-label prefix','Remove only the word Historical from the result label or its proof cross-reference. Existing D numbering, theorem/definition kind, hypotheses, proof text and all mathematical glyphs stay unchanged.');historical_tokens+=1
# Standalone prose clarifications.
replace('IX_traditional',19,'in the fixed\nversion of Nishibuchi’s paper used for the statement comparison.','in Nishibuchi’s cited statement.',kind='replace_phrase')
replace('IX_traditional',69,'historical subtype-valued chart','subtype-valued chart',kind='replace_phrase')
replace('IX_traditional',110,'This appendix reproduces','This appendix presents restricted polynomial obstruction, finite reconstruction, rectangularity and topological arguments as ordinary proofs. The intrinsic commutative-algebra obstruction uses the cited Stacks specialization and its finiteness argument. These results do not complete unrestricted Native 13.2 or Native 13.3 and have no new Lean certification.')
replace('IX_traditional',121,'The original line is retained only as a corrected historical record.','Use the recurrence-derived tail for this example.',kind='replace_phrase')
replace('IX_traditional',159,'D.11.4 Historical scope','D.11.4 Scope',kind='replace_phrase')
replace('IX_traditional',169,'The weighted dyadic theory','The weighted dyadic theory and general odd-prime finite-difference theorem lie outside this argument. No continuum convergence or analytic summability theorem follows from the formal power-series identities.')
replace('IX_traditional',176,'This is a formalization companion','The Bernoulli closed form for the inverse coefficients has no dedicated universal formalization here. Formal-series identities do not establish analytic convergence. The global odd-prime finite-difference theorem is developed separately.')
replace('IX_traditional',220,'Its coefficient condition','The coefficient condition agrees with the singular-Amice construction. The formal source checks the complete formal-series statement below.')
replace('IX_traditional',237,'Reproducibility.','The eight examples use exact rational and integer arithmetic. The computation scripts and tested ranges accompany the sources. This atlas adds no Lean endpoint and changes no formal claim in the companion.')
# Production-only paragraphs on mixed mathematical pages.
block_region('IX_traditional',212,[1],'Retained source and development history','Pure provenance and build-cache paragraph; preserve the following all-residue range and ratio boundary.')
block_region('IX_traditional',229,[0,1,2,3],'Compiler reproduction and forensic history','Pure launcher, audit-policy and retained-run provenance. Preserve the subsequent mathematical completion limits and bibliographic source entry.')
# Reader methods remain in the source package, separated from the mathematical walkthrough.
block_region('IX_lean',11,list(range(1,12)),'Static review, source paths and reader reproduction','Entire pure production/reconciliation subsection. The preceding analytic-radius argument and following formalization criterion remain unchanged.')
block_region('IX_lean',14,list(range(3,8)),'Recorded compiler/runtime and static reconciliation','Compiler pins, source/log census and forensic provenance only. Mathematical Lean-notation explanations above remain unchanged; exact foundational axiom scope is retained elsewhere in the guide.')
block_region('IX_lean',53,list(range(1,7)),'Source audit and dated compiler record','Source reconciliation, parser tests, timestamp/runtime/hash evidence. Preserve Section12 heading and all negative-control mathematical boundaries beginning12.2.')
block_region('IX_lean',54,list(range(4,8)),'Compiler replay and PDF building procedure','Pure reproduction commands and PDF-production discussion. Preserve the mathematical negative-control explanation above and open-obligation scope below.')
block_region('IX_lean',54,[11],'Stale inventory-scalar reconciliation','Forensic declaration-count discrepancy belongs to exact source records.')
replace('IX_lean',54,'12.4 Unclosed obligations and recovered history','12.4 Remaining questions',kind='replace_phrase')
replace('IX_lean',5,'The chapter brings together','The chapter combines Nishibuchi’s conjecture, the four-packet theory at every row, and stronger written congruences. The capstone, step-sensitive four-packet bound, exact first-difference periods and isometry have Lean sources and compiler records. General prime-power closure, mixed factorial estimates, exact higher-order laws and Taylor radii have mathematical proofs but no compiled Lean endpoint.')
replace('IX_lean',6,'The chapter titles in this table','The table identifies mathematical topics and their formal coverage. The crosswalk links the corresponding monograph statements and source interfaces. Separate routes identify the strengthening statements and eight exact worked examples.')
replace('IX_lean',13,'source version.','source file.',kind='replace_phrase')
# Local table-cell substitutions preserve the actual claim coverage and all neighboring formal identifiers/math.
for pn,pairs in [(5,[('Historically\ncompiled.\nSource\nand evidence reconciled anew.','Compiled in the recorded source.')]),(6,[('Historically compiled, including','Compiled, including'),('Historically compiled with expo-','Compiled with expo-'),('Historically compiled under the','Compiled under the'),('Proved in the new continuation.','Proved in the text.'),('Proved in the new continua-\ntion.','Proved in the text.')])]:
 for old,new in pairs:
  matches=[b for b in D['IX_lean'][pn-1].get_text('blocks') if old in b[4]]
  for bi,b in enumerate(matches):
   # Same plain phrase can occur in multiple independent cells; give its full unique cell text as anchor.
   if len(matches)>1:
    # Exact line regions are pure printed metadata; remove only temporal adjective, keeping coverage status.
    continue
   if matches:
    A.append({'component_id':'IX_lean','source_page_1based':pn,'kind':'replace_table_cells','action':'replace_table_cells','old':old,'new':new,'bbox':list(matches[0][:4]),'context':'Formal-coverage table cell','reason':'Keep the formal status and assumptions; remove temporal publication framing within the cell only.','category':'source_metadata'})
# Non-ambiguous per-cell word removals for repeated Proved-in-new-continuation labels are optional source
# history, not needed to state the actual proved/Lean boundary. Root may leave these benign claims.
# Every newly omitted whole page is source/verification/evidence records, not an actual derivation.
for pn in page_omit:
 assert not bbox_math('IX_traditional',pn,D['IX_traditional'][pn-1].rect),(pn,'math on omission page')
# Existing edits that lie wholly inside new production omissions are superseded, avoiding duplicate overlays.
old=json.loads((O/'ix_xii_plan.json').read_text())
for idx,x in enumerate(old['changes']):
 cid=x['component_id'];pn=x['source_page_1based']
 if cid=='IX_traditional' and pn in page_omit:continue
 if not x.get('bbox'):continue
 bb=fitz.Rect(x['bbox'])
 for n in A:
  if n['kind']=='omit_region' and n['component_id']==cid and n['source_page_1based']==pn and fitz.Rect(n['bbox']).contains(bb):supersede.append({'existing_index':idx,'old':x['old'],'component_id':cid,'source_page_1based':pn,'reason':'Entire existing edit lies inside newly omitted pure production region.'});break
out={'status':'FROZEN_PROPOSAL','scope':'IX residuals anchored to preceding ZIP compiled bytes, no PDF mutation.','changes':A,'whole_page_exclusion_candidates':[{'component_id':'IX_traditional','source_pages_1based':page_omit,'reason':'Pure compiler censuses, test counts, reproduction records and obsolete progress registers; mathematical derivations and current formal scope remain elsewhere.'}],'supersede_existing':supersede,'counts':{'catalogue_source_fields':fields,'source_version_metadata_rows':source_file_rows,'appendix_D_prefix_tokens':historical_tokens,'added_operations':len(A)},'retained_uses':['Mathematical versions such as finite, power-series, unit-step and open-set forms are not publication versions.','Historical-priority qualifications are mathematical attribution boundaries, not production chronology.','Every current open conjecture, counterexample and restriction remains explicit.'],'bookmark_notes':['Omit pure-production subsection bookmarks 1.9 Fresh review, inherited compilation, and reproducible replay; 2.3 What the retained proof evidence establishes; 12.1 What was freshly repeated; 12.3 How to perform a new compiler replay.','Strip Historical prefix from AppendixD result-title bookmarks consistently with bounded printed-token removal.']}
(O/'ix_residual_additions.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':out['status'],'counts':out['counts'],'superseded_edits':len(supersede),'whole_production_pages':page_omit},indent=2))
