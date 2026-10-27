#!/usr/bin/env python3
"""Verify XI ONLY and prepare complete changed-paragraph rereads."""
from pathlib import Path
from collections import Counter
import difflib,hashlib,json,re
import xi_xii_inventory as inv

ROOT=inv.ROOT;OUT=inv.OUT
files=json.loads((OUT/'xi_xii_files.json').read_text())
journal=json.loads((OUT/'xi_xii_journal.json').read_text())
assert all('/XI/' in e['file'] for e in files+journal)

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def protected(s,name):
    no_literal=inv.LITERAL.sub(lambda m:' '*len(m.group()),s)
    result={
      'preamble':[s.split('\\begin{document}',1)[0]] if '\\begin{document}' in s else [],
      'literal_and_quote_environments':[m.group() for m in inv.LITERAL.finditer(s)],
      'math_spans':[m.group() for m in inv.MATH.finditer(no_literal)],
      'literal_identifier_reference_macros':[s[a:b] for a,b in inv.macro_spans(s)],
      'additional_cross_references':re.findall(r'\\(?:cref|Cref|autoref)\*?\{[^}]+\}',s),
      'control_sequence_order':re.findall(r'\\(?:[A-Za-z@]+|[^A-Za-z\s])',s),
      'brace_order':re.findall('[{}]',s),
      'environment_order':re.findall(r'\\(?:begin|end)\{[^}]+\}',s),
      'numeric_token_order':re.findall(r'\d+(?:[.,]\d+)*',s),
      'comments':re.findall(r'(?<!\\)%[^\n]*',s),
    }
    if name.endswith('XI_Lean_Guide_Final.tex'):
      result['exact_generated_appendices']=[s[s.index('\\appendix\\chapter{Complete selected named-source catalog}'):]]
      a=s.index('Fix the declared class',s.index('\\section{The publication statement}'))
      result['exact_conjecture_66_publication_paragraph']=[s[a:s.index('\n\n',a)]]
    elif name.endswith('XI_Visual_Guide_Final.tex'):
      a=s.index('\\textbf{Conjecture 66 (arithmetic packet realization).}')
      result['exact_conjecture_66_visual_paragraph']=[s[a:s.index('\n\n',a)]]
    elif name.endswith('XI_Traditional_Final.tex'):
      result['exact_conjecture_environments']=re.findall(r'\\begin\{conjecture\}.*?\\end\{conjecture\}',s,re.S)
      a=s.index("Fix this chapter's reciprocity,")
      b=s.index('An \\emph{arithmetic realization witness}',a)
      result['exact_H1_H4_inputs']=[s[a:b]]
      a=s.index('\\begin{proposition}[Comparison of one realized candidate]')
      b=s.index('\\end{proof}',a)+len('\\end{proof}')
      result['exact_H5_comparison_and_proof']=[s[a:b]]
    return result

validation=[];patch=[];contexts=[]
for f in files:
 name=f['file'];before=(ROOT/f['backup']).read_text();after=(ROOT/name).read_text()
 replay=before
 for e in [e for e in journal if e['file']==name]:
  assert replay.count(e['old'])==e['occurrences'],(name,e['old'])
  replay=replay.replace(e['old'],e['new'],e['occurrences'])
 assert replay==after,('journal_replay',name)
 a,b=protected(before,name),protected(after,name)
 checks={k:{'identical':a[k]==b[k],'count':len(a[k]),'sha256':sha(json.dumps(a[k],ensure_ascii=False))} for k in a}
 assert all(e['identical'] for e in checks.values()),(name,{k:v for k,v in checks.items() if not v['identical']})
 validation.append({'file':name,'before_sha256':sha(before),'after_sha256':sha(after),'checks':checks,'journal_replay_exact':True})
 patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=f['backup'],tofile=name))
 al=before.splitlines(True);bl=after.splitlines(True)
 dirty=set()
 for tag,a1,a2,b1,b2 in difflib.SequenceMatcher(a=al,b=bl,autojunk=False).get_opcodes():
  if tag!='equal':dirty.update(range(b1+1,b2+1))
 for m in re.finditer(r'\S(?:.|\n)*?(?=\n\s*\n|\Z)',after):
  start=after[:m.start()].count('\n')+1;end=after[:m.end()].count('\n')+1
  if any(start<=n<=end for n in dirty):
   text=inv.MATH.sub('⟨math⟩',m.group());text=re.sub(r'\\(?:cref|Cref|ref|label|cite|eqref)\{[^}]*\}','[reference]',text)
   contexts.append(f"{name}:{start}–{end}\n"+' '.join(text.split()))

(OUT/'xi_xii_preservation.json').write_text(json.dumps({'scope':'XI ONLY','files':validation,'all_checks_pass':True},indent=2)+'\n')
(OUT/'xi_xii_changes.patch').write_text(''.join(patch))
batches=[];batch=[];words=0
for c in contexts:
 n=len(c.split())
 if batch and words+n>2600:batches.append(batch);batch=[];words=0
 batch.append(c);words+=n
if batch:batches.append(batch)
for i,batch in enumerate(batches,1):(OUT/f'xi_xii_reread_{i}.txt').write_text('\n\n'.join(batch)+'\n')
print(json.dumps({'scope':'XI ONLY','files':len(files),'journal_entries':len(journal),'actual_replacements':sum(e['occurrences'] for e in journal),
 'categories':dict(Counter(e['category'] for e in journal)),'protected_checks':'ALL IDENTICAL','changed_paragraphs':len(contexts),'reread_batches':len(batches),
 'math_spans':sum(f['checks']['math_spans']['count'] for f in validation),
 'literal_quote_environments':sum(f['checks']['literal_and_quote_environments']['count'] for f in validation),
 'literal_identifier_reference_macros':sum(f['checks']['literal_identifier_reference_macros']['count'] for f in validation)},indent=2))
