"""Create an identified proofreading revision while retaining the original cache."""
from pathlib import Path
import collections,copy,gzip,hashlib,html,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/publication/mnr-html-reading/2026-11-04'
WORK=ROOT/'output/mnr-html-work'
sys.path.insert(0,str(ROOT/'site/tools'))
from reading_payload import decode,PREFIX
from check_reader_site import Page
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def main():
    base_raw=(OUT/'READING.json').read_bytes();base=json.loads(base_raw)
    meta=json.loads((WORK/'reading-metadata.json').read_bytes())
    original={p['file']:p for p in base['pages']};images={f['file']:f for f in base['images']}
    assert [p['file'] for p in meta['pages']]==[p['file'] for p in base['pages']]
    corrections={
      'chapter-62.html':('in the 64-case case.','in the 64-case example.'),
      'chapter-88.html':('visible at at least two nodes','visible at least two nodes'),
      'large-signal-model-visual-atlas.html':('Plates 10–16 develop behavior spaces, positivity, curved geometry and statistical guarantees. Plate 17 locates the formal proofs.','Plates 10–13 develop behavior spaces, positivity, curved geometry and probability integration. Formal routes accompany the plates.'),
    }
    buffers=[bytearray()];pages=[];changed=[];maths=0;code_added=0
    for p in meta['pages']:
        body=(WORK/'pages'/p['file']).read_text(encoding='utf-8')
        def size(m):
            tag=m[0];name=re.search(r'mnr-figure/([^" ]+)',tag)[1];f=images[name]
            return tag.replace('<img ','<img loading="lazy" decoding="async" style="max-width:'+str(min(760,f.get('display_width',760)))+'px" ',1)
        body=re.sub(r'<img\b[^>]*>',size,body)
        def caption(m):
            block=m[0];image=re.search(r'mnr-figure/(figure-\d+\.webp)',block)
            if image:
                number=images[image[1]].get('number','')
                if number:block=block.replace('<figcaption>','<figcaption><strong>Figure '+html.escape(number)+'.</strong> ',1)
            return block
        body=re.sub(r'<figure\b.*?</figure>',caption,body,flags=re.S)
        if p['file'] in corrections:
            before,after=corrections[p['file']];assert body.count(before)==1
            body=body.replace(before,after,1)
        chapter_labels={'chapter-60.html':1,'chapter-63.html':2,'chapter-66.html':2}
        if p['file'] in chapter_labels:
            body,count=re.subn(r'\bPart(\s*<a href="chapter-\d{2}\.html#SII:part:[^"]+">)',r'Chapter\1',body)
            assert count==chapter_labels[p['file']],('Unexpected chapter-reference label count',p['file'],count)
        previous=original[p['file']];spec=dict(previous['payload']);spec['path']=PREFIX+spec.pop('part');spec['figure_root']='mnr-figure/'
        old=decode(spec,ROOT/'site')
        pattern=r'<span\b[^>]*class="[^"]*arithmatex[^"]*"[^>]*>.*?</span>'
        oldmath=re.findall(pattern,old,re.S);newmath=re.findall(pattern,body,re.S)
        assert oldmath==newmath,('Mathematical display changed',p['file']);maths+=len(newmath)
        a,b=Page(old),Page(body);assert a.ids==b.ids,('Reading anchors changed',p['file']);assert a.links==b.links,('Reference destinations changed',p['file'])
        code_added+=body.count('<code')-old.count('<code')
        if body!=old:changed.append(p['file'])
        raw=body.encode();compressed=gzip.compress(raw,compresslevel=9,mtime=0)
        if len(buffers[-1])+len(compressed)>512*1024:buffers.append(bytearray())
        number=len(buffers)+9;offset=len(buffers[-1]);buffers[-1].extend(compressed)
        preview=next((q for q in re.findall(r'<p>.*?</p>',body,re.S) if len(re.sub('<[^>]+>','',q))>35),'<p>'+html.escape(p['title'])+'</p>')
        pages.append(dict(**p,payload=dict(part=f'parts/{number:03}.bin',offset=offset,bytes=len(compressed),html_sha256=sha(raw),html_bytes=len(raw)),preview=preview,source=previous['source'],line=previous['line']))
    parts=[]
    for i,buffer in enumerate(buffers,10):
        path=f'parts/{i:03}.bin';target=OUT/path
        if target.exists() and target.read_bytes()!=buffer:raise ValueError('Refuse to replace a retained reading part: '+path)
        target.write_bytes(buffer);parts.append(dict(path=path,bytes=len(buffer),sha256=sha(buffer)))
    bypart={p['path']:p for p in parts}
    for p in pages:p['payload']['part_sha256']=bypart[p['payload']['part']]['sha256']
    result={k:v for k,v in meta.items() if k not in ('pages','aliases')}
    result.update(pages=pages,payload_parts=parts,images=base['images'],sources=base['sources'],prefix=base['prefix'],converter=base['converter'],mathjax_validation=base['mathjax_validation'])
    result['reading_edition']=dict(id='mnr-html-proofread-2026-11-04',kind='copyedited-web-edition',base_manifest=PREFIX+'READING.json',base_manifest_sha256=sha(base_raw),review=PREFIX+'proofread/FINAL_REVIEW.json')
    (OUT/'FINAL_READING.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    review=dict(scope='Manual proofreading of welcome/reader copy, all reading-page titles, chapter openings, all 126 figure captions, and flagged prose in context; automated transcription and structure checks across all 121 reading pages. This is not a line-by-line manual review of every paragraph.',
      routine_edits=['Restored literal filenames, module names and declaration names omitted by the original LaTeX path-command conversion.',
                     'Chapter 62: "64-case case" changed to "64-case example".',
                     'Chapter 88: "visible at at least" corrected to "visible at least".',
                     'The visual-atlas section menu now uses its actual heading level, exposing all 13 plates.',
                     'The visual-atlas reading route now describes the 13 plates present in this edition instead of referring to absent plates 14–17.',
                     'Five cross-references in Chapters 60, 63 and 66 now call the referenced chapters "Chapter" instead of retaining the component manuscript\'s "Part" label. Their reference destinations are unchanged.'],
      mathematical_token_changes=[],unresolved_editorial_issues=[],
      retained_wording=['Chapter 84: "that that gate" is a grammatical conjunction followed by a demonstrative.'],
      validation=dict(reading_pages=121,chapters=97,proofs=527,numbered_statements=803,images=141,tables=74,mathematical_expressions_identical=maths,inline_code_nodes_restored=code_added,literal_path_url_commands_checked=469,literal_path_url_commands_missing=0,all_anchor_sequences_identical=True,all_reference_destinations_identical=True),
      changed_reading_pages=changed,base_manifest=result['reading_edition']['base_manifest'],base_manifest_sha256=sha(base_raw),
      pdf_and_source_zip='Retained original release artifacts; this identified correction applies to the web edition.',new_proof_audit=False,new_lean_execution=False)
    target=OUT/'proofread';target.mkdir(exist_ok=True)
    (target/'FINAL_REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    for name in ['build_mnr_html.py','package_mnr_final_reading.py']:
        shutil.copyfile(ROOT/'tools'/name,target/name)
    shutil.copyfile(ROOT/'output/mnr-figure-work/figure-export.numbers',target/'statement-counter-trace.txt')
    print(json.dumps(dict(changed_pages=len(changed),maths_identical=maths,code_nodes_restored=code_added,parts=parts)))

if __name__=='__main__':main()
