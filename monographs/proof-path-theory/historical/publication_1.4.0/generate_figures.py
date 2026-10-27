
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import networkx as nx
import numpy as np

from proof_path_theory import (
    BridgeGraph,
    Representation,
    TaskRequirement,
    compression_report,
    effective_reviewer_count,
    equicorrelated_covariance,
    exact_cardinality_retention,
    greedy_cardinality_retention,
    load_proof_field,
    optimal_depth,
    simulate_audit_queue,
    unique_and_dag_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / 'docs' / 'figures'
DATA = ROOT / 'data'
FIGURES.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

TEAL = '#285A50'
TEAL_DARK = '#1E3430'
TEAL_LIGHT = '#BFD7D0'
GOLD = '#B57F2A'
GOLD_LIGHT = '#E9D6A7'
SLATE = '#62716B'
PAPER = '#F5F2E9'
MINT = '#EAF0ED'
ROSE = '#D98673'
ROSE_LIGHT = '#F2D7D1'
BLUE = '#4C6A92'
BLUE_LIGHT = '#D7E2F0'
LINE = '#7A867F'

plt.rcParams.update(
    {
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 10,
        'legend.fontsize': 9,
        'figure.dpi': 160,
        'savefig.dpi': 220,
        'savefig.bbox': 'tight',
        'axes.facecolor': PAPER,
        'figure.facecolor': PAPER,
        'font.family': 'DejaVu Sans',
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f'{stem}.pdf', facecolor=fig.get_facecolor())
    fig.savefig(FIGURES / f'{stem}.png', facecolor=fig.get_facecolor())
    plt.close(fig)


def decorate(ax, title: str, subtitle: str | None = None) -> None:
    ax.set_facecolor(PAPER)
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor=PAPER, edgecolor='none', zorder=-20))
    ax.add_patch(Rectangle((0, 0.97), 1, 0.03, transform=ax.transAxes, facecolor=TEAL, edgecolor='none', zorder=-10))
    ax.text(0.0, 1.045, title, transform=ax.transAxes, ha='left', va='bottom', fontsize=14, fontweight='bold', color=TEAL_DARK)
    if subtitle:
        ax.text(0.0, 1.005, subtitle, transform=ax.transAxes, ha='left', va='top', fontsize=9.2, color=SLATE)


def card(ax, xy, width, height, text, *, fc='white', ec=LINE, lw=1.2, fontsize=9.5, rounding=0.04, textcolor=TEAL_DARK, z=2):
    patch = FancyBboxPatch(xy, width, height, boxstyle=f'round,pad=0.02,rounding_size={rounding}',
                           facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha='center', va='center', fontsize=fontsize, color=textcolor, zorder=z+1)
    return patch


def arrow(ax, start, end, *, color=LINE, linewidth=1.5, connectionstyle='arc3', rad=None, z=3):
    if rad is not None:
        connectionstyle = f'arc3,rad={rad}'
    patch = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=13,
                            linewidth=linewidth, color=color, connectionstyle=connectionstyle, zorder=z)
    ax.add_patch(patch)
    return patch


def chip(ax, x, y, text, *, fc=MINT, ec=TEAL, color=TEAL_DARK):
    card(ax, (x, y), 1.45, 0.34, text, fc=fc, ec=ec, lw=1.0, fontsize=8.3, rounding=0.07, textcolor=color)


