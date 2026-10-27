#!/usr/bin/env python3
"""Build the editable Paper XI manuscript with XeLaTeX and BibTeX.

Usage: python build.py --output-dir /path/to/pdf-output
The source and appendices are already prepared and require no Pandoc at build time.
"""
from pathlib import Path
import argparse, os, shutil, subprocess, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--keep-build', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    build = output / '_build_traditional'
    build.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['SOURCE_DATE_EPOCH'] = '1791244800'
    env['FORCE_SOURCE_DATE'] = '1'
    env['BIBINPUTS'] = str(root) + os.pathsep + env.get('BIBINPUTS','')
    for executable in ('xelatex','bibtex'):
        if not shutil.which(executable):
            raise SystemExit(f'Required executable missing: {executable}')
    name = 'Paper_XI_Traditional_Final'
    commands = [
        ['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}',name+'.tex'],
        ['bibtex',name],
        ['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}',name+'.tex'],
        ['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}',name+'.tex'],
    ]
    for i,cmd in enumerate(commands,1):
        result = subprocess.run(cmd,cwd=build if cmd[0]=='bibtex' else root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (build/f'pass_{i}.txt').write_text(result.stdout)
        if result.returncode:
            sys.stderr.write(result.stdout[-6000:])
            raise SystemExit(f'Build failed at pass {i}; complete output: {build/f"pass_{i}.txt"}')
    target = output/(name+'.pdf')
    shutil.copy2(build/(name+'.pdf'),target)
    shutil.copy2(build/(name+'.log'),output/(name+'.log'))
    print(target)
    if not args.keep_build:
        shutil.rmtree(build)

if __name__ == '__main__':
    main()
