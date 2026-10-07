#!/usr/bin/env python3
"""Relayout archival illustrations; never rerun a scientific computation.

CSV charts use the original decimal fields. Three illustrations whose plotted
vectors were not archived are replaced by recorded audit summaries or
unchanged rounded illustration labels. No hidden samples are reconstructed.
Original images and data under ../engine are read-only provenance inputs.
"""
from pathlib import Path
import csv, hashlib, json, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BASE=Path(__file__).resolve().parent
SOURCE=BASE.parent/'engine'
OUT=BASE/'figures_final'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
 'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,
 'axes.linewidth':.8,'lines.linewidth':1.8,'savefig.dpi':300})
REPORT=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_files=list(SOURCE.glob('*.csv'))+list((SOURCE/'figures_final').glob('*.png'))
source_hashes_before={str(p.relative_to(SOURCE)):sha(p) for p in sorted(source_files)}
def rows(name):
 with (SOURCE/name).open(newline='') as f: return list(csv.DictReader(f))
def nums(data,key): return np.array([float(r[key]) for r in data])
def record(name,method,inputs=(),series=(),extra=None):
 item={'file':name,'method':method,'original_sha256':sha(SOURCE/'figures_final'/name),
       'derivative_sha256':sha(OUT/name),'inputs':[{'file':n,'sha256':sha(SOURCE/n)} for n in inputs],
       'plotted_series':series,'scientific_computation_rerun':False}
 if extra: item.update(extra)
 REPORT.append(item)
def setup(title,note=''):
 fig=plt.figure(figsize=(8,5.7))
 ax=fig.add_axes([.14,.27,.82,.52])
 fig.text(.52,.965,'\n'.join(textwrap.wrap(title,78)),ha='center',va='top',fontsize=13.5)
 if note: fig.text(.14,.065,note,ha='left',va='bottom',fontsize=10.2,linespacing=1.45)
 ax.grid(True,alpha=.2)
 return fig,ax
def legend(ax,ncol=2):
 ax.legend(loc='lower center',bbox_to_anchor=(.5,1.025),ncol=ncol,
           frameon=False,fontsize=9.5,columnspacing=1.5,handlelength=2.4)
def finish(fig,name,method,inputs=(),series=(),extra=None):
 fig.savefig(OUT/name,facecolor='white')
 plt.close(fig)
 record(name,method,inputs,series,extra)
def series(data,x,y,label,transform=None):
 xx=nums(data,x); yy=nums(data,y)
 if transform: yy=transform(yy)
 return {'label':label,'x_field':x,'y_field':y,'x':xx.tolist(),'y':yy.tolist()}
def add_line(ax,data,x,y,label,color=None,marker='o',ls='-'):
 s=series(data,x,y,label)
 line,=ax.plot(s['x'],s['y'],label=label,marker=marker,color=color,linestyle=ls,markersize=5)
 assert np.array_equal(line.get_xdata(),nums(data,x))
 assert np.array_equal(line.get_ydata(),nums(data,y))
 return s

# Figure 1: the original illustrative endpoint is (2.25,1.75).
fig,ax=setup('Projection geometry behind residualization',
 'The covariate component lies in the null-model span.\nThe residual component is orthogonal to that span.')
ax.set_position([.14,.28,.82,.49]); ax.set_xlim(-.6,3.6); ax.set_ylim(-.6,2.05)
ax.axhline(0,color='tab:blue',lw=1.5); ax.axvline(0,color='tab:blue',lw=1)
for p,q in [((0,0),(2.25,1.75)),((0,0),(2.25,0)),((2.25,0),(2.25,1.75))]:
 ax.annotate('',xy=q,xytext=p,arrowprops={'arrowstyle':'->','lw':2,'color':'black'})
