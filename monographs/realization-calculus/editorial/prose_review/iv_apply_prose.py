from pathlib import Path
import json, shutil, hashlib
root=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
b=Path('source_i_iv/IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable')
edits=[]
def add(file,old,new,why,count=1):
 edits.append({'file':str(b/file),'old':old,'new':new,'rationale':why,'expected_occurrences':count})
t='traditional/Paper_IV_Traditional_Final.tex'
add(t,'Inherited formal contract: earlier papers.','Inherited formal contract: earlier chapters.','Use the volume\'s chapter terminology in reader-facing scope text.')
add(t,'The reciprocal chapters then build','The reciprocal sections then build','The local reciprocal material is organized into sections, not separate chapters.')
add(t,'The visual atlas at the end of this volume','The visual atlas at the end of this chapter','Describe the atlas at the end of the Chapter IV component.')
add(t,'The paper treats only this','This chapter treats only this','Use chapter terminology for the current contribution.')
add(t,'reserved for Papers IX,','reserved for Chapters IX,','Use Chapter I–XII for internal volume references.')
add(t,'Papers I and II developed','Chapters I and II developed','Use Chapter I–XII for internal volume references.')
add(t,'while Paper III treated','while Chapter III treated','Use Chapter I–XII for internal volume references.')
add(t,"Paper III's general typed-edge theory.","Chapter III's general typed-edge theory.",'Use Chapter I–XII for internal volume references.')
add(t,'This volume follows the consequences','This chapter follows the consequences','Identify the current chapter rather than the whole collected volume.')
add(t,'The second half of the paper concerns','The second half of this chapter concerns','Use chapter terminology for the current contribution.')
add(t,'Two variables appear throughout the paper.','Two variables appear throughout this chapter.','Use chapter terminology for the current contribution.')
add(t,'the first and second halves of the paper.','the first and second halves of this chapter.','Use chapter terminology for the current contribution.')
add(t,'Paper I.','Chapter I.','Use Chapter I–XII for internal volume references.')
add(t,'the packet labelled by','the packet labeled by','Use American English spelling.')
add(t,'the cofactor sign is cancelled by','the cofactor sign is canceled by','Use American English spelling.')
add(t,'the general nonlinear operation-tree theory of Paper III.','the general nonlinear operation-tree theory of Chapter III.','Use Chapter I–XII for internal volume references.')
add(t,'not a result of this paper.','not a result of this chapter.','Use chapter terminology for the current contribution.')
add(t,'belongs to Paper IX.','belongs to Chapter IX.','Use Chapter I–XII for internal volume references.')
add(t,'Feshbach theory belongs to Paper VI. Paper III owns general nonlinear','Feshbach theory belongs to Chapter VI. Chapter III covers general nonlinear','Use Chapter I–XII for internal volume references and direct descriptive wording.')
add(t,'Paper X. None of those theories','Chapter X. None of those theories','Use Chapter I–XII for internal volume references.')
add(t,'Compiled Paper IV scope','Compiled Chapter IV scope','Use the current volume\'s chapter terminology in the ledger column heading.',2)
add(t,'Each stable label Plate IV.1 through Plate IV.26 names a mathematical mechanism and points back to the relevant statements.','The stable labels for Plates IV.1--IV.26 name mathematical mechanisms and point back to the relevant statements.','Repair the malformed singular range subject and use a plural plate-range reference.')
add(t,'For algebra, read Plate IV.3 through Plate IV.16. For zero geometry and its consequences, read Plate IV.17 through Plate IV.24.','For algebra, read Plates IV.3--IV.16. For zero geometry and its consequences, read Plates IV.17--IV.24.','Use plural plate-range references.')
a='traditional/atlas-pages.tex'
add(a,'Traditional monograph:','Chapter IV:','Identify internal statement locators by chapter, while preserving every locator.',26)
add(a,'the scalar cyclic specialization used by the paper.','the scalar cyclic specialization used in this chapter.','Use chapter terminology for the current contribution.')
add(a,'For every order in the paper,','For every order in this chapter,','Use chapter terminology for the current contribution.')
add(a,'The paper leaves universal simplicity','This chapter leaves universal simplicity','Use chapter terminology for the current contribution.')
l='lean_guide/chapters/01_orientation.tex'
add(l,'Paper IV studies','Chapter IV studies','Use Chapter I–XII for internal volume references.')
add(l,"Paper IV's diagonal determinant","Chapter IV's diagonal determinant",'Use Chapter I–XII for internal volume references.')
add(l,'allocated to Paper VI, the arithmetic interpolation theory of Paper IX, or the abstract completion questions of Paper X.','allocated to Chapter VI, the arithmetic interpolation theory of Chapter IX, or the abstract completion questions of Chapter X.','Use Chapter I–XII for internal volume references.')
add('lean_guide/chapters/03_analytic.tex','These are proved source routes.','These results are proved in the source.','Replace an awkward noun phrase with a direct statement of the same evidence claim.')
add('lean_guide/Paper_IV_Lean_Guide_Final.tex','The verification chapter records the pinned-source replay and its precise scope; static reconciliation remains a distinct form of evidence.','The verification chapter records the pinned-source replay and its precise scope. Static reconciliation remains a distinct form of evidence.','Use separate sentences for the two explanatory evidence claims.')
# All exact replacements are bounded and logged; back up each changed file once before writing it.
byfile={}
for e in edits: byfile.setdefault(e['file'],[]).append(e)
for name,items in byfile.items():
 p=root/name
 before=p.read_text()
 after=before
 for e in items:
  actual=after.count(e['old'])
  if actual != e['expected_occurrences']: raise RuntimeError((name,e['old'],actual,e['expected_occurrences']))
  e['line_before']=before[:before.index(e['old'])].count('\n')+1
  e['occurrences']=actual
  after=after.replace(e['old'],e['new'])
 dst=root/'editorial/prose_review/iii_iv_before'/name
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():
  if dst.read_text()!=before: raise RuntimeError('Existing backup differs: '+str(dst))
 else: shutil.copyfile(p,dst)
 p.write_text(after)
(root/'editorial/prose_review/iv_exact_journal.json').write_text(json.dumps(edits,indent=2,ensure_ascii=False)+'\n')
print('Changed',len(byfile),'files in',len(edits),'exact journal entries; occurrences',sum(e['occurrences'] for e in edits))
