"""Four exact bridges between seeds, taps, responses and generating functions.

Run: python figures_bridges.py
All sequence and polynomial arithmetic is exact. Floating point is used only
for figure placement, logarithmic coordinates, and the declared display mesh.
"""
from fractions import Fraction as Q
from math import comb, log10, sqrt
from datetime import datetime, timezone
import hashlib
import json
import platform
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from guide_style import ROOT, COLORS, INK, MUTED, PALE, save_figure

N = 18
STEMS=['B01_surviving_modes','B02_recurrence_tap_reduction',
       'B03_reciprocal_stability','B04_catalan_integration']

def mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return trim(out)

def add(a,b,sign=1):
    out=[Q(0)]*max(len(a),len(b))
    for i,x in enumerate(a):out[i]+=x
    for i,x in enumerate(b):out[i]+=sign*x
    return trim(out)

def trim(a):
    out=list(a)
    while len(out)>1 and out[-1]==0:out.pop()
    return out

def poly_div(a,b):
    remainder=list(map(Q,trim(a)));b=list(map(Q,trim(b)))
    quotient=[Q(0)]*max(1,len(remainder)-len(b)+1)
    while len(remainder)>=len(b) and any(remainder):
        k=len(remainder)-len(b);c=remainder[-1]/b[-1]
        quotient[k]+=c
        for j,v in enumerate(b):remainder[j+k]-=c*v
        remainder=trim(remainder)
    return trim(quotient),trim(remainder)

def filter_full(h,x):
    # Full finite convolution, including every output-tail coefficient.
    return mul(h,x)

def series_inverse(d,degree=N):
    d=list(map(Q,d));assert d[0]!=0
    out=[1/d[0]]
    for n in range(1,degree+1):
        out.append(-sum(d[k]*out[n-k] for k in range(1,min(n,len(d)-1)+1))/d[0])
    return out

def table(ax,rows,cols,labels=None,font=12,scale=1.5,bbox=None):
    ax.axis('off')
    kwargs={'bbox':bbox} if bbox is not None else {'loc':'center'}
    tab=ax.table(cellText=rows,colLabels=cols,rowLabels=labels,
                 cellLoc='center',rowLoc='center',**kwargs)
    tab.auto_set_font_size(False);tab.set_fontsize(font);tab.scale(1,scale)
    for (row,column),cell in tab.get_celld().items():
        cell.set_edgecolor('#D8E3E4');cell.set_linewidth(.7)
        if row==0 or column==-1:
            cell.set_facecolor(PALE);cell.get_text().set_color(COLORS[0])
    return tab

def qfield_mul(x,y):
    # Exact Q(sqrt(2)) arithmetic, represented as (a,b) for a+b*sqrt(2).
    a,b=x;c,d=y
    return (a*c+2*b*d,a*d+b*c)

def serialize_q(a):
    return [str(v) for v in a]