def theory_map() -> None:
    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.set_xlim(0, 10.6); ax.set_ylim(0, 4.6); ax.axis('off')
    decorate(ax, 'Theory at a glance', 'The monograph moves from proof fields to realization, compression, collective interpretation, and executable records.')
    xs = [0.2, 2.22, 4.24, 6.26, 8.28]
    labels = [
        ('Proof field', 'claims, justifications,\nfailed routes, scope'),
        ('Coherent realization', 'local models, gluing,\nobstruction, ambiguity'),
        ('Compression', 'task sufficiency,\nloss, debt, retention'),
        ('Collective interpretation', 'revision, correlated review,\naudit capacity, queues'),
        ('Executable record', 'examples, software,\nformal interfaces, boundaries'),
    ]
    colors = [MINT, '#DDE9E5', '#EFE5D1', '#E6ECF4', '#F0DDD8']
    edgecolors = [TEAL, TEAL, GOLD, BLUE, ROSE]
    for i, (x, (title, body)) in enumerate(zip(xs, labels)):
        card(ax, (x, 1.15), 1.75, 2.15, '', fc=colors[i], ec=edgecolors[i], lw=1.4, rounding=0.06)
        ax.text(x+0.18, 2.95, title, ha='left', va='center', fontsize=11.2, fontweight='bold', color=TEAL_DARK)
        ax.text(x+0.18, 2.28, body, ha='left', va='top', fontsize=9.0, color=SLATE)
        ax.add_patch(Rectangle((x+0.18, 2.72), 1.1, 0.03, facecolor=edgecolors[i], edgecolor='none'))
        if i < len(xs)-1:
            arrow(ax, (x+1.79, 2.22), (xs[i+1]-0.06, 2.22), color=edgecolors[i])
    ax.text(5.3, 0.42, 'Every stage preserves logical scope while exposing a different part of the mathematical record.', ha='center', color=SLATE, fontsize=9.2)
    save(fig, 'fig_00_theory_map')


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 5.0))
    ax.set_xlim(0, 10.2); ax.set_ylim(0, 5.0); ax.axis('off')
    decorate(ax, 'Proof Path Theory as an integrated architecture', 'The certificate is one verified projection of a larger, versioned proof field.')
    card(ax, (0.3, 2.85), 1.8, 1.05, 'Typed proof field\nclaims, rules, evidence', fc=MINT, ec=TEAL, lw=1.4)
    card(ax, (2.55, 2.85), 1.45, 1.05, 'Certified\nsubfield', fc='white', ec=TEAL, lw=1.4)
    card(ax, (4.35, 2.85), 1.6, 1.05, 'Certificate and\ncompression', fc='#F8F2E3', ec=GOLD, lw=1.4)
    card(ax, (6.35, 2.85), 1.8, 1.05, 'Bridges and\nmathematical memory', fc='#E8EEF6', ec=BLUE, lw=1.4)
    card(ax, (8.55, 1.15), 1.2, 1.0, 'Compiled\nartifact', fc='white', ec=TEAL, lw=1.4)
    card(ax, (5.55, 1.15), 1.85, 1.0, 'Review, provenance,\naudit capacity', fc='#F4E3DE', ec=ROSE, lw=1.4)
    card(ax, (2.85, 1.15), 1.9, 1.0, 'Tasks, loss, debt,\nrecoverability', fc='#F8F2E3', ec=GOLD, lw=1.4)
    for s,e,c in [((2.13,3.37),(2.53,3.37),TEAL),((4.02,3.37),(4.33,3.37),TEAL),((5.98,3.37),(6.33,3.37),GOLD)]:
        arrow(ax, s,e,color=c)
    arrow(ax, (5.1,2.85), (3.8,2.15), color=GOLD, rad=0.18)
    arrow(ax, (7.1,2.85), (6.55,2.15), color=BLUE, rad=-0.1)
    arrow(ax, (8.1,2.85), (9.15,2.15), color=TEAL, rad=-0.08)
    arrow(ax, (4.8,1.65), (5.52,1.65), color=SLATE)
    arrow(ax, (7.43,1.65), (8.52,1.65), color=SLATE)
    chip(ax, 0.45, 0.35, 'validity')
    chip(ax, 2.15, 0.35, 'realization', fc='#F8F2E3', ec=GOLD)
    chip(ax, 3.85, 0.35, 'compression', fc='#F8F2E3', ec=GOLD)
    chip(ax, 5.55, 0.35, 'review', fc='#F4E3DE', ec=ROSE)
    chip(ax, 7.25, 0.35, 'implementation', fc=MINT, ec=TEAL)
    save(fig, 'fig_01_architecture')


