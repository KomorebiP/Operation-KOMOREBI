#!/usr/bin/env python3
"""Regenerate the monograph's publication graphics from declared inputs.

No engine benchmarks or Lean builds are performed. Recorded experimental data
are redrawn without smoothing. Finite illustrative models are recomputed below.
The manifest names every data source and distinguishes its evidence level.
"""
from pathlib import Path
import argparse
import json
import math
from decimal import Decimal, localcontext
import numpy as np
import pandas as pd
import mpmath as mp
from scipy.stats import gamma
from matplotlib.patches import Rectangle, Polygon
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
from figure_style import *

ENGINE=ROOT/'engine'
DATA=ROOT/'illustrations/publication_data'
WORKED=ROOT/'verification/current_revision/worked_example.json'
W=json.loads(WORKED.read_text())
CONTROL=json.loads((ROOT/'illustrations/finite_control.json').read_text())['checks']
MAIN_SOURCE=ROOT/'illustrations/production_figures.py'
SIZING='Algebraic storage or timing model, not a new hardware measurement.'
RETAINED='Redraw of retained measurements; no new numerical benchmark was executed.'
TOY='Declared finite illustration. Numerical plot values are not directed interval certificates.'


def df(name):return pd.read_csv(ENGINE/name)
def main_save(fig,stem,files=(),scope=RETAINED,**kw):
    save(fig,stem,sources=[ENGINE/f for f in files],scope=scope,**kw)
def toy_save(fig,stem,**kw):
    save(fig,stem,sources=[MAIN_SOURCE],scope=TOY,**kw)
def fixed_x(ax,x): ax.set_xticks(x)
def comma(ax,axis='x'):
    getattr(ax,axis+'axis').set_major_formatter(FuncFormatter(lambda x,p:f'{x:,.0f}'))


def basic_diagrams():
    # Orthogonal projection is a declared geometric model, not sample data.
    fig,ax=canvas('Residualization separates nuisance and signal', 'EXACT GEOMETRY',
        'The displayed coordinates are illustrative. Orthogonality is the invariant.',height=3.55,rect=[.15,.22,.79,.53])
    ax.grid(False);ax.set(xlim=(-.2,3.9),ylim=(-.2,2.45),xticks=[0,1,2,3],yticks=[0,1,2],
        xlabel='Coordinate in the covariate span',ylabel='Orthogonal coordinate')
    ax.axhline(0,color=RULE,lw=.8)
    arrow(ax,(0,0),(2.5,1.8),EXACT,1.9)
    arrow(ax,(0,0),(2.5,0),BOUND,2)
    arrow(ax,(2.5,0),(2.5,1.8),APPROX,2)
    ax.plot([0,2.5],[1.8,1.8],ls=':',color=RULE,lw=1)
    ax.add_patch(Rectangle((2.35,0),.15,.15,fill=False,ec=GRAY,lw=.7))
    number(ax,2.65,1.94,r'$y$',color=EXACT,size=12)
    number(ax,1.3,.2,r'$Q_XQ_X^{\mathsf{T}}y$',color=BOUND,size=11)
    number(ax,2.66,.85,r'$M_Xy$',color=APPROX,ha='left',size=11)
    toy_save(fig,'figure_01_residualization_geometry',checks={'vector_decomposition':[2.5,1.8]})

    fig,ax=canvas('Column blocks contribute exact Gram summands','EXACT REPRESENTATION',
        r'Horizontal partitioning changes residence, not the identity $K=\sum_b A_bA_b^{\mathsf{T}}$.',height=3.55,diagram=True)
    ax.set(ylim=(0,5))
    for j,(c,lab) in enumerate(zip([EXACT,APPROX,BOUND],[r'$A_1$',r'$A_2$',r'$A_3$'])):
        ax.add_patch(Rectangle((.2+j*.56,1.05),.56,2.7,fc=c,alpha=.12,ec=c,lw=.8))
        number(ax,.48+j*.56,4,lab,size=12,color=c)
        y=3.55-j*1.35
        arrow(ax,(2.0,2.4),(3.05,y-.12),c)
        card(ax,3.1,y-.7,3.15,1.05,r'$K_%d=A_%dA_%d^{\mathsf{T}}$'%(j+1,j+1,j+1),color=c)
        arrow(ax,(6.35,y-.15),(7.48,2.25),c)
    card(ax,7.6,1.3,2.1,1.9,r'$K=AA^{\mathsf{T}}$',r'$K_1+K_2+K_3$',EXACT)
    toy_save(fig,'figure_02_exact_block_kernel_assembly')

    # Preserve the observed rank inventory, not invented singular value vectors.
    d=df('phase_local_rank_audit.csv');fig,ax=canvas('Allocate basis width to the rank of each phase',note='All six constructed ranks agree with the recorded numerical ranks.',rect=[.14,.22,.78,.53])
    y=np.arange(len(d));ax.barh(y,12,color=PALE,height=.58,edgecolor=RULE,lw=.5,label='Uniform width 12')
    ax.barh(y,d.minimum_exact_width,color=APPROX,height=.58,label='Minimum exact width')
    for i,v in enumerate(d.minimum_exact_width):number(ax,v+.2,i,str(v),color=APPROX,ha='left',size=9)
    ax.set(yticks=y,yticklabels=[f'Phase {i}' for i in d.phase],xlabel='Basis directions',xlim=(0,12.7));ax.invert_yaxis();ax.grid(axis='y',visible=False);ax.grid(axis='x',color=RULE,lw=.5)
    legend(ax,2);main_save(fig,'figure_05_phase_local_rank',['phase_local_rank_audit.csv'])

    d=df('qr_core_update_audit.csv').iloc[0]
    fig,ax=canvas('A compact update core preserves nonzero singular values',note='Recorded QR control: 128 rows, 180 initial columns, 37 appended columns.',diagram=True,height=3.55)
    card(ax,.15,2.5,4.0,1.45,'Full updated factor',r'$[A,\,U]$',EXACT)
    card(ax,5.8,2.5,4.0,1.45,'Compact update core',r'$C_{\rm core}$',APPROX)
    arrow(ax,(4.35,3.2),(5.6,3.2),GRAY,1.1,'<->')
    number(ax,5,2.15,r'$[A,\,U]=[Q,\,Q_\perp]C_{\rm core}$',size=13)
    for x,label,value in [(.25,'Maximum absolute discrepancy',d.max_abs_singular_difference),(5.6,'Relative spectrum discrepancy',d.relative_l2_singular_difference)]:
        number(ax,x,.95,label,size=8.5,color=GRAY,ha='left');number(ax,x,.35,f'{value:.3e}',size=15,color=EXACT,ha='left')
    main_save(fig,'figure_06_qr_core_equivalence',['qr_core_update_audit.csv'],caption='QR-core identity and retained scalar discrepancy metrics. Raw singular-value vectors are not reconstructed.')


