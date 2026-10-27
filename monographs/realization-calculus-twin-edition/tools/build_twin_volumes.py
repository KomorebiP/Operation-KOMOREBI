#!/usr/bin/env python3
"""Build the paired monographs. This publication command does not run Lean."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
VOLUMES={
 'I':('publication/volume_i/source','Komorebi_Space_Monograph.tex','Realization_Calculus_Volume_I_Komorebi_Space.pdf'),
 'II':('publication/volume_ii/manuscript','monograph.tex','Realization_Calculus_Volume_II_Realization_Boundaries.pdf')}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--volume',choices=['I','II','all'],default='all');args=parser.parse_args()
 if not shutil.which('latexmk'):parser.error('Install latexmk and TeX Live with the packages imported by the source preambles.')
 for volume,(source_dir,source_name,output_name) in VOLUMES.items():
  if args.volume not in ('all',volume):continue
  build=ROOT/'build'/('volume_'+volume.lower());build.mkdir(parents=True,exist_ok=True)
  command=['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir='+str(build),source_name]
  with (build/'console.log').open('wb') as log:run=subprocess.run(command,cwd=ROOT/source_dir,stdout=log,stderr=subprocess.STDOUT)
  if run.returncode:raise SystemExit(f'Volume {volume}: TeX failed, see {build / "console.log"}')
  log=(build/(Path(source_name).stem+'.log')).read_text(errors='replace')
  warnings=[line for line in log.splitlines() if re.search(r'Overfull|undefined|multiply defined|Missing character|Rerun to get',line)]
  pdf=build/(Path(source_name).stem+'.pdf');destination=ROOT/'books'/output_name
  shutil.copy2(pdf,destination)
  receipt={'volume':volume,'exit_code':run.returncode,'pdf':str(destination.relative_to(ROOT)),
   'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'layout_or_reference_warnings':warnings,
   'scope':'LaTeX publication build. No Lean commands were run.'}
  (build/'build_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print(f'Volume {volume}: {len(warnings)} layout/reference warnings',flush=True)
  if warnings:raise SystemExit('Resolve the recorded warnings before release.')
if __name__=='__main__':main()
