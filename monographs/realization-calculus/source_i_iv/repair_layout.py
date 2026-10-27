from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent
results=ROOT/'build_results.json';shutil.copy2(results,ROOT/'initial_build_results.json')
for p in ROOT.glob('**/core-layout.tex'):
 with p.open('a') as f:f.write('\n\\BeforeBeginEnvironment{tabularx}{\\noindent}\n')
for kind in ['lean_guide','machine']:
 p=next((ROOT/'I/editable'/kind).glob('Paper_I*Final.tex'));s=p.read_text().replace('\\endgroup\\clearpage\\pagenumbering{roman}\\hypersetup','\\endgroup\\clearpage\\pagenumbering{arabic}\\hypersetup');p.write_text(s)
fonts=r'''% Installed external fonts; change paths here for another system.
\providecommand{\CoreURWFonts}{/usr/share/fonts/opentype/urw-base35/}
\providecommand{\CoreLMFonts}{/usr/share/texmf/fonts/opentype/public/lm/}
\providecommand{\CoreMathFonts}{/usr/share/texmf/fonts/opentype/public/lm-math/}
'''
for role in ['traditional','lean_guide']:
 d=ROOT/'IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable'/role
 (d/'font-locations.tex').write_text(fonts)
 for name in ['komorebi-monograph.sty','preamble.tex']:
  p=d/name
  if not p.exists():continue
  b=ROOT/'before'/p.relative_to(ROOT);b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():b.write_bytes(p.read_bytes())
  s=p.read_text();out=[]
  for ln in s.splitlines(True):
   if 'Path=fonts/' in ln:
    key='CoreMathFonts' if 'math' in ln else 'CoreLMFonts' if 'mono' in ln else 'CoreURWFonts'
    ln=ln.replace('Path=fonts/','Path=\\'+key)
   out.append(ln)
  s=''.join(out)
  loc='\\RequirePackage{fontspec,unicode-math,setspace,tocloft}' if name.endswith('.sty') else '\\usepackage{fontspec}'
  s=s.replace(loc,loc+'\n\\input{font-locations.tex}')
  p.write_text(s)
# Reusable build module from the first authoring script without its prepare loop.
s=(ROOT/'prepare_and_build.py').read_text();portion=s[s.index('def build(e):'):s.index('with concurrent.futures.ThreadPoolExecutor')]
header='from pathlib import Path\nimport json,hashlib,subprocess,os,re,concurrent.futures\nROOT=Path(__file__).resolve().parent\n'
runner=header+portion+'''\nif __name__=='__main__':
 import sys
 entries=json.loads((ROOT/'selected_sources.json').read_text())
 if len(sys.argv)>1:entries=[e for e in entries if e['paper']+':'+e['role'] in sys.argv[1:]]
 # Resolve retained metadata paths against this package for portability.
 for e in entries:
  p=Path(e['source']);suffix=p.parts[p.parts.index('source_i_iv')+1:];e['source']=str(ROOT.joinpath(*suffix))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(build,entries))
 prior=json.loads((ROOT/'build_results.json').read_text())
 keys={(e['paper'],e['role']) for e in out};out+=[e for e in prior if (e['paper'],e['role']) not in keys]
 (ROOT/'build_results.json').write_text(json.dumps(out,indent=2))
'''
(ROOT/'build_components.py').write_text(runner)