def streaming_and_structure():
    d=df('memory_asymptotic_sweep.csv');fig,ax=canvas('Resident storage does not grow with total factor width','STORAGE MODEL',
       'Binary64 payload only. Backend workspace and additional I/O buffers are excluded.',rect=[.14,.22,.66,.54])
    for i,(c,lab) in enumerate([('full_factor_MiB','Full factor'),('stream_kernel_action_MiB','Streamed action'),('tiled_gram_MiB','Tiled Gram')]):
        series(ax,d.m,d[c],index=i)
        ax.annotate(lab,(d.m.iloc[-1],d[c].iloc[-1]),xytext=(8,0),textcoords='offset points',fontsize=8.3,color=COLORS[i],va='center')
    logaxis(ax,'x');logaxis(ax);ax.set(xlim=(8000,1.1e6),ylim=(4,3e4),xlabel='Total factor columns',ylabel='Payload (MiB)');ax.set_xticks([1e4,1e5,1e6])
    main_save(fig,'figure_03_memory_law',['memory_asymptotic_sweep.csv'],scope=SIZING)

    d=df('partition_invariance.csv');fig,ax=canvas('Different partitions preserve the same operator',note='The discrepancies shown are floating comparisons, not interval enclosures.',rect=[.22,.22,.72,.54])
    y=np.arange(len(d));ax.hlines(y,d.gram_rel_error*1e16,d.action_rel_error*1e16,color=RULE,lw=2)
    ax.scatter(d.gram_rel_error*1e16,y,s=30,marker='o',color=EXACT,label='Gram matrix')
    ax.scatter(d.action_rel_error*1e16,y,s=30,marker='s',facecolors='white',edgecolors=APPROX,label='Operator action')
    ax.set(yticks=y,yticklabels=['Coarse (4)','Fine (32)','Irregular (9)','Singleton front','Permuted (29)'],xlabel=r'Relative discrepancy ($\times10^{-16}$)',xlim=(0,7.3));ax.invert_yaxis();ax.grid(axis='y',visible=False);ax.grid(axis='x',color=RULE,lw=.5);legend(ax,2)
    main_save(fig,'figure_08_partition_invariance',['partition_invariance.csv'])

    d=df('polyphase_psd_light_cone.csv');fig,ax=canvas('A finite-depth query has an exact phase frontier',note='Recorded PSD chain control. Every stored norm outside the graph frontier is zero.',rect=[.11,.22,.83,.54])
    assert (d.loc[d.outside_light_cone,'norm']==0).all()
    for row in d.itertuples():
        active=row.norm!=0
        ax.scatter(row.k,row.phase,s=40,marker='s' if active else 'o',color=APPROX if active else 'white',edgecolors=APPROX if active else RULE,lw=.65)
    ax.plot(np.arange(8),np.arange(8)+.45,ls='--',color=BOUND,lw=1)
    ax.text(2.9,8.3,'Outside frontier: exact zero',fontsize=8.5,color=GRAY)
    ax.set(xlim=(-.5,7.5),ylim=(-.5,9.5),xticks=range(8),yticks=range(10),xlabel=r'Operator depth $k$',ylabel='Phase index');ax.grid(False)
    main_save(fig,'figure_04_polyphase_lightcone',['polyphase_psd_light_cone.csv'],checks={'outside_frontier_zero':True})

    for filename,stem,title,x,y1,y2,xlabel,ylabel in [
      ('approximate_lightcone_depth.csv','figure_09_approximate_lightcone_certificate','A transfer bound controls discarded propagation','depth','actual_difference_norm','certified_difference_norm','Operator depth','Difference norm'),
      ('approximate_lightcone_threshold_sweep.csv','figure_10_threshold_tradeoff','Retaining more phase blocks reduces the error budget','retained_fraction','actual_error_frobenius','certified_error_frobenius','Fraction of off-diagonal blocks retained','Frobenius error')]:
        d=df(filename).sort_values(x);fig,ax=canvas(title,note='Line segments connect recorded samples. The bound concerns the stated arithmetic model.')
        series(ax,d[x],d[y1],'Observed difference',0);series(ax,d[x],d[y2],'Transfer bound',2)
        ax.fill_between(d[x],d[y1],d[y2],color=BOUND,alpha=.07)
        ax.set(xlabel=xlabel,ylabel=ylabel);legend(ax,2)
        if x=='depth':fixed_x(ax,d[x])
        assert np.all(d[y1]<=d[y2]+1e-10)
        main_save(fig,stem,[filename],checks={'recorded_error_below_bound':True})

    d=df('budget_scheduler_large.csv');fig,ax=canvas('A query-aware schedule can omit more phase pairs',note='66 candidate phase pairs in this retained control. This is not a universal speedup claim.',rect=[.12,.22,.68,.54])
    for i,(c,lab) in enumerate([('refined_omitted','Envelope refinement'),('additive_opt_omitted','Additive scheduler'),('norm_threshold_omitted','Norm threshold')]):
        series(ax,d.budget,d[c],index=i);ax.annotate(lab,(d.budget.iloc[-1],d[c].iloc[-1]),xytext=(8,0),textcoords='offset points',color=COLORS[i],fontsize=8.3,va='center')
    ax.set(xlabel='Query-error budget',ylabel='Omitted phase pairs',ylim=(-2,42),xlim=(0,.0104));ax.set_xticks([0,.002,.005,.01]);main_save(fig,'figure_11_budget_scheduler_comparison',['budget_scheduler_large.csv'])

    d=df('edge_risk_vs_block_norm.csv');fig,ax=canvas('Block magnitude alone does not identify query risk',note='Each point is one phase pair. Risk is conditioned on the declared Krylov query.')
    for i,(condition,lab) in enumerate([(d.graph_distance==1,'Adjacent phases'),(d.graph_distance>1,'Nonadjacent phases')]):
        ax.scatter(d.loc[condition,'block_norm'],d.loc[condition,'query_risk'],s=25,marker=MARKERS[i],facecolors='white' if i else COLORS[i],edgecolors=COLORS[i],lw=.9,label=lab)
    logaxis(ax,'x');logaxis(ax);ax.set(xlabel='Phase-block operator norm',ylabel='Query-dependent risk');legend(ax,2)
    main_save(fig,'figure_13_edge_risk_vs_block_norm',['edge_risk_vs_block_norm.csv'])

    d=df('double_buffer_model.csv');fig,ax=canvas('Overlap can hide part of the transfer time','EXECUTION MODEL',
       '64 blocks per setting. Wall times are model predictions, not measured accelerator timings.',rect=[.17,.22,.77,.54])
    y=np.arange(len(d));x1=d.single_buffer_ms/1000;x2=d.double_buffer_ms/1000
    ax.hlines(y,x2,x1,lw=4,color=RULE)
    ax.scatter(x1,y,s=34,color=EXACT,marker='o',label='Single buffer')
    ax.scatter(x2,y,s=34,edgecolors=APPROX,facecolors='white',marker='s',label='Double buffer')
    ax.set(yticks=y,yticklabels=[f'{int(a)} / {int(b)} ms' for a,b in zip(d.io_ms_per_block,d.compute_ms_per_block)],xlabel='Model wall time (seconds)',ylabel='I/O / compute',xlim=(0,.9));ax.invert_yaxis();ax.grid(False);ax.grid(axis='x',color=RULE,lw=.5);legend(ax,2)
    main_save(fig,'figure_12_double_buffer_model',['double_buffer_model.csv'],scope=SIZING)


