from pathlib import Path
import shutil,json,re
R=Path(__file__).resolve().parent
for n in ['V','VI','VII','VIII']:
 for role in ['traditional','visual_guide','lean_guide']:
  p=R/n/'editable'/role/'component-layout.tex';s=p.read_text()
  note=(r'\vspace{24pt}{\small\sffamily\color{pubMuted}\textbf{Edition locators.} The contents and live internal links use this typeset component. Fixed page locators quoted from earlier reader editions retain their original pagination. Traditional-paper locators refer to the supplied frozen reader: \par\smallskip\nolinkurl{frozen_readers/Paper_'+n+r'_Traditional_Final.pdf}\par}'+'\n')
  s=s.replace(' \\vfill\n', ' '+note+' \\vfill\n');p.write_text(s)
 if n in ['VI','VII','VIII']:
  p=R/n/'editable/lean_guide/generated/traditional_navigation.tex';before=R/'before'/n/'lean_guide/generated/traditional_navigation.tex';before.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,before)
  s=p.read_text();s=s.replace('Printed pages are the labels in the traditional volume.', 'Printed pages are the labels in the frozen traditional volume.').replace('These locations refer to the final 152-page monograph.', 'These locations refer to the frozen 152-page monograph.').replace('The final traditional volume has 159 physical PDF pages.', 'The frozen traditional volume has 159 physical PDF pages.').replace('The traditional volume contains 124 physical PDF pages.', 'The frozen traditional volume contains 124 physical PDF pages.')
  s=s.replace('Every location below was resolved', 'Every frozen-edition location below was resolved').replace('The locations below are resolved from the current source map', 'The frozen-edition locations below are resolved from its source map')
  p.write_text(s)
# Final build script: font dependencies discovered locally; source/figures are never regenerated.
s=(R/'polish_build.py').read_text();s=s.replace("todo=[r for r in records if r['role']!='lean_guide']", "todo=records")
s=s.replace("ROOT/'BUILD_RESULTS_FINAL.json'", "ROOT/'BUILD_RESULTS_FINAL.json'")
(R/'final_build.py').write_text(s)
