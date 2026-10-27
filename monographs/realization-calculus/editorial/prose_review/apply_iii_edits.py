from pathlib import Path
import json, shutil, re, hashlib
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
BACK=ROOT/'editorial/prose_review/iii_iv_before'
journal=[]

def edit(rel, changes):
 p=ROOT/rel; bp=BACK/rel; old=bp.read_text() if bp.exists() else p.read_text(); text=old; entries=[]
 for a,b,reason in changes:
  if a not in text: continue
  for match in re.finditer(re.escape(a),text):
   entries.append({'file':rel,'line_before_at_step':text[:match.start()].count('\n')+1,'old':a,'new':b,'rationale':reason})
  text=text.replace(a,b)
 if text!=old:
  bp=BACK/rel;bp.parent.mkdir(parents=True,exist_ok=True)
  if not bp.exists():shutil.copy2(p,bp)
  assert bp.read_text()==old,(rel,'backup differs')
  p.write_text(text);journal.extend(entries)

CH='Use Chapter for ordinary internal references, following STYLE.md; exact code identifiers are unchanged.'
TERM='Use the established mathematical text/formal companion terminology for the current volume.'
GRAM='Correct grammatical integration without changing mathematical content.'
HYPH='Hyphenate a necessary technical compound used as a modifier.'
base='source_i_iv/III/manuscript/'
for name in ['01_finite_coordinates.tex','02_connections_obstructions.tex']:
 p=ROOT/base/'chapters'/name
 changes=[]
 for a,b in [('Papers I--II','Chapters I--II'),('Paper III','Chapter III'),('Paper I or II','Chapter I or Chapter II'),('Paper II','Chapter II'),('Paper I','Chapter I'),('Paper~II','Chapter~II')]:
  if a in ((BACK/p.relative_to(ROOT)).read_text() if (BACK/p.relative_to(ROOT)).exists() else p.read_text()):changes.append((a,b,CH))
 if name.startswith('01'):
  changes += [('The present paper begins','The present chapter begins',CH),('fixed in this paper.','fixed in this chapter.',CH)]
 else:
  changes += [('The Lean and evidence guide records','The formal companion records',TERM)]
 edit(base+'chapters/'+name,changes)
edit(base+'Paper_III_Traditional_Final.tex',[
 ('Inherited formal contract: Papers I--II.','Inherited formal contract: Chapters I--II.',CH),
 ('The paper presents','The chapter presents',CH),
 ('The companion Lean and evidence guide gives','The formal companion gives',TERM),
 ('related statements in the paper.','related statements in the chapter.',CH)])
edit(base+'chapters/03_nonlinear_coordinates.tex',[
 ('The article does not claim','The chapter does not claim',CH),('The paper uses finite packet systems','The chapter uses finite packet systems',CH),
 ('The unlabelled tree majorant','The unlabeled tree majorant','Use American English spelling.'),
 ('Off diagonal correction blocks','Off-diagonal correction blocks',HYPH),
 ('is $q$ Lipschitz','is $q$-Lipschitz',HYPH),('is $L$ Lipschitz','is $L$-Lipschitz',HYPH)])
edit(base+'chapters/04_correction_transport.tex',[
 ('be $L$ Lipschitz','be $L$-Lipschitz',HYPH),
 ('Well defined lift classes','Well-defined lift classes',HYPH),
 ('One step lifting criterion','One-step lifting criterion',HYPH),
 ('One step direct rotation estimate','One-step direct rotation estimate',HYPH),
 ('self adjoint projection','self-adjoint projection',HYPH),
 ('skew adjoint:','skew-adjoint:',HYPH),
 ('Skew adjointness','Skew-adjointness',HYPH),
 ('rank one packet','rank-one packet',HYPH),
 ('orthogonal projector valued map','orthogonal projector-valued map',HYPH),
 ('non tree edges','non-tree edges',HYPH)])
for rel in [base+'visual_atlas.tex','source_i_iv/III/guides/visual/source/pages_final.tex']:
 edit(rel,[
  ('One paper, three tests','One chapter, three tests',CH),('broader paper.','broader chapter.',CH),
  ("the paper's", "the chapter's",CH),
  ('The traditional paper','The mathematical text',TERM),('the traditional paper','the mathematical text',TERM),
  ('Inclusion in that paper','Inclusion in that text',TERM),
  ('does not require pairwise annihilation for its general reconstruction statement.','does not require pairwise annihilation.','Remove a duplicated statement-ending clause.'),
  ('the Section 16 and 17 additions','the additions in Sections 16 and 17',GRAM),
  ('for the Section 16 and 17 examples','for the examples in Sections 16 and 17',GRAM)])
edit('source_i_iv/III/guides/visual/Paper_III_Visual_Guide_Final.tex',[
 ('From the finite models to the broader paper','From the finite models to the broader chapter',CH)])
lbase='source_i_iv/III/guides/lean/'
edit(lbase+'chapters/01_orientation.tex',[
 ('Reading the formal paper','Reading the formal development',TERM),
 ('Paper III turns','Chapter III turns',CH),('Paper III also preserves','Chapter III also preserves',CH),
 ('The expanded traditional companion','The expanded mathematical text',TERM),
 ("the authors' constructions", "the author's constructions",'The named author is singular; correct the possessive agreement.')])
edit(lbase+'chapters/03_heterogeneous.tex',[
 ('The traditional companion','The mathematical text',TERM)])
edit(lbase+'chapters/06_nonlinear.tex',[
 ('The traditional companion','The mathematical text',TERM)])
edit(lbase+'chapters/07_replay.tex',[
 ('mapped to the paper.','mapped to the chapter.',CH),
 ('The inherited Papers I--II references','The inherited Chapters I--II references',CH),
 ('Paper III records twelve','Chapter III records twelve',CH),
 ("the paper's earlier bounded mathematical review", "the chapter's earlier bounded mathematical review",CH)])
edit('source_i_iv/III/docs/Paper_III_Section17_Analytic_Closeout.tex',[
 ('let $B:\\X^r\\to\\Y$ be continuous multilinear, $r\\ge1$.','let $B:\\X^r\\to\\Y$ be a continuous multilinear map, $r\\ge1$.',GRAM),
 ("the Fr\\'echet derivative $\\D^rF(x)$ is continuous multilinear.","the Fr\\'echet derivative $\\D^rF(x)$ is a continuous multilinear map.",GRAM),
 ('Then output component $\\gamma$ is','Then the output component $\\gamma$ is','Supply the missing definite article.'),
 ("Applying the ordinary Fr\\'echet chain rule repeatedly, their derivatives of order at least two vanish. Hence the stated formula.","Their derivatives of order at least two vanish. Repeated application of the ordinary Fr\\'echet chain rule therefore gives the stated formula.",'Remove a dangling modifier and integrate the concluding fragment.'),
 ('were freshly compiled in the pinned Lean environment.','were compiled in the pinned Lean environment.','Remove a time-relative adverb while retaining the historical compilation claim.')])
(ROOT/'editorial/prose_review/iii_journal.json').write_text(json.dumps(journal,indent=2)+'\n')
print('Edited',len(set(x['file'] for x in journal)),'files;',len(journal),'exact replacements logged.')
