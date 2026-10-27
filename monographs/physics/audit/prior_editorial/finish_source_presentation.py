from pathlib import Path
import re,json
P=Path('/mnt/data/physics_editorial_work/publication');M=P/'source/monographs';notes=[]
for rel in ['foundation_visual/visual_body.tex','visual/visual_body.tex','gauge_visual/visual_body.tex','gravity_visual/visual_body.tex','adic_visual/visual_body.tex']:
 p=M/rel;s=p.read_text().replace('edition root','source root').replace('software versions','software dependencies')
 if 'gauge_visual' in rel:
  start=s.find('\\paragraph{Failures and recovery.}')
  if start>=0:
   off=start+len('\\paragraph{Failures and recovery.}')
   nex=re.search(r'\\(?:paragraph|section|clearpage|end\{document)',s[off:]);end=off+nex.start() if nex else len(s)
   notes.append({'file':rel,'text':s[start:end]})
   s=s[:start]+'''The numerical provenance record retains failed and corrected checks as well as successful outputs. A successful bounded calculation is evidence for its specified input and tolerance, not a universal proof.\n\n'''+s[end:]
 s=s.replace('All figures were regenerated using','The figure generator is').replace('The current endpoint','The operator construction')
 p.write_text(s)
for rel in ['foundations/references.tex','references.tex','gauge/references.tex','gravity/references.tex','adic/references.tex']:
 p=M/rel;s=p.read_text();s=re.sub(r'v0\.49\.0','source archive',s);s=re.sub(r'Checked\s*Block\s*49','formal verification record',s);p.write_text(s)
(P/'audit/moved_atlas_provenance.json').write_text(json.dumps(notes,indent=2))
