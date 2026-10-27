from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
OUT=ROOT/'editorial/rhythm_review'
changes=[]
def add(file,old,new,why):changes.append({'file':file,'old':old,'new':new,'rationale':why})
I='source_i_iv/I/editable/'
II='source_i_iv/II/editable/'
add(I+'traditional/01_orientation.tex','final semantic-realization criterion','final semantic realization criterion','Remove an optional hyphen in the established name of the criterion.')
add(I+'traditional/02_foundations.tex','A realization is simply a pair of spaces and a linear map','A realization is a pair of spaces and a linear map','Remove an unnecessary introductory qualifier.')
add(I+'traditional/visual_atlas.tex','compatible semisimple decompositions; the split formula','compatible semisimple decompositions. The split formula','Separate two complete explanatory clauses.')
add(I+'traditional/visual_atlas.tex','one genuinely new coordinate','one new coordinate','Remove an unnecessary intensifier.')
add(I+'traditional/visual_atlas.tex','Higher powers of $y$ are rewritten using the relation. They are not simply discarded.','Higher powers of $y$ are rewritten using the relation rather than discarded.','State the distinction directly in one sentence.')
add(II+'lean_guide/Paper_II_Lean_Guide_Final.tex','foundational declaration-level walkthrough','foundational walkthrough of declarations','Use a natural prepositional phrase instead of an optional compound.')
f=II+'lean_guide/chapters/01_orientation.tex'
for old,new in [
('formalization/lean/}; the versioned path','formalization/lean/}. The versioned path'),
('Distinct mapped declarations; not all are theorem declarations.','Distinct mapped declarations. Not all are theorem declarations.'),
('A ring, possibly noncommutative; multiplicative order remains significant.','A ring, possibly noncommutative. Multiplicative order remains significant.'),
('A scalar action with its laws; the scalar type is explicitly named.','A scalar action with its laws. The scalar type is explicitly named.'),
('A ring or semiring homomorphism; it preserves the operations used to transport an inverse.','A ring or semiring homomorphism. It preserves the operations used to transport an inverse.'),
('Integers modulo $n$; the nonzero modulus hypotheses matter for finite cardinality.','Integers modulo $n$. The nonzero modulus hypotheses matter for finite cardinality.'),
('Existence of a term of type $A$; it does not by itself supply a computational search procedure.','Existence of a term of type $A$. It does not by itself supply a computational search procedure.')]:
 add(f,old,new,'Separate complete clauses in explanatory prose without changing the formal expression or its scope.')
f=II+'lean_guide/chapters/03_transfer.tex'
add(f,"Rows 12--13 and 25 are among the component's strongest construction results.",'Rows 12--13 and 25 describe the finite graph construction.','Replace an evaluative introduction with its concrete subject.')
add(f,'The crucial proof is the identification of the independently enumerated series matrix with this rational matrix.','The proof identifies the independently enumerated series matrix with this rational matrix.','Use a direct verb and remove an evaluative adjective.')
add(f,'This is the familiar uniqueness calculation','This is the uniqueness calculation','Remove an unnecessary familiarity claim.')
add(f,'It makes the construction claim auditable: rationality was not an assumption about the enumerated coefficients.','Rationality was not assumed for the enumerated coefficients.','State the same scope distinction directly.')
add(f,'The final existential theorem simply packages','The final existential theorem packages','Remove an unnecessary qualifier.')
f=II+'lean_guide/chapters/06_replay.tex'
for old,new in [
('Read \\code{lean-toolchain}; do not silently substitute','Read \\code{lean-toolchain}. Do not silently substitute'),
('a successful aggregate build; verify source and manifest identity.','a successful aggregate build. Verify source and manifest identity.'),
('the actual equation required by the chosen theorem; naming a candidate','the actual equation required by the chosen theorem. Naming a candidate'),
('the failing declaration and transcript; do not weaken the allowed-axiom gate','the failing declaration and transcript. Do not weaken the allowed-axiom gate'),
('tests of the Python component; they are not Lean kernel evidence.','tests of the Python component. They are not Lean kernel evidence.'),
('verifies rendering and navigation; formal coverage depends','verifies rendering and navigation. Formal coverage depends')]:
 add(f,old,new,'Separate complete instructions or explanatory clauses into sentences.')