def spectra_and_residuals():
    d=df('dual_budget_spectral_scheduler.csv');fig,ax=canvas('An operator budget constrains the tail bracket',note='Fixed query budget 0.05. The reference is at log₁₀ p = −8.',rect=[.135,.22,.80,.54])
    x=d.operator_budget
    ax.fill_between(x,d.lower_log10_p,d.upper_log10_p,color=BOUND,alpha=.12)
    series(ax,x,d.lower_log10_p,'Lower endpoint',0);series(ax,x,d.upper_log10_p,'Upper endpoint',2)
    ax.axhline(-8,color=APPROX,ls=':',lw=1.5,label='Reference')
    logaxis(ax,'x');ax.set(xlabel='Operator-error budget',ylabel=r'Tail bracket in $\log_{10}p$');legend(ax,3)
    main_save(fig,'figure_14_dual_budget_tail_bridge',['dual_budget_spectral_scheduler.csv'])

    d=df('certify_after_prune_range_core.csv');fig,ax=canvas('A larger captured range leaves less unresolved action',note='Residual norms are measured against the original factor, after basis discovery.')
    series(ax,d.sample_basis_dim,d.range_residual_over_sigma1,index=0)
    ax.set(xlabel='Captured sample-space dimension',ylabel=r'Range residual / $\sigma_1$',ylim=(-.03,1.08));fixed_x(ax,d.sample_basis_dim[::2])
    main_save(fig,'figure_15_range_core_certification',['certify_after_prune_range_core.csv'])

    d=df('trace_cap_vs_weyl.csv');fig,ax=canvas('Residual moments sharpen incomplete-range tail bounds',note='Infinite Weyl widths are marked explicitly; recorded zeros stay at zero on the symmetric-log axis.')
    finite=np.isfinite(d.v07_weyl_width_decades)
    series(ax,d.loc[finite,'basis_dim'],d.loc[finite,'v07_weyl_width_decades'],'Coefficientwise Weyl',0)
    series(ax,d.basis_dim,d.two_sided_width_decades,'Residual moments',2)
    ax.set_yscale('symlog',linthresh=1e-13);ax.set(xlabel='Captured basis dimension',ylabel='Tail-bracket width (decades)',ylim=(-1e-14,3e5));ax.set_yticks([0,1e-12,1e-8,1e-4,1,1e4]);fixed_x(ax,d.basis_dim[::2]);legend(ax,2)
    for x in d.loc[~finite,'basis_dim']:
        ax.annotate(r'$\infty$',xy=(x,1.5e5),xytext=(x,2e4),ha='center',va='bottom',fontsize=12,color=EXACT,arrowprops={'arrowstyle':'-|>','color':EXACT,'lw':1})
    main_save(fig,'figure_16_trace_moment_vs_weyl',['trace_cap_vs_weyl.csv'],checks={'infinite_widths_explicit':int((~finite).sum())})

    d=df('residual_completion_audit.csv');fig,ax=canvas('Moment bounds identify the remaining rank',note='Coincident lower and upper bounds determine the rank in this finite control.')
    ax.fill_between(d.depth,d.integer_rank_lower,d.rank_upper,color=BOUND,alpha=.15)
    series(ax,d.depth,d.rank_upper,'Complement upper bound',0,markersize=7)
    series(ax,d.depth,d.integer_rank_lower,'Moment lower bound',2,markersize=3.5)
    ax.scatter(d.depth,d.actual_residual_rank,color=APPROX,marker='x',s=28,label='Observed rank',zorder=5)
    ax.set(xlabel='Krylov depth',ylabel='Residual rank',ylim=(0,43));fixed_x(ax,d.depth);legend(ax,3,fontsize=7.6)
    main_save(fig,'figure_17_residual_rank_completion',['residual_completion_audit.csv'])


