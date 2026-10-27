"""Reproduce existing scientific checks, with graphics rendering omitted.
No new mathematical assertions or substitute pytest implementation are added.
"""
from __future__ import annotations
import contextlib, hashlib, io, json, os, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'release_package/Komorebi_Paper_II_Release_2026-10-15'
OUTPUT = (ROOT / sys.argv[1]).resolve()
assert OUTPUT.is_dir(), 'bounded runner must create fresh output directory'
CANONICAL = RELEASE / 'source/canonical_v1.2.1'
VISUAL = RELEASE / 'editable/visual_guide'
TRAD = RELEASE / 'editable/traditional'
START = time.monotonic()
RUNS = []

def write(name, obj):
    (OUTPUT/name).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def run(name, argv, cwd, env):
    start = time.monotonic()
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=90)
    (OUTPUT/(name+'.stdout.txt')).write_text(p.stdout)
    (OUTPUT/(name+'.stderr.txt')).write_text(p.stderr)
    RUNS.append({'name':name,'argv':argv,'cwd':str(cwd),'returncode':p.returncode,
                 'elapsed_seconds':time.monotonic()-start})
    if p.returncode:
        raise RuntimeError(name+' failed: '+p.stderr[-2000:]+p.stdout[-2000:])
    return p.stdout

# Import the current canonical implementation directly; no source edits or writes.
sys.path.insert(0, str(CANONICAL/'code/python'))
from seed_refinement.experiments import run_experiments, write_numerical_summary, numerical_summary_rows
from seed_refinement.release_validation import compare_generated_records, assert_records_close

canonical_output = OUTPUT/'canonical'
results = run_experiments(canonical_output/'results/numerical_results.json')
write_numerical_summary(results, canonical_output/'results/numerical_summary.csv')
compare_generated_records(canonical_output, CANONICAL)
canonical = {'status':'PASS','summary_rows':len(numerical_summary_rows(results)),
             'method':'Existing run_experiments + write_numerical_summary + compare_generated_records; same data path used by run_all.py, excluding make_visuals.',
             'record_comparison':'Full record and all nine CSV rows; nonintegral reals rtol=1e-12, atol=1e-14; exact counts, strings, Boolean flags.',
             'pytest':'Not rerun: pytest unavailable. Historical 48-case result is not represented as fresh.'}
write('canonical_comparison.json',canonical)

env = os.environ.copy()
env['PYTHONDONTWRITEBYTECODE']='1'
env['MPLBACKEND']='Agg'
ignore = shutil.ignore_patterns('__pycache__','.pytest_cache','*.pyc')
with tempfile.TemporaryDirectory(prefix='temporary_inputs_', dir=OUTPUT) as td:
    temp=Path(td)
    visual=temp/'visual_guide'
    for name in ('source','checks'):
        shutil.copytree(VISUAL/name, visual/name, ignore=ignore)
    stdout=run('visual_exact',[sys.executable,'checks/verify_examples.py'],visual,env)
    exact=json.loads((visual/'checks/EXACT_CHECKS.json').read_text())
    saved=json.loads((VISUAL/'checks/EXACT_CHECKS.json').read_text())
    exact_normalized={k:v for k,v in exact.items() if k!='timestamp_utc'}
    saved_normalized={k:v for k,v in saved.items() if k!='timestamp_utc'}
    if exact_normalized != saved_normalized:
        raise AssertionError('Exact example record differs beyond timestamp')
    write('EXACT_CHECKS.json',exact)
    run('atlas_sources',[sys.executable,'source/generate_graphics.py'],visual,env)
    atlas=[]
    for f in sorted((visual/'graphics').glob('*.tex')):
        data=f.read_bytes()
        atlas.append({'name':f.name,'generated_sha256':hashlib.sha256(data).hexdigest(),
                      'visual_match':data==(VISUAL/'graphics'/f.name).read_bytes(),
                      'traditional_match':data==(TRAD/'visual_graphics'/f.name).read_bytes()})
    if len(atlas)!=22 or not all(x['visual_match'] and x['traditional_match'] for x in atlas):
        raise AssertionError('Atlas source-byte comparison failed')
    write('atlas_comparison.json',{'status':'PASS','count':len(atlas),'plates':atlas})

    # Execute unmodified generator/data functions, replacing only the shared
    # final serialization hook. Every data assertion still runs; no PDF/PNG claim.
    figures=temp/'traditional'
    shutil.copytree(TRAD/'figure_sources',figures/'figure_sources',ignore=ignore)
    shutil.copytree(TRAD/'fonts',figures/'fonts',ignore=ignore)
    (figures/'mplconfig').mkdir()
    figure_env=env.copy();figure_env['MPLCONFIGDIR']=str(figures/'mplconfig')
    script="""import json,sys
from pathlib import Path
sys.path.insert(0,'figure_sources')
import common
stems=[]
def data_only_save(fig,stem):
    stems.append(stem)
    common.plt.close(fig)
common.save=data_only_save
import draw_matrix_visuals,draw_graph_visuals
matrix=draw_matrix_visuals.generate()
graph=draw_graph_visuals.generate()
Path(sys.argv[1]).write_text(json.dumps({'stems':stems,'matrix':matrix,'graph':graph},indent=2)+'\\n')
print('PASS: data/assertion paths for',len(stems),'figures; PDF/PNG serialization suppressed')
"""
    (OUTPUT/'figure_data_command.py').write_text(script)
    # This exact helper is created from the above literal, pinned by wrapper hash.
    run('figure_data',[sys.executable,str(OUTPUT/'figure_data_command.py'),str(OUTPUT/'figure_data.json')],figures,figure_env)
    figure=json.loads((OUTPUT/'figure_data.json').read_text())
    assert len(figure['stems'])==13 and len(set(figure['stems']))==13
    assert_records_close(figure['matrix'],json.loads((TRAD/'figure_sources/matrix_visual_data.json').read_text()))
    assert_records_close(figure['graph'],json.loads((TRAD/'figure_sources/graph_visuals_validation.json').read_text()))

# Original expanded verifier includes nine finite mathematical groups and one
# check of its OWN archived annals source; the latter is not current-publication QA.
expanded_stdout=run('expanded_examples',[sys.executable,str(RELEASE/'source/annals_expanded/verification/verify_revised_results.py')],RELEASE,env)
expanded_groups=[line.removeprefix('PASS ') for line in expanded_stdout.splitlines() if line.startswith('PASS ')]
assert len(expanded_groups)==10
summary={'status':'PASS','finished_at_utc':datetime.now(timezone.utc).isoformat(),
         'runtime_seconds':time.monotonic()-START,'canonical':canonical,
         'visual_exact_count':exact['check_count'],'exact_saved_record_matches_except_timestamp':True,
         'atlas_source_count':len(atlas),'all_atlas_bytes_match_both_current_copies':True,
         'main_figure_data_paths':len(figure['stems']),'main_figure_data_match_current_saved_records':True,
         'main_image_generation':'Omitted; no PDF/PNG regeneration or byte-equality claim.',
         'expanded_groups':expanded_groups,'expanded_scope':'9 finite mathematical groups; historical annals source-integrity group separately identified.',
         'runs':RUNS,'non_claims':['No universal theorem inferred from finite checks.','No fresh 48-case pytest run.','No Lean replay performed by this computation run.','No current-publication source QA inferred from archived annals source-integrity check.','Floating residuals remain tolerance-dependent.']}
write('RESULT.json',summary)
print('PASS: 9 canonical summary rows; 118 exact checks; 13 figure data paths; 22 atlas source matches; 9 expanded mathematical groups plus historical source-integrity check.')