def and_dag_core() -> None:
    field = load_proof_field(ROOT / 'examples' / 'and_dag.json')
    certificate = unique_and_dag_certificate(field)
    graph = nx.DiGraph(); graph.add_nodes_from(field.nodes); graph.add_edges_from(field.dependency_edges())
    pos = {'A': (0.2, 0), 'D': (1.8, 0), 'L1': (3.4, 0), 'L2': (5.0, 0), 'B': (6.6, 0), 'E': (2.6, -1.5), 'C': (4.2, -1.5), 'F': (1.0, 1.5)}
    fig, ax = plt.subplots(figsize=(9.1, 4.8))
    ax.axis('off'); decorate(ax, 'Least certificate in a fixed AND-DAG', 'The core closure is forced once the target and admitted leaves are fixed.')
    nx.draw_networkx_edges(graph, pos, ax=ax, arrows=True, arrowstyle='-|>', arrowsize=15, width=1.3, edge_color=LINE)
    core = list(certificate.node_ids)
    optional = [node_id for node_id in graph.nodes if node_id not in certificate.node_ids]
    nx.draw_networkx_nodes(graph, pos, nodelist=core, node_size=1850, node_shape='o', edgecolors=TEAL_DARK, linewidths=1.5, node_color=TEAL_LIGHT, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=optional, node_size=1850, node_shape='s', edgecolors=GOLD, linewidths=1.4, node_color=GOLD_LIGHT, ax=ax)
    nx.draw_networkx_labels(graph, pos, labels={node_id: field.nodes[node_id].label for node_id in graph.nodes}, font_size=8.6, font_color=TEAL_DARK, ax=ax)
    card(ax, (0.2, -2.25), 2.3, 0.55, 'Circles = forced certificate core', fc=MINT, ec=TEAL, fontsize=8.8)
    card(ax, (3.0, -2.25), 2.5, 0.55, 'Squares = optional discovery material', fc='#F8F2E3', ec=GOLD, fontsize=8.8)
    save(fig, 'fig_02_and_dag_core')


def alternative_hypergraph() -> None:
    fig, ax = plt.subplots(figsize=(8.9, 4.9))
    ax.set_xlim(0, 8.9); ax.set_ylim(0, 4.9); ax.axis('off')
    decorate(ax, 'Alternative justifications', 'Each rule is conjunctive in its premises, while multiple rules provide OR alternatives.')
    card(ax, (0.4, 1.95), 1.2, 0.7, 'Premise A', fc=MINT, ec=TEAL)
    card(ax, (2.2, 3.15), 1.55, 0.7, 'Short lemma', fc='white', ec=TEAL)
    card(ax, (2.2, 0.85), 1.55, 0.7, 'Rich lemma', fc='#FFF9EF', ec=GOLD)
    card(ax, (7.05, 1.95), 1.1, 0.7, 'Goal B', fc=MINT, ec=TEAL)
    for x, y, label, col in [(1.82,3.35,'j₁',TEAL),(1.82,1.05,'j₂',GOLD),(5.78,3.35,'j₃',TEAL),(5.78,1.05,'j₄',GOLD)]:
        card(ax, (x-0.18,y-0.18), 0.36, 0.36, label, fc='white', ec=col, lw=1.3, fontsize=8.5, rounding=0.05)
    arrow(ax, (1.6,2.28), (1.82,3.17), color=TEAL)
    arrow(ax, (1.6,2.28), (1.82,1.23), color=GOLD)
    arrow(ax, (2.0,3.35), (2.2,3.5), color=TEAL)
    arrow(ax, (2.0,1.05), (2.2,1.2), color=GOLD)
    arrow(ax, (3.75,3.5), (5.6,3.35), color=TEAL)
    arrow(ax, (3.75,1.2), (5.6,1.05), color=GOLD)
    arrow(ax, (5.96,3.35), (7.05,2.3), color=TEAL)
    arrow(ax, (5.96,1.05), (7.05,2.0), color=GOLD)
    card(ax, (0.45, 0.1), 2.2, 0.52, 'Top route: shorter certificate', fc='#EAF6F2', ec=TEAL, fontsize=8.8)
    card(ax, (3.05, 0.1), 2.5, 0.52, 'Bottom route: richer retained information', fc='#FFF6E8', ec=GOLD, fontsize=8.8)
    save(fig, 'fig_03_alternative_hypergraph')


