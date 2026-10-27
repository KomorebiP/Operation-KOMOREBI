from pathlib import Path
import json,re
D=Path('editorial/rhythm_review')
rows=json.loads((D/'v_vi_semicolon_candidates.json').read_text())
journal=[]
# Reviewed individually in their paragraphs. These separators belong to lists,
# exact declaration catalogues, historical edition metadata, or locators.
retain={7,8,9,10,*range(27,36),99,*range(115,120),154,159,184}
# These headings read more naturally as connected clauses.
headings={131:('Coordinates retain; aggregation forgets; elimination remembers','Coordinates retain, aggregation forgets, and elimination remembers'),161:('Coordinates retain; aggregation forgets; elimination remembers','Coordinates retain, aggregation forgets, and elimination remembers'),133:('The modes stay; their clocks change','The modes stay as their clocks change'),163:('The modes stay; their clocks change','The modes stay as their clocks change'),144:('Reconstruction preserves the modes; time changes their weights','Reconstruction preserves the modes as time changes their weights'),174:('Reconstruction preserves the modes; time changes their weights','Reconstruction preserves the modes as time changes their weights')}
def edit(f,old,new,reason,category):
 p=Path(f);s=p.read_text();assert old in s,(f,old)
 assert s.count(old)==1,(f,old,s.count(old))
 line=s[:s.index(old)].count('\n')+1
 s=s.replace(old,new,1);p.write_text(s)
 journal.append({'file':f,'line_at_edit':line,'old':old,'new':new,'rationale':reason,'category':category})
for i,r in enumerate(rows,1):
 if i in retain:continue
 old=r['raw'];new=old
 if i in headings:
  a,b=headings[i];new=new.replace(a,b)
  reason='Connect the short heading clauses with commas and a conjunction, preserving their parallel meaning.'
 else:
  # Each selected clause pair was read in context before this script was run.
  # Uppercase only ordinary alphabetic sentence starts, never math or commands.
  new=re.sub(r';(\s+)([a-z])',lambda m:'.'+m[1]+m[2].upper(),new)
  new=new.replace(';','.');reason='Split independent prose clauses into short grammatical sentences without changing the argument.'
 if i==16:
  new=new.replace('including equality. Refine otherwise.','including equality, and refine otherwise.')
  reason='Use a conjunction for the two branches of the instruction and a sentence break for the work-bound explanation.'
 if i in {135,165}:
  new=new.replace('Here $t$ is the external time. $s$ is the ordinary diffusion time being mixed.','Here $t$ is the external time, and $s$ is the ordinary diffusion time being mixed.')
  reason='Connect the two time-variable descriptions with a conjunction rather than a semicolon.'
 if i==111:
  old+='\nequivalently, apply';new+='\nEquivalently, apply'
 if i==122:
  old+='\ncomplexification';new+='\nComplexification'
 edit(r['file'],old,new,reason,'semicolon_rhythm')
# Local prose changes beyond semicolons. Literal contracts, source identifiers,
# technical compounds and mathematical tokens remain unchanged.
V='source_v_viii/V/editable/'
VI='source_v_viii/VI/editable/'
for f in [V+'traditional/atlas-pages.tex',V+'visual_guide/source/pages_final.tex']:
 edit(f,'A familiar-looking matrix does not supply them automatically.','A familiar matrix does not supply them automatically.','Remove an optional compound that adds no useful distinction in this explanation.','optional_modifier')
 edit(f,'The always-valid estimate in this setting is','The estimate that always holds in this setting is','Replace an awkward compound with ordinary syntax, preserving the universal assertion.','optional_modifier')
 edit(f,'The fresh source-release checker','The checker for the source release','Use a concrete noun phrase in the recorded-execution description.','optional_modifier')
 edit(f,'The expanded-source numerical audit','The numerical audit of the expanded source','Use ordinary syntax instead of a compressed modifier.','optional_modifier')
 edit(f,'with a separate finite-example checker.','with a separate checker for the finite examples.','Replace an optional compound with a concrete noun phrase.','optional_modifier')
 edit(f,'a universal signal-quality score.','a universal score for signal quality.','Replace a compressed modifier with ordinary syntax.','optional_modifier')
 edit(f,'The new pages below are mathematical explanations and exact worked specializations','The following pages give mathematical explanations and exact worked specializations','Remove revision-relative wording and a formulaic opening while preserving the description.','formulaic_prose')
