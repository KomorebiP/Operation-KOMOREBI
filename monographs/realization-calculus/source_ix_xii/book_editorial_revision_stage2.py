from pathlib import Path
import json,re,difflib
G=Path(__file__).resolve().parent;ROOT=G.parent
record=ROOT/'editorial/book_revision/ix_xii_substitutions.json'
LOG=json.loads(record.read_text())
def edit(rel,old,new):
 p=G/rel;t=p.read_text()
 if old not in t:raise ValueError(f'Missing exact edit in {rel}: {old[:100]}')
 LOG.append({'path':str(p.relative_to(ROOT)),'occurrences':t.count(old),'old':old,'new':new});p.write_text(t.replace(old,new))

# Give each development a stable descriptive reference, independent of its
# former development-block number. The source and Lean identifiers stay intact.
rel='X/manuscript/Paper_X_Block27_Amended.tex';p=G/rel;t=p.read_text();new=t
names={
  12:'group, inertia and monodromy finite-sum construction',
  13:'finite-exponential reconstruction',
  14:'completion from conjugacy classes',
  15:'fixed-depth comparison-certificate construction',
  16:'derived comparison-bound argument',
  17:'finite-group comparison with precision loss',
  18:'supplied-carrier summand-lifting construction',
  19:'simultaneous projector-family lifting construction',
  20:'finite logarithmic recovery argument',
  21:'fixed-quadratic-packet interpretation',
  22:'quadratic local-condition construction',
  23:'conditional completion construction',
  24:'conditional existence-boundary argument',
  25:'system-isomorphism and finite-cyclotomic comparison',
  26:'absolute-Galois restriction construction',
  27:'finite-number-field Frobenius comparison',
}
for number in names:
 pattern=r'(\\paragraph\{[^{}]*?) \(Block '+str(number)+r'\)(\.\})'
 new=re.sub(pattern,lambda m:m[1]+m[2]+r'\label{book:x-construction-'+str(number)+'}',new)
# Remove numerical progress accounting only; retain every mathematical boundary.
new=re.sub(r' At the Block (?:18|19|20|21) checkpoint, the ledger recorded.*?(?:above|correction above)\.', '',new,flags=re.S)
new=re.sub(r'At the Block 20 checkpoint, the ledger recorded fifteen checked claims\nand five partial claims; see the Block 23 scope correction above\.\n','',new)
new=new.replace('The full arithmetic\nledger at the Block 22 checkpoint recorded fifteen checked source claims\nand five partial claims; the Block 23 conditional-scope correction gives\nsixteen checked and four partial.\n','')
new=new.replace('The Block 23 source-claim count was therefore sixteen checked and four partial.\n','')
new=new.replace(r'\paragraph{New checked realization of the finite pattern.}',r'\paragraph{An explicit realization of the finite pattern.}')
new=new.replace('The Block 04 implementation separately uses','A separate finite-complex implementation uses')
new=new.replace('This is a new specified\nrealization of the displayed dimension pattern, not a claimed rerun of\nthe original companion implementation.', 'This realizes the displayed dimension pattern. Its formal check is\ndistinct from the original companion implementation.')
new=new.replace(r'\paragraph{New explicit checked realization.}',r'\paragraph{An explicit realization of the directed graph.}')
new=new.replace('Separately from the unretrieved original companion implementation, Block 05\nspecifies vertices', 'An independently specified graph has vertices')
new=new.replace('This observation and the real logarithmic limit are both formalized in Block 02.', 'The formal companion identifies proofs of both this observation and the real logarithmic limit.')
new=new.replace('The eighth formalization block works with actual matrix representations of a\nfixed group, not only with underlying sets.', 'The representation-level completion construction works with actual matrix\nrepresentations of a fixed group.')
new=new.replace('Blocks 21--22', 'the fixed-quadratic-packet and local-condition constructions')
for number,name in names.items():
 # Preserve a named construction rather than replacing it by an unexplained ID.
 anchor=r'\hyperref[book:x-construction-'+str(number)+']{'+name+'}'
 new=new.replace('The Block '+str(number), 'The '+anchor)
 new=new.replace('the Block '+str(number), 'the '+anchor)
 new=new.replace('Block '+str(number), 'the '+anchor)
