#!/usr/bin/env python3
"""Redraw selected retained numerical tables as readable vector figures.

This changes presentation, not measurements. No benchmark is rerun here.
All line segments join recorded samples. Infinite widths are not replaced
by finite values. Run from any directory.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];ENGINE=ROOT/'engine';OUT=ROOT/'book/figures_edition';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':11.5,'axes.labelsize':11.5,'legend.fontsize':9.5,'pdf.fonttype':42})
records=[]
def data(name):return pd.read_csv(ENGINE/name)
def axes():
 fig,ax=plt.subplots(figsize=(6.4,3.3),layout='constrained');ax.spines[['top','right']].set_visible(False);return fig,ax
def save(fig,ax,stem,sources,note=''):
 handles,labels=ax.get_legend_handles_labels()
 if labels:ax.legend(frameon=False)
 fig.savefig(OUT/(stem+'.pdf'),bbox_inches='tight',pad_inches=.06);plt.close(fig)
 records.append({'figure':stem+'.pdf','sources':{s:hashlib.sha256((ENGINE/s).read_bytes()).hexdigest() for s in sources},'note':note,'semantics':'Redrawn retained measurements or algebraic sizing data; not a new execution.'})
def lines(ax,d,x,series):
 for col,label,marker in series:ax.plot(d[x],d[col],marker,label=label,lw=1.5,markersize=4.5)
name='memory_asymptotic_sweep.csv';d=data(name);fig,ax=axes()
for col,label,fmt in [('full_factor_MiB','Full factor','o-'),('stream_kernel_action_MiB','Streamed action','s--'),('tiled_gram_MiB','Tiled Gram','^:')]:ax.plot(d.m,d[col],fmt,label=label,markersize=4.5)
ax.set(xlabel='Total factor columns',ylabel='Binary64 payload (MiB)',yscale='log');ax.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
save(fig,ax,'figure_03_memory_law',[name])
name='partition_invariance.csv';d=data(name);fig,ax=axes();x=np.arange(len(d));ax.bar(x-.18,d.gram_rel_error,.36,label='Gram error');ax.bar(x+.18,d.action_rel_error,.36,label='Action error');ax.set(xticks=x,xticklabels=['Coarse\n4 blocks','Fine\n32 blocks','Irregular\n9 blocks','Singleton\nfront','Permuted\n29 blocks'],ylabel='Relative discrepancy');ax.set_ylim(0,7.5e-16);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));save(fig,ax,'figure_08_partition_invariance',[name])
name='approximate_lightcone_depth.csv';d=data(name);fig,ax=axes();lines(ax,d,'depth',[('actual_difference_norm','Observed difference','o-'),('certified_difference_norm','Transfer bound','s--')]);ax.set(xlabel='Operator depth',ylabel='Difference norm',xticks=d.depth);save(fig,ax,'figure_09_approximate_lightcone_certificate',[name])
name='approximate_lightcone_threshold_sweep.csv';d=data(name).sort_values('retained_fraction');fig,ax=axes();lines(ax,d,'retained_fraction',[('actual_error_frobenius','Observed error','o-'),('certified_error_frobenius','Transfer bound','s--')]);ax.set(xlabel='Fraction of off-diagonal blocks retained',ylabel='Frobenius error');save(fig,ax,'figure_10_threshold_tradeoff',[name])
name='budget_scheduler_large.csv';d=data(name);fig,ax=axes();lines(ax,d,'budget',[('additive_opt_omitted','Additive scheduler','o-'),('refined_omitted','Envelope refinement','s--'),('norm_threshold_omitted','Norm threshold','^:')]);ax.set(xlabel='Query-error budget',ylabel='Omitted phase pairs');ax.ticklabel_format(axis='x',style='sci',scilimits=(-2,2));save(fig,ax,'figure_11_budget_scheduler_comparison',[name])
name='double_buffer_model.csv';d=data(name);fig,ax=axes();x=np.arange(len(d));ax.bar(x-.18,d.single_buffer_ms/1000,.36,label='Single buffer');ax.bar(x+.18,d.double_buffer_ms/1000,.36,label='Double buffer');ax.set(xticks=x,xticklabels=[f'{int(a)} / {int(b)}' for a,b in zip(d.io_ms_per_block,d.compute_ms_per_block)],xlabel='I/O / compute time per block (milliseconds)',ylabel='Model wall time (seconds)');save(fig,ax,'figure_12_double_buffer_model',[name],'Five settings with 64 blocks each. Timing model, not measured hardware speed.')
name='edge_risk_vs_block_norm.csv';d=data(name);fig,ax=axes();ax.scatter(d.block_norm,d.query_risk,s=18);ax.set(xlabel='Phase-block operator norm',ylabel='Query-dependent risk');save(fig,ax,'figure_13_edge_risk_vs_block_norm',[name])
name='certify_after_prune_range_core.csv';d=data(name);fig,ax=axes();ax.plot(d.sample_basis_dim,d.range_residual_over_sigma1,'o-');ax.set(xlabel='Captured sample-space dimension',ylabel='Range residual / leading singular value');save(fig,ax,'figure_15_range_core_certification',[name])
name='trace_cap_vs_weyl.csv';d=data(name);fig,ax=axes();finite=np.isfinite(d.v07_weyl_width_decades);ax.semilogy(d.loc[finite,'basis_dim'],d.loc[finite,'v07_weyl_width_decades'],'o-',label='Coefficientwise Weyl');ax.semilogy(d.basis_dim,d.two_sided_width_decades,'s--',label='Residual moments');ax.set(xlabel='Captured basis dimension',ylabel='Tail-bracket width (decades)');save(fig,ax,'figure_16_trace_moment_vs_weyl',[name],'The first two Weyl widths are infinite and have no finite plotted point.')
name='residual_completion_audit.csv';d=data(name);fig,ax=axes();lines(ax,d,'depth',[('integer_rank_lower','Moment lower bound','o-'),('rank_upper','Complement upper bound','s--'),('actual_residual_rank','Observed residual rank','x:')]);ax.set(xlabel='Krylov depth',ylabel='Residual rank',xticks=d.depth);save(fig,ax,'figure_17_residual_rank_completion',[name])
name='realistic_skat_scenarios.csv';d=data(name);fig,ax=axes();x=np.arange(len(d));ax.bar(x-.18,d['rank'],.36,label='Nonzero rank');ax.bar(x+.18,d.effective_rank,.36,label='Effective rank');names={'gaussian_ld_moderate':'Gaussian\nmoderate','gaussian_ld_strong':'Gaussian\nstrong','copy_ld_strong_fixed':'Copy\nstrong','copy_ld_large_fixed':'Copy\nlarge'};labels=[names.get(s,s.replace('_','\n')) for s in d.scenario];ax.set(xticks=x,xticklabels=labels,ylabel='Rank');save(fig,ax,'figure_18_realistic_ld_effective_rank',[name])
name='realistic_streaming_invariance.csv';d=data(name);fig,ax=axes()
for k,g in d.groupby('scenario',sort=False):ax.plot(g.block_size,g.kernel_relative_error,'o-',label=names.get(k,k).replace('\n',' '))
ax.set(xlabel='Resident column-block width',ylabel='Kernel relative discrepancy');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));save(fig,ax,'figure_19_realistic_streaming_invariance',[name])
name='realistic_deep_tail_accuracy.csv';d=data(name);fig,ax=axes()
for k,g in d.groupby('scenario',sort=False):ax.plot(-g.kcos_log10_p,abs(g.difference_decades),'o',label=names.get(k,k).replace('\n',' '),markersize=4.5)
ax.set(xlabel='Tail depth (−log₁₀ probability)',ylabel='Absolute difference (decades)');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));save(fig,ax,'figure_20_realistic_deep_tail_accuracy',[name])
name='reference_convergence.csv';d=data(name);fig,ax=axes();x=np.arange(len(d));ax.plot(x,d.adaptive_minus_reference_decades,'o-');ax.set(xticks=x,xticklabels=[f'{int(a)} / {int(b)}' for a,b in zip(d.reference_K,d.reference_L)],xlabel='Reference modes / support factor',ylabel='Adaptive minus reference (decades)');save(fig,ax,'figure_21_reference_convergence',[name])
(ROOT/'verification/current_revision/redrawn_figures.json').write_text(json.dumps(records,indent=2)+'\n')
for r in records:print(r['figure'])