edit(V+'traditional/Paper_V_Traditional_Final.tex','The point is that the seed calculus records both systems','The seed calculus records both systems','Remove a formulaic lead-in; the sentence states the observation directly.','formulaic_prose')
edit(V+'traditional/Paper_V_Traditional_Final.tex','The point is that once a meaningful packet has been identified, its approximation error can be removed from the smooth approximation problem exactly.','Once a meaningful packet has been identified, its approximation error can be removed from the smooth approximation problem exactly.','Remove a formulaic lead-in while retaining the hypothesis and exact conclusion.','formulaic_prose')
edit(V+'lean_guide/chapters/04_haar.tex','a similar-looking formula','a similar formula','Remove an optional compound without changing the adjoint-identity caution.','optional_modifier')
edit(V+'lean_guide/chapters/08_reproduction.tex','A theorem-use checklist','A checklist for using the theorems','Replace a compressed compound in a prose heading with ordinary syntax.','optional_modifier')
edit(V+'visual_guide/Paper_V_Visual_Guide_Final.tex','worked-example checker.','checker for the worked examples.','Replace an optional compound with a concrete noun phrase.','optional_modifier')
edit(V+'visual_guide/Paper_V_Visual_Guide_Final.tex','All source-drawn plates are editable TikZ','All plates drawn from the source are editable TikZ','Replace an optional compound with ordinary syntax.','optional_modifier')
for f in [VI+'traditional/atlas-pages.tex',VI+'visual_guide/source/pages.tex']:
 edit(f,'A correct-looking tent can give a wrong solution if the grid weight is omitted.','A tent that looks correct can give a wrong solution if the grid weight is omitted.','Replace an optional compound with ordinary syntax while preserving the warning about the grid weight.','optional_modifier')
edit(VI+'traditional/Paper_VI_Traditional_Final.tex','The Bayesian map is a particularly transparent probabilistic realization.','The Bayesian map is a probabilistic realization.','Remove promotional phrasing without changing the nonlinear coordinate claim.','formulaic_prose')
edit(VI+'traditional/Paper_VI_Traditional_Final.tex','Hidden packets provide the final structural lesson. Exact elimination does not erase them. It returns them as a rational self-energy','Exact elimination returns hidden packets as a rational self-energy','Replace a formulaic transition and repetitive sentences with a direct statement, preserving the exact elimination claim.','formulaic_prose')
edit(VI+'visual_guide/source/front.tex','a separate written-proof collection.','a separate collection of written proofs.','Replace an optional compound with ordinary syntax.','optional_modifier')
edit(VI+'lean_guide/chapters/11_reproduction.tex','the editable Lean-guide directory','the directory for the editable Lean guide','Replace an optional compound with ordinary syntax.','optional_modifier')
edit(VI+'lean_guide/chapters/11_reproduction.tex','a separate documentation-generation step.','a separate step for generating documentation.','Replace an optional compound with ordinary syntax.','optional_modifier')
edit(VI+'lean_guide/chapters/11_reproduction.tex','an independent-result count.','a count of independent results.','Replace an optional compound while preserving the warning about overlapping finite evidence.','optional_modifier')
edit(V+'traditional/Paper_V_Traditional_Final.tex',"iterations. ``harmonic filling'' describes that iteration","iterations. The term ``harmonic filling'' describes that iteration",'Give the new sentence an ordinary noun phrase while preserving the quoted term exactly.','sentence_integration')
(D/'v_vi_journal.json').write_text(json.dumps(journal,indent=2,ensure_ascii=False)+'\n')
print('JOURNAL',len(journal),'files',len({x['file'] for x in journal}))