def main():
    started=datetime.now(timezone.utc).isoformat();t0=time.monotonic()
    input_names=['figures_bridges.py','chapters_bridges.tex','guide_style.py',
                 'source_data/oeis/A000045.txt','source_data/oeis/A000984.txt',
                 'source_data/oeis/A000108.txt','evidence/OEIS_SOURCE_RECORDS.json']
    inputs=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
            for p in input_names]
    checks={}

    # 01: recurrence, exact residual numerator, and closed modes.
    D=[1,-3,2];cases=[]
    seeds=[(1,2),(1,1),(0,1)]
    expected_modes=[(0,1),(1,0),(-1,1)]
    expected_numerators=[[1,-1],[1,-2],[0,1]]
    for index,(a0,a1) in enumerate(seeds):
        a=[a0,a1]
        for n in range(2,N+1):a.append(3*a[-1]-2*a[-2])
        mode=(2*a0-a1,a1-a0)
        assert mode==expected_modes[index]
        assert a==[mode[0]+mode[1]*2**n for n in range(N+1)]
        residual=filter_full(D,a)
        numerator=[a0,a1-3*a0]
        assert numerator==expected_numerators[index]
        assert residual[:N+1]==numerator+[0]*(N-1)
        # Exact factor relations authenticate each canceled candidate pole.
        if index==0:assert mul([1,-1],[1,-2])==list(map(Q,D))
        if index==1:assert mul([1,-2],[1,-1])==list(map(Q,D))
        cases.append({'seeds':[a0,a1],'coefficients':a,'numerator':numerator,
                      'constant_mode_coefficient':mode[0],'dyadic_mode_coefficient':mode[1],
                      'surviving_poles':(['1/2'] if index==0 else ['1'] if index==1 else ['1/2','1'])})
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1.8,1]})
    rows=[['(1, 2)',r'$1-z$',r'$2^n$'],['(1, 1)',r'$1-2z$',r'$1$'],['(0, 1)',r'$z$',r'$2^n-1$']]
    table(axs[0],rows,['Seeds','Numerator','Coefficients'],font=13,scale=1,bbox=[.01,.15,.98,.7])
    axs[0].set_title('Same recurrence, different seeds',pad=12)
    axs[1].set(xlim=(.23,1.2),ylim=(0,1),xticks=[.5,1],yticks=[])
    axs[1].set_xticklabels([r'$z=1/2$',r'$z=1$'])
    axs[1].xaxis.tick_top();axs[1].spines['left'].set_visible(False);axs[1].spines['bottom'].set_visible(False)
    positions=[.5875,.4125,.2375];survives=[[True,False],[False,True],[True,True]]
    for xpos in [.5,1]:axs[1].plot([xpos,xpos],[.16,.66],color='#D8E3E4',lw=1,zorder=0)
    for row,ypos in enumerate(positions):
        for col,xpos in enumerate([.5,1]):
            axs[1].scatter(xpos,ypos,s=135,marker='o' if survives[row][col] else 'x',
                           color=COLORS[0] if survives[row][col] else COLORS[1],linewidth=2,zorder=3)
    axs[1].set_title('Poles after reduction',pad=31)
    axs[1].legend(handles=[Line2D([],[],marker='o',ls='',color=COLORS[0],label='Survives',ms=8),
                          Line2D([],[],marker='x',ls='',color=COLORS[1],label='Canceled',ms=8)],
                  loc='lower center',bbox_to_anchor=(.5,-.04),ncol=2,fontsize=10.5,frameon=False)
    save_figure(fig,STEMS[0]);checks['B01']={'cases':cases,'recurrence_domain':'n>=0','max_sequence_index':N,'pole_cancellation_verified_by_exact_factors':True}

    # 02: exact filter reduction and its initial residual.
    fib=[0,1]
    for n in range(2,N+3):fib.append(fib[-1]+fib[-2])
    D=[1,-1,-1];h=[1,2,1];r=[2,1];q=[-1]
    assert add(r,mul(q,D))==list(map(Q,h))
    quotient,remainder=poly_div(h,D);assert quotient==list(map(Q,q)) and remainder==list(map(Q,r))
    output=[sum(h[k]*fib[n-k] for k in range(3) if n>=k) for n in range(N+1)]
    uncorrected=[2*fib[n]+(fib[n-1] if n else 0) for n in range(N+1)]
    correction=[-int(n==1) for n in range(N+1)]
    corrected=[x+y for x,y in zip(uncorrected,correction)]
    assert corrected==output
    assert output==[fib[n+2]-int(n==0)-int(n==1) for n in range(N+1)]
    # Every finite-input tail is retained: use its actual residual N=D*F.
    finite_contracts=[]
    for length in [1,2,5,12,19]:
        x=fib[:length];residual=filter_full(D,x)
        left=filter_full(h,x);right=add(filter_full(r,x),filter_full(q,residual))
        assert left==right
        finite_contracts.append({'input_length':length,'full_output_length':len(x)+len(h)-1,
                                 'residual':serialize_q(residual),'output':serialize_q(left+[Q(0)]*(len(x)+len(h)-1-len(left)))})
    # General division witnesses (including signed taps, exact rational quotient).
    general_cases=[]
    for kernel in [[1],h,[1,-1],[2,0,3,-2],[Q(1,2),-1,Q(3,4),2,1]]:
        quo,rem=poly_div(kernel,D);assert add(mul(quo,D),rem)==list(map(Q,trim(kernel)))
        x=fib[:12];residual=filter_full(D,x)
        assert filter_full(kernel,x)==add(filter_full(rem,x),filter_full(quo,residual))
        general_cases.append({'h':serialize_q(kernel),'q':serialize_q(quo),'r':serialize_q(rem)})
    fig=plt.figure(figsize=(8.1,4.1),layout='constrained');grid=fig.add_gridspec(2,2,height_ratios=[1.1,1.4])
    left=fig.add_subplot(grid[0,0]);right=fig.add_subplot(grid[0,1]);bottom=fig.add_subplot(grid[1,:])
    for ax,values,color,title in [(left,h,COLORS[0],'Original taps h'),(right,r,COLORS[1],'Reduced taps r')]:
        ax.bar(range(len(values)),values,color=color,width=.56)
        for k,v in enumerate(values):ax.text(k,v+.1,str(v),ha='center',fontsize=13)
        ax.set(xticks=[0,1,2],xlim=(-.55,2.55),ylim=(0,2.75),yticks=[0,1,2],xlabel='Fine delay',ylabel='Weight',title=title)
        ax.grid(axis='y');ax.set_axisbelow(True)
    tab=table(bottom,[output[:8],uncorrected[:8],correction[:8],corrected[:8]],list(range(8)),
              ['Three taps','Two taps','Correction','Corrected'],font=11.5,scale=1.33)
    for row in [2,3]:tab[(row,1)].set_facecolor('#F4DDD3')
    for row in [1,4]:tab[(row,1)].set_facecolor(PALE)
    save_figure(fig,STEMS[1]);checks['B02']={'Fibonacci':fib[:N+1],'h':h,'D':D,'q':q,'r':r,'three_tap_output':output,
           'two_tap_output':uncorrected,'boundary_correction':correction,'corrected_output':corrected,
           'finite_full_support_contracts':finite_contracts,'general_division_witnesses':general_cases,
           'coefficient_range':[0,N],'negative_Fibonacci_indices':'zero'}

    # 03: finite exact convolutions, convergence radii, and bounded/unstable witnesses.
    rates=[Q(1,2),Q(2)];responses=[];step_outputs=[]
    for rate in rates:
        impulse=[rate**n for n in range(N+1)];step=[sum(impulse[:n+1]) for n in range(N+1)]
        assert series_inverse([1,-rate],N)==impulse
        if rate==Q(1,2):assert step==[Q(2)-rate**n for n in range(N+1)]
        else:assert step==[Q(2)**(n+1)-1 for n in range(N+1)]
        responses.append(impulse);step_outputs.append(step)
    # Stable bounded-input finite prefixes, plus the geometric tail sum identity.
    inputs_stable=[[Q(1)]*(N+1),[Q((-1)**n) for n in range(N+1)],
                   [Q(((5*n+3)%11)-5,5) for n in range(N+1)]]
    stable_bounds=[]
    for x in inputs_stable:
        maximum=max(map(abs,x));y=[sum(responses[0][k]*x[n-k] for k in range(n+1)) for n in range(N+1)]
        assert all(abs(v)<=2*maximum for v in y)
        stable_bounds.append({'input_sup_norm':str(maximum),'max_output_abs':str(max(map(abs,y)))})
    assert Q(1)/(1-Q(1,2))==2
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1,1.25]})
    ax=axs[0]
    ax.add_patch(Circle((0,0),2,facecolor=COLORS[0],alpha=.045,edgecolor='none'))
    ax.add_patch(Circle((0,0),.5,facecolor=COLORS[1],alpha=.13,edgecolor='none'))
    ax.add_patch(Circle((0,0),2,fill=False,edgecolor=COLORS[0],lw=1.8))
    ax.add_patch(Circle((0,0),.5,fill=False,edgecolor=COLORS[1],lw=1.8))
    ax.add_patch(Circle((0,0),1,fill=False,edgecolor=MUTED,lw=1.2,ls='--'))
    ax.axhline(0,color='#D8E3E4',lw=.8);ax.axvline(0,color='#D8E3E4',lw=.8)
    ax.scatter([2,.5],[0,0],s=75,c=[COLORS[0],COLORS[1]],zorder=4)
    ax.text(-1.45,1.3,'R = 2',color=COLORS[0],fontsize=12)
    ax.text(.1,-.73,'R = 1/2',color=COLORS[1],fontsize=12)
    ax.annotate('unit circle',xy=(-.7,-.7),xytext=(-2.1,-1.67),fontsize=11.5,arrowprops={'arrowstyle':'->','lw':1,'color':MUTED})
    ax.annotate('poles',xy=(2,0),xytext=(1.3,.75),fontsize=11.5,arrowprops={'arrowstyle':'->','lw':1,'color':COLORS[0]},color=COLORS[0])
    ax.set(xlim=(-2.3,2.3),ylim=(-2.25,2.25),xticks=[-2,-1,0,1,2],yticks=[-2,-1,0,1,2],xlabel='Re z',ylabel='Im z',title='Series convergence in z');ax.set_aspect('equal')
    axs[1].plot(range(N+1),list(map(float,step_outputs[0])),'-o',ms=3.8,label=r'$r=1/2$',color=COLORS[0])
    axs[1].plot(range(N+1),list(map(float,step_outputs[1])),'-s',ms=3.8,label=r'$r=2$',color=COLORS[1])
    axs[1].axhline(2,color=COLORS[0],ls=':',lw=1.2);axs[1].text(12,2.6,'limit 2',fontsize=11,color=COLORS[0])
    axs[1].set_yscale('log');axs[1].set(xlabel='Output index n',ylabel='Output y[n] (log scale)',title='Same constant input x[n] = 1',xticks=[0,3,6,9,12,15,18],ylim=(.8,1e6))
    axs[1].grid(axis='y');axs[1].legend(loc='upper left',fontsize=11)
    save_figure(fig,STEMS[2]);checks['B03']={'rates':list(map(str,rates)),'impulse_responses':[serialize_q(x) for x in responses],
        'constant_input_outputs':[serialize_q(x) for x in step_outputs],'series_radii':['2','1/2'],
        'stable_absolute_impulse_sum':'2','stable_prefix_witnesses':stable_bounds,
        'structural_stable_bound':'triangle inequality and sum_{k>=0}(1/2)^k=2',
        'structural_unstable_witness':'bounded input one produces 2^(n+1)-1',
        'unit_circle_note':'For r=2 the rational function is finite on the unit circle, but the causal series diverges there because its terms do not tend to zero.',
        'tested_output_indices':[0,N]}

    # 04: exact binomial coefficients, formal integration, and algebraic area value.
    binomial=[comb(2*n,n) for n in range(N+1)]
    catalan=[Q(binomial[n],n+1) for n in range(N+1)]
    assert all(v.denominator==1 for v in catalan)
    # (1-4z)B'=2B exactly forces the central-binomial Taylor coefficients.
    assert all((n+1)*binomial[n+1]==2*(2*n+1)*binomial[n] for n in range(N))
    integrated=[Q(0)]+[Q(binomial[n],n+1) for n in range(N+1)]
    assert integrated[1:]==catalan
    # The algebraic Catalan equation independently checks its normalized prefix.
    assert catalan[0]==1
    assert all(catalan[n+1]==sum(catalan[k]*catalan[n-k] for k in range(n+1)) for n in range(N))
    z_exact=Q(1,8);area_pair=(Q(1,2),-Q(1,4));average_pair=(Q(4),-Q(2))
    assert qfield_mul((z_exact,Q(0)),average_pair)==area_pair
    sqrt_endpoint=(Q(0),Q(1,2));assert qfield_mul(sqrt_endpoint,sqrt_endpoint)==(Q(1,2),Q(0))
    endpoint=float(z_exact);mesh=np.linspace(0,endpoint,1001);curve=1/np.sqrt(1-4*mesh)
    area=float(area_pair[0])+float(area_pair[1])*sqrt(2)
    average=float(average_pair[0])+float(average_pair[1])*sqrt(2)
    trap=float(np.trapezoid(curve,mesh));display_error=abs(trap-area)
    assert display_error<1e-7
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1.4,1]})
    axs[0].fill_between(mesh,0,curve,color=COLORS[0],alpha=.16)
    axs[0].plot(mesh,curve,color=COLORS[0],label=r'$B(t)$')
    axs[0].axhline(average,color=COLORS[1],ls='--',label=r'Average $C(1/8)$')
    axs[0].text(.068,.5,r'Area $=(2-\sqrt{2})/4$',ha='center',va='center',fontsize=12.5,color=COLORS[0])
    axs[0].set(xlabel='Integration coordinate t',ylabel='Function value',xlim=(0,endpoint),ylim=(0,1.8),xticks=[0,1/16,1/8],title='Area divided by interval length')
    axs[0].set_xticklabels(['0',r'$1/16$',r'$1/8$']);axs[0].grid(axis='y');axs[0].legend(loc='upper left',fontsize=11)
    rows=[[0,1,1,1],[4,70,5,14],[5,252,6,42]]
    table(axs[1],rows,['n','b(n)',r'$\div(n+1)$','c(n)'],font=12.5,scale=1.9)
    axs[1].set_title('Integration divides\nby the new exponent',pad=10)
    axs[1].text(.5,.08,'C(0) = 1 by removal',transform=axs[1].transAxes,ha='center',fontsize=12,color=COLORS[0])
    save_figure(fig,STEMS[3]);current=json.loads((ROOT/'evidence/OEIS_SOURCE_RECORDS.json').read_text())
    source_records={record['id']:record for record in current['records']}
    for identifier,generated in [('A000045',fib),('A000984',binomial),('A000108',[int(v) for v in catalan])]:
        assert source_records[identifier]['initial_index']==0
        assert source_records[identifier]['first_eight_terms']==generated[:8]
    checks['B04']={'official_used_sequence_prefixes_checked':['A000045','A000984','A000108'],'central_binomial':binomial,'Catalan':serialize_q(catalan),
        'integral_coefficients':serialize_q(integrated),'coefficient_range':[0,N],
        'OGF_differential_equation_checked_through':N-1,'Catalan_convolution_checked_through_target':N,
        'display_z':'1/8','area_in_Q_sqrt2':serialize_q(area_pair),'average_in_Q_sqrt2':serialize_q(average_pair),
        'exact_area_average_relation':True,'display_mesh_points':1001,'display_polygon_trapezoid_error':display_error,
        'plot_area_value_source':'closed-form elementary integral, not numerical quadrature',
        'analytic_domain':'|z|<1/4, sqrt branch one at zero; C0=1 removable',
        'formal_domain':'Q[[z]], coefficientwise integration'}

    for item in inputs:
        item['sha256_after']=hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
        assert item['sha256_after']==item['sha256']
    outputs=[]
    for stem in STEMS:
        for suffix in ['.pdf','.png']:
            p=ROOT/'figures'/(stem+suffix)
            outputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest={
      'schema_version':1,'claim_id':'operator-bridges-exact-v0.4',
      'repository':{'commit':None,'dirty':True,'artifact_version':'v0.4; local document source; no Git revision'},
      'command':['python','figures_bridges.py'],
      'environment':{'software':[f'Python {platform.python_version()}',f'NumPy {np.__version__}',f'Matplotlib {matplotlib.__version__}'],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Four displayed elementary operator bridges agree with exact finite constructions, polynomial identities and stated independent invariants.',
         'coefficient_domain':'exact Python integers, fractions.Fraction rationals and Q(sqrt2) pairs; floating point only for display',
         'conventions':'ordinary generating functions in fine delay z; causal input zero at negative indices; full finite convolution support retained; exact reduced rational functions',
         'inputs':[p['path'] for p in inputs],'bounds':{'max_sequence_index':N,'finite_Fibonacci_lengths':[1,2,5,12,19],'polynomial_division_witnesses':5,'stable_input_prefixes':3,'area_display_mesh_points':1001},
         'non_claims':['No novelty, Lean certificate, or universal theorem is supplied by the bounded computations.','Exact mode cancellation is not numerical robustness or hidden-state stability.','Recurrence-aware tap reduction applies to the specified input equation DF=N, not arbitrary signals.','Unstable causal Fourier series is not represented by evaluating its rational continuation on the unit circle.','The area plot is a sampled polygon; its labeled exact integral comes from the elementary closed form.']},
      'randomness':{'used':False,'generator':'none','seed':None},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-t0,'exit_status':0},
      'outputs':outputs,'input_artifacts':inputs,
      'checks':[{'id':k,'status':'PASS','details':v} for k,v in checks.items()],
      'result':'implementation and finite assertions verified in the stated ranges; elementary symbolic reductions stated separately',
      'residual_risks':['Legacy-v1 manifest used with supplemental input hashes; no machine-enforced resource caps or Git revision claimed.','Assembled-PDF page layout is verified separately by the parent workflow.']}
    (ROOT/'evidence/bridge_checks.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'bridge_figures':4,'exact_checks':'PASS','runtime_seconds':manifest['run']['runtime_seconds']}))

if __name__=='__main__':main()
