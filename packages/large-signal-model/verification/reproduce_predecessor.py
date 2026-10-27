import json, warnings
import numpy as np
from komorebi_pr_lasm import MultiAtlasAnalyzer, UltimateLASMPacketizer, PacketTree
from komorebi_arc3_offline.exact_atlas import polyphase2d_synthesize, fourier_project
from komorebi_arc3_offline.bayes import normalized_probabilities
from komorebi_arc3_offline.lasm_graph import StateTransitionGraph
from komorebi_arc3_offline.types import ActionCandidate
results=[]
def run(name,fn):
 try:
  with warnings.catch_warnings(record=True) as ws:
   warnings.simplefilter('always')
   value=fn()
  results.append({'case':name,'result':value,'warnings':[str(w.message) for w in ws]})
 except Exception as exc:
  results.append({'case':name,'raised':type(exc).__name__,'message':str(exc)})
run('continuous_color_not_exact', lambda: MultiAtlasAnalyzer().analyze(np.full((8,8),0.25)).reconstruction_residuals())
run('odd_shape', lambda: list(MultiAtlasAnalyzer().analyze(np.zeros((7,9))).shape))
run('small_shape_nan_features', lambda: bool(np.isfinite(MultiAtlasAnalyzer().feature_vector(MultiAtlasAnalyzer().analyze(np.zeros((1,1))))).all()))
run('empty_polyphase_zero_modulus', lambda: polyphase2d_synthesize({}, (2,2),0).tolist())
run('packet_pruning_wrong_root_shape', lambda: PacketTree.analyze(np.arange(8.),3).synthesize({'':np.arange(2.)}).tolist())
run('all_minus_infinity_probabilities', lambda: normalized_probabilities(np.array([-np.inf,-np.inf])).tolist())
run('exact_archive_resized', lambda: list(UltimateLASMPacketizer().resolve(np.arange(64).reshape(8,8)%16).analysis.shape))
x=np.arange(16.).reshape(4,4); mask=np.zeros((4,4));mask[0,1]=1
run('asymmetric_fourier_not_projector', lambda: float(np.max(np.abs(fourier_project(fourier_project(x,mask),mask)-fourier_project(x,mask)))))
def graph_case():
 g=StateTransitionGraph(); a=ActionCandidate(1)
 for target in ['b','c']:
  g.record('a',a,target,reward=1,level_delta=1,terminal_win=False,terminal_loss=False)
 return {'nondeterministic':g.summary()['nondeterministic_edges'], 'progressing_action':g.progressing_action('a')}
run('nondeterministic_progress_replayed', graph_case)
print(json.dumps(results,indent=2,allow_nan=True))
