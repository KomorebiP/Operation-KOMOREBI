from pathlib import Path
import re,json,sys,hashlib,difflib,collections
sys.path.insert(0,str(Path(__file__).resolve().parent))
from vii_viii_scan import ROOT,OUT,FILES,PAT,masked
J=json.loads((OUT/'vii_viii_journal.json').read_text())
CMD=re.compile(r'\\(?:label|ref|eqref|cref|Cref|pageref|pagerefV|cite|citep|citet|input|include|includegraphics|code|lean|path|url|href|detokenize|lstinputlisting|inputminted)\*?(?:\[[^\]]*\])?\{(?:[^{}]|\{[^{}]*\})*\}')
ENV=re.compile(r'\\(?:begin|end)\{[^{}]+\}')
protected=[];diff=[];changed=[]
for f in FILES:
 old=(OUT/'vii_viii_before'/f).read_text();new=(ROOT/f).read_text()
 rec={'file':f,'protected_math_literal_figure_comments':len(list(PAT.finditer(old))),'protected_identifier_commands':len(CMD.findall(old)),'environment_delimiters':len(ENV.findall(old)),'pass':True}
 assert [m.group() for m in PAT.finditer(old)]==[m.group() for m in PAT.finditer(new)],('protected spans',f)
 assert CMD.findall(old)==CMD.findall(new),('commands',f)
 assert ENV.findall(old)==ENV.findall(new),('environments',f)
 assert old.count('{')==new.count('{') and old.count('}')==new.count('}'),('braces',f)
 expected=old
 for e in [x for x in J if x['file']==f]:
  assert expected.count(e['old'])==1,('journal reconstruct',f,e['old'])
  expected=expected.replace(e['old'],e['new'])
 assert expected==new,('unrecorded changes',f)
 if old!=new:
  changed.append({'file':f,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(new.encode()).hexdigest()})
  diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+f,tofile='after/'+f,n=2))
 protected.append(rec)
for name in ['pages.tex','extended_pages.tex']:
 assert (ROOT/f'source_v_viii/VIII/editable/traditional/atlas_sources/{name}').read_text()==(ROOT/f'source_v_viii/VIII/editable/visual_guide/source/{name}').read_text()
atlas=(ROOT/'source_v_viii/VII/editable/traditional/monograph_atlas.tex').read_text()
for name in ['pages.tex','extended_pages.tex']:
 assert (ROOT/f'source_v_viii/VII/editable/visual_guide/source/{name}').read_text() in atlas
(OUT/'vii_viii_preservation.json').write_text(json.dumps({'all_pass':True,'files':protected,'duplicate_plate_bodies_consistent':True,'journal_reconstructs_all_52_files':True,'mathematical_token_changes':0},indent=2)+'\n')
(OUT/'vii_viii_changes.diff').write_text(''.join(diff))
(OUT/'vii_viii_changed_files.json').write_text(json.dumps(changed,indent=2)+'\n')
print('PASS',len(FILES),'inputs;',len(changed),'changed files;',len(J),'exact journal entries')
print('protected spans',sum(x['protected_math_literal_figure_comments'] for x in protected),'identifier commands',sum(x['protected_identifier_commands'] for x in protected),'environment tokens',sum(x['environment_delimiters'] for x in protected))
# Compact after-edit reread: sentences that differ, with original line references.
parts=[]
for e in J:
 if '/traditional/atlas_sources/' in e['file'] or e['file'].endswith('traditional/monograph_atlas.tex'):continue
 a=e['old'];b=e['new'];sm=difflib.SequenceMatcher(None,a,b)
 rr=[]
 for tag,i,j,k,l in sm.get_opcodes():
  if tag!='equal':rr.append((max(0,k-80),min(len(b),l+100)))
 merged=[]
 for x,y in rr:
  if merged and x<=merged[-1][1]:merged[-1]=(merged[-1][0],max(y,merged[-1][1]))
  else:merged.append((x,y))
 parts.append(e['file']+'\n'+' ... '.join(b[x:y] for x,y in merged))
(OUT/'vii_viii_after_reread.txt').write_text('\n\n'.join(parts)+'\n')