ax.plot([2.25,2.25],[0,1.75],color='tab:orange',ls='--',lw=1)
ax.text(2.36,1.76,'$y$',fontsize=15); ax.text(2.39,.86,'$M_Xy$',fontsize=13)
ax.text(2.25,-.23,'$Q_XQ_X^{\\mathsf{T}}y$',ha='center',fontsize=12)
ax.text(3.53,.11,'$\\mathrm{span}(X)$',ha='right',fontsize=12)
fig.text(.52,.825,'$y=Q_XQ_X^{\\mathsf{T}}y+M_Xy$    |    $M_X=I-Q_XQ_X^{\\mathsf{T}}$',ha='center',fontsize=12)
ax.set_xlabel('Covariate-span coordinate'); ax.set_ylabel('Orthogonal residual coordinate')
finish(fig,'figure_01_residualization_geometry.png','diagram relayout; same coordinates, formulas and projection relations',extra={'illustrative_endpoint':[2.25,1.75]})

# Figure 2: formulas remain inside boxes; arrows start at box edges.
fig=plt.figure(figsize=(8,5.7)); ax=fig.add_axes([.03,.2,.94,.64]); ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
fig.text(.5,.865,'$K=AA^{\\mathsf{T}}=\\sum_{b=1}^{B}A_bA_b^{\\mathsf{T}}$',ha='center',fontsize=16)
ax.add_patch(Rectangle((.025,.11),.21,.78,fill=False,lw=1.6))
for i in range(1,3): ax.plot([.025+.07*i]*2,[.11,.89],lw=1.4)
for i in range(3): ax.text(.06+.07*i,.93,f'$A_{i+1}$',ha='center',fontsize=12)
ax.text(.13,.035,r'$A=[A_1\ A_2\ A_3]$',ha='center',fontsize=12)
for i,y in enumerate([.76,.5,.24],1):
 ax.add_patch(Rectangle((.36,y-.09),.29,.18,fill=False,lw=1.2))
 ax.text(.505,y,f'$K_{i}=A_{i}A_{i}^{{\\mathsf{{T}}}}$',ha='center',va='center',fontsize=12)
 ax.annotate('',xy=(.35,y),xytext=(.25,y),arrowprops={'arrowstyle':'->','lw':1.4})
 ax.annotate('',xy=(.78,.5),xytext=(.66,y),arrowprops={'arrowstyle':'->','lw':1.4})
ax.add_patch(Rectangle((.79,.35),.19,.3,fill=False,lw=1.6));ax.text(.885,.5,'$K$',ha='center',va='center',fontsize=19)
ax.text(.88,.7,'$K=K_1+K_2+K_3$',ha='center',fontsize=11)
fig.text(.06,.075,'Each resident variant block contributes one exact sample-interaction kernel.\nStreaming accumulates those kernels without changing their sum.',fontsize=10.3,linespacing=1.45)
finish(fig,'figure_02_exact_block_kernel_assembly.png','diagram relayout; unchanged block-sum identities and three-block connectivity')

data=rows('memory_asymptotic_sweep.csv')
fig,ax=setup('Blocking removes the full variant count from working memory',
 r'$M_{\mathrm{stream}}=O(nc+ns+cs+np)$; $M_A=O(nm)$.'+'\n'+
 'Fixed resident block size keeps the working set bounded; arithmetic and I/O grow with $m$.')
ss=[add_line(ax,data,'m',y,l) for y,l in [('full_factor_MiB','Full factor A'),('stream_kernel_action_MiB','Streamed kernel action'),('tiled_gram_MiB','Tiled Gram construction')]]
ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Total variant count $m$');ax.set_ylabel('Modeled working memory (MiB)');legend(ax,3)
finish(fig,'figure_03_memory_law.png','CSV relayout; notes outside axes', ['memory_asymptotic_sweep.csv'],ss)

fig,ax=setup('Exact propagation support across phases',
 'The staircase boundary is the graph light cone. A phase activates only\nafter a path of sufficient length can reach it.')