def worked_and_interval():
    theta=float(W['theta_at_q40']);q=40.;xx=np.linspace(0,160,1200)
    orig=.5*(np.exp(-xx/4)-np.exp(-xx/2))
    kappa=-np.log(1-2*theta)-np.log(1-4*theta)
    tilted=orig*np.exp(theta*xx-kappa)
    fig,ax=canvas('Tilting moves the query into the body of the law','DECLARED WORKED EXAMPLE',
        'Spectrum (1, 1, 2, 2). Both curves are point evaluations of explicit densities.')
    ax.plot(xx,orig,color=EXACT,lw=1.8,label='Original law')
    ax.plot(xx,tilted,color=APPROX,ls='--',lw=1.8,label='Tilted law')
    ax.fill_between(xx,tilted,where=xx>=40,color=APPROX,alpha=.08)
    ax.axvline(40,color=BOUND,ls=':',lw=1.3);ax.text(43,.11,r'$q=40$',fontsize=9,color=BOUND)
    ax.set(xlim=(0,160),ylim=(0,.14),xlabel=r'Quadratic-form value $x$',ylabel='Density');legend(ax,2)
    save(fig,'worked_tilt',sources=[WORKED,MAIN_SOURCE],scope=TOY)

    d=pd.DataFrame(W['packet_error_samples']);fig,ax=canvas('Moment refinement contracts the transform remainder','DECLARED WORKED EXAMPLE',
       'Packet (1.96, 1.98, 2.02, 2.04), center 2, at s = 0.1 + 0.4i.')
    x=d.order;y=np.array(d.observed_error,dtype=float);b=np.array(d.analytic_bound,dtype=float)
    series(ax,x,y,'Point-evaluated error',0);series(ax,x,b,'Analytic remainder',2)
    ax.fill_between(x,y,b,color=BOUND,alpha=.07)
    logaxis(ax);ax.set(xlabel='Retained moment order',ylabel='Absolute CGF error',ylim=(1e-23,1));fixed_x(ax,x);legend(ax,2)
    assert np.all(y<=b)
    save(fig,'worked_packet_error',sources=[WORKED],scope=TOY,checks={'errors_below_bounds':True})

    # Draw decimal interval endpoints only after subtracting the reference in Decimal.
    ref=Decimal(W['independent_log10_interval'].split(',')[0].strip('['))
    fig,ax=canvas('Refinement turns an unresolved query into acceptance','DIRECTED WORKED CONTROL',
        'Reference-centered endpoints are rounded only for display. The full decimal records govern acceptance.',height=3.65,rect=[.18,.24,.76,.49])
    fig.text(.945,.96,'Requested width: 2%',fontsize=8,color=APPROX,ha='right',va='top')
    for j,row in enumerate(W['refinements']):
        obj=row.get('result',row.get('interval'))
        interval=obj['log10_interval']
        lo,hi=map(Decimal,interval.strip('[]').split(','))
        with localcontext() as c:
            c.prec=120;left=float((lo-ref)*Decimal(1000));right=float((hi-ref)*Decimal(1000))
        acc=row['accuracy']['accepted'];color=APPROX if acc else FAIL
        ax.plot([left,right],[1-j,1-j],color=color,lw=4,solid_capstyle='butt')
        ax.plot([left,right],[1-j,1-j],marker='|',ls='',color=color,markersize=13)
        ratio=float(row['accuracy']['ratio_upper'])
        ax.text(0,1-j+.22,f'{ratio:.3%} width  /  '+('accepted' if acc else 'not accepted'),ha='center',fontsize=9,color=color,bbox=dict(facecolor='white',edgecolor='none',pad=2))
    ax.axvline(0,color=EXACT,lw=1.2,ls=':');ax.scatter([0,0],[0,1],marker='D',s=23,color=EXACT,zorder=4)
    ax.set(yticks=[1,0],yticklabels=['N = 8,192','N = 16,384'],ylim=(-.55,1.6),xlim=(-6.7,6.7),xlabel=r'Offset from independent $\log_{10}p$ reference ($\times10^{-3}$)');ax.grid(False);ax.grid(axis='x',color=RULE,lw=.5)
    save(fig,'worked_enclosure_refinement',sources=[WORKED],scope='Display of retained directed endpoints and acceptance results. Plot geometry itself is not an enclosure.')

    name='reference_convergence.csv';d=df(name);fig,ax=canvas('A reference calculation must also be refined',note='The last recorded discrepancy is −2.60 × 10⁻⁸ decades. Lines connect samples.')
    x=np.arange(len(d));series(ax,x,d.adaptive_minus_reference_decades,index=0)
    ax.axhline(0,color=GRAY,lw=.8,ls=':')
    ax.set(xticks=x,xticklabels=[f'{int(a):,}\nL = {int(b)}' for a,b in zip(d.reference_K,d.reference_L)],xlabel='Reference modes and support factor',ylabel='Adaptive minus reference (decades)',ylim=(-.007,.023))
    main_save(fig,'figure_21_reference_convergence',[name])

    path=ROOT/'verification/proofread_checks/corrected_fixed_resolution_controls.json';rows=json.loads(path.read_text())
    fig,ax=canvas('Fixed resolution gives wider enclosures deeper in the tail','DIRECTED CONTROL RECORD',
        'Widths use the corrected decimal endpoint records, not differences of binary64 endpoints.')
    x=[-int(r['target_log10_p']) for r in rows];y=[float(r['directed_width_upper']) for r in rows]
    series(ax,x,y,index=2);logaxis(ax,'x');logaxis(ax);ax.set(xlabel=r'Target tail depth $-\log_{10}p$',ylabel='Log-probability interval width',ylim=(4e-13,1e-10),xlim=(70,7500));fixed_x(ax,x);comma(ax)
    for a,b in zip(x,y):ax.annotate(f'{b:.3e}',(a,b),xytext=(0,12),textcoords='offset points',ha='center',fontsize=8.5,color=BOUND)
    save(fig,'figure_24_interval_deep_tail_width',sources=[path],scope=RETAINED,checks={'corrected_width_source':True})

    name='interval_precision_sweep_1e5000.csv';d=df(name);fig,ax=canvas('More digits do not remove the analytic remainder',note='Fixed support and mode count at the control near 10⁻⁵⁰⁰⁰. Precision alone is not refinement.')
    series(ax,d.interval_dps,d.total_width_decades_decimal,'Total enclosure width',2)
    series(ax,d.interval_dps,d.arithmetic_only_width_decades_decimal,'Finite-arithmetic width',0)
    logaxis(ax);ax.set(xlabel='Interval decimal precision',ylabel='Width in log-probability decades',ylim=(1e-125,1e-3));ax.set_yticks([1e-10,1e-35,1e-60,1e-85,1e-110]);fixed_x(ax,d.interval_dps);legend(ax,2)
    main_save(fig,'figure_25_interval_arithmetic_vs_analytic',[name])

    name='accuracy_driven_controls.csv';d=pd.concat([df(name),pd.read_csv(DATA/'accuracy_extreme_summary.csv')],ignore_index=True);fig,ax=canvas('The controller meets the requested probability width',note='All displayed controls pass. Repeated achieved widths correspond to the same accepted resolution.')
    # Dimensionless axes: requested and achieved accuracy orders. Higher is tighter.
    for i,(k,g) in enumerate(d.groupby('target_log10_p',sort=True)):
        x=-np.log10(g.requested_relative_accuracy.astype(float));y=-np.log10(g.achieved_ratio_minus_one.astype(float))
        series(ax,x,y,rf'$p\approx10^{{{int(k)}}}$',i)
    ax.plot([8,20],[8,20],ls=':',lw=1,color=GRAY);ax.text(16.9,16.2,'Equality',color=GRAY,fontsize=8)
    ax.set(xlabel=r'Requested accuracy order $-\log_{10}\varepsilon$',ylabel='Achieved width order',xlim=(7.5,20.5),ylim=(7.7,21));legend(ax,3)
    save(fig,'figure_26_accuracy_driven_refinement',sources=[ENGINE/name,DATA/'accuracy_extreme_summary.csv'],scope=RETAINED,caption='Requested and achieved multiplicative widths shown as decimal orders. Above equality meets the request.')