def set_cover_complexity() -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.set_xlim(0, 9.7); ax.set_ylim(0, 5.7); ax.axis('off')
    decorate(ax, 'Why minimum certificates with alternatives are hard', 'Selecting optional lemmas that cover every obligation reproduces Set Cover.')
    sets = {'S1': ('u1','u2'), 'S2': ('u2','u3'), 'S3': ('u3','u4'), 'S4': ('u1','u4')}
    sy = {'S1':4.5,'S2':3.45,'S3':2.4,'S4':1.35}
    ey = {'u1':4.5,'u2':3.45,'u3':2.4,'u4':1.35}
    for name, y in sy.items(): card(ax, (0.5, y-0.25), 1.15, 0.5, name, fc=GOLD_LIGHT, ec=GOLD)
    for name, y in ey.items(): card(ax, (4.1, y-0.25), 1.05, 0.5, name, fc='white', ec=LINE)
    card(ax, (8.0, 2.45), 1.1, 0.6, 'Target T', fc=MINT, ec=TEAL)
    for s, els in sets.items():
        for e in els:
            arrow(ax, (1.65, sy[s]), (4.1, ey[e]), color=GOLD, linewidth=1.0)
    for e,y in ey.items():
        arrow(ax, (5.15, y), (8.0, 2.75), color=TEAL, linewidth=1.0)
    card(ax, (2.7, 0.35), 4.0, 0.62, 'A certificate must choose enough source lemmas to discharge every element obligation.', fc='white', ec=LINE, fontsize=8.8)
    save(fig, 'fig_04_certificate_complexity')


def recoverability_preorder() -> None:
    fig, ax = plt.subplots(figsize=(8.9, 5.2))
    ax.set_xlim(0, 9); ax.set_ylim(0, 6); ax.axis('off')
    decorate(ax, 'Task-relative recoverability', 'Different views can preserve different future capabilities even when they verify the same theorem.')
    coords = {'archive':(3.45,4.9),'discovery':(0.9,3.15),'teaching':(3.45,3.15),'formal':(6.0,3.15),'journal':(3.45,1.5),'certificate':(3.45,0.2)}
    labels = {'archive':'Canonical\narchive','discovery':'Discovery\nview','teaching':'Teaching\nview','formal':'Formal\nview','journal':'Journal\nview','certificate':'Minimal\ncertificate'}
    palettes = {'archive':(MINT,TEAL),'discovery':('#FFF6E8',GOLD),'teaching':('#EAF6F2',TEAL),'formal':('#E6ECF4',BLUE),'journal':('white',LINE),'certificate':('#F5ECEA',ROSE)}
    for key,(x,y) in coords.items():
        fc,ec=palettes[key]; card(ax,(x,y),1.5,0.7,labels[key],fc=fc,ec=ec,lw=1.3)
    edges=[('discovery','archive'),('teaching','archive'),('formal','archive'),('journal','discovery'),('journal','teaching'),('journal','formal'),('certificate','journal')]
    for lower, upper in edges:
        lx,ly=coords[lower]; ux,uy=coords[upper]
        arrow(ax,(lx+0.75,ly+0.7),(ux+0.75,uy),color=SLATE,linewidth=1.1)
    save(fig, 'fig_05_recoverability_preorder')