ax.set_position([.12,.26,.69,.55]); support=(np.arange(10)[:,None]<=np.arange(8)[None,:]).astype(int)
im=ax.imshow(support,origin='lower',aspect='auto',interpolation='nearest',cmap='viridis',vmin=0,vmax=1)
ax.grid(False);ax.set_xticks(range(8));ax.set_yticks(range(10));ax.set_xlabel('Krylov depth $k$');ax.set_ylabel('Phase index')
cax=fig.add_axes([.85,.26,.025,.55]);fig.colorbar(im,cax=cax,ticks=[0,1],label='Active support')
fig.text(.5,.853,'$P_hH^kP_g=0$  when  $\\mathrm{dist}(g,h)>k$',ha='center',fontsize=11.5)
finish(fig,'figure_04_polyphase_lightcone.png','structural support-array relayout; same 10 by 8 binary staircase',extra={'support':support.tolist()})

# Raw plotted vectors were not archived for figures 5--7. Replace the
# occluded raster curves with exact archived audit values / rounded labels.
data=rows('phase_local_rank_audit.csv')
fig,ax=setup('Phase-local rank determines the minimum basis width',
 'Constructed rank, numerical rank and minimum exact width agree in all six phases.\nPhase 3 has rank 4; a uniform width of 12 allocates eight unused directions.')
x=nums(data,'phase'); used=nums(data,'minimum_exact_width'); waste=nums(data,'uniform_width_12_waste')
assert np.array_equal(nums(data,'constructed_rank'),used)
assert np.array_equal(nums(data,'svd_numerical_rank'),used)
assert np.array_equal(used+waste,np.full(len(data),12.0))
bars=ax.bar(x,used,label='Minimum exact width',color='tab:blue',width=.6)
unused=ax.bar(x,waste,bottom=used,label='Unused uniform width 12',color='#e0e6ec',width=.6)
for i,(u,v) in enumerate(zip(used,waste)):
 assert bars[i].get_height()==u and unused[i].get_height()==v
 ax.text(x[i],u/2,str(int(u)),ha='center',va='center',color='white',fontsize=12)
ax.set_xticks(x);ax.set_ylim(0,12.6);ax.set_yticks([0,4,8,12]);ax.set_xlabel('Phase index');ax.set_ylabel('Basis directions');legend(ax)
ss=[series(data,'phase','minimum_exact_width','Minimum exact width'),series(data,'phase','uniform_width_12_waste','Unused uniform width 12')]
finish(fig,'figure_05_phase_local_rank.png','replacement summary from exact archived rank audit; no singular-value vector reconstructed',['phase_local_rank_audit.csv'],ss,
 {'archived_rank_checks':data,'source_vectors_available':False,'original_singular_curve_reconstructed':False})

data=rows('qr_core_update_audit.csv'); assert len(data)==1
r=data[0]; maxdiff=float(r['max_abs_singular_difference']); reldiff=float(r['relative_l2_singular_difference'])
fig=plt.figure(figsize=(8,5.7));ax=fig.add_axes([.06,.2,.88,.57]);ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
fig.text(.5,.96,'Exact QR-core identity and archived numerical control',ha='center',va='top',fontsize=13.5)
fig.text(.5,.825,r'$[A,U]=[Q,Q_\perp]C_{\mathrm{core}}$',ha='center',fontsize=16)
for xx,label in [(.02,r'Full updated factor $[A,U]$'),(.56,r'Compact update core $C_{\mathrm{core}}$')]:
 ax.add_patch(Rectangle((xx,.62),.42,.22,fill=False,lw=1.3))
 ax.text(xx+.21,.73,label,ha='center',va='center',fontsize=11)
ax.annotate('',xy=(.55,.73),xytext=(.45,.73),arrowprops={'arrowstyle':'<->','lw':1.5})
ax.text(.5,.49,'Same nonzero singular values under the stated orthonormality hypotheses',ha='center',fontsize=10.5)
for xx,title,value in [(.02,'Maximum absolute singular-value discrepancy',f'{maxdiff:.8e}'),(.56,'Relative singular-spectrum L2 discrepancy',f'{reldiff:.8e}')]:
 ax.add_patch(Rectangle((xx,.06),.42,.29,facecolor='#f0f5f8',edgecolor='#c9d4db'))
 ax.text(xx+.21,.28,title,ha='center',va='center',fontsize=8.7)
 ax.text(xx+.21,.16,value,ha='center',va='center',fontsize=15,color='tab:blue')
