from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from vii_viii_scan import ROOT,OUT
J=json.loads((OUT/'vii_viii_journal.json').read_text())
def e(f,old,new,reason):
 p=ROOT/f;s=p.read_text();assert s.count(old)==1,(f,old,s.count(old));p.write_text(s.replace(old,new));J.append({'file':f,'old':old,'new':new,'rationale':reason})
VII='source_v_viii/VII/editable/'
VIII='source_v_viii/VIII/editable/'
e(VII+'traditional/parts/01_finite_core.tex','the arbitrary-family statement','the statement for arbitrary families','Replace an optional modifier with a natural prepositional phrase.')
e(VII+'traditional/parts/03_supplement_05.tex',"The previous block's recovery is now instantiated from these derived syndromes, rather than from an assumed orthogonal error family.","The recovery from the previous block is instantiated from these derived syndromes, rather than from an assumed orthogonal error family.",'Remove an unnecessary temporal transition and smooth the possessive phrase while retaining the technical distinction.')
e(VII+'lean_guide/chapters/geometry.tex','The crucial off-diagonal derivative block is proved','The off-diagonal derivative block','Remove generic emphasis and the formulaic result-announcement ending from the subsection title.')
e(VII+'lean_guide/chapters/reading.tex','For a derivative identity the important move is often \\code{HasDerivAt.unique}:','For a derivative identity, \\code{HasDerivAt.unique} often supplies the final step:','Name the proof step directly without generic emphasis.')
e(VII+'lean_guide/chapters/seed_packets.tex','A seed now contains one coefficient array in every block.','A seed contains one coefficient array in every block.','Remove an unnecessary temporal transition.')
e(VII+'traditional/Paper_VII_Traditional_Final.tex','Part III retains the detailed proof completions rather than reducing them to a status summary.','Part III supplies the detailed proof completions.','State the contents directly without an unnecessary editorial contrast.')
e(VII+'traditional/Paper_VII_Traditional_Final.tex','outside that nineteen-item contract','outside that contract for nineteen items','Replace an optional count modifier with a natural phrase.')
e(VII+'lean_guide/Paper_VII_Lean_Guide_Final.tex','the recorded nineteen-result formal-core build','the recorded formal core build for nineteen results','Unstack count modifiers while preserving the exact recorded scope.')
e(VII+'visual_guide/source/pages.tex','Exact finite structure is valuable because its boundary is explicit.','The finite constructions have explicit scope.','Replace a general evaluative phrase with a concrete statement of scope.')
e(VIII+'traditional/parts/01_manuscript.tex','rather than full-provenance fair matches','rather than fair matches with complete provenance','Replace a stacked modifier with a natural phrase.')
e(VIII+'traditional/parts/01_manuscript.tex','A multiply--accumulate charges two scalar operations','A multiplication with accumulation charges two scalar operations','Express the modeled operation without dash punctuation; the two-operation charge is unchanged.')
e(VIII+'traditional/parts/01_manuscript.tex','the core best-approximation inequality also lower-bounds the error of every ambient competitor','the core best-approximation inequality also bounds the error of every ambient competitor from below','Avoid an unnecessary hyphen in the verb.')
e(VIII+'traditional/parts/01_manuscript.tex','complete-workflow timing medians','timing medians for complete workflows','Replace an optional modifier with a natural phrase.')
e(VIII+'traditional/parts/01_manuscript.tex','The accompanying verification record reports eleven passing unit tests','It also reports eleven passing unit tests','Avoid repeating the full subject in adjacent sentences.')
e(VIII+'traditional/parts/02_supplement_02.tex','the declared two-operations-per-coefficient model','the declared model of two operations per coefficient','Unstack an unnecessary chain of hyphenated modifiers.')
e(VIII+'traditional/parts/02_supplement_02.tex','memory-system behavior','memory system behavior','Remove an optional hyphen where the familiar noun phrase is clear.')
e(VIII+'traditional/parts/02_supplement_03.tex','the already-solved tail table','the already solved tail table','Remove an unnecessary hyphen after an adverb.')
e(VIII+'traditional/parts/02_supplement_04.tex','The closed form and its logarithmic re-expression are both checked:','The closed form and its equivalent logarithmic expression are both checked:','Use a familiar noun phrase instead of an optional hyphenated nominalization.')
e(VIII+'traditional/parts/02_supplement_05.tex','Finite-dimensionality makes that restricted map surjective.','Finite dimensionality makes that restricted map surjective.','Remove the adjectival hyphen from the standalone noun phrase, retaining the hypothesis.')
e(VIII+'traditional/parts/02_supplement_06.tex','This is the key global bridge: $B$ is not required to lie in the supplied row and column spaces.','The competitor $B$ is not required to lie in the supplied row and column spaces.','State the relevant property directly without a formulaic bridge announcement.')
e(VIII+'lean_guide/chapters/compiler.tex','the already-proved specification semantics','the already proved specification semantics','Remove an unnecessary hyphen after an adverb.')
e(VIII+'lean_guide/chapters/representations.tex','reverses conjugate-transposes of products','reverses conjugate transposes of products','Use the ordinary open noun phrase for the adjoint operation.')
e(VIII+'lean_guide/chapters/structured.tex','Its equality is an algorithm-correctness statement.','Its equality states algorithm correctness.','Replace an optional compound modifier with direct syntax.')
e(VIII+'visual_guide/source/pages.tex','This guide makes those distinctions visible through calculations rather than a pipeline of boxes.','This guide illustrates those distinctions with calculations.','Replace an unnecessary editorial contrast with a direct statement of the method.')
e(VIII+'visual_guide/source/pages.tex','contains already-perturbed later factors','contains later factors that have already been perturbed','Remove an optional adverbial hyphen while preserving the factor order and perturbation distinction.')
e(VIII+'visual_guide/source/pages.tex',"This is a reader-facing reconstruction of the paper's finite concepts, with reproducible examples and preserved source evidence.","This guide explains the chapter's finite concepts through reproducible examples and preserved source evidence.",'Replace an editorial label with a direct description.')
e(VIII+'visual_guide/source/extended_pages.tex','The integer model rejects a genuinely real-feasible assignment.','The integer model rejects an assignment that is feasible for the real-valued problem.','Replace an awkward coined compound and unnecessary intensifier while retaining the feasibility distinction.')
# Synchronize edited plate prose in both active copies, without copying layout.
for name in ['pages.tex','extended_pages.tex']:
 src=VIII+'visual_guide/source/'+name;dst=VIII+'traditional/atlas_sources/'+name
 for r in [x for x in J if x['file']==src]:
  s=(ROOT/dst).read_text()
  if r['old'] in s and r['new'] not in s:
   assert s.count(r['old'])==1
   (ROOT/dst).write_text(s.replace(r['old'],r['new']))
   J.append({**r,'file':dst,'rationale':'Synchronize duplicate plate prose. '+r['rationale']})
# Chapter VII has a concatenated atlas body with a separate layout preface.
src=VII+'visual_guide/source/pages.tex';dst=VII+'traditional/monograph_atlas.tex'
for r in [x for x in J if x['file']==src]:
 s=(ROOT/dst).read_text();assert s.count(r['old'])==1
 (ROOT/dst).write_text(s.replace(r['old'],r['new']))
 J.append({**r,'file':dst,'rationale':'Synchronize duplicate plate prose. '+r['rationale']})
(OUT/'vii_viii_journal.json').write_text(json.dumps(J,indent=2)+'\n')
print(len(J),'journal entries',len({x['file'] for x in J}),'edited files')
