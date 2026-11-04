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
    'paper-ix':'sources/visual.tex',
    'paper-x':'visual_appendix/appendix.tex',
    'paper-xi':'publication/source/visual_guide/Paper_XI_Visual_Guide_Final.tex',
    'paper-xii':'core/publication/source/visual_guide/source/pages.tex',
}


def audit(root,git='git'):
    from readable_chapters import BOOKS
    from visual_guide_provenance import check as check_provenance
    provenance=check_provenance(root)
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
        children={'paper-viii':['editable/visual_guide/source/extended_pages.tex'],
            'paper-ix':['sources/visual_body.tex','sources/worked_atlas.tex','sources/generated/worked_newton_values.tex'],
            'paper-x':['visual_appendix/source/pages.tex'],
            'paper-xi':['publication/source/visual_guide/reader_route.tex']}.get(work,[])
        if children:
            for child in children:
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
        if work=='paper-ix':
            # AtlasHead is a section in the standalone guide and a subsection
            # only when the same input is included in the main manuscript.
            body=subprocess.check_output([git,'show',revision+':'+component['destination']+'/sources/visual_body.tex'],cwd=root).decode('utf-8-sig')
            worked=subprocess.check_output([git,'show',revision+':'+component['destination']+'/sources/worked_atlas.tex'],cwd=root).decode('utf-8-sig')
            count=len(re.findall(r'\\section\{',body))+len(re.findall(r'\\AtlasHead\{',worked))
        resource=next((r for r in component['resources'] if r['kind']=='visual'),None)
        integrated=resource is None
        resource=resource or next(r for r in component['resources'] if r['kind']=='pdf')
        pdf_path=component['destination']+'/'+resource['path']
        rows.append(dict(work=work,source=path,source_sha256=expected['sha256'],inputs=inputs,
            source_units=count,source_unit_kind=unit,
            visual_pdf=pdf_path,visual_pdf_sha256=retained[resource['path']]['sha256'],
            integrated_pdf=integrated,html_atlas=BOOKS[work].get('atlas_index'),
            remaining='Complete HTML visual guide available' if BOOKS[work].get('atlas_index') else
                'Port the visual companion, its figures, source text and manuscript links'))
        if work=='paper-x':
            rows[-1]['opening_scope']=dict(sections=2,drawings=1,
                handling='The HTML contents retain both opening scope sections and the separate-output diagram, before the 30 numbered plates')
        if work=='paper-xi':
            rows[-1]['opening_scope']=dict(orientation=True,reader_route_sections=2,handling='The contents page preserves the opening orientation, both reader-route sections, theorem-number corrections and evidence scope')
        if work=='paper-xii':
            rows[-1]['drawing_inventory']=dict(separate_drawings_used=21,inline_drawings=2,total_drawings=23,retained_unused=['support_rotated'])
        if work=='paper-ix':
            readme='sources/visual_README.md'
            readme_raw=subprocess.check_output([git,'show',revision+':'+component['destination']+'/'+readme],cwd=root)
            assert hashlib.sha256(readme_raw).hexdigest()==retained[readme]['sha256']
            rows[-1]['inherited_readme_inventory']=dict(source=component['destination']+'/'+readme,
                source_sha256=retained[readme]['sha256'],sections=15,figures=12,current=False,
                handling='Preserved unchanged; actual entrypoint and retained 25-page PDF have 23 sections and 20 figures')
        if work=='paper-viii':
            current=provenance['works'][work]
            crosswalk_path=current['source']['path']
            crosswalk_raw=(root/crosswalk_path).read_bytes()
            crosswalk_sha=hashlib.sha256(crosswalk_raw).hexdigest()
            if crosswalk_sha!=current['source']['sha256']:raise ValueError('Changed visual crosswalk')
            declared=json.loads(crosswalk_raw)['visual_pdf_sha256']
            rows[-1]['reference_crosswalk']=dict(source=crosswalk_path,source_sha256=crosswalk_sha,
                declared_visual_pdf_sha256=declared,retained_visual_pdf_sha256=retained[resource['path']]['sha256'],
                pdf_checksum_current=declared==retained[resource['path']]['sha256'],
                supersedes=current['original_crosswalk'],
                handling='Resolved by a new checksum-bound crosswalk revision; original crosswalk preserved. All 32 PDF pages and stable manuscript targets rechecked.')
        if work=='paper-iv':
            current=provenance['works'][work]
            rows[-1]['current_visual_edition']=dict(status=current['status'],source=current['source'],
                pdf=current['pdf'],build_record=current['build_record'],original_pdf=current['original_pdf'],
                handling='Resolved by the labeled reconstructed edition: all 27 content pages match; cover identifies the reconstruction; all 28 pages visually reviewed.')
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
