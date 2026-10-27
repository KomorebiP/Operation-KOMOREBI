from pathlib import Path
import json,re,hashlib
r=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
out=r/'editorial/prose_review'
journal=json.loads((out/'xi_traditional_exact_journal.json').read_text())
changed=sorted({e['file'] for e in journal})
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
patterns={
 'math':r'(?s)(?<!\\)\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?|displaymath|math)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?|displaymath|math)\}',
 'literal':r'(?s)\\(?:path)\{[^}]*\}|\\begin\{(?:Verbatim|verbatim|lstlisting|minted)\}.*?\\end\{(?:Verbatim|verbatim|lstlisting|minted)\}|\\(?:code|leanname|texttt|nolinkurl|url)\{[^\n]*?\}|\\excerpt\{[^}]*\}\{[^}]*\}',
 'labels_refs_citations_inputs':r'\\(?:label|ref|pageref|cref|Cref|eqref|cite|bibliography|bibliographystyle|input|include|vfig)\*?(?:\[[^\]]*\])?\{[^}]*\}|\\excerpt\{[^}]*\}\{[^}]*\}|\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}',
 'latex_environment_sequence':r'\\(?:begin|end)\{[^}]*\}',
 'conjecture_status':r'(?s)\\begin\{conjecture\}.*?\\end\{conjecture\}',
 'numeric_tokens':r'\d+',
 'hyperlink_destinations':r'\\href\{[^}]*\}|\\hypertarget\{[^}]*\}'
}
checks=[]
for name in changed:
 before=(out/'xi_xii_before'/name).read_text();after=(r/name).read_text()
 row={'file':name,'before_sha256':sha(before),'after_sha256':sha(after)}
 for key,pat in patterns.items():
  a=re.findall(pat,before);b=re.findall(pat,after)
  row[key]={'count_before':len(a),'count_after':len(b),'before_sha256':sha(json.dumps(a,ensure_ascii=False)),'after_sha256':sha(json.dumps(b,ensure_ascii=False)),'identical':a==b}
  assert a==b,(name,key)
 # Replaying exact logged replacements from original bytes must reconstruct current file.
 replay=before
 for e in [x for x in journal if x['file']==name]:
  assert replay.count(e['old'])==e['occurrences']
  replay=replay.replace(e['old'],e['new'])
 assert replay==after,name
 row['exact_journal_reconstruction']=True
 checks.append(row)
manifest=json.loads((out/'xi_traditional_before_hashes.json').read_text())
actual_changed=[]
for name,digest in manifest.items():
 assert (r/name).is_file(),name
 if hashlib.sha256((r/name).read_bytes()).hexdigest()!=digest: actual_changed.append(name)
assert sorted(actual_changed)==changed,(actual_changed,changed)
record={'status':'PASS','changed_files':checks,'baseline_files_checked':len(manifest),'only_journaled_files_changed':True,'math_token_changes':'none','literal_or_code_changes':'none','label_citation_input_or_figure_source_changes':'none','rebuild':'Not run: root coordinates source rebuild after editing is sealed.'}
(out/'xi_traditional_preservation_check.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'PASS','changed_files':len(checks),'baseline_files_checked':len(manifest),'math_regions_compared':sum(x['math']['count_before'] for x in checks),'literal_regions_compared':sum(x['literal']['count_before'] for x in checks)},indent=2))
