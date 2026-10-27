from pathlib import Path
import re,json,hashlib,difflib
S=Path(__file__).resolve().parent; E=S.parent/'editorial/book_revision'
def edit(rel,reps):
 p=S/rel;t=p.read_text();o=t
 for a,b in reps:
  assert a in t,(rel,a);t=t.replace(a,b)
 if t!=o:
  b=S/'book_revision_before'/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():b.write_bytes(p.read_bytes())
  p.write_text(t)
edit('I/editable/traditional/02_foundations.tex',[('This edition proves the algebraic and topological statements printed below.','This chapter proves the algebraic and topological statements printed below.')])
edit('I/editable/traditional/06_reference.tex',[('The display numbers refer to this edition.','The display numbers refer to Chapter I.'),('twenty two plates','twenty-two plates'),('cross references match this edition','cross-references refer to the mathematical text')])
edit('I/editable/lean_guide/Paper_I_Lean_Guide_Final.tex',[("The expanded edition therefore explicitly includes the necessary nonzero-packet assumptions in its corrected $*$-support and source-component-count corollaries. Those editorial corrections do not create new Lean theorems. Row 25 already states its nontriviality scope, and all twenty formal source files remain unchanged.","The mathematical text therefore explicitly includes the necessary nonzero-packet assumptions in its $*$-support and source-component-count corollaries. Row 25 has its own nontriviality scope; the twenty-file foundational formalization retains that scope."),('different from the recorded release','different from the recorded source')])
edit('I/editable/machine/Paper_I_Machine_Native_Final.tex',[('This v1.0.1 implementation','This archived implementation'),('This is the eight-entry mapping attached to the frozen machine release.','This is the eight-entry mapping attached to the archived runtime.'),('The following is the successful release-gate run preserved from the earlier companion edition.','The following is the recorded successful runtime verification run.'),('not part of the frozen release','not part of the archived source')])
edit('II/editable/traditional/generated/current_scope.tex',[('Current targets and historical records are kept separately','Chapter-wide targets and foundational records are kept separately'),('recorded status and release gates','recorded status and verification checks')])
edit('II/editable/visual_guide/Paper_II_Visual_Guide_Final.tex',[('Chapter II: Visual Guide, Final Edition','Chapter II: Worked Visual Studies'),('Final companion edition\\quad\\textbullet\\quad 5 October 2026','Worked visual studies'),('traditional edition. The Lean guide separates current formal coverage from the inherited contract.','mathematical text. The formal companion distinguishes chapter-wide coverage from the foundational contract.')])
# Preserve exact code listings even where their archival strings resemble prose labels.
codepat=re.compile(r'\\begin\{(lstlisting|verbatim|Verbatim)\}.*?\\end\{\1\}',re.S)
results=[];diff=[]
mathpat=re.compile(r'(?<!\\)\$\$(?:.|\n)*?(?<!\\)\$\$|(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$|\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]|\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}',re.S)
for b in sorted((S/'book_revision_before').rglob('*.tex')):
 rel=b.relative_to(S/'book_revision_before')
 if rel.parts[0] not in ['I','II']:continue
 p=S/rel;o=b.read_text();t=p.read_text()
 oldcode=[m.group() for m in codepat.finditer(o)];newcode=[m.group() for m in codepat.finditer(t)]
 if oldcode!=newcode:
  assert len(oldcode)==len(newcode)
  it=iter(oldcode);t=codepat.sub(lambda m:next(it),t);p.write_text(t)
 strip=lambda x:re.sub(r'(?m)(?<!\\)%.*$','',x)
 oldmath=[m.group() for m in mathpat.finditer(strip(o))];newmath=[m.group() for m in mathpat.finditer(strip(t))]
 results.append({'file':str(rel),'before_sha256':hashlib.sha256(o.encode()).hexdigest(),'after_sha256':hashlib.sha256(t.encode()).hexdigest(),'math_regions_before':len(oldmath),'math_regions_after':len(newmath),'math_regions_identical':oldmath==newmath,'code_listings_identical':[m.group() for m in codepat.finditer(t)]==oldcode,'code_listing_count':len(oldcode)})
 diff.extend(difflib.unified_diff(o.splitlines(True),t.splitlines(True),fromfile='before/'+str(rel),tofile='after/'+str(rel)))
(E/'i_ii_edit_integrity.json').write_text(json.dumps(results,indent=2));(E/'i_ii_prose_diff.patch').write_text(''.join(diff))
print('files',len(results),'math-region differences',[x['file'] for x in results if not x['math_regions_identical']])
