"""The complete Paper II and III HTML atlases and their source table schemas."""
from worked_visual_atlas import WorkedAtlas
from worked_atlas_sources import SOURCES
from worked_atlas_descriptions import FIGURES

TABLE_AIDS={
 'paper-ii':{
  (2,'L24'):dict(caption='Objects and their roles in the refinement atlas',headers=[r'\textbf{Object}',r'\textbf{Role}',r'\textbf{Worked instance}'],row_header_column=0),
  (24,'L583'):dict(caption='Inherited interfaces, inputs and boundaries',headers=[r'\textbf{Inherited interface}',r'\textbf{Inputs and checked scope}',r'\textbf{Boundary of that interface}'],row_header_column=0),
 },
 'paper-iii':{
  (2,'L21'):dict(caption='Objects and their first worked plates',headers=[r'\textbf{Object}',r'\textbf{What it records}',r'\textbf{First worked page}'],row_header_column=0),
  (24,'L533'):dict(caption='Evidence and the scope it supports',headers=[r'\textbf{Evidence}',r'\textbf{What it supports}'],row_header_column=0),
 },
}
ATLASES={work:WorkedAtlas(work,spec,FIGURES[work],TABLE_AIDS[work],{24:['Edition and proof scope']} if work=='paper-ii' else {}) for work,spec in SOURCES.items()}


def prepare(reader):
    for atlas in ATLASES.values():atlas.prepare(reader)


def render(reader):
    for atlas in ATLASES.values():atlas.render(reader)


def verify(root,documents,pages):
    return {work:atlas.verify(root,documents,pages) for work,atlas in ATLASES.items()}
