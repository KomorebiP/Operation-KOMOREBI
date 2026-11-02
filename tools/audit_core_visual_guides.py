"""Inventory exact visual sources and current HTML routes; no proof assessment.

Run with --output PATH to save a dated record. Imported source bytes are read
from the committed tree and checked against their own source receipts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCES = {
    'paper-i':'editable/traditional/visual_atlas.tex',
    'paper-ii':'editable/traditional/visual_atlas.tex',
    'paper-iii':'manuscript/visual_atlas.tex',
    'paper-iv':'Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/atlas-pages.tex',
    'paper-v':'editable/traditional/atlas-pages.tex',
    'paper-vi':'editable/traditional/atlas-pages.tex',
    'paper-vii':'editable/traditional/monograph_atlas.tex',
    'paper-viii':'editable/visual_guide/source/pages.tex',
    'paper-ix':'sources/visual_body.tex',
    'paper-x':'visual_appendix/source/pages.tex',
    'paper-xi':'publication/source/visual_guide/Paper_XI_Visual_Guide_Final.tex',
    'paper-xii':'core/publication/source/visual_guide/source/pages.tex',
}


def audit(root,git='git'):
    from readable_chapters import BOOKS
    revision=subprocess.check_output([git,'rev-parse','HEAD'],cwd=root,text=True).strip()
    components=json.loads((root/'manifests/browse-resources.json').read_bytes())['components']
    rows=[]
    for component in components:
        work=component['id']
        if work not in SOURCES:continue
        receipt=json.loads((root/('manifests/source-imports/'+work+'.json')).read_bytes())
        retained={f['path']:f for f in receipt['files']}
        path=component['destination']+'/'+SOURCES[work]
        expected=retained[SOURCES[work]]
        raw=subprocess.check_output([git,'show',revision+':'+path],cwd=root)
        if len(raw)!=expected['size'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:
            raise ValueError('Visual source does not match its receipt: '+path)
        text=raw.decode('utf-8-sig')
        inputs=[]
        if work=='paper-viii':
            for name in ('extended_pages.tex',):
                child='editable/visual_guide/source/'+name
                child_path=component['destination']+'/'+child
                child_raw=subprocess.check_output([git,'show',revision+':'+child_path],cwd=root)
                digest=hashlib.sha256(child_raw).hexdigest()
                if digest!=retained[child]['sha256']:
                    raise ValueError('Atlas input differs from its receipt: '+child_path)
                inputs.append(dict(source=child_path,source_sha256=digest))
                text+='\n'+child_raw.decode('utf-8-sig')
        numbers=re.findall(r'\\vpage\{(\d+)\}',text)
        if numbers and numbers!=[str(n) for n in range(1,len(numbers)+1)]:
            raise ValueError('Review visual source numbering: '+path)
        unit='numbered plates' if numbers else 'lessons' if work=='paper-xi' else 'sections'
        count=len(numbers) if numbers else len(re.findall(r'\\lesson\{',text)) if work=='paper-xi' else len(re.findall(r'\\section\{',text))
        resource=next((r for r in component['resources'] if r['kind']=='visual'),None)
        integrated=resource is None
        resource=resource or next(r for r in component['resources'] if r['kind']=='pdf')
        pdf_path=component['destination']+'/'+resource['path']
        rows.append(dict(work=work,source=path,source_sha256=expected['sha256'],inputs=inputs,
            source_units=count,source_unit_kind=unit,
            visual_pdf=pdf_path,visual_pdf_sha256=retained[resource['path']]['sha256'],
            integrated_pdf=integrated,html_atlas=BOOKS[work].get('atlas_index'),
            remaining='Complete HTML atlas available' if BOOKS[work].get('atlas_index') else
                'Port the visual companion, its figures, source text and manuscript links'))
        if work=='paper-viii':
            crosswalk='editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json'
            crosswalk_path=component['destination']+'/'+crosswalk
            crosswalk_raw=subprocess.check_output([git,'show',revision+':'+crosswalk_path],cwd=root)
            crosswalk_sha=hashlib.sha256(crosswalk_raw).hexdigest()
            if crosswalk_sha!=retained[crosswalk]['sha256']:raise ValueError('Changed visual crosswalk')
            declared=json.loads(crosswalk_raw)['visual_pdf_sha256']
            rows[-1]['reference_crosswalk']=dict(source=crosswalk_path,source_sha256=crosswalk_sha,
                declared_visual_pdf_sha256=declared,retained_visual_pdf_sha256=retained[resource['path']]['sha256'],
                pdf_checksum_current=declared==retained[resource['path']]['sha256'],
                handling='Original crosswalk preserved; PDF plate titles, locators and page labels independently checked, and stable manuscript targets rederived by the HTML converter')
    return dict(source_revision=revision,reading_configuration='working tree',
        scope='Visual reading coverage only; no mathematical audit, example execution or Lean replay.',
        core_papers=len(rows),complete_html_atlases=sum(bool(r['html_atlas']) for r in rows),guides=rows)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--git',default='git')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=json.dumps(audit(args.root,args.git),indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(report,encoding='utf-8',newline='\n')
    else:print(report,end='')