new=new.replace('This block constructs one summand', 'This construction gives one summand')
new=new.replace('The release is designed to make every finite example and every displayed count independently reproducible without confusing computation with proof.', 'The source package makes the finite examples and displayed counts reproducible. Their computational checks remain distinct from universal proofs.')
new=new.replace('This edition\ncorrects the printed ceiling to the matching floor', 'The displayed extraction uses the matching floor')
# The preceding historical front matter is archival evidence, not an argument.
start=new.index(r'\section*{Historical ')
end=new.index(r'\paragraph{Retained checkpoint discussion.}',start)
new=new[:start]+r'''\section*{Further construction details}
The following constructions explain the representation, comparison and local
arithmetic steps used in the chapter. Appendix~\ref{sec:conditional-final}
assembles their conditional endpoint. The formal companion keeps the distinct
source contracts and verification records separate.

\paragraph{The formal model and its hypotheses.}
'''+new[end+len(r'\paragraph{Retained checkpoint discussion.}'):]
start=new.index('The cumulative ledger contains seventeen checked source proof claims')
end=new.index(r'\paragraph{Finite-group comparison',start)
new=new[:start]+r'''General prescribed-conjugacy prime coverage remains an input. Claims 8.2
and 11.2 retain their conditional hypotheses, including the required residual
levels, higher depths and supplied packets. Their nonemptiness and positive
trace are not unconditional conclusions. The finite cyclotomic comparison and
the fixed quadratic packet give restricted arithmetic realizations. In the
latter, the packet characters are trivial on actual valuation inertia at odd
primes. Identifying the decomposition group with the full local Galois group
remains a separate obligation, and ramification at two is not claimed.
The constructions do not identify every packet in the common arithmetic spine
or attach all Hodge--Tate and Weil--Deligne invariants. Universal occupancy and
natural finite seed rank remain conjectural.

'''+new[end:]
new=new.replace('The following thirty pages reproduce the worked atlas from the separate visual\nguide. They retain their own page labels Plates X.1--X.30, so the same example has the\nsame address in either reading route. The two opening contract pages of the\nstandalone guide are not repeated here.',
                'Plates X.1--X.30 form the worked visual atlas. Their chapter-qualified\nlabels identify the same examples throughout the collection.')
new=new.replace('The final page records the three distinct historical and current contracts.',
                'The final plate distinguishes the three source contracts and their\nmathematical boundaries.')
new=new.replace('The build script appends these source-built pages after this leaf and copies their\nbookmarks and internal links. The mathematical manuscript, its historical\ncheckpoint statements, and the later conditional assembly remain above.',
                'The visual studies connect these examples to the mathematical arguments\nand to the formal companion.')
if new!=t:edit(rel,t,new)

# Clean X's visual orientation while retaining its two independent branches.
rel='X/visual_appendix/appendix.tex';p=G/rel;t=p.read_text();new=t
new=new.replace(r'\section*{The current reading contract}',r'\section*{Two routes to realization}')
new=new.replace('This guide preserves the Block 27 and scalar/Mellin worked examples. Their stated checkpoint limits belong to those source revisions. The later occupied-system endpoint is checked at its amended conditional scope: 20/20 internal claims. Actual completed source members, inverse-limit profile closure, compatible carrier presentations and constituent local comparisons remain supplied inputs.',
                'The worked examples connect residual forests, finite occupancy and scalar/Mellin estimates. The conditional occupied-system theorem uses actual completed source members, inverse-limit profile closure, compatible carrier presentations and constituent local comparisons as explicit inputs.')
a=new.index(r'\section*{A checked scope and a later unpromoted scope}')
b=new.index(r'\clearpage',a)
new=new[:a]+r'''\section*{Reading the examples}
The mathematical text gives the arguments and the conditional assembly. The
formal companion explains the terminal source, its dependencies and recorded
verification. Each plate states the finite data used by its example and the
conclusion that those data support.

The target-family and carrier-recovery constructions have different inputs.
Their outputs need not be identified. A stronger residual-system contract,
retained in the research record, has no promoted endpoint. Its existence
requirements must not be substituted for the conditional theorem proved here.
'''+new[b:]
new=new.replace(r'\renewcommand{\thepage}{V\arabic{page}}',r'\renewcommand{\thepage}{\arabic{page}}')
new=new.replace(r'\selectfont\bfseries #3\par',r'\selectfont\bfseries Plate X.#1\quad /\quad #3\par')
if new!=t:edit(rel,t,new)

