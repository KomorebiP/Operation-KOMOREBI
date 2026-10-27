from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parent
arms=['linear_terminal','linear_relation','gru_terminal','gru_intermediate','token_only_terminal']
labels=[]; state=[]; state_control=[]; operator=[]; operator_control=[]
for arm in arms:
    records=[json.loads((root/'arms'/f'{arm}_seed{seed}.json').read_text()) for seed in (0,1)]
    labels.append(arm)
    state.append(np.mean([r['evaluation']['interventions']['state_patch_accuracy'] for r in records]))
    state_control.append(np.mean([r['evaluation']['interventions']['random_state_patch_accuracy'] for r in records]))
    operator.append(np.mean([r['evaluation']['interventions']['operator_patch_accuracy'] for r in records]))
    operator_control.append(np.mean([r['evaluation']['interventions']['random_operator_patch_accuracy'] for r in records]))

x=np.arange(len(labels)); width=.19
figure=plt.figure(figsize=(10,6),dpi=180)
axis=figure.add_subplot(111)
axis.bar(x-1.5*width,state,width,label='state patch')
axis.bar(x-.5*width,state_control,width,label='matched state control')
axis.bar(x+.5*width,operator,width,label='operator patch')
axis.bar(x+1.5*width,operator_control,width,label='matched operator control')
axis.set_xticks(x); axis.set_xticklabels(labels,rotation=20,ha='right')
axis.set_ylim(0,1.03); axis.set_ylabel('Exact counterfactual accuracy')
axis.set_title('Hardened causal intervention assay')
axis.legend(fontsize=8)
figure.tight_layout(); figure.savefig(root/'causal_interventions_hardened.png'); plt.close(figure)