def loss_vectors() -> None:
    field = load_proof_field(ROOT / 'examples' / 'and_dag.json')
    certificate = unique_and_dag_certificate(field)
    representation = Representation('certificate', certificate.node_ids, certificate=certificate)
    tasks = (
        TaskRequirement('verify', certificate.node_ids, probability=0.5),
        TaskRequirement('teach', frozenset({'E'}), probability=0.2),
        TaskRequirement('extend', frozenset({'F', 'C'}), probability=0.3),
    )
    report = compression_report(field, representation, tasks=tasks)
    names = list(report.retained_values.as_dict())
    retained = [report.retained_values.as_dict()[name] for name in names]
    lost = [report.loss_values.as_dict()[name] for name in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    decorate(ax, 'Value retained and value lost', 'A representation can be perfect for verification and still lose discovery or teaching value.')
    ax.bar(x, retained, color=TEAL_LIGHT, edgecolor=TEAL, width=0.58, label='retained')
    ax.bar(x, lost, bottom=retained, color=GOLD_LIGHT, edgecolor=GOLD, width=0.58, label='lost')
    ax.set_xticks(x, [name.capitalize() for name in names], rotation=12)
    ax.set_ylabel('Declared value units')
    ax.grid(axis='y', alpha=0.2, color=LINE)
    ax.legend(frameon=False)
    for xi,r,l in zip(x,retained,lost):
        ax.text(xi, r/2, f'{r:.1f}', ha='center', va='center', fontsize=8.4, color=TEAL_DARK)
        if l > 0:
            ax.text(xi, r+l/2, f'{l:.1f}', ha='center', va='center', fontsize=8.4, color=TEAL_DARK)
    save(fig, 'fig_06_loss_vectors')


def bridge_dominators() -> None:
    graph = nx.DiGraph()
    graph.add_edges_from([('Archive','Example'),('Archive','Failed route'),('Example','Boundary theorem'),('Failed route','Boundary theorem'),('Boundary theorem','Future A'),('Boundary theorem','Future B'),('Example','Future C')])
    pos = {'Archive':(0,0),'Example':(1.7,1.1),'Failed route':(1.7,-1.1),'Boundary theorem':(3.6,0),'Future A':(5.6,1.3),'Future B':(5.6,0),'Future C':(5.6,-1.3)}
    fig, ax = plt.subplots(figsize=(8.6, 4.7)); ax.axis('off')
    decorate(ax, 'Bridge criticality', 'A retained item is mathematically important when removing it destroys many future routes.')
    nx.draw_networkx_edges(graph,pos,ax=ax,arrows=True,arrowsize=15,width=1.25,edge_color=LINE)
    nx.draw_networkx_nodes(graph,pos,nodelist=['Boundary theorem'],node_shape='s',node_size=2400,edgecolors=BLUE,linewidths=1.8,node_color=BLUE_LIGHT,ax=ax)
    nx.draw_networkx_nodes(graph,pos,nodelist=[n for n in graph if n!='Boundary theorem'],node_size=1800,edgecolors=LINE,linewidths=1.2,node_color='white',ax=ax)
    label_map={n:n.replace('Boundary theorem','Boundary\ntheorem') for n in graph}
    nx.draw_networkx_labels(graph,pos,labels=label_map,font_size=8.5,font_color=TEAL_DARK,ax=ax)
    card(ax,(1.75,-2.1),3.7,0.58,'Removing the square node destroys every route to Future A and Future B.',fc='white',ec=LINE,fontsize=8.8)
    save(fig, 'fig_07_bridge_dominators')


def submodular_greedy() -> None:
    rng = np.random.default_rng(17)
    candidates=[f'c{i}' for i in range(10)]
    targets=[f't{i}' for i in range(16)]
    edges=[]
    for candidate in candidates:
        chosen=rng.choice(targets,size=rng.integers(3,8),replace=False)
        edges.extend((candidate,target) for target in chosen)
    graph=BridgeGraph(candidates+targets,edges)
    weights={target:float(rng.uniform(0.5,2.0)) for target in targets}
    budgets=range(0,6)
    greedy_values=[]; exact_values=[]; rows=[]
    for budget in budgets:
        greedy=greedy_cardinality_retention(graph,candidates,weights,budget=budget)
        exact=exact_cardinality_retention(graph,candidates,weights,budget=budget)
        greedy_values.append(greedy.utility); exact_values.append(exact.utility)
        rows.append((budget, greedy.utility, exact.utility, ','.join(greedy.retained), ','.join(exact.retained)))
    with (DATA/'retention_comparison.csv').open('w',newline='',encoding='utf-8') as handle:
        w=csv.writer(handle); w.writerow(['budget','greedy_utility','exact_utility','greedy_nodes','exact_nodes']); w.writerows(rows)
    fig, ax = plt.subplots(figsize=(7.9,4.8))
    decorate(ax, 'Greedy bridge retention', 'On this finite example, the submodular greedy rule closely tracks the exact optimum.')
    ax.plot(list(budgets), exact_values, marker='s', linestyle='--', color=BLUE, label='exact optimum')
    ax.plot(list(budgets), greedy_values, marker='o', color=TEAL, label='greedy rule')
    ax.fill_between(list(budgets), greedy_values, exact_values, color=BLUE_LIGHT, alpha=0.45)
    ax.set_xlabel('Retention budget'); ax.set_ylabel('Weighted future reach'); ax.grid(alpha=0.2, color=LINE); ax.legend(frameon=False)
    save(fig, 'fig_08_submodular_greedy')


def version_invalidation() -> None:
    graph = nx.DiGraph(); graph.add_edges_from([('A','L1'),('D','L1'),('L1','L2'),('L2','B'),('D','Example'),('Example','Boundary')])
    pos={'A':(0,1),'D':(0,-1),'L1':(2,0.6),'L2':(3.8,0.6),'B':(5.6,0.6),'Example':(2,-1.0),'Boundary':(3.8,-1.0)}
    affected={'L1','L2','B'}
    fig, ax = plt.subplots(figsize=(8.7,4.5)); ax.axis('off')
    decorate(ax, 'Version invalidation and review closure', 'A changed claim marks the forward dependency closure for renewed checking.')
    nx.draw_networkx_edges(graph,pos,arrows=True,arrowsize=15,width=1.2,edge_color=LINE,ax=ax)
    nx.draw_networkx_nodes(graph,pos,nodelist=list(affected),node_shape='s',node_size=1750,edgecolors=ROSE,linewidths=1.7,node_color=ROSE_LIGHT,ax=ax)
    nx.draw_networkx_nodes(graph,pos,nodelist=[n for n in graph if n not in affected],node_size=1750,edgecolors=LINE,linewidths=1.1,node_color='white',ax=ax)
    nx.draw_networkx_labels(graph,pos,font_size=9,font_color=TEAL_DARK,ax=ax)
    card(ax,(0.05,1.55),1.9,0.5,'Changed claim',fc=MINT,ec=TEAL,fontsize=8.6)
    card(ax,(2.75,-1.85),3.35,0.55,'The separate branch is untouched because no dependency path reaches it.',fc='white',ec=LINE,fontsize=8.6)
    save(fig, 'fig_09_version_invalidation')


def effective_reviewers() -> None:
    n_values=np.arange(1,101); correlations=[0.0,0.05,0.10,0.25]; rows=[]
    fig, ax = plt.subplots(figsize=(8.1,4.9))
    decorate(ax, 'Effective reviewer count under shared dependence', 'Agreement grows less informative when reviewers share systematic error.')
    palette=[TEAL, BLUE, GOLD, ROSE]
    for correlation, color in zip(correlations,palette):
        counts=[]
        for n in n_values:
            covariance=equicorrelated_covariance(int(n),1.0,correlation)
            count=effective_reviewer_count(covariance)
            counts.append(count); rows.append((int(n),correlation,count))
        ax.plot(n_values, counts, label=fr'$\rho={correlation:.2f}$', color=color, linewidth=2)
    with (DATA/'effective_reviewer_count.csv').open('w',newline='',encoding='utf-8') as handle:
        w=csv.writer(handle); w.writerow(['nominal_reviewers','pairwise_correlation','effective_reviewers']); w.writerows(rows)
    ax.set_xlabel('Nominal reviewers'); ax.set_ylabel('Effective independent reviewers'); ax.grid(alpha=0.22, color=LINE); ax.legend(frameon=False)
    save(fig, 'fig_10_effective_reviewers')


def audit_queues() -> None:
    steps=np.arange(40)
    stable=simulate_audit_queue(np.full(40,4.0),np.full(40,5.0),initial_backlog=10.0)
    critical=simulate_audit_queue(np.full(40,5.0),np.full(40,5.0),initial_backlog=10.0)
    unstable=simulate_audit_queue(np.full(40,6.0),np.full(40,5.0),initial_backlog=10.0)
    with (DATA/'audit_queue.csv').open('w',newline='',encoding='utf-8') as handle:
        w=csv.writer(handle); w.writerow(['step','stable','critical','unstable'])
        for i in steps: w.writerow([i, stable.backlog[i], critical.backlog[i], unstable.backlog[i]])
    fig, ax = plt.subplots(figsize=(8.1,4.8))
    decorate(ax, 'Audit queues', 'The backlog stays controlled, stalls, or diverges depending on whether arrivals stay below capacity.')
    ax.plot(steps, stable.backlog, label='stable', color=TEAL, linewidth=2)
    ax.plot(steps, critical.backlog, label='critical', color=GOLD, linewidth=2)
    ax.plot(steps, unstable.backlog, label='unstable', color=ROSE, linewidth=2)
    ax.set_xlabel('Audit cycle'); ax.set_ylabel('Unaudited backlog'); ax.grid(alpha=0.22, color=LINE); ax.legend(frameon=False)
    save(fig, 'fig_11_audit_queues')


def refinement_goals() -> None:
    residuals=np.array([1.0,0.55,0.30,0.18,0.12,0.09,0.075])
    costs=np.array([0.0,0.25,0.65,1.2,2.1,3.5,5.5])
    goals={'certificate':(1.0,0.75,TEAL),'teaching':(2.5,0.35,GOLD),'archive':(5.0,0.15,BLUE)}
    fig, ax = plt.subplots(figsize=(8.0,4.9))
    decorate(ax, 'Goal-relative expansion depth', 'Different tasks prefer different stopping depths in the same ambient proof field.')
    rows=[]
    for name,(rw,cw,color) in goals.items():
        objective=rw*residuals + cw*costs
        depth=optimal_depth(residuals,costs,residual_weight=rw,cost_weight=cw)
        rows.append((name,rw,cw,depth,objective[depth]))
        ax.plot(range(len(residuals)), objective, marker='o', color=color, label=f'{name}: depth {depth}')
        ax.scatter([depth],[objective[depth]],s=80,marker='s',color=color,edgecolor=TEAL_DARK)
    with (DATA/'refinement_depths.csv').open('w',newline='',encoding='utf-8') as handle:
        w=csv.writer(handle); w.writerow(['goal','residual_weight','cost_weight','optimal_depth','objective']); w.writerows(rows)
    ax.set_xlabel('Expansion depth'); ax.set_ylabel('Goal-relative objective'); ax.grid(alpha=0.22, color=LINE); ax.legend(frameon=False)
    save(fig, 'fig_12_refinement_goals')


def workflow() -> None:
    fig, ax = plt.subplots(figsize=(11.1, 5.1))
    ax.set_xlim(0,12); ax.set_ylim(0,5.1); ax.axis('off')
    decorate(ax, 'Repository workflow', 'The release is organized as an inspectable chain from canonical records to compiled artifacts.')
    stage_x=[0.25,2.55,4.85,7.15,9.45]; stage_w=1.8; stage_y=2.9; stage_h=1.0
    stage_labels=['Canonical JSON\nproof field','Validate schema,\nreferences, acyclicity','Extract core or\nexact minimum certificate','Audit loss, bridges,\nand provenance','Compile the\ntarget artifact']
    stage_fcs=[MINT,'white','#FFF6E8','#E6ECF4','white']; stage_ecs=[TEAL,TEAL,GOLD,BLUE,TEAL]
    for x,lbl,fc,ec in zip(stage_x,stage_labels,stage_fcs,stage_ecs): card(ax,(x,stage_y),stage_w,stage_h,lbl,fc=fc,ec=ec,lw=1.35,fontsize=8.5)
    for left,right,ec in zip(stage_x,stage_x[1:], [TEAL,TEAL,GOLD,BLUE]): arrow(ax,(left+stage_w+0.05,stage_y+stage_h/2),(right-0.05,stage_y+stage_h/2),color=ec)
    support_labels=['Theorem and\nstatus ledger','Tests and exact\nfinite examples','Figures, tables, and\nmachine records']
    support_y=0.8
    for x,label,ec in zip(stage_x[1:4],support_labels,[TEAL,GOLD,BLUE]):
        card(ax,(x,support_y),stage_w,0.9,label,fc='white',ec=ec,lw=1.2,fontsize=8.5)
        center=x+stage_w/2; arrow(ax,(center,support_y+0.92),(center,stage_y-0.05),color=ec)
    save(fig, 'fig_13_repository_workflow')


def ambient_field() -> None:
    fig, ax = plt.subplots(figsize=(9.3, 4.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.2); ax.axis('off')
    decorate(ax, 'Ambient proof field', 'A certified route and a locally blocked route can coexist inside the same declared proof field.')
    card(ax, (0.25, 0.55), 11.5, 2.95, '', fc='white', ec=LINE, lw=1.1, rounding=0.06)
    ax.add_patch(Rectangle((0.55,2.1), 10.9, 1.05, facecolor='#EEF7F3', edgecolor='none'))
    ax.add_patch(Rectangle((0.55,0.95), 10.9, 0.85, facecolor='#FFF4EA', edgecolor='none'))
    card(ax,(0.85,2.3),1.7,0.52,'Premise',fc='white',ec=LINE)
    card(ax,(4.1,2.3),1.85,0.52,'Certified lemma',fc=MINT,ec=TEAL)
    card(ax,(7.9,2.3),1.7,0.52,'Verified goal',fc=MINT,ec=TEAL)
    card(ax,(4.1,1.12),1.85,0.52,'Uncertified step',fc='#FFF8EE',ec=GOLD)
    card(ax,(7.9,1.12),1.95,0.52,'Local obstruction',fc='#F9ECE8',ec=ROSE)
    arrow(ax,(2.55,2.55),(4.1,2.55),color=TEAL)
    arrow(ax,(5.95,2.55),(7.9,2.55),color=TEAL)
    arrow(ax,(2.55,2.25),(4.1,1.38),color=GOLD,rad=0.0)
    arrow(ax,(5.95,1.38),(7.9,1.38),color=ROSE)
    ax.text(10.25, 1.37, 'The goal may still be\nprovable by another route.', ha='left', va='center', fontsize=8.5, color=SLATE)
    chip(ax,0.9,3.15,'certified corridor',fc='#EAF6F2',ec=TEAL)
    chip(ax,2.55,3.15,'blocked corridor',fc='#FFF6E8',ec=GOLD)
    save(fig, 'fig_14_ambient_field')


def write_results() -> None:
    and_field=load_proof_field(ROOT/'examples'/'and_dag.json')
    and_certificate=unique_and_dag_certificate(and_field)
    alt_field=load_proof_field(ROOT/'examples'/'alternative_proofs.json')
    from proof_path_theory import minimum_certificate, certificate_cost
    alt_certificate=minimum_certificate(alt_field)
    payload={'version':'1.4.0','and_dag_core':{'nodes':sorted(and_certificate.node_ids),'justifications':sorted(and_certificate.justification_ids)},'alternative_minimum':{'nodes':sorted(alt_certificate.node_ids),'justifications':sorted(alt_certificate.justification_ids),'cost':certificate_cost(alt_field,alt_certificate)},'figures':15}
    (DATA/'results.json').write_text(json.dumps(payload, indent=2)+'\n',encoding='utf-8')


def main() -> None:
    theory_map(); architecture(); and_dag_core(); alternative_hypergraph(); set_cover_complexity(); recoverability_preorder(); loss_vectors(); bridge_dominators(); submodular_greedy(); version_invalidation(); effective_reviewers(); audit_queues(); refinement_goals(); workflow(); ambient_field(); write_results()


if __name__ == '__main__':
    main()
