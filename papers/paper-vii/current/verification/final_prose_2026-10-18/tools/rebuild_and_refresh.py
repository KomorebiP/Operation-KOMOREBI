#!/usr/bin/env python3
"""Authoring pipeline: rebuild PDFs and navigation; renew metadata and reviews afterward."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, shutil, subprocess, sys, time
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'verification/final_prose_2026-10-18/build'
OUT.mkdir(parents=True, exist_ok=True)
records = []

def run(name, args):
    started = time.time()
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    path = OUT / (name + '.log')
    path.write_text(result.stdout)
    record = {'name': name, 'arguments': args, 'returncode': result.returncode,
              'seconds': round(time.time()-started, 2), 'log': str(path.relative_to(ROOT))}
    if result.returncode:
        print(result.stdout[-2500:], flush=True)
        raise RuntimeError(name + ' failed')
    print(name + ': PASS', flush=True)
    return record

records.append(run('traditional', ['editable/traditional/build.py']))
records.append(run('traditional_page_map', ['editable/traditional/map_pages.py']))
crosswalk = ['editable/visual_guide/make_crosswalk.py', '--traditional-map',
             'editable/traditional/canonical_label_to_final.json']
records.append(run('visual_source_locators', crosswalk + ['--refresh-source-locators']))
records.append(run('lean_navigation', ['editable/lean_guide/navigation.py']))
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = [pool.submit(run, role, [f'editable/{role}/build.py'])
               for role in ['visual_guide', 'lean_guide']]
    records.extend(f.result() for f in futures)
records.append(run('visual_final_crosswalk', crosswalk))
specs = [('traditional','Traditional'), ('visual_guide','Visual_Guide'), ('lean_guide','Lean_Guide')]
documents = []
for role, stem in specs:
    name = f'Paper_VII_{stem}_Final.pdf'
    source = ROOT / 'editable' / role / name
    for directory in ['papers', 'publication/pdfs']:
        shutil.copy2(source, ROOT / directory / name)
    with fitz.open(source) as pdf:
        pages = len(pdf)
    documents.append({'role': role, 'title': {'traditional':'Traditional monograph',
                      'visual_guide':'Visual guide','lean_guide':'Lean and evidence guide'}[role],
                      'path': 'papers/' + name, 'source_entry_point':
                      f'editable/{role}/' + name.replace('.pdf','.tex'),
                      'pages': pages, 'bytes': source.stat().st_size,
                      'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
report = {'status':'PASS','engine':'xelatex','pdf_driver':'xdvipdfmx',
          'driver_policy':'Four TeX passes without PDF emission, then one final driver call.',
          'records': records, 'documents': documents,
          'scope':'Fresh PDF builds, source locator refresh, and synchronization of all nine current PDF copies. No Lean compilation.'}
(OUT / 'BUILD_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','pages':{r['role']:r['pages'] for r in documents}}),flush=True)
