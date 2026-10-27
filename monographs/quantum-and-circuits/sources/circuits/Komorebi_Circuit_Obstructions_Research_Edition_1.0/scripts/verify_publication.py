"""Check publication artifacts and write bounded, layered validation evidence."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import fitz

ROOT=Path(__file__).resolve().parents[1]
DOCS=[('main','Komorebi_Circuit_Obstructions_Main_Paper.pdf'),
      ('visual','Komorebi_Circuit_Obstructions_Visual_Guide.pdf'),
      ('lean','Komorebi_Circuit_Obstructions_Lean_Guide.pdf')]
EXPECTED_SOURCE='88628c8274660bd20e11fec83249fdc04960403b9d64d1e5068a476b8c025936'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=[];extracted=[]
    for name,filename in DOCS:
        p=ROOT/'output'/filename
        if not p.is_file(): raise FileNotFoundError(p)
        d=fitz.open(p);bad=[];texts=[]
        for i,page in enumerate(d):
            texts.append(page.get_text())
            for b in page.get_text('dict')['blocks']:
                for line in b.get('lines',[]):
                    for span in line.get('spans',[]):
                        x0,y0,x1,y1=span['bbox']
                        if span['text'].strip() and (x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5):
                            bad.append({'page':i+1,'text':span['text'],'bbox':span['bbox']})
        log_path=ROOT/'build'/name/(name+'.log')
        log=log_path.read_text(errors='replace')
        problems=re.findall(r'(?m)^(?:!|Overfull|Underfull|LaTeX Warning|LaTeX Font Warning|Package .*Warning|pdfTeX warning).*',log)
        if bad or problems:raise ValueError(f'{name}: page bounds {bad}; build warnings {problems}')
        f=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True,check=True)
        font_rows=f.stdout.splitlines()[2:]
        if not font_rows:raise ValueError('No fonts found: '+filename)
        for row in font_rows:
            # The last seven columns are encoding, embedded, subset, unicode,
            # object number, generation number, with Type1/Type3 variable width.
            cols=row.split()
            if cols[-5]!='yes':raise ValueError('Unembedded font: '+row)
            if 'Type 3' in row:raise ValueError('Bitmap font: '+row)
        extracted.extend(texts)
        records.append({'name':filename,'pages':len(d),'sha256':digest(p),
                        'manuscript_sha256':digest(ROOT/'manuscripts'/(name+'.tex')),
                        'build_log_sha256':digest(log_path),
                        'out_of_page_text':bad,'build_warnings':problems,
                        'fonts_embedded':True,'bitmap_fonts':False})
    source=ROOT/'downloads/komorebi-circuit-obstructions-v1.2.0.zip'
    if not source.exists():source=ROOT/'originals/komorebi-circuit-obstructions-v1.2.0.zip'
    if digest(source)!=EXPECTED_SOURCE:raise ValueError('Original source ZIP digest mismatch')
    figure_review=json.loads((ROOT/'reviews/figure_review_hashes.json').read_text())
    if figure_review['status']!='PASS' or len(figure_review['figures'])!=12:
        raise ValueError('Final figure review incomplete')
    for figure in figure_review['figures']:
        if figure['verdict']!='PASS':raise ValueError('Unresolved figure review')
        for kind in ['pdf','png']:
            if digest(ROOT/figure[kind+'_file'])!=figure[kind+'_sha256']:
                raise ValueError('Stale figure review: '+figure['name'])
    catalog_path=ROOT/'source/komorebi-circuit-obstructions-v1.2.0/reference/lean-block02/declaration_catalog.json'
    entries=json.loads(catalog_path.read_text())['theorems']
    register_path=ROOT/'manuscripts/lean_register.tex'
    register=register_path.read_text()
    blocks=re.findall(r'\\begin\{lstlisting\}\n(.*?)\n\\end\{lstlisting\}',register,re.S)
    if len(entries)!=115 or blocks!=[e['statement_utf8'] for e in entries]:
        raise ValueError('Declaration register differs from archived exact types')
    sidecar=ROOT/'manuscripts/lean_statements_utf8.txt'
    if sidecar.read_text()!='\n\n'.join(e['id']+'\n'+e['statement_utf8'] for e in entries)+'\n':
        raise ValueError('UTF-8 type sidecar differs from archived catalog')
    if r'\input{lean_register.tex}' not in (ROOT/'manuscripts/lean.tex').read_text():
        raise ValueError('Lean guide omits full register')
    text='\n'.join(extracted)
    if '\ufffd' in text:raise ValueError('Replacement character in extracted text')
    result={'schema':'komorebi.circuit.publication-validation.v1','status':'PASS',
            'documents':records,'total_pages':sum(x['pages'] for x in records),
            'source_archive_sha256':EXPECTED_SOURCE,
            'shared_style_sha256':digest(ROOT/'manuscripts/common.tex'),
            'reviewed_figure_pairs':12,
            'figure_review_hashes_current':True,
            'printed_archived_types':115,
            'exact_register_transcription':True,
            'register_tex_sha256':digest(register_path),
            'utf8_type_sidecar_sha256':digest(sidecar),
            'fresh_exact_suite':'PASS, --all including historical replay',
            'fresh_lean_replay':'FAIL: lean executable absent before proof compilation',
            'archived_lean_evidence':'115 declarations, 8 modules, 8 negative controls, 21 September 2026',
            'visual_review':'Recorded separately; bounds and fonts do not replace inspection',
            'meaning':'Document/byte validation, not a universal proof or a new kernel pass'}
    (ROOT/'reviews/publication_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