fig.text(.06,.075,f"Archived control: {r['n']} rows, {r['old_columns']} old columns and {r['added_columns']} appended columns.\nThe unavailable singular-value vectors are replaced by the recorded discrepancy metrics.",fontsize=10,linespacing=1.45)
finish(fig,'figure_06_qr_core_equivalence.png','replacement identity diagram and exact archived singular-spectrum discrepancy summaries',['qr_core_update_audit.csv'],extra={'archived_control':r,'source_vectors_available':False,'original_singular_curves_reconstructed':False})

packet_summaries=[{'packet':1,'center_label':'9.97','second_centered_moment_label':'28.14'},
 {'packet':2,'center_label':'4.24','second_centered_moment_label':'2.95'},
 {'packet':3,'center_label':'1.30','second_centered_moment_label':'1.33'}]
fig=plt.figure(figsize=(8,5.7));ax=fig.add_axes([.07,.22,.86,.57]);ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
fig.text(.5,.96,'Centered spectral packets: recorded illustration summaries',ha='center',va='top',fontsize=13)
fig.text(.5,.84,r'$\mu_P=|P|^{-1}\sum_{j\in P}\lambda_j$     $M_{2,P}=\sum_{j\in P}(\lambda_j-\mu_P)^2$',ha='center',fontsize=12)
for x,label in [(.16,'Eigenvalue packets'),(.5,'Centered moments'),(.84,'Transform evaluation')]:
 ax.add_patch(Rectangle((x-.14,.72),.28,.17,facecolor='#edf4f7',edgecolor='#b8c9d3'))
 ax.text(x,.805,label,ha='center',va='center',fontsize=10)
for a,b in [(.3,.36),(.64,.7)]:ax.annotate('',xy=(b,.805),xytext=(a,.805),arrowprops={'arrowstyle':'->','lw':1.4})
cols=[.16,.5,.84]
for x,label in zip(cols,['Packet','Center '+r'$\mu$','Second centered moment '+r'$M_2$']):ax.text(x,.57,label,ha='center',fontsize=10)
for i,recorded in enumerate(packet_summaries):
 y=.43-i*.14
 for x,value in zip(cols,[str(recorded['packet']),recorded['center_label'],recorded['second_centered_moment_label']]):ax.text(x,y,value,ha='center',fontsize=14,color='tab:blue')
 ax.axhline(y-.055,xmin=.03,xmax=.97,color='#e4e9ed',lw=1)
fig.text(.07,.08,'Centers and moments reproduce the rounded labels in the archived illustration.\nNo eigenvalue vector is reconstructed. Matrix blocking precedes spectral packetization.',fontsize=10,linespacing=1.45)
finish(fig,'figure_07_spectral_packets.png','replacement centered-packet schematic and unchanged rounded original summary labels',extra={'packet_summaries_from_original_labels':packet_summaries,'source_vectors_available':False,'original_eigenvalue_curve_reconstructed':False})

data=rows('partition_invariance.csv')
fig,ax=setup('Execution partition changes the summation order, not the operator',
 'The discrepancies stay at floating-point summation scale.\nThe block representation implements the same exact operator.')
labels=['Coarse\n4','Fine\n64','Irregular','Singleton\nfront','Permuted\nblock 73']
ss=[]
for key,label in [('gram_rel_error','Gram relative error'),('action_rel_error','Action relative error')]:
 yy=nums(data,key);line,=ax.plot(range(len(data)),yy,marker='o',label=label);assert np.array_equal(line.get_ydata(),yy)
 ss.append({'label':label,'x_field':'partition (categorical)','x':[r['partition'] for r in data],'y_field':key,'y':yy.tolist()})
ax.set_xticks(range(len(data)),labels);ax.set_ylabel('Relative discrepancy');ax.set_xlabel('Execution partition');legend(ax)
finish(fig,'figure_08_partition_invariance.png','CSV relayout; wrapped partition identifiers and external notes',['partition_invariance.csv'],ss,{'displayed_category_labels':dict(zip([r['partition'] for r in data],labels))})

