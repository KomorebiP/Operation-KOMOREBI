"""Run from the package root with --baseline PATH to compare the technical input.

This is a preservation audit, not a proof checker. All text changes remain
visible in the generated source diff.
"""
from pathlib import Path
import argparse,re,json,hashlib,collections,difflib,platform,importlib.metadata,shutil
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[2];b=a.baseline;o=Path(__file__).resolve().parent
names=['theorem','proposition','corollary','lemma','remark','algorithm','proof']
def text(root):return '\n'.join(f.read_text() for f in sorted((root/'book/chapters').glob('*.tex')))
bt,rt=text(b),text(r)
counts=lambda t:{e:len(re.findall(r'\\begin\{'+e+r'\}',t)) for e in names}
label=lambda t:set(re.findall(r'\\label\{([^}]+)\}',t))
oldlabs,newlabs=label(bt),label(rt)
audit={'baseline_environment_counts':counts(bt),'current_environment_counts':counts(rt),'missing_source_labels':sorted(oldlabs-newlabs),'added_labels':sorted(newlabs-oldlabs)}
for folder in ['engine','lean']:
    fs=[f for f in (b/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ['.pyc','.olean','.ilean']]
    changed=[str(f.relative_to(b)) for f in fs if not (r/f.relative_to(b)).is_file() or f.read_bytes()!=(r/f.relative_to(b)).read_bytes()]
    audit[folder]={'compared_files':len(fs),'changed_or_missing':changed}
diff=[]
for f in sorted((b/'book').rglob('*.tex')):
    rf=r/f.relative_to(b)
    if rf.is_file():diff.extend(difflib.unified_diff(f.read_text().splitlines(True),rf.read_text().splitlines(True),fromfile='baseline/'+str(f.relative_to(b)),tofile='revised/'+str(f.relative_to(b))))
(o/'source_changes.patch').write_text(''.join(diff))
(o/'source_preservation.json').write_text(json.dumps(audit,indent=2)+'\n')
env={'python':platform.python_version(),'platform':platform.platform(),'packages':{},'tools':{x:shutil.which(x) for x in ['pdflatex','lean','lake']}}
for mod in ['numpy','scipy','mpmath','sympy','matplotlib','pandas','pypdfium2','PyMuPDF']:
 try:env['packages'][mod]=importlib.metadata.version(mod)
 except importlib.metadata.PackageNotFoundError:env['packages'][mod]=None
(o/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
print(json.dumps(audit,indent=2))
assert audit['baseline_environment_counts']==audit['current_environment_counts']
assert not audit['missing_source_labels']
assert not audit['engine']['changed_or_missing'] and not audit['lean']['changed_or_missing']
