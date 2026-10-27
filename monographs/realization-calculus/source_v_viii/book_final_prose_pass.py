from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parent.parent
S=ROOT/'source_v_viii'; OUT=ROOT/'editorial/book_revision'; B=S/'book_edit_baseline'
files=json.loads((OUT/'v_viii_active_sources.json').read_text())
changes=[]
def write(p,t,why):
 old=p.read_text()
 if t==old:return
 b=B/p.relative_to(S)
 if not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 p.write_text(t);changes.append({'file':str(p.relative_to(ROOT)),'reason':why})
def replace(p,a,b):
 t=p.read_text();assert a in t,(p,a);write(p,t.replace(a,b),a[:150])
for key,paths in files.items():
 for f in paths:
  p=Path(f)
  if any(x in str(p) for x in ['graphics','generated','component-layout']):continue
  t=p.read_text()
  t=re.sub(r'\b(?:Pages|pages) (?=\\pagerefV\{)', '',t)
  # The hyperlink macro already prints the fully qualified plate name.
  t=t.replace('The preserved v1.1.0 release maps twenty theorem-like statements', 'The Part I formal correspondence maps twenty theorem-like statements')
  t=t.replace('Its saved compiler and axiom records remain inherited evidence. No fresh Lean run is claimed for this edition.', 'Its compiler and axiom records provide the retained execution evidence; the formal companion gives their scope and reproduction instructions.')
  t=t.replace('The inherited v0.6.0 formal ledger has 19 scoped finite results.', 'The finite formal correspondence covers nineteen scoped results.')
  t=t.replace('The saved v0.6.0 formal record contains 56 manuscript-proved finite items,', 'The finite formal correspondence contains 56 manuscript-proved items,')
  t=t.replace('{What this edition certifies}', '{What the evidence certifies}')
  t=t.replace('The retained execution records describe the example suites, their tested inputs, and their rejected controls. This revision improves the prose and layout without presenting those earlier checks as new executions.', 'The retained execution records describe the example suites, their tested inputs, and their rejected controls. The formal companion distinguishes these finite checks from the theorem correspondence.')
  t=t.replace('The extension includes retained exact checks over specified finite ranges in $\\QQ(\\ii)$ using \\texttt{Fraction} from Python\'s standard library. The original appendix\'s record of 180 checks, including symbolic derivatives, is also retained. Both records come from earlier executions. This prose revision adds no symbolic or Lean kernel run. All model and vector sources remain supplied.', 'The extension includes retained exact checks over specified finite ranges in $\\QQ(\\ii)$ using \\texttt{Fraction} from Python\'s standard library. The original appendix\'s record of 180 checks, including symbolic derivatives, is also retained. The formal companion records the provenance of these checks. All model and vector sources remain supplied.')
  t=t.replace('Read this guide alongside the traditional volume. The first 28 worked pages retain the original appendix\'s examples and mathematical content, with source references updated to this edition.', 'Read these examples alongside the mathematical text. The first twenty-eight plates develop the finite constructions and their geometric interpretation.')
  t=t.replace('develop additional strengthened results.', 'develop the further results on bounded limits and constraints.')
  write(p,t,'Timeless evidence descriptions; avoid duplicated “Pages Plate” in plate cross-references')
# Source prose surrounding exact provenance, not the exact reproduction data themselves.
p=S/'V/editable/traditional/Paper_V_Traditional_Final.tex'
replace(p,'The September 2026 release records a successful build and axiom audit with warnings treated as errors. No fresh Lean build is asserted for this October final edition.', 'The retained compiler record documents a successful build and axiom audit with warnings treated as errors. The formal companion identifies its source, toolchain, and reproduction procedure.')
p=S/'VIII/editable/lean_guide/chapters/replay.tex'
replace(p,'\\subsection{The status of this edition}', '\\subsection{Static source and documentation checks}')
replace(p,'Lean and Lake are absent from the present host. The documentation report says \\code{fresh_lean_kernel_run: false}. This edition makes no fresh compilation claim. The source and accepted evidence are unchanged. The original accepted build remains inherited evidence rather than a current run.', 'The documentation report records \\code{fresh_lean_kernel_run: false}. Its source and documentation checks do not constitute a kernel replay. The accepted compiler record supplies the execution evidence; the procedure below explains how to reproduce it.')
replace(p,'The six retained supplements document successive proof blocks. Their earlier coverage and remaining-work lists are historical; the sixth ledger supersedes those live status statements. They remain preserved as evidence of what each release actually established.', 'The historical verification appendix records six successive proof blocks. Its earlier coverage and remaining-work lists describe those stages; the sixth ledger supplies the cumulative finite correspondence. These records preserve what each stage established.')
# Restore the exact useful locators to the embedded VIII atlas before deduplication.
for name in ['pages.tex','extended_pages.tex']:
 vp=S/'VIII/editable/visual_guide/source'/name;tp=S/'VIII/editable/traditional/atlas_sources'/name
 vt=vp.read_text()
 vt=vt.replace('Mathematical text: Section 13, Section 14, Section F.6, Section F.7.', 'Mathematical text: Sections 13--14; formal companion: historical verification appendix.')
 if name=='pages.tex':
  common='A source line beneath each title identifies the relevant result in the mathematical text. The preserved examples use rational, Gaussian-rational, symbolic, and finite-enumeration arithmetic. Portable checks use exact rational and Gaussian-rational arithmetic. The retained SymPy records list the assertions and rejected controls separately. Smooth drawing coordinates illustrate stated formulas; they are not additional proof evidence.'
  vt=re.sub(r'A source line beneath each title[^\n]+',lambda m:common,vt)
 write(vp,vt,'Reader-facing evidence and relocated verification locator')
 tt=tp.read_text()
 if name=='pages.tex':tt=re.sub(r'The standalone visual companion[^\n]+',lambda m:common,tt)
 lines={int(m.group(1)):m.group(0) for m in re.finditer(r'^\\vpage\{([0-9]+)\}[^\n]+',vt,re.M)}
 tt=re.sub(r'^\\vpage\{([0-9]+)\}[^\n]+',lambda m:lines[int(m.group(1))],tt,flags=re.M)
 write(tp,tt,'Restore named result locators from the corresponding standalone plates')
p=S/'VIII/editable/traditional/atlas_definitions.tex'
replace(p,'\\vspace{6pt}}', '{\\sffamily\\fontsize{8.7}{11}\\selectfont\\color{muted} #4\\par}\\vspace{6pt}}')
# Match harmless locator punctuation across the two VI presentations.
for name in ['pages.tex','extensions.tex']:
 p=S/'VI/editable/visual_guide/source'/name;t=p.read_text();write(p,t.replace('Mathematical text: Part ', 'Mathematical text, Part '),'Consistent locator punctuation')
(OUT/'v_viii_final_prose_journal.json').write_text(json.dumps(changes,indent=2))
print(len(changes),'final prose operations')
