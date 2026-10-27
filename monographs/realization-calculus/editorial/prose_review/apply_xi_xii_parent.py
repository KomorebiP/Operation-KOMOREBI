from pathlib import Path
import json,re,shutil
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222');ED=ROOT/'editorial/prose_review';BACK=ED/'xi_xii_before';journal=[]
CH='Use Chapter for ordinary internal references in the collected volume; preserve exact source identifiers and document titles.'
TERM='Use mathematical text or formal companion for the current readers, following STYLE.md.'
US='Use American English spelling, following STYLE.md.'
GRAM='Correct a grammatical or typographical compound without changing mathematical content.'
def edit(f,changes):
 p=ROOT/f;old=p.read_text();s=old
 for a,b,why in changes:
  if a not in s:continue
  for m in re.finditer(re.escape(a),s):journal.append({'file':f,'line_before_at_step':s[:m.start()].count('\n')+1,'old':a,'new':b,'rationale':why})
  s=s.replace(a,b)
 if old!=s:
  bp=BACK/f;bp.parent.mkdir(parents=True,exist_ok=True);assert not bp.exists(),f;shutil.copy2(p,bp);p.write_text(s)
xb='source_ix_xii/XI/publication/source/'
edit(xb+'visual_guide/Paper_XI_Visual_Guide_Final.tex',[
 ("follows the paper's mathematical route","follows the chapter's mathematical route",CH),
 ('normalizations used in the accompanying paper.','normalizations used in the accompanying mathematical text.',TERM),
 ('labelled','labeled',US)])
edit(xb+'lean_guide/Paper_XI_Lean_Guide_Final.tex',[
 ('Paper XI develops','Chapter XI develops',CH),
 ('The traditional paper gives','The mathematical text gives',TERM),
 ("presentation of the paper's conditional implication","presentation of the chapter's conditional implication",CH),
 ('fixed point free on','fixed-point-free on',GRAM),
 ('The final traditional paper repairs','The mathematical text repairs',TERM),
 ('The paper separates odd phases','The chapter separates odd phases',CH)])
edit(xb+'lean_guide/current_verification.tex',[
 ('uncatalogued','uncataloged',US),('catalogued','cataloged',US),('catalogue literal','catalog literal',US)])
yb='source_ix_xii/XII/publication/source/'
edit(yb+'traditional/Paper_XII_Traditional_Final.tex',[
 ("Neither Paper XI's general Conjecture~66","Neither Chapter XI's general Conjecture~66",CH),
 ('The present article does not replace','The present chapter does not replace',CH),
 ('The article treats','The chapter treats',CH),
 ('The article proves formal support','The chapter proves formal support',CH),
 ('Exact boundary of the article','Exact boundary of the chapter',CH),
 ('Proved in this article','Proved in this chapter',CH),
 ('Not proved in this article','Not proved in this chapter',CH),
 ('The article does not prove unrestricted','The chapter does not prove unrestricted',CH),
 ('left hand locus','left-hand locus',GRAM),('right hand locus','right-hand locus',GRAM),('left hand complex','left-hand complex',GRAM)])
edit(yb+'traditional/reading_route.tex',[
 ('The Lean and evidence guide exposes','The formal companion exposes',TERM),
 ("Paper XI's general realization conjecture is not an input to this paper.","Chapter XI's general realization conjecture is not an input to this chapter.",CH)])
edit(yb+'lean_guide/Paper_XII_Lean_Guide_Final.tex',[
 ('source accompanying Paper XII,','source accompanying Chapter XII,',CH),
 ("Paper XII's own public theorem count","Chapter XII's own public theorem count",CH),
 ('a twelve-paper total','a twelve-chapter total',CH),
 ('The production tree reuses Paper X, not Paper XI.','The production tree reuses Chapter X, not Chapter XI.',CH)])
plate_changes=[
 ('The paper repeatedly asks','The chapter repeatedly asks',CH),
 ("connected by the paper's theorems","connected by the chapter's theorems",CH),
 ('The paper proves that the transition maps','The chapter proves that the transition maps',CH),
 ('\\textbf{Guide} & \\textbf{Question or calculation} & \\textbf{Paper XII reference}',
  '\\textbf{Plate} & \\textbf{Question or calculation} & \\textbf{Chapter XII reference}',CH),
 ('Three short proof-reading tests','Three short proofreading tests','Use the standard closed compound proofreading.'),
 ('in the node of V--9,','in the node of Plate XII.9,','Replace an opaque reader label with the stable plate identifier.')]
for a,b in [('V--6--7','XII.6--XII.7'),('V--12--13','XII.12--XII.13'),('V--15--16','XII.15--XII.16')]+[(f'V--{i} &',f'XII.{i} &') for i in [3,4,5,8,9,10,11,14,17]]:
 plate_changes.append((a,b,'Identify plates by Chapter XII under the explicit Plate column heading; retain compact table labels.'))
edit(yb+'visual_guide/source/pages.tex',plate_changes)
(ED/'xi_xii_parent_journal.json').write_text(json.dumps(journal,indent=2)+'\n');print('Changed',len({x['file'] for x in journal}),'files;',len(journal),'journal entries.')
