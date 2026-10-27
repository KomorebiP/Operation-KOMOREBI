#!/usr/bin/env python3
"""Build both 1.1 reading editions from the preserved proofs and visual pages."""
from pathlib import Path
import hashlib,json,re,subprocess
from build_manuscript import format_tex
ROOT=Path(__file__).resolve().parent
CHAPTERS=[
 ('research_v11/coupled_growth_proof.md','coupled_growth_full'),
 ('research_v11/coupled_identifiability.md','coupled_inverse_full'),
 ('research_v11/coupled_structure.md','coupled_structure_full'),
 ('research_v11/resolution_atlas.md','resolution_full'),
 ('evidence/v11/coupled_lab_notes.md','coupled_lab_full'),
]
def converted(source,key):
    text=source.read_text()
    # Provenance remains in the exact source files and release evidence.
    text='\n\n'.join(p for p in text.split('\n\n') if not p.startswith('Checkpoint'))
    if key=='resolution_full':
        # The six figures already appear at full size in the visual chapter.
        text=re.sub(r'!\[[^\n]*\]\(figures_v11/[^\n]+\)',
                    '*The corresponding figure appears in the resolution visual chapter.*',text)
    if key=='coupled_lab_full':
        text=text.split('## Six visual plates')[0]
        text=text.replace('# Coupled laboratory integration note',
                          '# Exact laboratory and certified evaluation',1)
    result=subprocess.run(['pandoc','-f','markdown+tex_math_single_backslash','-t','latex','--no-highlight'],
                          input=text,capture_output=True,text=True,check=True)
    tex=format_tex(result.stdout,key)
    tex=re.sub(r'(\\(?:sub){0,2}section\{)\d+(?:\.\d+)*\.?(?:\s+)',r'\1',tex)
    # Separate independently converted appendix destinations.
    tex=re.sub(r'\\(hypertarget|label)\{([^}]+)\}',
               lambda m:'\\'+m.group(1)+'{v11-'+key+'-'+m.group(2)+'}',tex)
    if key=='coupled_growth_full':
        tex=tex.replace('Section 2 shows',
            r'Section~\ref{v11-coupled_growth_full-the-characteristic-exponent-and-its-positive-vector} shows')
    return tex

def main():
    record={'checkpoint':'SF-DISCOVERY-110','chapters':[],'builds':[]}
    for name,key in CHAPTERS:
        src=ROOT/name;out=ROOT/'sections_v11'/(key+'.tex')
        out.write_text(converted(src,key))
        record['chapters'].append({'source':name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
                                  'tex':str(out.relative_to(ROOT)),'tex_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
    for name in ['main','visual_guide']:
        for index in [1,2,3]:
            proc=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,
                                capture_output=True,text=True)
            (ROOT/'evidence/v11'/f'{name}-latex-{index}.txt').write_text(proc.stdout+proc.stderr)
            if proc.returncode:
                print(proc.stdout[-6000:]);proc.check_returncode()
        warnings=[line for line in (ROOT/(name+'.log')).read_text().splitlines()
                  if 'Overfull' in line or 'Warning:' in line]
        record['builds'].append({'name':name,'sha256':hashlib.sha256((ROOT/(name+'.pdf')).read_bytes()).hexdigest(),
                                'warnings':warnings})
    (ROOT/'evidence/v11/manuscript_build.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record['builds']))
if __name__=='__main__':main()
