#!/usr/bin/env python3
"""Generate editable mathematical source sections from preserved proof inputs.

This is an explicit authoring step; build_traditional.py never silently invokes it.
Original inputs are read only. The editorial differences are inventoried below.
"""
from pathlib import Path
import hashlib,json,re,subprocess
B=Path(__file__).resolve().parent
R=B.parent
specs=[
 ('theta','N','foundation_v0.3.0/*/PROOF.md', '## 1. Analytic input','## 9. What is', 'Canonical fifth-torsion normalization', {'1':'BCG','2':'DLMFWeierstrass'}),
 ('stark','A','stark_modulus/PROOF.md','## 1. Fixed conventions','## 8. Why','Arithmetic conductors and the exact modulus comparison',{'1':'BCG','2':'Milne','3':'DLMFWeierstrass'}),
 ('polarization','Q','continuation_chain/08/*/PROOF.md','## 1. Fixed field','## 6. Exact arithmetic logarithm','The polarized algebraic phase target',{'1':'BCG'}),
]
inventory=[]
for name,prefix,glob,start,end,title,refs in specs:
 p=next((R/'sources').glob(glob)); raw=p.read_text()
 chunk=raw[raw.index(start):raw.index(end)]
 original_chunk=chunk
 if name=='stark':
  appendix=raw[raw.index('## Appendix A.'):raw.index('## Appendix B.')]
  chunk+='\n'+appendix.replace('## Appendix A. Derivation','## 8. Derivation')
  original_chunk=chunk
  # Distinguish the field from the scalar gamma function, and the character
  # from the contracting period multiplier.
  chunk=chunk.replace('L_F','L_{F_0}').replace('F=\\mathbb Q','F_0=\\mathbb Q').replace('\\mathscr O_F','\\mathscr O_{F_0}').replace('E/F','E/F_0').replace('F(X)','F_0(X)').replace('F(\\beta)','F_0(\\beta)').replace('/F\\)', '/F_0\\)').replace('\\zeta_F','\\zeta_{F_0}')
  chunk=re.sub(r'(?<![A-Za-z])\\rho(?![A-Za-z])',r'\\varrho',chunk)
 if name=='polarization':
  # The polynomial arithmetic presentation is a scoped certificate, while
  # the geometric identification is ordinary source mathematics.
  chunk=chunk.replace('new ', '').replace('current interval', 'archived interval')
 # Prefix every retained local equation/theorem number so cross-block
 # source numbering stays unambiguous in the integrated manuscript.
 chunk=re.sub(r'\\tag\{([^}]+)\}',lambda m:'\\tag{'+prefix+m.group(1)+'}',chunk)
 protected=[]
 def protect(m):
  protected.append(m.group(0));return f'MATHSPANPLACEHOLDER{len(protected)-1}END'
 chunk=re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)',protect,chunk,flags=re.S)
 chunk=re.sub(r'(?<![A-Za-z_\\])\(([1-9]\d*(?:\.\d+)?)\)',lambda m:'('+prefix+m.group(1)+')',chunk)
 chunk=re.sub(r'(?m)^(### Theorem )(\d+\.\d+)',lambda m:m.group(1)+prefix+m.group(2),chunk)
 chunk=re.sub(r'(?m)^## (?:\d+\. |Appendix [A-Z]\. )', '## ', chunk)
 for n,key in refs.items(): chunk=chunk.replace('['+n+']', '\\cite{'+key+'}')
 for i,s in enumerate(protected):chunk=chunk.replace(f'MATHSPANPLACEHOLDER{i}END',s)
 # Audit all proper mathematical spans, independently of prose/reference
 # changes. No numerical value, exponent or function argument may change.
 def math_spans(s):
  return re.findall(r'\\\[(.*?)\\\]|\\\((.*?)\\\)',s,re.S)
 def normalize_math(s):
  s=re.sub(r'\\tag\{[A-Z]?([^}]+)\}',r'\\tag{\1}',s)
  s=s.replace('L_{F_0}','L_F').replace('F_0','F').replace('\\mathscr O_{F}','\\mathscr O_F').replace('\\zeta_{F}','\\zeta_F').replace('\\varrho','\\rho')
  return re.sub(r'\s+','',s)
 old=[normalize_math(''.join(x)) for x in math_spans(original_chunk)]
 new=[normalize_math(''.join(x)) for x in math_spans(chunk)]
 if old!=new:
  raise ValueError(f'Mathematical-token change beyond declared notation in {name}: '+repr([(a,b) for a,b in zip(old,new) if a!=b][:3]))
 # Source-relative references are preserved as source references, never
 # presented as links to nonexistent files in the derivative folder.
 chunk=chunk.replace('this release','the corresponding source checkpoint').replace('this block','this development').replace('new evaluated comparison','evaluated comparison')
 intro=f'\\section{{{title}}}\\label{{sec:{name}}}\n'
 intro+=f'\\noindent\\textit{{Source anchor {prefix}: preserved mathematical development; exact source path and hash are in the claim/source inventory. Retained local equation numbers carry this prefix.}}\\par\n'
 md=B/'sections'/f'{name}.md';md.write_text(chunk)
 tex=subprocess.run(['pandoc','-f','markdown+tex_math_dollars+tex_math_single_backslash','-t','latex',str(md)],text=True,capture_output=True,check=True).stdout
 tex=re.sub(r'\\(label|hypertarget|hyperlink)\{([^}]+)\}',lambda m:'\\'+m.group(1)+'{'+prefix+'-'+m.group(2)+'}',tex)
 if name=='stark':
  tex=tex.replace('given in Appendix A',r'given in the normalization subsection below (source A8)').replace('addition step in section 5','CM-product addition step above (source A5)')
  tex=tex.replace('Some key inherited algebraic certificates are rechecked here.', 'The archived source checks rechecked the following inherited algebraic certificates.')
 if name=='polarization':
  tex=tex.replace('F0(xi)',r'\(F_0(\xi)\)').replace('F0(beta/xi)',r'\(F_0(\beta/\xi)\)').replace('F0(beta xi)',r'\(F_0(\beta\xi)\)').replace('F0(beta)',r'\(F_0(\beta)\)')
  tex=tex.replace('omega epsilon2/epsilon1',r'\(\omega\epsilon_2/\epsilon_1\)').replace('omega/iota(A)',r'\(\omega/\iota(\mathcal A)\)').replace('omega A',r'\(\omega\mathcal A\)').replace('& omega \\',r'& \(\omega\) \\')
  tex=tex.replace('retained, rechecked distance bound','retained historical checkpoint distance bound').replace('The retained directed-interval check','The archived checkpoint directed-interval check')
  tex=tex.replace('The directed-interval calculation certifies','The retained historical directed-interval calculation reported')
  tex=tex.replace('A directed-interval computation','An archived checkpoint directed-interval computation')
  tex=tex.replace('certifies positivity','reported positivity')
  tex='\\noindent\\textit{Numerical intervals and decimal diagnostics in this source-derived arithmetic section are retained historical checkpoint evidence; they are not the fresh v0.14 replay and are not newly certified by this edition.}\\par\n'+tex
 (B/'sections'/f'{name}.tex').write_text(intro+tex)
 inventory.append({'section':name,'anchor':prefix,'source':str(p.relative_to(R)), 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_start':start,'source_end':end,'generated_source':f'sections/{name}.tex','mathematical_span_preservation':'PASS','mathematical_spans_checked':len(old)})
manual=[]
for name,anchor,glob in [('principal','P','continuation_chain/01/*/PROOF.md'),('reconstruction','D','v014/PROOF.md'),('norms','T','foundation_v0.1.0/*/PROOF.md'),('rigidity','S','continuation_chain/02/*/PROOF.md'),('product_proof','S','continuation_chain/02/*/PROOF.md')]:
 p=next((R/'sources').glob(glob));manual.append({'section':name,'anchor':anchor,'source':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'derivative':f'sections/{name}.tex','method':'manual mathematical typography and source-consistent proof integration; independent core audit is separately recorded'})
(B/'CLAIM_SOURCE_INVENTORY.json').write_text(json.dumps({'scope':'ordinary mathematical source integration; fresh computational and Lean status is separate','sources':inventory,'manual_source_sections':manual,'editorial_changes':['prefixed retained local equation/theorem numbers','removed historical status/evidence blocks from canonical mathematical sections','distinguished field F0 from gamma function F and ray character varrho from period rho','safe finite-theta grammar and R_* radius are authored in reconstruction.tex','source reference numbers mapped to bibliography keys','four fixed-field/norm rows typeset from plaintext source table after protected-span comparison']},indent=2)+'\n')
print('Generated three editable mathematical sections; mathematical spans passed preservation checks; originals unchanged.')
