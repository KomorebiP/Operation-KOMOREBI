from pathlib import Path
import re,json
S=Path(__file__).resolve().parent;changes=[]
def edit(rel,fn):
 p=S/rel;t=p.read_text();n=fn(t)
 if t!=n:
  b=S/'book_revision_before'/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():b.write_bytes(p.read_bytes())
  p.write_text(n);changes.append(rel)
edit('I/editable/traditional/Paper_I_Traditional_Final.tex',lambda t:t.replace('PLATE #1 / #3','Plate I.#1 / #3'))
edit('III/manuscript/Paper_III_Traditional_Final.tex',lambda t:t.replace('\\KomorebiKind}{Modern Monograph}','\\KomorebiKind}{Mathematical text}'))
for f in ['III/manuscript/visual_atlas.tex','III/guides/visual/source/pages_final.tex']:
 edit(f,lambda t:t.replace('Traditional paper:','Chapter III, mathematical text:'))
f='III/manuscript/chapters/01_finite_coordinates.tex'
a=r'\medskip\noindent The finite algebraic formalization uses Lean v4.34.0-rc2 against Mathlib revision \leanname{aeb72f1e9981b6d35b426b16dca7759be3e7ba06} \cite{lean,mathlib}. The accompanying verification record includes compilation at these exact pins, kernel replay, and axiom checks. References to declarations from Papers I--II retain their explicitly inherited status. The companion Lean guide distinguishes the original finite map from the additional packet-coordinate and analytic interfaces.'
b=r'\medskip\noindent The formal companion records the exact Lean and Mathlib dependencies \cite{lean,mathlib}, compilation, kernel replay, and axiom checks. References to declarations from Chapters I--II retain their explicitly inherited status. The companion distinguishes the finite algebraic contract from the additional packet-coordinate and analytic interfaces.'
assert a in (S/f).read_text();edit(f,lambda t:t.replace(a,b))
# The editable IV atlas remains a distinct, earlier source component; only its reference furniture changes.
f='IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/visual_atlas.tex'
if (S/f).exists():edit(f,lambda t:t.replace('Traditional manuscript:','Chapter IV, mathematical text:').replace('Traditional paper:','Chapter IV, mathematical text:'))
(S.parent/'editorial/book_revision/i_iv_final_furniture_changes.json').write_text(json.dumps(changes,indent=2));print(changes)
