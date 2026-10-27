#!/usr/bin/env python3
"""Rebuild the reading volume; optionally recompile all available LaTeX sources.

No Lean project, finite mathematical computation or figure generator is run.
Five supporting PDFs retain their original layouts. Display branding is adapted
after copying; all exact frozen inputs remain separately available.
"""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--from-sources',action='store_true',help='Recompile the 36 source-based components first.')
a=ap.parse_args()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def run(path,*args):subprocess.run([sys.executable,'-B',str(ROOT/path),*map(str,args)],cwd=ROOT,env=env,check=True)
if a.from_sources:
    run(Path('source_i_iv/rebuild_all.py'))
    run(Path('source_v_viii/build_all.py'))
    run(Path('source_ix_xii/typeset_ix_x.py'))
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    rebuilt=ROOT/'source_ix_xii'/('rebuild_'+stamp)
    run(Path('source_ix_xii/rebuild_xi_xii.py'),'--output',rebuilt)
    record=json.loads((ROOT/'component_builds.json').read_text())
    for comp in record['components']:
        if comp['paper'] in ('XI','XII') and comp['build_kind']=='source_retypeset':
            path=rebuilt/comp['paper']/comp['baseline_filename']
            if not path.is_file():raise FileNotFoundError(path)
            comp['output_pdf']=str(path.relative_to(ROOT))
    (ROOT/'component_builds.json').write_text(json.dumps(record,indent=2)+'\n')
run(Path('prepare_book.py'))
run(Path('assemble_monograph.py'))
run(Path('audit_monograph.py'),'--render-samples')
if not a.from_sources:
    run(Path('audit_rebranding.py'))
run(Path('make_preview.py'))
