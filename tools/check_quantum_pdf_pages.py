"""Recheck the HTML result-index page map against its retained original PDF.

Requires pypdfium2, also used by the figure reproduction helpers. This checks
document navigation, not mathematical claims or formal verification.
"""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def main():
    import pypdfium2 as pdfium
    data=json.loads((ROOT/'tools/quantum_sections.json').read_bytes())
    receipt=data['result_index_pdf'];raw=(ROOT/receipt['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==receipt['sha256'],'PDF identity changed'
    document=pdfium.PdfDocument(raw)
    def text(number):
        page=document[number-1];textpage=page.get_textpage()
        result=textpage.get_text_range();textpage.close();page.close()
        return result
    index=text(receipt['index_pdf_page']).replace('\ufffe','')
    index=index.split('No. Result Scope Page',1)[1].split('E.4 Baseline',1)[0]
    printed=[]
    for match in re.finditer(r'(?m)^(\d+\.\d+) (.*?)(?=^\d+\.\d+ |\Z)',index,re.S):
        printed.append((match[1],int(re.search(r'(\d+)\s*$',match[2])[1])))
    assert printed==[(r['number'],r['printed_page']) for r in receipt['rows']]
    assert len(printed)==30
    for row in receipt['rows']:
        target=text(row['pdf_page'])
        assert target.splitlines()[-1].strip()==str(row['printed_page']),'Wrong physical PDF page'
        assert re.search(r'\b'+re.escape(row['number'])+r'\b',target),'Statement number missing on target page'
    document.close()
    print('PASS: all 30 printed result-index pages and their physical PDF destinations.')


if __name__=='__main__':main()
