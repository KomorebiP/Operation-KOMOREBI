#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    frozen = json.loads((root/'results/PILOT_ANALYSIS.json').read_text())
    controls = json.loads((root/'results/POSTOUTCOME_CONTROLS.json').read_text())
    geom = json.loads((root/'results/POSTOUTCOME_GEOMETRY_AUDIT.json').read_text())
    sweep = json.loads((root/'results/POSTOUTCOME_INTERVENTION_SWEEP.json').read_text())
    recheck = json.loads((root/'results/DETERMINISTIC_RECHECK.json').read_text())
    freeze = json.loads((root/'PREOUTCOME_FREEZE.json').read_text())

    arm_labels = {
        'answer_only':'Answer only',
        'state_supervised':'State supervised',
        'operator_regularized':'Operator regularized',
    }
    splits = ['id','ood_length','ood_templates','ood_combined','long_chain']
    split_labels = ['ID','Long composition','Held-out syntax','Combined OOD','Long chain']

    # Figure 1: answer accuracy.
    x = np.arange(len(splits))
    width = 0.15
    plt.figure(figsize=(10.5, 5.8))
    series = [
        ('Query majority', [frozen['baselines']['query_type_majority'][s] for s in splits]),
        ('TF-IDF bigram', [frozen['baselines']['tfidf_bigram'][s] for s in splits]),
    ] + [
        (arm_labels[a], [frozen['aggregate'][a][f'splits.{s}.answer_accuracy']['mean'] for s in splits])
        for a in arm_labels
    ]
    for i,(label,values) in enumerate(series):
        plt.bar(x + (i-2)*width, values, width, label=label)
    plt.xticks(x, split_labels, rotation=15, ha='right')
    plt.ylabel('Answer accuracy')
    plt.ylim(0,1)
    plt.title('OSL sentence-world generalization')
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(root/'results/answer_accuracy.png', dpi=180)
    plt.close()

    # Figure 2: formal-state CKA.
    labels = ['Random untrained','Answer only','State supervised','Operator regularized']
    values = [
        geom['summary']['random_untrained']['cka']['mean'],
        geom['summary']['answer_only']['cka']['mean'],
        geom['summary']['state_supervised']['cka']['mean'],
        geom['summary']['operator_regularized']['cka']['mean'],
    ]
    plt.figure(figsize=(8.4,5.4))
    plt.bar(np.arange(len(labels)), values)
    plt.xticks(np.arange(len(labels)), labels, rotation=15, ha='right')
    plt.ylabel('Linear CKA with formal state')
    plt.title('Latent alignment with executable provenance state')
    plt.tight_layout()
    plt.savefig(root/'results/formal_state_cka.png', dpi=180)
    plt.close()

    # Figure 3: equivalence retrieval.
    values = [
        geom['summary']['random_untrained']['retrieval_top1']['mean'],
        geom['summary']['answer_only']['retrieval_top1']['mean'],
        geom['summary']['state_supervised']['retrieval_top1']['mean'],
        geom['summary']['operator_regularized']['retrieval_top1']['mean'],
    ]
    plt.figure(figsize=(8.4,5.4))
    plt.bar(np.arange(len(labels)), values)
    plt.xticks(np.arange(len(labels)), labels, rotation=15, ha='right')
    plt.ylabel('Equivalent-path top-1 retrieval')
    plt.title('Does the latent identify a different path to the same formal state?')
    plt.tight_layout()
    plt.savefig(root/'results/equivalence_retrieval.png', dpi=180)
    plt.close()

    # Figure 4: state probe controls.
    probe_labels = ['Random features','TF-IDF','Answer only','State supervised','Operator regularized']
    status = [
        controls['random_aggregate']['status_balanced_probe']['mean'],
        controls['tfidf_state_probe']['status_balanced_accuracy'],
        frozen['aggregate']['answer_only']['linear_probe.linear_probe_status_balanced_accuracy']['mean'],
        frozen['aggregate']['state_supervised']['linear_probe.linear_probe_status_balanced_accuracy']['mean'],
        frozen['aggregate']['operator_regularized']['linear_probe.linear_probe_status_balanced_accuracy']['mean'],
    ]
    origin = [
        controls['random_aggregate']['origin_balanced_probe']['mean'],
        controls['tfidf_state_probe']['origin_balanced_accuracy'],
        frozen['aggregate']['answer_only']['linear_probe.linear_probe_origin_balanced_accuracy']['mean'],
        frozen['aggregate']['state_supervised']['linear_probe.linear_probe_origin_balanced_accuracy']['mean'],
        frozen['aggregate']['operator_regularized']['linear_probe.linear_probe_origin_balanced_accuracy']['mean'],
    ]
    x = np.arange(len(probe_labels)); width=.36
    plt.figure(figsize=(9.3,5.6))
    plt.bar(x-width/2,status,width,label='Status')
    plt.bar(x+width/2,origin,width,label='Origin')
    plt.xticks(x,probe_labels,rotation=15,ha='right')
    plt.ylabel('Class-balanced probe accuracy')
    plt.title('Linear decodability is not sufficient evidence of learned semantics')
    plt.legend()
    plt.tight_layout()
    plt.savefig(root/'results/probe_controls.png',dpi=180)
    plt.close()

    # Figure 5: intervention sweep.
    labels2 = [arm_labels[a] for a in arm_labels]
    targeted = [sweep['summary'][a]['targeted_flip_rate']['mean'] for a in arm_labels]
    random_flip = [sweep['summary'][a]['random_flip_rate']['mean'] for a in arm_labels]
    x=np.arange(len(labels2)); width=.36
    plt.figure(figsize=(8.4,5.4))
    plt.bar(x-width/2,targeted,width,label='Probe-defined direction')
    plt.bar(x+width/2,random_flip,width,label='Random direction')
    plt.xticks(x,labels2,rotation=12,ha='right')
    plt.ylabel('Status-output flip rate across scale sweep')
    plt.title('Causal steering test')
    plt.legend()
    plt.tight_layout()
    plt.savefig(root/'results/intervention_sweep.png',dpi=180)
    plt.close()

    summary = {
        'schema':'osl.emergence.final-adjudication.v1',
        'version':'0.6.0.dev1',
        'scientific_status':'PARTIAL_OPERATOR_RELEVANT_STRUCTURE_NOT_FULL_SYMBOLIC_EMERGENCE',
        'preoutcome_freeze_digest':freeze['digest'],
        'frozen_analysis_digest':frozen['digest'],
        'postoutcome_control_digest':controls['digest'],
        'postoutcome_geometry_digest':geom['digest'],
        'postoutcome_intervention_digest':sweep['digest'],
        'frozen_endpoints':{
            'passed':frozen['endpoint_pass_count'],
            'total':frozen['endpoint_count'],
            'all_met':frozen['all_endpoints_met'],
            'important_qualification':'Several endpoint metrics were subsequently shown to have strong random-feature or lexical explanations.'
        },
        'principal_findings':{
            'answer_only_behavior':{
                s:frozen['aggregate']['answer_only'][f'splits.{s}.answer_accuracy']['mean'] for s in splits
            },
            'tfidf_behavior':frozen['baselines']['tfidf_bigram'],
            'operator_regularized_behavior':{
                s:frozen['aggregate']['operator_regularized'][f'splits.{s}.answer_accuracy']['mean'] for s in splits
            },
            'formal_state_cka':{
                'random':geom['summary']['random_untrained']['cka']['mean'],
                'answer_only':geom['summary']['answer_only']['cka']['mean'],
                'state_supervised':geom['summary']['state_supervised']['cka']['mean'],
                'operator_regularized':geom['summary']['operator_regularized']['cka']['mean'],
            },
            'equivalent_path_top1_retrieval':{
                'random':geom['summary']['random_untrained']['retrieval_top1']['mean'],
                'answer_only':geom['summary']['answer_only']['retrieval_top1']['mean'],
                'state_supervised':geom['summary']['state_supervised']['retrieval_top1']['mean'],
                'operator_regularized':geom['summary']['operator_regularized']['retrieval_top1']['mean'],
            },
            'probe_control':{
                'random_status_balanced':controls['random_aggregate']['status_balanced_probe']['mean'],
                'answer_status_balanced':frozen['aggregate']['answer_only']['linear_probe.linear_probe_status_balanced_accuracy']['mean'],
                'tfidf_status_balanced':controls['tfidf_state_probe']['status_balanced_accuracy'],
                'random_origin_balanced':controls['random_aggregate']['origin_balanced_probe']['mean'],
                'answer_origin_balanced':frozen['aggregate']['answer_only']['linear_probe.linear_probe_origin_balanced_accuracy']['mean'],
                'tfidf_origin_balanced':controls['tfidf_state_probe']['origin_balanced_accuracy'],
            },
            'transition_control':{
                'random_untrained_r2':controls['random_aggregate']['affine_transition_r2']['mean'],
                'answer_only_r2':frozen['aggregate']['answer_only']['transition_geometry.affine_transition_r2']['mean'],
                'conclusion':'The affine-transition score is architecture-induced and cannot support a learned-operator claim in this pilot.'
            },
            'causal_intervention':{
                a:{
                    'targeted_flip_rate':sweep['summary'][a]['targeted_flip_rate']['mean'],
                    'random_flip_rate':sweep['summary'][a]['random_flip_rate']['mean'],
                    'targeted_coherent_conversion':sweep['summary'][a]['targeted_coherent_rate']['mean'],
                    'random_coherent_conversion':sweep['summary'][a]['random_coherent_rate']['mean'],
                } for a in arm_labels
            }
        },
        'conclusion':(
            'Generated sentences were sufficient for nontrivial provenance-sensitive behavior and weak latent alignment, '
            'but not for a clean emergent operator-symbolic language. Explicit state supervision and equivalence regularization '
            'substantially strengthened formal-state alignment and path invariance. Random-feature, lexical, and causal-intervention '
            'controls reject the stronger claim that answer-only training produced a coherent, causally manipulable symbolic operator algebra.'
        ),
        'claim_boundary':(
            'This controlled pilot supports partial operator-relevant representation formation under generated sentence pressure. '
            'It does not establish spontaneous OSL emergence, open-ended symbol formation, or the same effect in large language models.'
        ),
        'deterministic_metric_replay':recheck['exact_metric_replay'],
    }
    summary['digest']=hashlib.sha256(json.dumps(summary,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    (root/'results/FINAL_ADJUDICATION.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')

    # Human-readable report.
    def pct(v): return f'{100*v:.2f}%'
    lines=[]
    lines.append('# OSL Emergent Operator Geometry Pilot v0.6')
    lines.append('')
    lines.append('## Final adjudication')
    lines.append('')
    lines.append('**Result:** Partial operator-relevant structure, but not a spontaneously formed formal OSL-like language.')
    lines.append('')
    lines.append('The predeclared frozen suite passed 8 of 8 endpoints. Stronger post-outcome controls then showed that two initially positive diagnostics—linear state probing and affine transition prediction—were largely explained by random recurrent features and surface lexical structure. The final conclusion is therefore narrower than the frozen endpoint count alone.')
    lines.append('')
    lines.append('## Behavioral generalization')
    lines.append('')
    lines.append('| System | ID | Long composition | Held-out syntax | Combined OOD | Long chain |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    rows=[
        ('Query-type majority', frozen['baselines']['query_type_majority']),
        ('TF-IDF bigram', frozen['baselines']['tfidf_bigram']),
    ]
    for a in arm_labels:
        rows.append((arm_labels[a], {s:frozen['aggregate'][a][f'splits.{s}.answer_accuracy']['mean'] for s in splits}))
    for label,row in rows:
        lines.append('| '+label+' | '+' | '.join(pct(row[s]) for s in splits)+' |')
    lines.append('')
    lines.append('Sentence-only training beat the per-query majority baseline on every split. It beat TF-IDF on held-out syntax and the combined long-plus-syntax split, but TF-IDF remained stronger in-distribution, on long composition alone, and on explicit communication chains. This is evidence for some sequence-sensitive generalization, not a decisive symbolic-emergence result.')
    lines.append('')
    lines.append('![Answer accuracy](answer_accuracy.png)')
    lines.append('')
    lines.append('## Formal-state geometry')
    lines.append('')
    lines.append('| Representation | Linear CKA | RSA Spearman | Equivalent-path top-1 | MRR |')
    lines.append('|---|---:|---:|---:|---:|')
    for key,label in [('random_untrained','Random untrained'),('answer_only','Answer only'),('state_supervised','State supervised'),('operator_regularized','Operator regularized')]:
        rec=geom['summary'][key]
        lines.append(f"| {label} | {rec['cka']['mean']:.4f} | {rec['rsa']['mean']:.4f} | {pct(rec['retrieval_top1']['mean'])} | {rec['retrieval_mrr']['mean']:.4f} |")
    lines.append('')
    lines.append('Answer-only training raised linear CKA above the untrained architecture, but its RSA correlation with formal state remained approximately zero. Explicit state supervision produced a much larger alignment. Operator regularization yielded the best equivalent-path retrieval, indicating that the quotient-style loss successfully compressed different derivations of the same executable state.')
    lines.append('')
    lines.append('![Formal-state CKA](formal_state_cka.png)')
    lines.append('')
    lines.append('![Equivalent-path retrieval](equivalence_retrieval.png)')
    lines.append('')
    lines.append('## Controls that changed the interpretation')
    lines.append('')
    lines.append('| Probe | Status balanced accuracy | Origin balanced accuracy |')
    lines.append('|---|---:|---:|')
    lines.append(f"| Random untrained recurrent features | {pct(controls['random_aggregate']['status_balanced_probe']['mean'])} | {pct(controls['random_aggregate']['origin_balanced_probe']['mean'])} |")
    lines.append(f"| TF-IDF story features | {pct(controls['tfidf_state_probe']['status_balanced_accuracy'])} | {pct(controls['tfidf_state_probe']['origin_balanced_accuracy'])} |")
    for a in arm_labels:
        lines.append(f"| {arm_labels[a]} | {pct(frozen['aggregate'][a]['linear_probe.linear_probe_status_balanced_accuracy']['mean'])} | {pct(frozen['aggregate'][a]['linear_probe.linear_probe_origin_balanced_accuracy']['mean'])} |")
    lines.append('')
    lines.append('Random untrained features and TF-IDF features matched or exceeded the trained latent probes. Therefore linear decodability alone does not show that the model learned the provenance algebra.')
    lines.append('')
    lines.append(f"The fitted affine transition metric was even more diagnostic of the problem: untrained recurrent features obtained R² = {controls['random_aggregate']['affine_transition_r2']['mean']:.4f}, compared with {frozen['aggregate']['answer_only']['transition_geometry.affine_transition_r2']['mean']:.4f} after answer-only training. The metric primarily measured the recurrent architecture, not learned operator semantics.")
    lines.append('')
    lines.append('![Probe controls](probe_controls.png)')
    lines.append('')
    lines.append('## Causal steering')
    lines.append('')
    lines.append('| Arm | Probe-direction status flip | Random-direction status flip | Coherent conversion |')
    lines.append('|---|---:|---:|---:|')
    for a in arm_labels:
        rec=sweep['summary'][a]
        lines.append(f"| {arm_labels[a]} | {pct(rec['targeted_flip_rate']['mean'])} | {pct(rec['random_flip_rate']['mean'])} | {pct(rec['targeted_coherent_rate']['mean'])} |")
    lines.append('')
    lines.append('State-supervised and operator-regularized models showed somewhat higher status-output flips along probe-defined directions than along random directions. However, complete coherent conversion across status, direct-observation, safe-write, knowledge, and origin queries remained near 1% and was not reliably above the random control. This fails the stronger causal-symbol hypothesis.')
    lines.append('')
    lines.append('![Intervention sweep](intervention_sweep.png)')
    lines.append('')
    lines.append('## What arose and what did not')
    lines.append('')
    lines.append('### Supported')
    lines.append('')
    lines.append('- Generated sentence worlds can train a small recurrent model to perform provenance-sensitive reasoning above majority baselines and to generalize modestly to longer and syntactically rearranged stories.')
    lines.append('- Answer-only training changes latent geometry relative to an untrained network, including weak formal-state CKA and improved equivalent-path retrieval.')
    lines.append('- Explicit formal-state supervision sharply strengthens alignment with the executable state.')
    lines.append('- Algebraic equivalence regularization further strengthens path invariance and modestly improves several OOD answer splits.')
    lines.append('')
    lines.append('### Not supported')
    lines.append('')
    lines.append('- Linear probe decodability is not evidence of learned symbolic state in this setup; random and lexical features explain it.')
    lines.append('- Affine latent transition predictability is not evidence of learned operators; the untrained recurrent architecture scores higher.')
    lines.append('- The probe-defined provenance direction does not causally implement a coherent observed-versus-communicated operator in the answer head.')
    lines.append('- The experiment does not show open-ended symbol discovery or a naturally emergent OSL language.')
    lines.append('')
    lines.append('## Next decisive experiment')
    lines.append('')
    lines.append('The next study should freeze the random-feature and lexical controls in advance, hold out entire algebra generators rather than only longer compositions, use architecture-independent causal interventions, require systematic zero-shot recombination, and compare recurrent, transformer, state-space, and explicit symbolic baselines. A stronger criterion would require causal edits that change all logically implied answers while preserving unrelated content.')
    lines.append('')
    lines.append('## Reproducibility')
    lines.append('')
    lines.append(f"- Pre-outcome freeze: `{freeze['digest']}`")
    lines.append(f"- Frozen analysis: `{frozen['digest']}`")
    lines.append(f"- Final adjudication: `{summary['digest']}`")
    lines.append(f"- Deterministic metric replay: `{recheck['exact_metric_replay']}`")
    lines.append('')
    lines.append('## Claim boundary')
    lines.append('')
    lines.append(summary['claim_boundary'])
    (root/'results/FINAL_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'summary_digest':summary['digest'],'report':str(root/'results/FINAL_REPORT.md')},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
