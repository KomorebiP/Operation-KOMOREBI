from pathlib import Path
import re,json,shutil
r=Path('/dev/shm/komorebi_core_monograph_fbc994080222');b=Path('source_ix_xii/XI/publication/source/traditional');journal=[]
files=[b/'Paper_XI_Traditional_Final.tex',b/'reader_route.tex',*sorted((b/'appendices').glob('*.tex'))]
original={str(p):(r/p).read_text() for p in files};texts=dict(original)
def apply(file,old,new,why,expected=None):
 name=str(b/file);s=texts[name];n=s.count(old)
 if expected is not None:assert n==expected,(file,old,n,expected)
 if n:
  journal.append({'file':name,'old':old,'new':new,'rationale':why,'occurrences':n,'line_before':original[name][:original[name].index(old)].count('\n')+1})
  texts[name]=s.replace(old,new)
def all_prose(old,new,why):
 for p in files:
  apply(p.relative_to(b),old,new,why)
m='Paper_XI_Traditional_Final.tex'
for old,new in [
('The present article asks','This chapter asks'),('First, the article proves','First, this chapter proves'),('throughout the paper.','throughout this chapter.'),('The article is organized as follows.','This chapter is organized as follows.'),('The present article uses this theorem','This chapter uses this theorem'),("Fix the paper's reciprocity","Fix this chapter's reciprocity"),('The article proves the following statements','This chapter proves the following statements'),('The article does not independently prove','This chapter does not independently prove')]:
 apply(m,old,new,'Use chapter terminology for the current volume contribution.',1)
apply(m,'Tensor refinement separates into greatest common divisor many packets, each with least common multiple carrier dimension.','Tensor refinement gives as many packets as the greatest common divisor, each with carrier dimension equal to the least common multiple.','Repair awkward caption syntax without changing the packet count or carrier-dimension statement.',1)
rt='reader_route.tex'
apply(rt,"This monograph presents the finite packet theory and retains the detailed restricted arithmetic constructions. Two separate research companions explain the later progress toward Conjecture 66. They do not replace the monograph's proved statements or turn its conditional comparison into an existence theorem.","This chapter presents the finite packet theory and retains the detailed restricted arithmetic constructions. Two separate research companions explain the later progress toward Conjecture 66. They do not replace this chapter's proved statements or turn its conditional comparison into an existence theorem.",'Identify the current chapter and preserve the exact realization/comparison boundary.',1)
apply(rt,'Core monograph &','Mathematical text &','Use the volume\'s reader label for the mathematical text.',1)
apply(rt,'Geometric route through the core paper','Geometric route through the mathematical text','Use the volume\'s reader label in link text while preserving the link target.',1)
apply(rt,'Lean and evidence guide &','Formal companion &','Use formal companion as the general back-matter label.',1)
apply(rt,'{Toward Arithmetic Packet Realization}, Connected proofs','{Toward Arithmetic Packet Realization}. Connected proofs','Repair the sentence boundary after the exact companion title.',1)
apply(rt,'{Arithmetic Packet Realization}, Thirty-two worked plates','{Arithmetic Packet Realization}. Thirty-two worked plates','Repair the sentence boundary after the exact companion title.',1)
# American spelling. Every occurrence was read in its prose context.
all_prose('labelled','labeled','Use American English spelling.')
all_prose('relabelling','relabeling','Use American English spelling.')
# Objective joined-word errors in the retained narrative, not mathematical tokens.
for old,new in [
('dimension6','dimension 6'),('dimension8','dimension 8'),('dimension1','dimension 1'),('dimension2d','dimension 2d'),('dimension4','dimension 4'),('dimension27','dimension 27'),('dimension2s','dimension 2s'),('dimension2(R-s)','dimension 2(R-s)'),
('factor of2','factor of 2'),('ranks2 and4','ranks 2 and 4'),('period2','period 2'),('period4','period 4'),('between2 and4','between 2 and 4'),('index2','index 2'),('index4','index 4'),('coefficient of1','coefficient of 1'),
('or3.','or 3.'),('congruent to1','congruent to 1'),('to1 or -1','to 1 or -1'),('quadratic character1','quadratic character 1'),('modulo4','modulo 4'),('order4','order 4'),('order8','order 8'),('order2','order 2'),
('starting line4911','starting line 4911'),('starting line4834','starting line 4834'),('lines6892--6947','lines 6892--6947'),('lines4911--4923','lines 4911--4923'),('and4.','and 4.'),('Sections~13 and15','Sections~13 and 15'),('refutation of16.2','refutation of 16.2')]:
 all_prose(old,new,'Insert an omitted word/number boundary in reader-facing prose; preserve the mathematical value or source locator.')
# Checkpoint numbers here are explicit historical provenance, not chapter numbers.
for old,new in [('from166','from Block 166'),('as166','as in Block 166'),('in166','in Block 166'),('of166','of Block 166'),('final166 files','final Block 166 files'),('in161','in Block 161'),('Blocks161 and165','Blocks 161 and 165')]:
 all_prose(old,new,'Restore the omitted boundary in an explicit historical checkpoint reference, preserving its identifier.')
for old,new in [('Proposition9.8','Proposition 9.8'),('Proposition11.3','Proposition 11.3'),('Proposition13.7','Proposition 13.7'),('Fact13.4','Fact 13.4'),('Fact10.2','Fact 10.2'),('Remark2.2.7','Remark 2.2.7'),('Proposition3.1.9','Proposition 3.1.9'),('Proposition3.2.5','Proposition 3.2.5'),('Corollary3.3.18','Corollary 3.3.18'),('Condition3.6.13','Condition 3.6.13'),('Corollary3.15','Corollary 3.15'),('Lemmas2.6,2.8,3.9,3.12,3.14','Lemmas 2.6, 2.8, 3.9, 3.12, 3.14'),('Criterion(1)','Criterion (1)'),('Equation(4)','Equation (4)'),('Formula(8)','Formula (8)'),('printed p55','printed p. 55'),('printed98--100','printed pp. 98--100'),('printed112--113','printed pp. 112--113'),('printed90--91','printed pp. 90--91'),('printed136--137','printed pp. 136--137')]:
 all_prose(old,new,'Restore spacing in a source citation or local formula reference without changing its number.')
for old,new in [('BK3.','BK 3.'),('BK1.','BK 1.'),('BK2.','BK 2.')]:
 all_prose(old,new,'Separate the bibliographic shorthand from its result number.')
for old,new in [('{4. Rank2 failure','{4. Rank 2 failure'),('{5. Rank4 failure','{5. Rank 4 failure'),('{6. Rank8:','{6. Rank 8:')]:
 apply('appendices/dyadic_capacity.tex',old,new,'Restore the omitted word/number boundary in a sentence-case heading.',1)
apply('appendices/dyadic_tower.tex','universal Paper XI closure','universal Chapter XI closure','Use Chapter XI for an ordinary volume reference.',1)
changed=[]
for name,after in texts.items():
 if after==original[name]:continue
 p=r/name;dst=r/'editorial/prose_review/xi_xii_before'/name;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_text()==original[name]
 else:shutil.copyfile(p,dst)
 p.write_text(after);changed.append(name)
(r/'editorial/prose_review/xi_traditional_exact_journal.json').write_text(json.dumps(journal,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'changed_files':len(changed),'journal_entries':len(journal),'replacement_occurrences':sum(x['occurrences'] for x in journal)},indent=2))