# Replace opaque arithmetic block tags in XI's visual source references with
# the actual named construction. These are publication tags, not theorem IDs.
rel='XI/publication/source/visual_guide/Paper_XI_Visual_Guide_Final.tex';p=G/rel;t=p.read_text();new=t
new=new.replace('developed in Blocks 166--167','developed in the detailed odd-prime and dyadic construction appendices')
new=new.replace('Blocks 166--167 contain ordinary mathematical arguments', 'The odd-prime and dyadic constructions have ordinary mathematical proofs')
new=new.replace('The release corrects the historical mixed-convention sentence.', 'The geometric-Frobenius convention is used consistently here.')
new=new.replace('Blocks 162, 166--167, profile and capacity audits','Profile and quotient-capacity comparisons')
new=new.replace('Blocks 166--167, ', 'Odd-prime and dyadic constructions: ')
new=new.replace('Block 166, ', 'Odd-prime construction: ')
new=new.replace('Block 167, ', 'Dyadic construction: ')
new=new.replace('Block 167 also records', 'The dyadic construction also gives')
new=new.replace('No fresh Lean certificate for Blocks 166--167 is asserted by this guide.', 'The arbitrary-length arithmetic constructions have ordinary proofs. Their formal coverage is stated separately in the formal companion.')
new=new.replace('From the checkpoint root, run', 'From the source-package root, run')
new=new.replace('Release source collection','Source collection')
new=new.replace('The release traditional paper preserves the route with the Frobenius correction and explicit realization boundary.', 'The mathematical text uses the geometric-Frobenius convention and states the realization boundary explicitly.')
if new!=t:edit(rel,t,new)

# Chapter XI's appendix headers identify their mathematics, rather than the
# date or administrative status at which a draft was first reviewed.
for p in (G/'XI/publication/source/traditional/appendices').glob('*.tex'):
 t=p.read_text();new=t
 new=re.sub(r'Date: 2026-10-05\. Ordinary proof(?:, submitted for independent audit| submitted for independent review)?\.\n', '',new)
 new=new.replace('Date: 2026-10-05. Ordinary proof. No character, quotient-dimension,', 'No character, quotient-dimension,')
 new=new.replace('Date: 2026-10-05. Corollary to', 'Corollary to')
 new=new.replace('Date: 2026-10-05. Base: the final reviewed Block166, pinned in', 'The odd-prime construction used here is pinned in')
 new=new.replace('Date: 2026-10-05. Parent:', 'Source record:')
 new=new.replace('Parent checkpoint: Paper\\_XI\\_Base\\_Realization165. New arithmetic', 'Source record: Paper\\_XI\\_Base\\_Realization165. Arithmetic')
 new=new.replace('Checkpoint: Paper\\_XI\\_Dyadic167. Parent: final', 'Source record: Paper\\_XI\\_Dyadic167. Dependency:')
 if new!=t:edit(p.relative_to(G),t,new)

# Local plate ranges are displayed compactly but remain explicit and clickable.
for k,rel,base in [('X','X/visual_appendix/appendix.tex','PXA.visual'),('XII','XII/publication/source/visual_guide/Paper_XII_Visual_Guide_Final.tex','v:')]:
 p=G/rel;t=p.read_text();new=t
 if k=='X':definition=r'\newcommand{\pagerefVrange}[2]{Plates~\hyperlink{PXA.visual#1.1}{X.#1}--\hyperlink{PXA.visual#2.1}{X.#2}}'
 else:definition=r'\newcommand{\pagerefVrange}[2]{Plates~\hyperref[v:#1]{XII.#1}--\hyperref[v:#2]{XII.#2}}'
 # Insert immediately before the shared style comment or next custom macro.
 marker=r'\newcommand{\pagerefV}[1]'
 line=next(line for line in new.splitlines() if line.startswith(marker))
 new=new.replace(line,line+'\n'+definition)
 if new!=t:edit(rel,t,new)
 for source in [G/rel,(G/rel).parent/'source/pages.tex']:
  if not source.exists():continue
  t=source.read_text();new=re.sub(r'\\pagerefV\{(\d+)\}--\\pagerefV\{(\d+)\}',lambda m:r'\pagerefVrange{'+m[1]+'}{'+m[2]+'}',t)
  new=new.replace('Lessons \\pagerefVrange','\\pagerefVrange').replace('Lessons \\pagerefV','\\pagerefV')
  if new!=t:edit(source.relative_to(G),t,new)

record.write_text(json.dumps(LOG,indent=2)+'\n')
diffs=[];changed=[]
for row in json.loads((ROOT/'editorial/book_revision/ix_xii_prose_inventory_before.json').read_text()):
 p=ROOT/row['path'];old=(G/'book_edit_before'/p.relative_to(G)).read_text();new=p.read_text()
 if old!=new:
  changed.append(row['path']);diffs.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+row['path'],tofile=row['path']))
(ROOT/'editorial/book_revision/ix_xii_prose.patch').write_text(''.join(diffs))
print(json.dumps({'changed_files':len(changed),'substitution_records':len(LOG)}))
