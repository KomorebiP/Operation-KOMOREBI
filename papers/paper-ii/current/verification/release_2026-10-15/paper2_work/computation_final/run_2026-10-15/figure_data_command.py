import json,sys
from pathlib import Path
sys.path.insert(0,'figure_sources')
import common
stems=[]
def data_only_save(fig,stem):
    stems.append(stem)
    common.plt.close(fig)
common.save=data_only_save
import draw_matrix_visuals,draw_graph_visuals
matrix=draw_matrix_visuals.generate()
graph=draw_graph_visuals.generate()
Path(sys.argv[1]).write_text(json.dumps({'stems':stems,'matrix':matrix,'graph':graph},indent=2)+'\n')
print('PASS: data/assertion paths for',len(stems),'figures; PDF/PNG serialization suppressed')
