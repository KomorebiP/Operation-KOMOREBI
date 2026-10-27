#!/usr/bin/env python3
"""Apply individually reviewed paragraph edits from the frozen rhythm baseline."""
from pathlib import Path
import json,re,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'editorial/rhythm_review'
spec=importlib.util.spec_from_file_location('inventory',OUT/'ix_x_candidates.py');inv=importlib.util.module_from_spec(spec);spec.loader.exec_module(inv)
D=json.loads((OUT/'ix_x_candidates.json').read_text());journal=[];decisions=[]
# Logical/hypothesis lists and exact source/bibliographic catalogues retain their separators.
RETAIN={286:'structured mathematical list',815:'structured open-question list',973:'structured mathematical definition list',974:'structured theorem hypothesis list',1049:'structured theorem hypothesis list',662:'declaration catalogue separators',705:'source-module catalogue separators',1135:'bibliographic edition record'}
SPECIAL={
2:[('original statement; explicit','original statement, with explicit'),('Every prime-power width; signed steps','Every prime-power width, with signed steps'),('addresses $0,1,2$; stated','addresses $0,1,2$ and stated')],
42:[('conjecture_3_9}; original','conjecture_3_9}, with the original'),('Historically compiled; includes','Historically compiled, including'),('Historically compiled; exponent','Historically compiled with exponent'),('new continuation; not Lean formalized here.','new continuation. Not formalized in Lean here.'),('addresses zero and one; mixed','addresses zero and one and the mixed'),('beyond $N=4$; all-rank','beyond $N=4$ and the all-rank'),('new continuation; not implied','new continuation. Not implied'),('addresses two and three; unrestricted','addresses two and three and the unrestricted')],
123:[('It fixes $z_0=x$; $F(z_n)$','It fixes $z_0=x$. $F(z_n)$'),('$q^{L+n}$; successive','$q^{L+n}$. Successive'),('$q^{L+n}$; every','$q^{L+n}$. Every'),('earlier depth; the digit','earlier depth. The digit'),('starting one; and surjectivity','starting one. Surjectivity')],
734:[('reaches every depth; separation','reaches every depth, but separation')],
739:[('Proved; later prose development','Proved in the later prose development'),('Proved; no fresh Lean build','Proved. No fresh Lean build')],
856:[('completed; formal capstone','completed as the formal capstone'),('false; exact witnesses retained','false, with exact witnesses retained'),('open; a distinct research program','open as a distinct research program')],
1068:[('supplied commuting split operators; characteristic-zero trace criterion','supplied commuting split operators and a characteristic-zero trace criterion')],
}
# Local wording chosen after reading these paragraphs and their mathematical context.
WORDS={
0:[('The strongest common-step conclusion in width four is particularly compact.','The strongest common-step conclusion in width four is compact.')],
3:[('named-source catalog','catalog of named sources')],
16:[('not merely assigned a suggestive name','not just assigned a suggestive name')],
29:[('Positivity is load-bearing: it justifies the finite address set.','Positivity justifies the finite address set.')],
33:[('It is therefore essential to distinguish a raw formal coefficient from its degree-indexed generalized Euler number.','A raw formal coefficient must therefore be distinguished from its degree-indexed generalized Euler number.')],
34:[('The important change of basis is','The change of basis is')],
50:[('It is not necessary to relabel an already formalized four-packet statement as an unformalized new theorem in order to explain that extension.','Explaining this extension does not require relabeling an already formalized four-packet statement as an unformalized new theorem.')],
58:[('a genuine special case','a special case')],
72:[('The important controls include','The controls include')],
116:[('was actually run','was run')],
117:[('freshly re-observed here','observed again here')],
136:[('that additional divisible-fixed-point precision argument','that additional precision argument for divisible fixed points')],
316:[('internal computational-assistant reviews','internal reviews by computational assistants')],
319:[('the editable three-document sources','the editable sources for the three documents')],
335:[('not an as-written certificate','not a certificate as written')],
431:[('The per-point\ninvertibility hypothesis','The invertibility hypothesis at each point')],
444:[('the genuine binomial convolution','the binomial convolution')],
470:[('a genuine unit inverse','a unit inverse')],
493:[('Fourteen manuscript-proved items','Fourteen items proved in the manuscript')],
548:[('Remaining named manuscript-proved items','Remaining named items proved in the manuscript')],
576:[('Four manuscript-proved items','Four items proved in the manuscript')],
635:[('The reciprocal is genuinely integral','The reciprocal is integral')],
884:[('the conjectural finite-seed-rank statement','the conjecture that the seed rank is finite')],
922:[('a genuine zeroth-order coordinate','a zeroth-order coordinate')],
1116:[('Their chapter-qualified labels','Their labels, qualified by chapter,')],
1124:[('not re-proved by this final module','not proved again by this final module')],
1128:[('a hypothesis-by-hypothesis guide','a guide to each hypothesis')],
1162:[('The same-looking symbol can refer to quite different spaces.','The same symbol can refer to quite different spaces.')],
1182:[('The quotient is the important step','Passing to the quotient')],
1190:[('What full rank buys','What full rank implies')],
1194:[('a genuine sub-sum of that carrier','a sum of selected constituents of that carrier')],
1199:[('The hypotheses do real work','Why the hypotheses are needed'),('Two tiny matrices show why','Two matrices show why')],
1201:[('CLOSEDNESS IS NOT DECORATION','CLOSEDNESS OF THE LOCAL CONDITIONS')],
1203:[('The smallest counterexample is already decisive','A counterexample over the integers')],
1218:[('making this a square-root-in-area bound for this square-box model','giving a bound proportional to the square root of the area in this square model')],
1220:[('What a power-saving bound buys analytically','Analytic consequences of a power-saving bound')],
}
# Prose coverage-count sentences (not catalogue cells) use a normal relative phrase.
for i in [438,465,496,524,551,578,602,627,651]:WORDS.setdefault(i,[]).append(('named manuscript-proved items','named items proved in the manuscript'))
for name in D['files']:
 before=(OUT/'ix_x_before'/name).read_text();clean=inv.mask(before)
 pars={clean[:m.start()].count('\n')+1:m for m in re.finditer(r'\S.*?(?=\n\s*\n|\Z)',clean,re.S)}
 changes=[]
 for i,p in enumerate(D['paragraphs']):
  if p['file']!=name:continue
  m=pars[p['line']];old=before[m.start():m.end()];new=old;reasons=[]
  semipos=[x.start() for x in re.finditer(r'(?<!\\);',m.group())]
  retained=[]
  if semipos and i not in RETAIN and i not in SPECIAL:
   # Candidate decisions are paragraph-specific. Structured contract enumerations,
   # locator headings, and the named-source catalogue remain literal separators.
   selected=[]
   for pos in semipos:
    prefix=old[:pos];line=prefix.rsplit('\n',1)[-1]
    contract_start=prefix.rfind('\\contract{');contract_end=prefix.rfind('\\excerpt{')
    in_contract=contract_start>=0 and contract_start>contract_end and i in {106,109,137}
    if '\\pageheading{' in line or '\\vpage{' in line or in_contract:retained.append(pos)
    else:selected.append(pos)
   for pos in reversed(selected):
    tail=new[pos+1:];n=re.search(r'\S',tail)
    if n and tail[n.start()].isalpha():tail=tail[:n.start()]+tail[n.start()].upper()+tail[n.start()+1:]
    new=new[:pos]+'.'+tail
   if selected:reasons.append('Replace the reviewed independent-clause separator with a sentence boundary; capitalize only ordinary prose starts.')
  elif semipos and i in RETAIN:retained=semipos
  if i in SPECIAL:
   for a,b in SPECIAL[i]:
    if a not in new:raise AssertionError((i,a))
    new=new.replace(a,b)
   reasons.append('Use a conjunction or sentence suited to this scope table, heading, or explanatory list.')
  for a,b in WORDS.get(i,[]):
   if a not in new:
    found=re.search(r'\s+'.join(re.escape(w) for w in a.split()),new)
    if not found:raise AssertionError((i,a))
    a=found.group()
   new=new.replace(a,b);reasons.append('Use direct syntax and remove optional hyphenation or emphasis while retaining the same claim.')
  decisions.append({'id':i,'file':name,'line':p['line'],'candidates':p['candidates'],'changed':new!=old,'retained_semicolons':len(retained),'retention_reason':RETAIN.get(i,'technical compounds, ranges/eponyms, necessary logical distinctions, or structured locator/hypothesis punctuation retained after contextual review')})
  if old!=new:
   changes.append((m.start(),m.end(),new));journal.append({'id':i,'file':name,'line_before':p['line'],'old':old,'new':new,'rationale':' '.join(dict.fromkeys(reasons))})
 after=before
 for start,end,new in reversed(changes):after=after[:start]+new+after[end:]
 (ROOT/name).write_text(after)
(OUT/'ix_x_journal.json').write_text(json.dumps(journal,indent=2,ensure_ascii=False)+'\n')
(OUT/'ix_x_decisions.json').write_text(json.dumps(decisions,indent=2,ensure_ascii=False)+'\n')
print(len(journal),'changed paragraphs',len({e['file']for e in journal}),'files')
