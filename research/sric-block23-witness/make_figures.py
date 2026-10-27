from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
RESULT=json.loads((ROOT/"results"/"block23_final.json").read_text())
records=RESULT["records"]
families=["identified","answer_shortcut","gauge_equivalent","semantic_ambiguity","partial_ontology","destructive_loss"]
certs=["ONTOLOGY_IDENTIFIED","ONTOLOGY_IDENTIFIED_UP_TO_GAUGE","PARTIAL_ONTOLOGY","ONTOLOGY_UNDERIDENTIFIED","SEMANTIC_INFORMATION_LOSS"]

# Certificate matrix.
mat=np.zeros((len(families),len(certs)),dtype=int)
for r in records:
    mat[families.index(r["family"]),certs.index(r["certificate"])]+=1
fig,ax=plt.subplots(figsize=(10,5.8))
im=ax.imshow(mat,aspect="auto")
ax.set_xticks(range(len(certs)),["identified","up to gauge","partial","underidentified","information loss"],rotation=25,ha="right")
ax.set_yticks(range(len(families)),[x.replace("_"," ") for x in families])
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        ax.text(j,i,str(mat[i,j]),ha="center",va="center")
ax.set_title("Block 23 final ontology certificates")
ax.set_xlabel("Issued certificate")
ax.set_ylabel("Hidden audit regime")
fig.tight_layout()
fig.savefig(ROOT/"figures"/"block23_certificate_matrix.png",dpi=220)
plt.close(fig)

# Selected rank/method.
rank=[]; labels=[]
for fam in families:
    xs=[r for r in records if r["family"]==fam]
    rank.append(float(np.mean([r["selected_rank"] or 0 for r in xs])))
    labels.append(str(xs[0]["selected_method"]))
fig,ax=plt.subplots(figsize=(9,5.2))
pos=np.arange(len(families))
ax.bar(pos,rank)
ax.set_xticks(pos,[x.replace("_"," ") for x in families],rotation=25,ha="right")
for x,y,label in zip(pos,rank,labels):
    ax.text(x,y+0.08,label,ha="center",va="bottom",rotation=15,fontsize=8)
ax.set_ylabel("Selected quotient rank (0 = no-go)")
ax.set_title("Minimum valid semantic quotient selected before hidden reveal")
ax.set_ylim(0,5.2)
fig.tight_layout()
fig.savefig(ROOT/"figures"/"block23_minimal_quotients.png",dpi=220)
plt.close(fig)

# Counterfactual patch controls.
summary=RESULT["summary"]["counterfactual_patch"]
vals=[summary["minimum_selected_future_r2"],summary["maximum_answer_only_future_r2"],summary["maximum_pca_future_r2"],summary["maximum_random_future_r2"]]
fig,ax=plt.subplots(figsize=(8.2,4.8))
ax.bar(np.arange(4),vals)
ax.axhline(0,linewidth=1)
ax.set_xticks(np.arange(4),["selected packet\n(min)","answer-only\n(max)","PCA\n(max)","random\n(max)"])
ax.set_ylabel("Donor future-state reconstruction R²")
ax.set_title("Audit-only counterfactual patching separates causal semantics from shortcuts")
for i,v in enumerate(vals):
    ax.text(i,v+(0.04 if v>=0 else -0.08),f"{v:.3f}",ha="center",va="bottom" if v>=0 else "top")
fig.tight_layout()
fig.savefig(ROOT/"figures"/"block23_counterfactual_controls.png",dpi=220)
plt.close(fig)

print("BLOCK23_FIGURES=3")
