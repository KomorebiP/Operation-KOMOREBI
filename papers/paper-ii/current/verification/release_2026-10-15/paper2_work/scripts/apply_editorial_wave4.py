from pathlib import Path
import hashlib,json,difflib
root=Path('/workspace/scratch/9f53d520971c')
release=root/'release_package/Komorebi_Paper_II_Release_2026-10-15'
backup=root/'paper2_work/editorial_before_wave4';backup.mkdir(exist_ok=True)
changes=[]
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()

def update(rel,before,after,reason):
 p=release/rel;s=p.read_text();assert s.count(before)==1,(rel,s.count(before))
 b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_text(s)
 new=s.replace(before,after);p.write_text(new)
 changes.append({'source':rel,'before':before,'after':after,'before_sha256':sha(s),'after_sha256':sha(new),'source_evidence':'paper2_work/audit/rectifiable_dunford_source.json','reason':reason})

update('editable/traditional/chapters/05_defects.tex',
'The holomorphic functional calculus gives\n',
r'''The assertion is immediate if either space is zero. Otherwise, use the rectifiable-cycle form of the holomorphic functional calculus in \cite[Chapter~VII, \S4, Theorem~4.1, formula~(4.5), and Proposition~4.6]{Conway1990}. For each operator $T$, compare $\Gamma$ with a positive simple system around its spectrum. Their difference has zero winding outside $U\setminus\sigma(T)$, so Theorem~4.1 applied to the resolvent-valued integrand identifies the two integrals. Consequently,
''',
'Attach verified rectifiable Dunford source and make the winding-number translation explicit; theorem scope and defect argument unchanged.')

update('editable/traditional/references.bib','@book{Daubechies1992,',r'''@book{Conway1990,
  author    = {John B. Conway},
  title     = {A Course in Functional Analysis},
  edition   = {Second},
  publisher = {Springer},
  year      = {1990},
  doi       = {10.1007/978-1-4757-4383-8},
  isbn      = {978-0-387-97245-9}
}

@book{Daubechies1992,''',
'Exact verified Conway edition and publisher identifier; existing Kato background record retained.')

report={'schema':'komorebi.paper_ii.editorial_wave4.v1','status':'APPLIED_PENDING_PDF_BUILD','changes':changes,'authoring_marker':'Already run exactly once before wave1.','formal_scope_status_changes':False,'verification':'Source attribution/translation supplied by root verified-source report; this agent did not claim an independent whole-source inspection.'}
(root/'paper2_work/audit/editorial_wave4.json').write_text(json.dumps(report,indent=2)+'\n')
diffs=[]
for c in changes:
 rel=c['source'];old=(backup/rel).read_text();new=(release/rel).read_text()
 diffs.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=rel+' (before)',tofile=rel+' (after)'))
(root/'paper2_work/audit/editorial_wave4.diff').write_text(''.join(diffs))
print(json.dumps({'status':'APPLIED','changes':len(changes)}))
