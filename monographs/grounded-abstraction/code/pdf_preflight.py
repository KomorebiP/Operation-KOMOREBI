"""PDF geometry/text/build diagnostics. Requires PyMuPDF; not a proof check."""
from pathlib import Path
import json,re,subprocess
import fitz
ROOT=Path(__file__).resolve().parents[1]


def main():
    pdf=ROOT/'Grounded_Abstraction_v1.0.0.pdf';doc=fitz.open(pdf)
    out=[];markers=[];stats=[]
    for i,page in enumerate(doc):
        text=page.get_text();stats.append({'physical_page':i+1,'characters':len(text),'words':len(page.get_text('words'))})
        if '\ufffd' in text or '??' in text:markers.append(i+1)
        for w in page.get_text('words'):
            if w[0]<-.25 or w[1]<-.25 or w[2]>page.rect.width+.25 or w[3]>page.rect.height+.25:
                out.append({'page':i+1,'word':w[4],'box':w[:4]})
    log=(ROOT/'build/Grounded_Abstraction_v1.0.0.log').read_text(errors='replace')
    warnings=[line for line in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined',line)]
    fontproc=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True)
    (ROOT/'validation/pdffonts.txt').write_text(fontproc.stdout)
    unembedded=[]
    for line in fontproc.stdout.splitlines()[2:]:
        columns=line.split()
        if len(columns)>=8 and columns[-5]!='yes':unembedded.append(line)
    record={'status':'PASS' if not(out or markers or warnings or unembedded) else 'FAIL',
            'pages':len(doc),'out_of_page_words':out,'unresolved_or_replacement_pages':markers,
            'latex_diagnostics':warnings,'unembedded_font_rows':unembedded,'page_statistics':stats,
            'limits':['Geometry is not proof validity.','No PDF/A or accessibility tagging certified.','Visual review recorded separately.']}
    (ROOT/'validation/pdf_preflight.json').write_text(json.dumps(record,indent=2)+'\n')
    print(record['status'],len(doc),'pages;',len(warnings),'LaTeX diagnostics;',len(out),'out-of-page words')
    if record['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