data=rows('approximate_lightcone_depth.csv')
fig,ax=setup('Weak couplings produce a phasewise envelope',
 r'$\rho(H^kX)\leq\mathcal{B}^k\rho(X)$'+'\n'+r'$\rho((H^k-H_0^k)X)\leq(\mathcal{B}^k-\mathcal{B}_0^k)\rho(X)$')
ss=[add_line(ax,data,'depth',y,l) for y,l in [('actual_outside_cone_norm','Actual outside-cone norm'),('certified_outside_cone_norm','Phasewise upper bound')]]
ax.set_yscale('log');ax.set_xlabel('Krylov depth $k$');ax.set_ylabel('Frobenius norm');legend(ax)
finish(fig,'figure_09_approximate_lightcone_certificate.png','CSV relayout of original generator; equations outside axes',['approximate_lightcone_depth.csv'],ss)

data=sorted([r for r in rows('approximate_lightcone_threshold_sweep.csv') if float(r['certified_error_frobenius'])>0],key=lambda r:int(r['retained_directed_off_diagonal_blocks']))
fig,ax=setup('Sparsity and error for thresholded phase graphs',
 'Moving left prunes more weak phase couplings.\nThe analytic certificate remains valid while communication decreases.')
ss=[add_line(ax,data,'retained_directed_off_diagonal_blocks',y,l) for y,l in [('actual_error_frobenius','Actual truncation error'),('certified_error_frobenius','Analytic upper bound')]]
ax.set_yscale('log');ax.set_xlabel('Retained directed off-diagonal phase blocks');ax.set_ylabel('Depth-5 Frobenius error');legend(ax)
finish(fig,'figure_10_threshold_tradeoff.png','CSV relayout of original generator; notes outside axes',['approximate_lightcone_threshold_sweep.csv'],ss)

data=rows('budget_scheduler_large.csv')
fig,ax=setup('Risk-aware scheduling follows the Krylov query',
 'A single block-norm threshold ignores start phase and Krylov depth.\nEdge-risk scores incorporate both.')
ss=[add_line(ax,data,'budget',y,l) for y,l in [('norm_threshold_retained','Global norm threshold'),('additive_opt_retained','Additive-risk optimum'),('refined_retained','Exact-envelope refinement')]]
ax.set_xscale('log');ax.set_xlabel('Analytic error budget');ax.set_ylabel('Retained undirected phase pairs');legend(ax,3)
finish(fig,'figure_11_budget_scheduler_comparison.png','CSV relayout; legend and commentary separated',['budget_scheduler_large.csv'],ss)

data=rows('double_buffer_model.csv')
fig,ax=setup('Double buffering overlaps transfer with block compute',
 r'$T_{\mathrm{double}}=t_{\mathrm{io},1}+\sum_b\max(t_{\mathrm{comp},b},t_{\mathrm{io},b+1})+t_{\mathrm{comp},B}$')
ss=[]
for key,label in [('single_buffer_ms','Single buffer'),('double_buffer_ms','Ideal double buffer')]:
 yy=nums(data,key);line,=ax.plot(range(len(data)),yy,marker='o',label=label);assert np.array_equal(line.get_ydata(),yy)
 ss.append({'label':label,'x_field':'I/O and compute (categorical)','x':[[r['io_ms_per_block'],r['compute_ms_per_block']] for r in data],'y_field':key,'y':yy.tolist()})
ax.set_xticks(range(len(data)),[f"I/O {r['io_ms_per_block']}\ncompute {r['compute_ms_per_block']}" for r in data]);ax.set_ylabel('Modeled total time (ms)');legend(ax)
finish(fig,'figure_12_double_buffer_model.png','CSV relayout; formula outside axes',['double_buffer_model.csv'],ss)

data=rows('edge_risk_vs_block_norm.csv')
fig,ax=setup('Query risk and block norm carry different information',
 'Risk depends on the start phase and propagation through the graph.\nSimilar block norms can carry different query-specific risks.')