def empirical_controls():
    name='deep_tail_precision_summary.csv';d=pd.concat([df(name),df('signed_precision_summary.csv')],ignore_index=True)
    fig,ax=canvas('Deep-tail discrepancies across retained control families',note='The symmetric-log axis keeps recorded zeros at zero; no positive display floor is imposed.',height=3.75,rect=[.14,.22,.80,.49])
    names={'analytic scaled chi-square':'Scaled chi-square','production-scale 2000x50000':'Large positive spectrum','realistic corrected LD':'Corrected LD','noncentral exact controls':'Noncentral','-0.02 chi2_80':'Negative chi-square','0.07*(chi2_2-chi2_2)':'Rank-four Laplace','signed mixed multiscale rank 340':'Mixed-sign / rank 340'}
    for i,(k,g) in enumerate(d.groupby('family',sort=False)):
        color=[EXACT,APPROX,BOUND,FAIL,'#657A90','#966F5D','#7B627F'][i]
        ax.scatter(g.tail_depth,g.abs_error_decades,s=27,marker=['o','s','D','^','v','P','X'][i],edgecolors=color,facecolors='white' if i%2 else color,label=names[k])
    logaxis(ax,'x');ax.set_yscale('symlog',linthresh=1e-14)
    ax.set(xlabel=r'Tail depth $-\log_{10}p$',ylabel='Absolute discrepancy (decades)',ylim=(-2e-15,1e-8));ax.set_yticks([0,1e-14,1e-12,1e-10,1e-8]);legend(ax,3,fontsize=7.2)
    main_save(fig,'figure_23_deep_tail_precision_envelope',[name,'signed_precision_summary.csv'])

    name='imhof_heterogeneous_p1e16_battery.csv';d=df(name);fig,ax=canvas('Independent inversion resolves heterogeneous controls',note='The truncation bound is one reference error term, not its complete numerical error budget.',rect=[.22,.22,.72,.54])
    y=np.arange(len(d));ax.hlines(y,d.imhof_tail_bound_relative_to_p,d.implied_relative_difference,color=RULE,lw=1.4)
    ax.scatter(d.implied_relative_difference,y,s=30,color=EXACT,label='Relative difference',marker='o')
    ax.scatter(d.imhof_tail_bound_relative_to_p,y,s=32,facecolors='white',edgecolors=BOUND,label='Reference tail bound',marker='D')
    logaxis(ax,'x');ax.set(yticks=y,yticklabels=['Balanced / 80','Skewed / 80','Spiky / 80','Balanced / 120'],xlabel='Relative scale',xlim=(1e-30,1e-12));ax.invert_yaxis();ax.grid(False);ax.grid(axis='x',color=RULE,lw=.5);legend(ax,2)
    main_save(fig,'figure_27_imhof_p1e16_validation',[name])

    name='signed_exact_controls.csv';d=df(name);fig,ax=canvas('Low-rank signed controls expose a certificate boundary',note='Analytic bounds only. Numerical agreement does not turn a failed tolerance check into a pass.')
    for i,(k,g) in enumerate(d.groupby('family',sort=False)):
        x=-g.exact_log10_p;y=g.certificate
        series(ax,x,y,'Negative / passes' if i==0 else 'Rank 4 / fails',0 if i==0 else 3)
    mixed=df('signed_mixed_highrank_audit.csv')
    series(ax,-mixed.exact_grid_log10_p,mixed.packet_certificate,'Rank 340 / passes',1)
    ax.axhline(1e-8,color=BOUND,ls=':',lw=1.2);ax.text(110,1.6e-8,r'$\varepsilon=10^{-8}$',fontsize=9,color=BOUND)
    logaxis(ax);ax.set(xlabel=r'Tail depth $-\log_{10}p$',ylabel='Reported analytic\nrelative bound',ylim=(1e-13,1e-2));legend(ax,2,fontsize=7.8)
    main_save(fig,'figure_24_signed_certificate_boundary',[name,'signed_mixed_highrank_audit.csv'])

    name='noncentral_exact_controls.csv';d=df(name);fig,ax=canvas('Noncentral controls retain small pointwise discrepancies',note='Zeros remain zeros. These are analytic-ledger comparisons, not directed probability enclosures.')
    for i,((deg,nc),g) in enumerate(d.groupby(['df','nc'],sort=False)):
        series(ax,-g.scipy_log10_p,np.abs(g.difference_decades)*1e14,rf'ν = {int(deg)}, δ = {nc:g}',i)
    ax.set(xlabel=r'Tail depth $-\log_{10}p$',ylabel='Absolute discrepancy\n'+r'($\times10^{-14}$ decades)',ylim=(-.06,1.1));legend(ax,3,fontsize=7.6)
    main_save(fig,'figure_22_noncentral_controls',[name])

    labels={'gaussian_ld_moderate':'Gaussian / moderate','gaussian_ld_strong':'Gaussian / strong','copy_ld_strong_fixed':'Copy / strong','copy_ld_large_fixed':'Copy / large'}
    name='realistic_skat_scenarios.csv';d=df(name);fig,ax=canvas('Dependence changes effective rank, not just matrix size',note='Synthetic LD scenarios. Effective rank and nonzero rank answer different questions.',rect=[.27,.22,.67,.54])
    y=np.arange(len(d));ax.hlines(y,d.effective_rank,d['rank'],color=RULE,lw=3)
    ax.scatter(d['rank'],y,s=30,color=EXACT,label='Nonzero rank')
    ax.scatter(d.effective_rank,y,s=34,marker='D',edgecolors=APPROX,facecolors='white',label='Effective rank')
    ax.set(yticks=y,yticklabels=[labels[s] for s in d.scenario],xlabel='Rank',xlim=(0,1100));ax.invert_yaxis();ax.grid(False);ax.grid(axis='x',color=RULE,lw=.5);legend(ax,2)
    main_save(fig,'figure_18_realistic_ld_effective_rank',[name])

    name='realistic_streaming_invariance.csv';d=df(name);fig,ax=canvas('Block size leaves the represented kernel unchanged',note='Recorded floating discrepancies from raw-genotype streaming, grouped by synthetic scenario.')
    for i,(k,g) in enumerate(d.groupby('scenario',sort=False)):
        series(ax,g.block_size,g.kernel_relative_error*1e16,labels[k],i)
    ax.set(xlabel='Resident column-block width',ylabel=r'Kernel discrepancy ($\times10^{-16}$)');legend(ax,2,fontsize=7.8)
    main_save(fig,'figure_19_realistic_streaming_invariance',[name])

    name='realistic_deep_tail_accuracy.csv';extra=df('realistic_large_deeper_tail.csv');extra['scenario']='copy_ld_large_fixed';d=pd.concat([df(name),extra],ignore_index=True);fig,ax=canvas('Heterogeneous spectra are checked beyond a single law',note='Absolute log-probability differences from the retained synthetic LD controls.')
    for i,(k,g) in enumerate(d.groupby('scenario',sort=False)):
        ax.scatter(-g.kcos_log10_p,np.abs(g.difference_decades)*1e12,s=29,marker=MARKERS[i],facecolors='white' if i%2 else COLORS[i],edgecolors=COLORS[i],label=labels[k])
    ax.set(xlabel=r'Tail depth $-\log_{10}p$',ylabel='Absolute discrepancy\n'+r'($\times10^{-12}$ decades)',ylim=(-.08,None));legend(ax,2,fontsize=7.8)
    main_save(fig,'figure_20_realistic_deep_tail_accuracy',[name,'realistic_large_deeper_tail.csv'])

    p=DATA/'adaptive_certificate_accuracy.csv';d=pd.read_csv(p);fig,ax=canvas('Every recorded point lies below its analytic bound','RETAINED PACKET EXPERIMENT',
      'Twelve genotype-derived queries. The diagonal is equality; bounds exclude floating-point roundoff.')
    for i,(seed,g) in enumerate(d.groupby('seed')):
        ax.scatter(g.observed_relative_error,g.certified_relative_bound,s=35,marker=MARKERS[i],facecolors='white',edgecolors=COLORS[i],label=f'Spectrum {seed+1}',lw=1.2)
    ax.plot([2e-14,2e-8],[2e-14,2e-8],color=GRAY,ls=':',lw=1)
    logaxis(ax,'x');logaxis(ax);ax.set(xlabel='Observed relative error',ylabel='Analytic relative bound',xlim=(2e-14,2e-8),ylim=(2e-14,2e-8));legend(ax,3)
    assert np.all(d.observed_relative_error<=d.certified_relative_bound)
    save(fig,'certificate_coverage',sources=[p],scope=RETAINED,checks={'all_12_below_bound':True})

    p=DATA/'adaptive_tolerance_ladder.csv';d=pd.read_csv(p);fig,ax=canvas('Tighter tolerances refine the packet representation','RETAINED PACKET EXPERIMENT',
      'From left to right: 10 → 15 → 24 packets; modes 128 → 128 → 256.')
    x=-np.log10(d.requested_tolerance)
    series(ax,x,d.requested_tolerance,'Requested tolerance',1)
    series(ax,x,d.certified_relative_bound,'Analytic bound',2)
    series(ax,x,d.observed_relative_error,'Observed error',0)
    logaxis(ax);ax.set(xticks=x,xticklabels=[r'$10^{-6}$',r'$10^{-8}$',r'$10^{-10}$'],xlabel='Requested relative tolerance',ylabel='Relative scale',ylim=(1e-14,1e-5));legend(ax,3,fontsize=7.8)
    save(fig,'tolerance_ladder',sources=[p],scope=RETAINED)

    p=DATA/'adaptive_runtime_scaling.csv';d=pd.read_csv(p);fig,ax=canvas('Compiled reuse and first-query costs are different','RETAINED CPU TIMINGS',
       'Median prototype times. Adaptive total includes planning; compiled reuse does not.',rect=[.13,.22,.67,.54])
    for i,(col,lab) in enumerate([('exact_tilted_seconds','Exact tilted COS'),('adaptive_total_seconds','Adaptive total'),('compiled_plan_eval_seconds','Compiled reuse')]):
        y=1000*d[col];series(ax,d['rank'],y,index=i)
        ax.annotate(lab,(d['rank'].iloc[-1],y.iloc[-1]),xytext=(8,0),textcoords='offset points',color=COLORS[i],fontsize=8.3,va='center')
    logaxis(ax);ax.set(xlabel='Nonzero quadratic-form rank',ylabel='Median runtime (ms)',xlim=(350,1240),ylim=(.35,35));fixed_x(ax,d['rank'])
    save(fig,'runtime_scaling',sources=[p],scope=RETAINED)