f=II+'traditional/Paper_II_Traditional_Final.tex'
add(f,'The worked plates supply concrete models; the formal companion identifies','The worked plates supply concrete models. The formal companion identifies','Separate the roles of the two companions into sentences.')
f=II+'traditional/chapters/04_arithmetic.tex'
add(f,'inputs to the transport statement; it does not provide an extracted','inputs to the transport statement. It does not provide an extracted','Separate the supplied inputs from the stated implementation boundary.')
f=II+'traditional/chapters/07_scope.tex'
add(f,'one written theorem; these are distinct counting units.','one written theorem. These are distinct counting units.','Separate the explanatory conclusion from the preceding clause.')
add(f,'statement scopes it identifies; an earlier preservation report','statement scopes it identifies. An earlier preservation report','Separate independent verification-scope statements.')
for f in [II+'traditional/visual_atlas.tex',II+'visual_guide/source/pages_final.tex']:
 add(f,'The apparently larger list of fine packets simply has smaller individual packet spaces.','The larger list of fine packets has smaller individual packet spaces.','Remove unnecessary qualifiers from the concrete coordinate comparison.')
 add(f,'One extra digit is genuinely necessary','One extra digit is necessary','Remove an unnecessary intensifier from the plate title.')
 add(f,'A SHARP PRECISION-DELAY EXAMPLE','A SHARP EXAMPLE OF PRECISION DELAY','Replace an optional compound modifier with a natural phrase.')
 add(f,'An ordinary integer-lattice picture','A picture of the ordinary integer lattice','Replace an optional compound modifier with a natural phrase.')
 add(f,'A DEPTH-BY-DEPTH FIBER BUDGET','A FIBER BUDGET AT EACH DEPTH','Use direct syntax instead of a stacked compound modifier.')
 add(f,'the quotient-and-remainder information needed','the information about quotient and remainder needed','Replace a stacked compound with a natural phrase.')
 add(f,'a uniform-in-$n$ small error','a small error uniformly in $n$','Remove an awkward compound while preserving the uniformity variable.')
 add(f,'a one-sided-witness version','a version using one-sided witnesses','Remove the optional attachment hyphen while retaining the technical term one-sided.')
 add(f,'twenty-one numbered main-text definitions and results','twenty-one numbered definitions and results in the main text','Replace an optional compound with a natural phrase.')
 add(f,'the foundational interfaces; the chapter-wide map','the foundational interfaces. The chapter-wide map','Separate independent scope descriptions.')
add(II+'visual_guide/Paper_II_Visual_Guide_Final.tex','One extra digit is genuinely necessary','One extra digit is necessary','Keep the navigation title identical to the revised plate title.')
f=I+'lean_guide/generated/release_current.tex'
for old,new in [
('supplies the statements and proofs; the machine catalog','supplies the statements and proofs. The machine catalog'),
('stable identifiers and source locators; the formal correspondence map','stable identifiers and source locators. The formal correspondence map'),
('These quantities describe that receipt; it does not claim','These quantities describe that receipt. It does not claim'),
('may strengthen those earlier results; the original theorem signatures','may strengthen those earlier results. The original theorem signatures'),
('These are source-navigation entries.','These entries support source navigation.'),
('the exact declaration names and hypotheses; its verification receipt','the exact declaration names and hypotheses. Its verification receipt'),
('and the combined presentation; its two comparison maps','and the combined presentation. Its two comparison maps'),
('\\code{formal/evidence/RELEASE_VERIFICATION.json}; its detailed compiler','\\code{formal/evidence/RELEASE_VERIFICATION.json}. Its detailed compiler'),
("Logical replay uses Lean's official kernel; it is not an independently implemented checker.","Logical replay uses Lean's official kernel. It is not an independently implemented checker.")]:
 add(f,old,new,'Clarify current overview prose while preserving exact source paths, evidence counts, and contract text.')
f=I+'machine/generated/release_verification.tex'
for old,new in [
('at their recorded scopes; they do not count','at their recorded scopes. They do not count'),
('\\nolinkurl{formal/evidence/RELEASE_VERIFICATION.json}; its detailed compiler','\\nolinkurl{formal/evidence/RELEASE_VERIFICATION.json}. Its detailed compiler'),
("Logical replay uses Lean's official kernel; it is not an independently implemented checker.","Logical replay uses Lean's official kernel. It is not an independently implemented checker.")]:
 add(f,old,new,'Separate complete clauses in the current evidence overview without altering recorded evidence.')
f=II+'lean_guide/generated/current_release.tex'
add(f,'The table records the results of those checks; typesetting does not repeat them.','The table records the results of those checks. Typesetting does not repeat them.','Separate the evidence statement from the typesetting boundary.')
# Validate every exact replacement before writing anything.
working={}
for c in changes:
 p=ROOT/c['file'];s=working.setdefault(c['file'],p.read_text())
 n=s.count(c['old'])
 if n!=1:raise ValueError((c['file'],c['old'],n))
 c['line_before_current']=s[:s.index(c['old'])].count('\n')+1
 working[c['file']]=s.replace(c['old'],c['new'],1)
backup=OUT/'i_ii_before'
for f,s in working.items():
 p=ROOT/f;b=backup/f;b.parent.mkdir(parents=True,exist_ok=True)
 if b.exists():raise ValueError('backup already exists: '+str(b))
 shutil.copyfile(p,b)
 p.write_text(s)
for n,c in enumerate(changes,1):c['id']=n
(OUT/'i_ii_journal.json').write_text(json.dumps({'status':'APPLIED_PENDING_REVIEW','changes':changes},indent=2)+'\n')
print(json.dumps({'changed_files':len(working),'exact_replacements':len(changes),'files':list(working)},indent=2))