xx=nums(data,'block_norm');yy=nums(data,'query_risk');dots=ax.scatter(xx,yy,s=27)
assert np.array_equal(dots.get_offsets().data,np.column_stack([xx,yy]))
ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Phase-block operator norm');ax.set_ylabel('Additive query-risk score')
finish(fig,'figure_13_edge_risk_vs_block_norm.png','CSV relayout; commentary outside scatter',['edge_risk_vs_block_norm.csv'],[series(data,'block_norm','query_risk','Edge risks')])

data=rows('dual_budget_spectral_scheduler.csv')
fig=plt.figure(figsize=(8,6.2));top=fig.add_axes([.14,.57,.82,.23]);bottom=fig.add_axes([.14,.27,.82,.23])
fig.text(.52,.965,'Dual budgets control pruning and final tail uncertainty',ha='center',va='top',fontsize=13)
ss=[add_line(top,data,'operator_budget','omitted_pairs','Omitted phase pairs','tab:blue'),add_line(bottom,data,'operator_budget','bracket_width_decades','Tail bracket width','tab:orange',marker='s')]
for ax in [top,bottom]:ax.set_xscale('log');ax.grid(True,alpha=.2)
top.set_ylabel('Omitted pairs');top.tick_params(labelbottom=False)
bottom.set_ylabel('Width (decades)');bottom.set_xlabel('Operator-norm budget')
fig.text(.14,.06,'Query budget fixed at 0.05. A loose operator budget can admit a strong\ncoupling and widen the tail bracket.',fontsize=10.3,linespacing=1.45)
finish(fig,'figure_14_dual_budget_tail_bridge.png','CSV relayout; two labeled panels replace indistinguishable twin-axis lines',['dual_budget_spectral_scheduler.csv'],ss)

data=rows('certify_after_prune_range_core.csv')
fig,ax=setup('A useful tail bracket can require nearly complete range capture',
 'The theorem remains valid at every depth. The deep-tail interval stays\ncoarse until the residual collapses.')
ss=[add_line(ax,data,'depth','range_residual_over_sigma1','Range residual / top singular value')]
ax.set_yscale('log');ax.set_xlabel('Pruned Krylov depth');ax.set_ylabel('Relative range residual');legend(ax,1)
finish(fig,'figure_15_range_core_certification.png','CSV relayout; wrapped commentary outside axes',['certify_after_prune_range_core.csv'],ss)

data=rows('residual_completion_audit.csv')
fig,ax=setup('Moment rank bounds identify a small residual completion',
 'From depth 3 onward the integer lower bound, orthogonal-complement upper\nbound and actual residual rank coincide. Hollow markers preserve visibility.')
styles=[('integer_rank_lower','Moment integer lower bound','tab:blue','o',9,'--'),('rank_upper','Orthogonal-complement upper bound','tab:orange','s',6,':'),('actual_residual_rank','Actual residual rank','tab:green','.',4,'-')]
ss=[]
for key,label,color,marker,size,ls in styles:
 s=series(data,'depth',key,label);ss.append(s)
 line,=ax.plot(s['x'],s['y'],color=color,marker=marker,markersize=size,markerfacecolor='none' if marker!='.' else color,linestyle=ls,label=label)
 assert np.array_equal(line.get_ydata(),nums(data,key))
ax.set_xlabel('Pruned Krylov depth');ax.set_ylabel('Residual rank');legend(ax,1)
finish(fig,'figure_17_residual_rank_completion.png','CSV relayout; distinguish coincident curves without jitter',['residual_completion_audit.csv'],ss)

source_hashes_after={str(p.relative_to(SOURCE)):sha(p) for p in sorted(source_files)}
assert source_hashes_before==source_hashes_after, 'An archival provenance input changed.'
(BASE/'FIGURE_RELAYOUT_EARLY.json').write_text(json.dumps({'generator':'relayout_figures.py','edition_date':'2026-10-07','figures':REPORT,'original_engine_inputs_modified':False,'source_hashes_before':source_hashes_before,'source_hashes_after':source_hashes_after,'all_source_hashes_preserved':True},indent=2)+'\n')
print(f'Relaid out {len(REPORT)} early figures; archival sources retained.')
