"""Extract only the peer-reviewed narrative chapters from the frozen core source.
The original source is preserved byte-identically under sources/core/src/core.tex.
The emitted file remains verbatim between the mainmatter and backmatter boundaries.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
core=(root/'sources/core/src/core.tex').read_text()
first=r'\chapter{From evidence to a reusable state}'
start=core.index(first)
end=core.index(r'\backmatter',start)
part=core[start:end]
(root/'core_chapters.tex').write_text(part)
print('Preserved source chapter span',len(part),'characters',part.count('\\begin{theorem}')+part.count('\\begin{proposition}')+part.count('\\begin{corollary}'),'theorem-like environments')
