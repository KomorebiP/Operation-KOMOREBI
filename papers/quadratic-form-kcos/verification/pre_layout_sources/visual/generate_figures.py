#!/usr/bin/env python3
"""Regenerate every exact-model illustration in the K-COS visual guide.

All inputs are declared here. Integer identities are checked exactly. Floating
plots are explanatory evaluations of finite toy models, not probability
enclosures or production benchmarks. Run: python generate_figures.py.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import numpy as np
import scipy
from scipy.stats import gamma
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from decimal import Decimal, localcontext
from math import factorial

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--record-output',help='Also save the finite control record here for a provenance runner.')
args=parser.parse_args()
NAVY, TEAL, GOLD, RED, GRAY = '#17334d', '#168b8d', '#d99a2b', '#b55752', '#77828c'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.labelcolor': NAVY, 'text.color': NAVY, 'axes.edgecolor': '#bac4cc',
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.alpha': .18, 'figure.facecolor': 'white',
    'savefig.facecolor': 'white', 'pdf.fonttype': 42, 'ps.fonttype': 42})
checks = {}

def save(fig, name):
    pdf_tmp=OUT / (name + '.pdf.tmp')
    png_tmp=OUT / (name + '.png.tmp')
    fig.savefig(pdf_tmp, format='pdf', bbox_inches='tight', pad_inches=.12)
    fig.savefig(png_tmp, format='png', bbox_inches='tight', pad_inches=.12, dpi=220)
    pdf_tmp.replace(OUT / (name+'.pdf'))
    png_tmp.replace(OUT / (name+'.png'))
    plt.close(fig)

def box(ax, xy, width, height, title, detail='', color=TEAL):
    x,y=xy
    ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0.025',
                              ec=color, fc='#f6f9fa', lw=1.4))
    ax.text(x+width/2,y+height*.66,title,ha='center',va='center',weight='bold',fontsize=12)
    ax.text(x+width/2,y+height*.29,detail,ha='center',va='center',fontsize=10)

# Declared integer factor shared by the algebraic pages.
A = np.array([[2,1,0,0,1,0,0,1,0], [1,2,1,0,0,1,0,0,1],
              [0,1,2,1,0,0,1,0,0], [0,0,1,2,1,0,0,1,0],
              [1,0,0,1,2,1,0,0,1], [0,1,0,0,1,2,1,0,0]], dtype=np.int64)
blocks = [A[:, i:i+3] for i in (0,3,6)]
K = A @ A.T
assert np.array_equal(sum((b@b.T for b in blocks)), K)
checks['integer_block_gram'] = {'shape':[6,9], 'block_widths':[3,3,3], 'exact':True}

fig,ax=plt.subplots(figsize=(8.5,3.2)); ax.set(xlim=(0,10),ylim=(0,3.7));ax.axis('off')
items=[('Factor','resident blocks',TEAL),('Operator','phase / range',TEAL),
       ('Spectrum','spikes + packets',GOLD),('Tail','enclosure + decision',RED)]
for i,(title,detail,c) in enumerate(items):
    box(ax,(.12+i*2.5,1.25),2.18,1.5,title,detail,c)
    if i<3:ax.annotate('',xy=(2.56+i*2.5,2),xytext=(2.32+i*2.5,2),arrowprops={'arrowstyle':'->','color':NAVY,'lw':1.7})
ax.text(5,.35,'An accuracy obligation travels with each approximation.',ha='center',fontsize=13)
save(fig,'00_pipeline')

fig,axs=plt.subplots(1,2,figsize=(8.6,3.1),gridspec_kw={'width_ratios':[1,1.5]})
im=axs[0].imshow(K,cmap='Blues');axs[0].set(title=r'$K=AA^{\mathsf{T}}$',xlabel='sample coordinate',ylabel='sample coordinate')
axs[0].grid(False);fig.colorbar(im,ax=axs[0],fraction=.046,pad=.04)
large=np.linalg.eigvalsh(K); small=np.linalg.eigvalsh(A.T@A); positive=small[small>1e-10]
axs[1].plot(np.arange(1,7),large,'o-',color=TEAL,label=r'$AA^{\mathsf{T}}$')
axs[1].scatter(np.arange(1,7),positive,s=85,facecolors='none',edgecolors=GOLD,label=r'nonzero $A^{\mathsf{T}}A$')
axs[1].set(xlabel='eigenvalue index',ylabel='coefficient',title='One nonzero spectrum, two spaces');axs[1].legend(fontsize=10)
checks['nonzero_spectrum_float_max_abs_error']=float(np.max(np.abs(large-positive)))
save(fig,'01_factor_spectrum')

fig,axs=plt.subplots(1,4,figsize=(9,2.9))
vmax=K.max()
for i,ax in enumerate(axs):
    matrix=blocks[i]@blocks[i].T if i<3 else K
    ax.imshow(matrix,cmap='Blues',vmin=0,vmax=vmax);ax.grid(False);ax.set_xticks([]);ax.set_yticks([])
    ax.set_title(r'$A_%dA_%d^{\mathsf{T}}$'%(i+1,i+1) if i<3 else r'$AA^{\mathsf{T}}$')
    if i<3: ax.text(1.12,.5,'+' if i<2 else '=',transform=ax.transAxes,fontsize=23,va='center')
fig.text(.5,.02,'Exact integer model: three column blocks; every cross-sample interaction remains.',ha='center',fontsize=11)
save(fig,'02_block_gram')

fig,ax=plt.subplots(figsize=(8.5,3.4))
m=np.linspace(512,50000,160);n,c,s,p=2000,512,32,3
resident_elements=n*c+2*n*s+c*s+n*p
ax.plot(m,8*n*m/2**30,color=NAVY,lw=2.4,label=r'full factor: $8nm$ bytes')
ax.axhline(8*resident_elements/2**30,color=TEAL,lw=2.4,label='illustrative streamed payload')
ax.set(xlabel='total factor column count m',ylabel='GiB of binary64 payload',ylim=(0,.82),xlim=(0,50000))
ax.legend(loc='upper left');ax.text(29000,.12,'Fixed resident width c = 512\nBlock-vector width s = 32',fontsize=11)
checks['memory_payload']={'n':n,'c':c,'s':s,'p':p,'formula':'8*(n*c+2*n*s+c*s+n*p)',
    'bytes':8*resident_elements,'exclusions':['backend workspace','I/O buffers','stored output','spectral solver']}
save(fig,'03_memory')

fig,ax=plt.subplots(figsize=(8.2,3.5));ax.set(xlim=(-.5,4.7),ylim=(-.4,3.7),aspect='equal');ax.grid(alpha=.2)
ax.axhline(0,color=GRAY,lw=1);ax.axvline(0,color=GRAY,lw=1)
for end,c,label in [((4,3),NAVY,'original feature'),((4,0),GOLD,'covariate component'),((0,3),TEAL,'residual feature')]:
    ax.annotate('',xy=end,xytext=(0,0),arrowprops={'arrowstyle':'->','color':c,'lw':2.5})
    ax.text(end[0]+.07,end[1]+.07,label,color=c,fontsize=11)
ax.plot([4,4],[0,3],':',color=GRAY);ax.plot([0,4],[3,3],':',color=GRAY)
ax.set(xlabel='coordinate in covariate span',ylabel='orthogonal coordinate')
save(fig,'04_residualization')

# A scalar phase chain: H is positive definite, and has exact one-step locality.
H = 2*np.eye(9,dtype=np.int64)+np.eye(9,k=1,dtype=np.int64)+np.eye(9,k=-1,dtype=np.int64)
x=np.zeros(9,dtype=np.int64);x[4]=1
profiles=np.array([np.linalg.matrix_power(H,k)@x for k in range(5)])
for k in range(5):assert all(profiles[k,j]==0 for j in range(9) if abs(j-4)>k)
checks['integer_phase_cone']={'phases':9,'start_phase':5,'depths':list(range(5)),'exact_zeros':True}
fig,ax=plt.subplots(figsize=(8.4,3.4))
ax.imshow(profiles!=0,cmap=matplotlib.colors.ListedColormap(['#f1f4f6',TEAL]),aspect='auto',origin='lower')
ax.set(xticks=range(9),xticklabels=range(1,10),yticks=range(5),xlabel='phase address',ylabel='operator depth k')
ax.grid(False)
for k in range(5):
    for j in range(9):
        if profiles[k,j]!=0:ax.text(j,k,str(profiles[k,j]),color='white',ha='center',va='center',fontsize=10)
save(fig,'05_phase_cone')

H0=H.astype(float); Hw=H0.copy();Hw[0,8]=Hw[8,0]=-.035
B=np.abs(Hw);B0=np.abs(H0)
actual=[];envelope=[]
for k in range(1,9):
    actual.append(np.linalg.norm((np.linalg.matrix_power(Hw,k)-np.linalg.matrix_power(H0,k))@x))
    envelope.append(np.linalg.norm((np.linalg.matrix_power(B,k)-np.linalg.matrix_power(B0,k))@x))
assert np.all(np.array(actual)<=np.array(envelope)+1e-8)
fig,ax=plt.subplots(figsize=(8.4,3.4));ax.semilogy(range(1,9),np.maximum(actual,1e-13),'o-',color=TEAL,label='floating observed power error')
ax.semilogy(range(1,9),np.maximum(envelope,1e-13),'s--',color=GOLD,label='phase-transfer envelope')
ax.set(xlabel='operator depth k',ylabel='Euclidean norm',xticks=range(1,9));ax.legend()
checks['approximate_phase_cone']={'weak_edge':[1,9],'signed_weight':-.035,'depths':list(range(1,9)),
    'floating_error':actual,'floating_envelope':envelope,'enclosure_float_check':True}
save(fig,'06_approximate_cone')

U=np.eye(6)[:,:3].astype(np.int64);P=U@U.T;Bc=U.T@A;F=(np.eye(6,dtype=np.int64)-P)@A
assert np.array_equal(A.T@A, Bc.T@Bc+F.T@F)
rvals=np.linalg.eigvalsh(F@F.T);rvals=rvals[rvals>1e-10]
t=int(np.trace(F.T@F));v=int(np.trace((F.T@F)@(F.T@F)));rho=float(rvals.max())
fig,axs=plt.subplots(1,2,figsize=(8.4,3.5))
axs[0].bar(range(1,4),rvals,color=TEAL);axs[0].set(xlabel='unresolved eigenvalue index',ylabel='coefficient',title='Residual spectrum is positive')
axs[1].axis('off');box(axs[1],(.08,.62),.82,.22,'trace t = '+str(t),'total missing mean')
box(axs[1],(.08,.32),.82,.22,'square trace v = '+str(v),'concentration of missing mass',GOLD)
box(axs[1],(.08,.02),.82,.22,r'cap ρ ≈ %.3f'%rho,'largest unresolved coefficient',RED)
checks['integer_core_residual']={'exact':True,'captured_dimension':3,'trace':t,'square_trace':v,
    'spectral_cap_float':rho,'residual_rank':3,'rank_lower_bound_float':int(np.ceil(max(t/rho,t*t/v)))}
save(fig,'07_residual')

W=np.eye(6,dtype=np.int64)[:,3:];D=W.T@F;C=np.vstack([Bc,D]);A_complete=np.column_stack([U,W])@C
assert np.array_equal(A,A_complete)
fig,ax=plt.subplots(figsize=(8.4,3.4))
full=np.linalg.svd(A,compute_uv=False);partial=np.linalg.svd(Bc,compute_uv=False);completed=np.linalg.svd(C,compute_uv=False)
ax.plot(range(1,7),full,'o-',color=NAVY,label='full factor')
ax.scatter(range(1,7),completed,s=110,facecolors='none',edgecolors=TEAL,label='completed core')
ax.plot(range(1,4),partial,'s--',color=GOLD,label='captured core only')
ax.set(xlabel='singular-value index, descending',ylabel='singular value',xticks=range(1,7));ax.legend()
checks['integer_residual_completion']={'exact_factor_reconstruction':True,
    'floating_singular_max_error':float(np.max(np.abs(full-completed))),'completed_shape':list(C.shape)}
save(fig,'08_completion')

lam=.02;df=80;query=4;shape=df/2;theta=(1-df*lam/query)/(2*lam)
xx=np.linspace(0,7,700)
fig,ax=plt.subplots(figsize=(8.4,3.4));ax.plot(xx,gamma.pdf(xx,shape,scale=2*lam),color=NAVY,lw=2,label='original law')
ax.plot(xx,gamma.pdf(xx,shape,scale=2*lam/(1-2*theta*lam)),color=TEAL,lw=2,label='tilted law')
ax.axvline(query,color=RED,ls='--',label='query q = 4');ax.set(xlabel='quadratic-form value x',ylabel='density')
ax.legend();ax.set_ylim(0,1.7)
checks['tilt_control']={'law':'0.02 chi-square(80)','query':query,'theta':theta,'tilted_mean':query}
save(fig,'09_tilt')

packet=np.array([.09,.095,.10,.105,.11]);mu=packet.mean();d=packet-mu;npack=len(packet)
theta_pkt=1.0;freqs=np.linspace(0,18,220);complex_grid=theta_pkt+1j*freqs
alpha=2*complex_grid/(1-2*complex_grid*mu);rho_grid=np.abs(alpha)*np.max(np.abs(d))
assert rho_grid.max()<1
exact=-.5*np.log(1-2*complex_grid[:,None]*packet).sum(axis=1)
orders=range(1,9);errs=[];bounds=[]
for order in orders:
    approx=-npack/2*np.log(1-2*complex_grid*mu)
    for j in range(1,order+1):approx=approx+.5*alpha**j*np.sum(d**j)/j
    errs.append(float(np.max(np.abs(exact-approx))))
    bound=npack/2*rho_grid**(order+1)/((order+1)*(1-rho_grid))
    bounds.append(float(np.max(bound)))
assert np.all(np.array(errs)<=np.array(bounds)+1e-13)
fig,axs=plt.subplots(1,2,figsize=(8.5,3.3),gridspec_kw={'wspace':.48,'width_ratios':[1,1.3]})
axs[0].scatter(packet,np.zeros(len(packet)),s=100,color=TEAL);axs[0].axvline(mu,color=GOLD,ls='--');axs[0].set(xlabel='eigenvalue λ',yticks=[],ylim=(-.5,.5),title='Center and deviations')
axs[0].text(mu,.18,r'center $\mu=0.10$',ha='center',fontsize=11)
axs[1].semilogy(list(orders),errs,'o-',color=TEAL,label='floating log-transform error')
axs[1].semilogy(list(orders),bounds,'s--',color=GOLD,label='analytic remainder');axs[1].set(xlabel='packet order p',ylabel='maximum on declared grid',xticks=list(orders));axs[1].legend(fontsize=9)
checks['packet_control']={'eigenvalues':packet.tolist(),'center':float(mu),'orders':list(orders),
    'theta':theta_pkt,'frequency_min':0,'frequency_max':18,'grid_points':220,'rho_max':float(rho_grid.max()),
    'floating_errors':errs,'analytic_bounds':bounds,'float_check':True}
save(fig,'10_packet')

fig,ax=plt.subplots(figsize=(8.4,3.4))
for th,c in [(0,NAVY),(2,TEAL),(4,GOLD)]:
    ss=th+1j*freqs;rr=np.abs(2*ss/(1-2*ss*mu))*max(abs(d))
    ax.plot(freqs,rr,color=c,lw=2,label=r'tilt $\theta=%d$'%th)
ax.set(xlabel='COS frequency u',ylabel=r'packet radius ratio $\rho(\theta+iu)$',ylim=(0,.42));ax.legend()
ax.text(.02,.88,'Same five eigenvalues; same packet center.\nThe query changes the admissible expansion ratio.',transform=ax.transAxes,fontsize=11)
save(fig,'11_query_grid')

q,Ucos,thetacos=4,7,15
fig,axs=plt.subplots(1,2,figsize=(8.6,3.3));xx=np.linspace(0,Ucos,550)
pay=np.where(xx>=q,np.exp(-thetacos*(xx-q)),0)
axs[0].plot(xx,pay,color=TEAL,lw=2);axs[0].set(xlabel='x in [0, U]',ylabel='weighted payoff',title='Integrate the tail directly');axs[0].axvline(q,color=RED,ls='--')
for k,c in [(1,NAVY),(2,TEAL),(5,GOLD)]:axs[1].plot(xx,np.cos(k*np.pi*xx/Ucos),color=c,label='k = '+str(k))
axs[1].set(xlabel='x in [0, U]',ylabel='cosine mode',title='Modes on the finite interval');axs[1].legend(fontsize=9)
save(fig,'12_cos')

fig,ax=plt.subplots(figsize=(8.4,3.4));tt=np.geomspace(.01,100,350)
for coeffs,c,label in [([.02]*80,NAVY,'80 equal coefficients'),([.02]*8,TEAL,'8 equal coefficients')]:
    coeffs=np.array(coeffs);a=2*coeffs/(1-2*.5*coeffs)
    logmod=-.25*np.log1p((a[:,None]*tt)**2).sum(axis=0)
    ax.loglog(tt,np.exp(logmod),color=c,lw=2,label=label)
ax.set(xlabel='frequency t',ylabel=r'$|\phi_\theta(t)|$',ylim=(1e-22,1.2));ax.legend(loc='lower left')
ax.text(.04,.90,'Declared tilt θ = 0.5\nMagnitude is normalized to 1 at t = 0.',transform=ax.transAxes,fontsize=11)
save(fig,'13_mode_decay')

fig,ax=plt.subplots(figsize=(8.5,3.5));ax.set(xlim=(0,10),ylim=(0,4));ax.axis('off')
ledger=[('Packet\nerror','split / increase\norder',TEAL),('Support\n+ alias','increase upper\nendpoint',GOLD),
        ('Omitted\nmodes','increase mode\ncount',NAVY),('Arithmetic\nwidth','increase\nprecision',RED)]
for i,(title,detail,col) in enumerate(ledger):
    box(ax,(.2+i*2.5,1.4),2.12,1.65,title,detail,col)
ax.text(5,.55,'Add justified bounds; test the resulting enclosure.',ha='center',fontsize=13)
save(fig,'14_ledger')

fig,ax=plt.subplots(figsize=(8.4,3.4));xs=np.linspace(0,1.1e-8,250)
ax.plot(xs,np.expm1(np.log(10)*xs),color=TEAL,lw=2.4)
ax.axhline(1e-8,color=RED,ls='--',label=r'requested $\varepsilon=10^{-8}$')
cut=np.log1p(1e-8)/np.log(10);ax.axvline(cut,color=GOLD,ls=':',label='largest acceptable log width')
ax.set(xlabel=r'logarithmic interval width $w=d_+-d_-$',ylabel=r'multiplicative uncertainty $10^w-1$')
ax.ticklabel_format(style='sci',axis='both',scilimits=(0,0));ax.legend(fontsize=10)
save(fig,'15_acceptance')

# Exact-law control: even-degree chi-square survival is an Erlang finite sum.
qpoints=[1.6,2,4,8,16,32,64,128,256,500]
logs=[]
with localcontext() as context:
    context.prec=90
    for qv in qpoints:
        z=Decimal(str(qv))/Decimal('.04')
        l= -z+sum((z**k/Decimal(factorial(k)) for k in range(40))).ln()
        logs.append(str(l/Decimal(10).ln()))
fig,ax=plt.subplots(figsize=(8.4,3.4));ax.plot(qpoints,[float(z) for z in logs],'o-',color=NAVY,lw=2)
ax.set(xlabel='threshold q',ylabel=r'$\log_{10}\,P(0.02\chi^2_{80}\geq q)$')
ax.text(.05,.12,'Evaluate the logarithm of a positive finite sum.\nThe law is exact; plotted arithmetic is high-precision numerical.',transform=ax.transAxes,fontsize=11)
checks['erlang_control']={'lambda_decimal':'0.02','degrees':80,'arithmetic':'Python Decimal 90 digits; not an interval enclosure',
    'thresholds_decimal':[str(z) for z in qpoints],'log10_survival':logs,
    'formula':'-q/.04 + log(sum((q/.04)^k/k!, k=0..39))'}
save(fig,'16_exact_control')

record={'status':'finite illustration checks passed', 'scope':'Declared toy models only; floating checks are not interval certificates.',
    'command':'python generate_figures.py','software':{'python':platform.python_version(),
    'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},
    'checks':checks,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
record['figure_files']=[{'path':str(p.relative_to(ROOT)),
    'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(OUT.glob('*')) if p.suffix in {'.pdf','.png'}]
(ROOT/'finite_control.json').write_text(json.dumps(record,indent=2)+'\n')
if args.record_output:
    Path(args.record_output).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'figures':len(list(OUT.glob('*.pdf'))),'control_record':'finite_control.json'}))
