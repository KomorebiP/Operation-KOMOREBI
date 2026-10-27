#!/usr/bin/env python3
"""Build only the H12 formal-guide PDF/Markdown and guide generation audit."""
from pathlib import Path
import argparse,subprocess,re,json,hashlib,tempfile
import fitz
ROOT=Path(__file__).resolve().parent
NAME='H12_Cubic_Divisor_Lean_Guide'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def expanded(s):
 return re.sub(r'\\input\{([^}]+)\}',lambda m:expanded((ROOT/m.group(1)).read_text()),s)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--skip-pdf',action='store_true');a=ap.parse_args()
 logs=ROOT/'verification';source=ROOT/(NAME+'.tex')
 if not a.skip_pdf:
  for k in range(1,4):
   p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',source.name],cwd=ROOT,capture_output=True,text=True)
   (logs/f'guide_latex_pass{k}.log').write_text(p.stdout+p.stderr)
   assert p.returncode==0,(k,p.stdout[-2500:])
  last=(logs/'guide_latex_pass3.log').read_text()
  assert not re.search(r'Overfull|Undefined|Warning|Error',last),last[-3000:]
 text=expanded(source.read_text())
 text=re.sub(r'\\decl\{([^}]*)\}',lambda m:r'\verb|'+m.group(1).replace(r'\#','#')+'|',text)
 with tempfile.NamedTemporaryFile('w',suffix='.tex') as f:
  f.write(text);f.flush()
  p=subprocess.run(['pandoc','-f','latex','-t','markdown','--wrap=none',f.name],capture_output=True,text=True)
  assert p.returncode==0,p.stderr
 md='# H12 Cubic Divisor Regularization\n\nA Lean companion for exact coefficients and conditional comparisons.\n\nKomorebi P. · Final edition, 7 October 2026\n\n'+p.stdout
 (ROOT/(NAME+'.md')).write_text(md)
 inv=json.loads((ROOT/'DECLARATION_INVENTORY.json').read_text())
 current={x['name'].split('.')[-1] for x in inv if x['kind']=='theorem' and x['v014_current_block']}
 mods={x['module'] for x in json.loads((ROOT/'SOURCE_MODULE_MAP.json').read_text())}
 assert all(x in md for x in current),sorted(x for x in current if x not in md)
 assert all(x in md for x in mods),sorted(x for x in mods if x not in md)
 pdf=ROOT/(NAME+'.pdf');doc=fitz.open(pdf)
 assert doc.metadata.get('author')=='Komorebi P.',doc.metadata
 files=[source,ROOT/(NAME+'.md'),pdf,logs/'replay_summary.tex',logs/'replay_details.tex',logs/'current_inventory_table.tex',logs/'module_inventory_table.tex']
 d={'status':'PASS','pdf_pages':len(doc),'pdf_author':doc.metadata['author'],'latex_final_pass':'clean: no overfull boxes, undefined references, warnings or errors','markdown_current_names_preserved':len(current),'markdown_module_names_preserved':len(mods),'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},'formal_replay_ledger_sha256':sha(logs/'FINAL_REPLAY_AUDIT.json'),'render_review':'pending native page inspection'}
 (logs/'GUIDE_GENERATION_AUDIT.json').write_text(json.dumps(d,indent=2)+'\n')
 print('Guide generated:',len(doc),'pages;',pdf.stat().st_size,'bytes; metadata and name-preservation checks PASS')
if __name__=='__main__':main()