# Atlas functions are defined below.

def atlas():
    A=np.array([[2,1,0,0,1,0,0,1,0],[1,2,1,0,0,1,0,0,1],
       [0,1,2,1,0,0,1,0,0],[0,0,1,2,1,0,0,1,0],
       [1,0,0,1,2,1,0,0,1],[0,1,0,0,1,2,1,0,0]],dtype=np.int64)
    blocks=[A[:,i:i+3] for i in (0,3,6)];K=A@A.T
    assert np.array_equal(sum(b@b.T for b in blocks),K)
    U=np.eye(6,dtype=np.int64)[:,:3];B=U.T@A;F=(np.eye(6,dtype=np.int64)-U@U.T)@A
    H=2*np.eye(9,dtype=np.int64)+np.eye(9,k=1,dtype=np.int64)+np.eye(9,k=-1,dtype=np.int64)
    x=np.zeros(9,dtype=np.int64);x[4]=1
    def ac(title,note='',*,diagram=False,height=3.08,rect=None):
        return canvas(title,'DECLARED VISUAL STUDY',note,height=height,diagram=diagram,rect=rect)

    # One connected diagram, not a collage of screenshots.
    fig,ax=canvas('Every representation has its own accuracy obligation','METHOD MAP',
        '',height=2.5,diagram=True)
    ax.set(ylim=(0,4.8))
    items=[('01  Factor',r'$A=[A_1\ \cdots\ A_B]$','Resident blocks',EXACT),
           ('02  Operator',r'$K=AA^{\mathsf{T}}$','Phase and range',EXACT),
           ('03  Spectrum',r'$\{\lambda_j\}$','Intervals / packets',APPROX),
           ('04  Probability',r'$[p_-,p_+]$','Width and decision',BOUND)]
    for i,(title,formula,detail,c) in enumerate(items):
        xx=.08+2.52*i
        card(ax,xx,1.0,2.2,3.05,title,'',c,True)
        number(ax,xx+1.1,2.45,formula,color=c,size=11)
        number(ax,xx+1.1,1.5,detail,size=7.6,color=GRAY)
        if i<3:arrow(ax,(xx+2.25,2.4),(xx+2.48,2.4),GRAY)
    toy_save(fig,'00_pipeline')

    vals=np.linalg.eigvalsh(K);dual=np.linalg.eigvalsh(A.T@A);positive=dual[dual>1e-10]
    assert len(positive)==6 and np.allclose(vals,positive,rtol=1e-13)
    fig,ax=ac('Two Gram matrices share the same nonzero spectrum',
       'Six sample coordinates; nine feature coordinates. The dual Gram has three extra zero eigenvalues.')
    series(ax,np.arange(1,7),vals,r'$AA^{\mathsf{T}}$',0,markersize=7)
    ax.scatter(np.arange(1,7),positive,s=22,marker='D',facecolors='white',edgecolors=APPROX,label=r'Nonzero $A^{\mathsf{T}}A$',zorder=5)
    ax.set(xlabel='Eigenvalue index (ascending)',ylabel='Eigenvalue',xticks=range(1,7),ylim=(0,26));legend(ax,2)
    toy_save(fig,'01_factor_spectrum',checks={'nonzero_spectrum_max_discrepancy':float(np.max(abs(vals-positive)))})

    fig,ax=ac('Block storage preserves every Gram contribution',
       'One shared intensity scale. The displayed integer identity is checked exactly.',diagram=True)
    vmax=int(K.max())
    for i,M in enumerate([blocks[0]@blocks[0].T,blocks[1]@blocks[1].T,blocks[2]@blocks[2].T,K]):
        xx=.2+2.55*i
        matrix(ax,M,(xx,1.5),size=1.75,label=r'$A_%dA_%d^{\mathsf{T}}$'%(i+1,i+1) if i<3 else r'$AA^{\mathsf{T}}$',vmax=vmax)
        if i<3:number(ax,xx+2.14,2.4,'+' if i<2 else '=',size=17)
    for j in range(vmax+1):
        ax.add_patch(Rectangle((2.5+j*.2,.5),.2,.18,facecolor=APPROX if j else PALE,alpha=(.18+.82*j/vmax) if j else 1,ec='white',lw=.1))
    number(ax,2.25,.58,'0',size=8,color=GRAY);number(ax,2.5+(vmax+1)*.2+.23,.58,str(vmax),size=8,color=GRAY)
    toy_save(fig,'02_block_gram',checks={'integer_block_identity':True})

    fig,ax=ac('Resident width controls the working payload',
       'n = 2,000; c = 512; s = 32; p = 3. Algebraic payload, excluding backend workspace.')
    m=np.linspace(512,50000,180);payload=8*(2000*512+2*2000*32+512*32+2000*3)
    ax.plot(m,8*2000*m/2**20,color=EXACT,label='Full factor')
    ax.axhline(payload/2**20,color=APPROX,ls='--',label='Streamed payload')
    logaxis(ax);ax.set(xlabel='Total factor columns',ylabel='Binary64 payload (MiB)',xlim=(0,50000),ylim=(4,1500));comma(ax);legend(ax,2)
    toy_save(fig,'03_memory',checks={'payload_bytes':payload})

    fig,ax=ac('Project away the nuisance component',
       r'The exact coordinate split is $(4,3)=(4,0)+(0,3)$.',rect=[.16,.22,.78,.54])
    ax.grid(False);ax.set(xlim=(-.3,5),ylim=(-.2,4.1),xticks=range(5),yticks=range(4),xlabel='Covariate-span coordinate',ylabel='Orthogonal coordinate')
    arrow(ax,(0,0),(4,3),EXACT,1.8);arrow(ax,(0,0),(4,0),BOUND,1.8);arrow(ax,(0,0),(0,3),APPROX,1.8)
    ax.plot([0,4,4],[3,3,0],':',color=RULE,lw=1)
    number(ax,4.3,3.2,'Feature',color=EXACT,size=8.5)
    number(ax,2,.3,'Removed',color=BOUND,size=8.5)
    number(ax,.17,3.5,'Retained residual',color=APPROX,size=8.5,ha='left')
    toy_save(fig,'04_residualization')

    profiles=np.array([np.linalg.matrix_power(H,k)@x for k in range(5)])
    assert all(profiles[k,j]==0 for k in range(5) for j in range(9) if abs(j-4)>k)
    fig,ax=ac('Finite propagation produces an exact light cone',
       'Chain operator H = 2I + adjacency. Labels show the exact integer amplitudes.',rect=[.11,.22,.83,.54])
    for k in range(5):
      for j in range(9):
        v=profiles[k,j]
        ax.add_patch(Rectangle((j+.55,k-.42),.9,.84,fc=APPROX if v else PALE,ec='white',lw=.8))
        if v:number(ax,j+1,k,str(v),color='white',size=8.5)
    ax.set(xticks=range(1,10),yticks=range(5),xlim=(.5,9.5),ylim=(-.5,4.5),xlabel='Phase address',ylabel=r'Operator depth $k$');ax.grid(False)
    toy_save(fig,'05_phase_cone',checks={'integer_outside_cone_zeros':True})

    H0=H.astype(float);Hw=H0.copy();Hw[0,8]=Hw[8,0]=-.035
    actual=[];bound=[]
    for k in range(1,9):
        actual.append(np.linalg.norm((np.linalg.matrix_power(Hw,k)-np.linalg.matrix_power(H0,k))@x))
        bound.append(np.linalg.norm((np.linalg.matrix_power(abs(Hw),k)-np.linalg.matrix_power(abs(H0),k))@x))
    assert np.all(np.array(actual)<=np.array(bound)+1e-8)
    fig,ax=ac('A weak long-range edge creates controlled leakage',
       'A symmetric-log scale retains the exact zeros at depths 1–4. No artificial positive floor is used.')
    series(ax,range(1,9),actual,'Observed power error',0,markersize=6)
    series(ax,range(1,9),bound,'Transfer envelope',2,markersize=3)
    ax.set_yscale('symlog',linthresh=.01);ax.set(xlabel='Operator depth',ylabel='Euclidean norm',xticks=range(1,9),ylim=(-.002,max(bound)*4));legend(ax,2)
    toy_save(fig,'06_approximate_cone',checks={'float_error_below_bound':True,'zero_depths':[1,2,3,4]})

    rv=np.linalg.eigvalsh(F@F.T);rv=rv[rv>1e-10];t=int(np.trace(F.T@F));v=int(np.trace((F.T@F)@(F.T@F)))
    assert np.array_equal(A.T@A,B.T@B+F.T@F)
    fig,ax=ac('The residual has a spectrum and measurable invariants',
       f'Trace t = {t}; square trace v = {v}; spectral cap ρ ≈ {max(rv):.3f}.',rect=[.135,.22,.81,.54])
    ax.bar(range(1,4),rv,width=.45,color=APPROX,zorder=3)
    for j,a in enumerate(rv):number(ax,j+1,a+.6,f'{a:.3f}',size=9,color=APPROX)
    ax.set(xlabel='Unresolved eigenvalue index',ylabel='Eigenvalue',xticks=[1,2,3],ylim=(0,max(rv)*1.25))
    toy_save(fig,'07_residual',checks={'residual_gram_identity':True,'trace':t,'square_trace':v})

    W0=np.eye(6,dtype=np.int64)[:,3:];D=W0.T@F;C=np.vstack([B,D]);assert np.array_equal(A,np.column_stack([U,W0])@C)
    full=np.linalg.svd(A,compute_uv=False);partial=np.linalg.svd(B,compute_uv=False);complete=np.linalg.svd(C,compute_uv=False)
    fig,ax=ac('Completing the residual restores the full nonzero spectrum',
       'The factor reconstruction is checked in integer arithmetic. The plotted singular values are numerical.')
    series(ax,range(1,7),full,'Full factor',0,markersize=7)
    ax.scatter(range(1,7),complete,s=20,marker='D',color='white',edgecolors=APPROX,label='Completed core',zorder=5)
    series(ax,range(1,4),partial,'Captured core only',2,markersize=4)
    ax.set(xlabel='Singular-value index (descending)',ylabel='Singular value',xticks=range(1,7),ylim=(0,5.5));legend(ax,3,fontsize=7.6)
    toy_save(fig,'08_completion',checks={'integer_factor_completion':True,'max_singular_discrepancy':float(np.max(abs(full-complete)))})

    xx=np.linspace(0,7,800);theta=15
    fig,ax=ac('Exponential tilting centers the law on the tail query',
       'Q = 0.02 χ²₈₀; q = 4; θ = 15. The tilted mean equals the query.')
    ax.plot(xx,gamma.pdf(xx,40,scale=.04),color=EXACT,label='Original density')
    ax.plot(xx,gamma.pdf(xx,40,scale=.1),color=APPROX,ls='--',label='Tilted density')
    ax.axvline(4,color=BOUND,ls=':',lw=1.3);ax.text(4.12,1.4,'q = 4',fontsize=9,color=BOUND)
    ax.set(xlabel=r'Quadratic-form value $x$',ylabel='Density',xlim=(0,7),ylim=(0,1.8));legend(ax,2)
    toy_save(fig,'09_tilt',checks={'tilted_mean':4})

    packet=np.array([.09,.095,.1,.105,.11]);mu=float(packet.mean());delta=packet-mu;u=np.linspace(0,18,220);s=1+1j*u
    alpha=2*s/(1-2*s*mu);rho=np.abs(alpha)*max(abs(delta));exact=-.5*np.log(1-2*s[:,None]*packet).sum(axis=1)
    errors=[];bounds=[]
    for p in range(1,9):
        approx=-len(packet)/2*np.log(1-2*s*mu)
        for j in range(1,p+1):approx+=.5*alpha**j*np.sum(delta**j)/j
        errors.append(float(np.max(abs(exact-approx))))
        bounds.append(float(np.max(len(packet)/2*rho**(p+1)/((p+1)*(1-rho)))))
    assert max(rho)<1 and np.all(np.array(errors)<=np.array(bounds)+1e-13)
    fig,ax=ac('Centered packets compress the transform on its query grid',
       'Coefficients 0.090, 0.095, 0.100, 0.105, 0.110. Center μ = 0.1; θ = 1; 0 ≤ u ≤ 18.')
    series(ax,range(1,9),errors,'Floating transform error',0);series(ax,range(1,9),bounds,'Analytic remainder',2)
    logaxis(ax);ax.set(xlabel='Retained moment order',ylabel='Maximum CGF error\non the declared grid',xticks=range(1,9));legend(ax,2)
    toy_save(fig,'10_packet',checks={'rho_max':float(max(rho)),'errors_below_bounds_float_check':True})

    fig,ax=ac('The same packet behaves differently at different tilts',
       'A larger tilt changes the complex-grid radius, even though the five coefficients are unchanged.')
    for i,th in enumerate([0,2,4]):
        s=th+1j*u;ratio=abs(2*s/(1-2*s*mu))*max(abs(delta))
        ax.plot(u,ratio,color=COLORS[i],ls=STYLES[i],label=rf'$\theta={th}$')
    ax.set(xlabel=r'COS frequency $u$',ylabel=r'Packet radius ratio $\rho(\theta+iu)$',xlim=(0,18),ylim=(0,.43));legend(ax,3)
    toy_save(fig,'11_query_grid')

    fig,ax=ac('Integrate a weighted tail against cosine modes',
       'The jump at q is displayed explicitly. q = 4; b = 7; θ = 15.',rect=[.135,.22,.81,.54])
    xx=np.linspace(0,7,1000)
    for i,k in enumerate([1,2,5]):ax.plot(xx,np.cos(k*np.pi*xx/7),color=COLORS[i],ls=STYLES[i],lw=1.05,alpha=.68,label=rf'$k={k}$')
    xp=np.linspace(4,7,700);pay=np.exp(-15*(xp-4))
    ax.fill_between(xp,0,pay,color=EXACT,alpha=.13)
    ax.plot([0,4],[0,0],color=EXACT,lw=2)
    ax.plot(xp,pay,color=EXACT,lw=2,label='Weighted payoff')
    ax.scatter([4],[0],facecolors='white',edgecolors=EXACT,s=20,zorder=6);ax.scatter([4],[1],color=EXACT,s=22,zorder=6)
    ax.set(xlabel=r'$x$ in the finite interval $[0,b]$',ylabel='Basis / weighted payoff',xlim=(0,7),ylim=(-1.2,1.25));legend(ax,4,fontsize=7.8)
    toy_save(fig,'12_cos')

    fig,ax=ac('More active coefficients accelerate transform decay',
       'All coefficients are 0.02; θ = 0.5. The characteristic-function magnitude starts at one.')
    u=np.geomspace(.01,100,400)
    for i,r in enumerate([80,8]):
        aj=.04/(1-.02);mod=np.exp(-r/4*np.log1p((aj*u)**2))
        ax.plot(u,mod,color=COLORS[i],ls=STYLES[i],lw=1.8,label=f'Rank {r}')
    logaxis(ax,'x');logaxis(ax);ax.set(xlabel=r'Frequency $u$',ylabel=r'$|\phi_\theta(u)|$',ylim=(1e-27,3));ax.set_yticks([1,1e-5,1e-10,1e-15,1e-20,1e-25]);legend(ax,2)
    toy_save(fig,'13_mode_decay')

    # A dependency diagram with explicit path scope, rather than four unrelated boxes.
    fig,ax=ac('Refine the cause of uncertainty, not just a total',
       'The exact-spectrum interval path omits packet approximation; arithmetic width is a separate obligation.',diagram=True)
    cols=[EXACT,BOUND,BOUND,APPROX]
    titles=['Packet error','Support / alias','Omitted modes','Arithmetic width']
    body=['Split the packet\nor raise its order','Extend the\nsupport endpoint','Retain more\ncosine modes','Raise directed\nprecision']
    for i in range(4):
        xx=.03+i*2.52;card(ax,xx,1.4,2.35,2.7,titles[i],body[i],cols[i],True)
        arrow(ax,(xx+1.17,1.3),(5,.55),cols[i],.8)
    number(ax,5,.2,'Combine justified errors, then test the resulting enclosure',size=8.3,color=EXACT)
    toy_save(fig,'14_ledger')

    fig,ax=ac('Acceptance is determined by logarithmic interval width',
       'Illustrative ε = 10⁻⁸. Directed arithmetic, not the plotted curve, is required for a certified decision.')
    w=np.linspace(0,1.1e-8,250);v=np.expm1(np.log(10)*w);cut=np.log1p(1e-8)/np.log(10)
    ax.axvspan(0,cut*1e9,color=APPROX,alpha=.09)
    ax.plot(w*1e9,v*1e8,color=EXACT,lw=1.8)
    ax.axhline(1,color=BOUND,lw=1.2,ls='--');ax.axvline(cut*1e9,color=APPROX,lw=1,ls=':')
    ax.text(1.1,2.1,'Accepted\nwidth region',color=APPROX,fontsize=9)
    ax.text(6.9,.82,'Tolerance',color=BOUND,fontsize=8.5)
    ax.set(xlabel=r'Logarithmic width $w$ ($\times10^{-9}$)',ylabel=r'Multiplicative width ($\times10^{-8}$)',xlim=(0,11),ylim=(0,2.8))
    toy_save(fig,'15_acceptance',checks={'maximum_acceptable_log_width':cut})

    qpoints=[1.6,2,4,8,16,32,64,128,256,500];logs=[]
    with localcontext() as ctx:
        ctx.prec=90
        for q in qpoints:
            z=Decimal(str(q))/Decimal('.04');sm=sum(z**k/Decimal(math.factorial(k)) for k in range(40));logs.append(float((-z+sm.ln())/Decimal(10).ln()))
    fig,ax=ac('An independent exact law remains usable in extreme tails',
       'Positive Erlang finite sum evaluated with 90 decimal digits. The plotted values are not intervals.')
    series(ax,qpoints,logs,index=0)
    ax.axhline(-5000,color=BOUND,ls=':',lw=1);ax.text(20,-4850,r'$10^{-5000}$',color=BOUND,fontsize=9)
    ax.set(xlabel=r'Threshold $q$',ylabel=r'$\log_{10}\,P(0.02\chi^2_{80}\geq q)$',xlim=(0,520),ylim=(-5600,200));comma(ax,'y')
    toy_save(fig,'16_exact_control',checks={'thresholds':qpoints,'log10_survival':logs,'decimal_precision':90})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group',choices=['all','main','atlas'],default='all')
    args=parser.parse_args()
    old={}
    if (QA/'figure_manifest.json').exists():
        old={r['figure']:r for r in json.loads((QA/'figure_manifest.json').read_text())}
    if args.group in ['main','all']:
        for fun in [basic_diagrams,streaming_and_structure,spectra_and_residuals,worked_and_interval,empirical_controls]:
            print('Generating',fun.__name__,flush=True);fun()
    if args.group in ['atlas','all']:atlas()
    for r in RECORDS:old[r['figure']]=r
    (QA/'figure_manifest.json').write_text(json.dumps(list(old.values()),indent=2)+'\n')
    print('Generated',len(RECORDS),'figures;',len(old),'in manifest.',flush=True)

if __name__=='__main__':main()
