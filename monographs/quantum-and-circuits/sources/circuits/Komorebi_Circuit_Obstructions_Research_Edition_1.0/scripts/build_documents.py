"""Build the three publication PDFs. This does not compile Lean proofs."""
from pathlib import Path
import subprocess, shutil, json, time

ROOT=Path(__file__).resolve().parents[1]
DOCS=[('main','Komorebi_Circuit_Obstructions_Main_Paper.pdf'),
      ('visual','Komorebi_Circuit_Obstructions_Visual_Guide.pdf'),
      ('lean','Komorebi_Circuit_Obstructions_Lean_Guide.pdf')]

def main():
    (ROOT/'output').mkdir(exist_ok=True)
    results=[]
    for name,filename in DOCS:
        work=ROOT/'build'/name
        work.mkdir(parents=True,exist_ok=True)
        t=time.monotonic()
        passes=[]
        for i in range(3):
            cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error',
                 '-output-directory='+str(work),name+'.tex']
            p=subprocess.run(cmd,cwd=ROOT/'manuscripts',capture_output=True)
            (work/f'console_pass{i+1}.log').write_bytes(p.stdout+p.stderr)
            passes.append(p.returncode)
            if p.returncode:
                raise RuntimeError(f'{name}: pass {i+1} failed; see {work}')
        shutil.copy2(work/(name+'.pdf'),ROOT/'output'/filename)
        results.append({'document':name,'filename':filename,'passes':passes,
                        'seconds':time.monotonic()-t})
    (ROOT/'reviews/document_build.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
