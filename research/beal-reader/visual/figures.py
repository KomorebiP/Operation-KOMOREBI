"""Exact source-linked figures for the Beal visual companion.
Integer/Fraction and finite-field calculations determine data. Floating drawing
coordinates illustrate topology only, never an arithmetic realization.
"""
from pathlib import Path
from fractions import Fraction as F
from math import gcd
import argparse,hashlib,json,platform,time,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch,Rectangle
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
SHARED=ROOT.parent/'shared/figures';SHARED.mkdir(parents=True,exist_ok=True)
INK='#243138';TEAL='#21676B';COPPER='#A45C36';PALE='#E9F0EF';GRAY='#627078';RED='#A55050';GOLD='#B67E35'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.labelsize':14,'xtick.labelsize':12,'ytick.labelsize':12,'text.color':INK,'axes.labelcolor':INK,'pdf.fonttype':42,'savefig.facecolor':'white','mathtext.fontset':'dejavusans'})
S=json.loads((ROOT/'inputs/block80_finite_inputs.json').read_text())
P=json.loads((ROOT/'inputs/block80_primary80.json').read_text())
TARGET=json.loads((ROOT/'inputs/block80_target_evaluator80.json').read_text())
TRACE=json.loads((ROOT/'inputs/block47_modular_correlations.json').read_text())
LAYOUT=[];CHECKS=[]
DATA={'conventions':{'positive_equation':'A^x+B^y=C^z, x,y,z>2','primitive':'gcd(A,B,C)=1, equivalent to pairwise coprime in this equation','focused_signature':[3,5,7],'base_field':'Q(sqrt(5)), phi=(1+sqrt(5))/2','coefficient_field':'F7[w]/(w^2-5), encoding a+7b for a+bw','matrix_field':'F7 with deliberate scalar extension to F49','source_pattern_scope':'stipulated depth-one all-inert plus-component necessary system, complete beta support with each beta-ramifying rational prime<=2000','display':'real coordinates and palettes illustrate exact data, not finite-field geometry','nonclaims':['No proof of Beal','No actual affine target or global p0 values','No synthetic target authenticates a Frey representation','No full-signature or unrestricted-conductor closure']},'figures':{}}
def check(name,v):assert v,name;CHECKS.append(name)
def field_add(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
def field_mul(x,y):
 a,b=x%7,x//7;c,d=y%7,y//7
 return (a*c+5*b*d)%7+7*((a*d+b*c)%7)
def field_pow(x,n):
 z=1
 while n:
  if n&1:z=field_mul(z,x)
  x=field_mul(x,x);n//=2
 return z
def matmul(a,b):return [[sum(x*y for x,y in zip(row,col))%7 for col in zip(*b)]for row in a]
def mv(a,v):return [sum(x*y for x,y in zip(row,v))%7 for row in a]
def rank(a):
 b=[list(map(lambda x:x%7,row))for row in a];i=0
 for j in range(len(b[0])):
  pivot=next((k for k in range(i,len(b))if b[k][j]),None)
  if pivot is None:continue
  b[i],b[pivot]=b[pivot],b[i];inv=pow(b[i][j],-1,7);b[i]=[x*inv%7 for x in b[i]]
  for k in range(len(b)):
   if k!=i:
    c=b[k][j];b[k]=[(x-c*y)%7 for x,y in zip(b[k],b[i])]
  i+=1
  if i==len(b):break
 return i
def audit():
 check('shared-prime worked example',3**3+6**3==3**5 and gcd(gcd(3,6),3)==3)
 check('squares boundary worked example',3**2+4**2==5**2 and gcd(3,4)==1)
 check('w^2=5 is nonsquare over F7',5 not in{a*a%7 for a in range(7)})
 for x in range(49):check(f'F49 Frobenius at code{x}',field_pow(x,7)==x%7+7*((-(x//7))%7))
 for t in [F(1,2),F(2,3),F(3,11)]:
  s=1-t; aa=t**12*s**28;bb=t**7*s**17;cc=t**5*s**12
  check(f'rational parameter identity at{t}',aa**3+bb**5==cc**7)
 # Derive q=11 roots from exact source polynomials, not the stored count.
 roots=set()
 for d in TRACE['q11_regular_point_counts']:
  coeff=d['trace_polynomial']+[0]*(3-len(d['trace_polynomial']));c,b,a=coeff
  for x in range(49):
   z=field_add(field_add(field_mul(a,field_mul(x,x)),field_mul(b%7,x)),c%7)
   if z==0:roots.add(x)
 check('q11 trace residues reconstructed',len(roots)==15)
 DATA['q11_roots']=sorted(roots)
 DATA['q11_conjugate_pairs']=[[x,field_pow(x,7)]for x in sorted(roots)]
 for n,v in P['patterns'].items():
  L=v['localization_relations'];J=v['localization_image_basis'];E=v['constraint_matrix'];A=v['global_to_constraint_matrix'];N=v['dual_obstruction_basis'];K=v['kernel_basis'];r=v['rank']
  check(n+' exact EJ equals A',matmul(E,J)==A)
  check(n+' LJ zero',not any(any(row)for row in matmul(L,J)))
  check(n+' L rank14',rank(L)==14)
  check(n+' J rank10',rank(J)==10)
  check(n+' A rank',rank(A)==r)
  check(n+' N rank',rank(N)==15-r)
  check(n+' NA zero',not any(any(row)for row in matmul(N,A)))
  check(n+' kernel rank',rank(K)==10-r)
  check(n+' AKtransposezero',not any(any(row)for row in matmul(A,list(map(list,zip(*K))))))
  check(n+' support9',len(S['patterns'][n]['support'])==9 and S['patterns'][n]['support']==v['support'])
  check(n+' synthetic e1 obstructions',mv(N,v['synthetic_nonimage_target'])==TARGET['examples'][n]['output']['obstruction_coordinates'])
  check(n+' actualtarget explicitlymissing',v['actual_affine_target_computed'] is False and v['particular_cochain_computed']is False)
 check('PatternC certificate determinant1',(3*2-5*1)%7==1)
 for q,scale in [(197,5),(307,2),(337,5),(547,4),(673,1),(743,1),(797,4),(883,3),(1483,1),(1933,1)]:
  DATA.setdefault('inertia_conversion',{})[str(q)]=scale
 for n,v in P['patterns'].items():
  frozen=dict(zip(S['patterns'][n]['support'],S['patterns'][n]['inertia']))
  for row in v['toric_values']:check(n+' inertia conversion at'+str(row['q']),row['c']==DATA['inertia_conversion'][str(row['q'])]*frozen[row['q']]%7)
 DATA['pattern_data']={n:{k:v[k]for k in['support','inertia','rank','homogeneous_dimension_over_k','affine_obstruction_dimension_over_k','remaining_character_support','common_semilinear_bound_if_nonempty','toric_values']}for n,v in P['patterns'].items()}

def canvas():
 f,a=plt.subplots(figsize=(9,5.7));f.subplots_adjust(left=.04,right=.96,bottom=.07,top=.95);a.set(xlim=(0,10),ylim=(0,7));a.axis('off');return f,a
def chart():
 f,a=plt.subplots(figsize=(9,5.7));f.subplots_adjust(left=.14,right=.97,bottom=.19,top=.88);a.spines[['top','right']].set_visible(False);return f,a
def title(a,s):a.text(5,6.62,s,ha='center',va='center',fontsize=17,color=TEAL)
def card(a,x,y,w,h,s,size=16,color=PALE):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.06,rounding_size=.1',facecolor=color,edgecolor=color,lw=1))
 t=a.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=size)
 if not hasattr(a,'_cards'):a._cards=[]
 a._cards.append((t,(x,y,w,h)));return t
def arrow(a,p,q,dashed=False,color=GRAY):a.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=15,color=color,lw=1.6,linestyle='--'if dashed else '-'))
def text(a,x,y,s,size=16,col=INK,ha='center'):return a.text(x,y,s,ha=ha,va='center',fontsize=size,color=col)
def save(f,key,domain,values=None):
 f.canvas.draw();r=f.canvas.get_renderer();texts=[];cards=[]
 for ax in f.axes:
  for t,(x,y,w,h)in getattr(ax,'_cards',[]):
   b=t.get_window_extent(r);p=ax.transData.transform((x+.025,y+.025));q=ax.transData.transform((x+w-.025,y+h-.025));good=b.x0>=p[0]-1 and b.x1<=q[0]+1 and b.y0>=p[1]-1 and b.y1<=q[1]+1
   assert good,(key,'card containment',t.get_text(),b.bounds);cards.append({'text':t.get_text(),'passed':bool(good),'bounds_pixels':list(b.bounds),'inner_bounds_pixels':[p.tolist(),q.tolist()]})
 ignored=set()
 for ax in f.axes:
  for axis in[ax.xaxis,ax.yaxis]:
   lo,hi=sorted(axis.get_view_interval())
   for tick in axis.get_major_ticks()+axis.get_minor_ticks():
    if not lo<=tick.get_loc()<=hi:ignored.update([id(tick.label1),id(tick.label2)])
 for t in f.findobj(matplotlib.text.Text):
  if not t.get_visible()or not t.get_text()or id(t)in ignored:continue
  b=t.get_window_extent(r);good=b.x0>=-1 and b.y0>=-1 and b.x1<=f.bbox.width+1 and b.y1<=f.bbox.height+1
  assert good,(key,'canvas containment',t.get_text(),b.bounds);texts.append({'text':t.get_text(),'bounds_pixels':list(b.bounds)})
 f.savefig(OUT/(key+'.pdf'),metadata={'CreationDate':None,'ModDate':None,'Creator':'Operation Komorebi exact Beal guide'});f.savefig(OUT/(key+'.png'),dpi=160);plt.close(f)
 DATA['figures'][key]={'domain':domain,'values':values or{}}
 LAYOUT.append({'figure':key,'canvas_inches':[9,5.7],'text_bounds_passed':True,'card_text_bounds_passed':True,'text_bounds':texts,'card_text_bounds':cards})
def fig01():
 f,a=canvas();title(a,'The equation permits powers with a shared prime')
 for x,s in[(.2,'A = 3\n3³ = 27'),(3.6,'B = 6\n6³ = 216'),(7,'C = 3\n3⁵ = 243')]:card(a,x,4.35,2.8,1.25,s,size=23)
 text(a,3.3,4.97,'+',25);text(a,6.7,4.97,'=',25)
 for x,s in[(1.6,'3'),(5,'2 · 3'),(8.4,'3')]:text(a,x,3.25,s,26,col=COPPER)
 card(a,1.3,.95,7.4,1.2,'The common prime is 3\ngcd(A, B, C) = 3',size=23)
 save(f,'01_beal_terms','exact nonprimitive positive Beal equation',{'bases':[3,6,3],'exponents':[3,3,5],'terms':[27,216,243],'common_gcd':3})
def fig02():
 f,a=canvas();title(a,'Exponent absorption preserves each base’s prime support')
 for x,orig,red,base in[(.35,12,4,'A³'),(3.7,15,3,'B⁵'),(7.05,14,7,'C²')]:
  card(a,x,3.95,2.6,1.7,f'exponent {orig}\n↓\nexponent {red}',size=20);text(a,x+1.3,2.35,'new base '+base,18)
 card(a,.6,.6,8.8,1.05,'Retain odd prime exponents and exponent 4\nThe resulting signature family is still infinite',size=19)
 save(f,'02_exponent_reduction','coordinatewise exponent absorption; illustrative signature12,15,14',{'source_signature':[12,15,14],'reduced_signature':[4,3,7],'new_base_powers':[3,5,2]})
def fig03():
 f,a=canvas();title(a,'One rational parameter retains three power conditions')
 for x,h,s,col in[(.25,'positive v(t)' ,'v(t) = 3a\nv(1−t) = 0',TEAL),(3.6,'positive v(1−t)' ,'v(t) = 0\nv(1−t) = 5b',TEAL),(6.95,'shared denominator','v(t) = v(1−t)\n= −7c',COPPER)]:
  card(a,x,3.7,2.8,1.6,s,size=19);text(a,x+1.4,5.72,h,16,col=col)
 text(a,5,2.55,'t = A³/C⁷     and     1−t = B⁵/C⁷',22,col=TEAL)
 card(a,.65,.7,8.7,1,'Enforce each valuation condition at its active primes\na, b, c are positive integers in their active sectors',size=17)
 save(f,'03_valuation_packets','written primitive recognition criterion at every rational prime',{'signature':[3,5,7],'active_sectors':[{'m':3,'n':0,'output':[1,0,0]},{'m':0,'n':5,'output':[0,1,0]},{'m':-7,'n':-7,'output':[0,0,1]}]})
def fig04():
 f,a=canvas();title(a,'Universal rational parametrization keeps an integral cost')
 card(a,.45,4.4,9.1,1.15,'A₀ = t¹²s²⁸     B₀ = t⁷s¹⁷     C₀ = t⁵s¹²\ns = 1−t,   0 < t < 1',size=22)
 text(a,5,3.63,'A₀³ + B₀⁵ = C₀⁷',27,col=TEAL)
 card(a,.45,1.9,9.1,1.1,'A = λ³⁵A₀     B = λ²¹B₀     C = λ¹⁵C₀',size=24)
 text(a,5,.73,'The same positive rational λ must make all three bases primitive integers.',15,col=COPPER)
 save(f,'04_rational_scaling','exact polynomial parametrization and weighted scaling identity',{'parameter_exponents':[[12,28],[7,17],[5,12]],'weighted_scale':[35,21,15],'homogeneous_degree':105})
def fig05():
 f,a=canvas();title(a,'A local solution at every place need not be global')
 card(a,.55,4.25,8.9,1.05,'27u⁶ + 3125v¹⁰ = 128w¹⁴\nSquarefree coefficients (a,b,c) = (3,5,2)',size=22)
 for x,h,s in[(.4,'at 2','3 + 5 ≡ 0 (mod 8)'),(3.75,'at 3','10 ≡ 1 (mod 3)'),(7.1,'at 5','6 ≡ 1 (mod 5)')]:
  text(a,x+1.25,3.22,h,20,col=TEAL);card(a,x,1.8,2.5,.95,s,size=16)
 text(a,5,.62,'Local root variables may differ at each prime. Exact integer equality is unproved.',15,col=COPPER)
 save(f,'05_local_saturation','written local squareclass survivor; no integer solution claimed',{'coefficients':[3,5,2],'dyadic_C_even':True,'odd_tests':{'3':1,'5':1},'scope':'all local completions by separate proof, not a single global triple'})
def fig06():
 f,a=canvas();title(a,'Two radicals have different mathematical jobs')
 card(a,.4,3.0,4.2,2.2,'Base field K = ℚ(√5)\nCharacteristic zero\nφ = (1+√5)/2',size=21)
 card(a,5.4,3.0,4.2,2.2,'Coefficient field k = 𝔽₄₉\nCharacteristic seven\nw² = 5',size=21)
 text(a,5,1.83,'No identification of the two radicals is supplied by this notation.',17,col=COPPER)
 card(a,1.3,.45,7.4,.9,'Code a+7b represents a+bw, with a,b ∈ 𝔽₇',size=19)
 save(f,'06_two_fields','base/coefficient domain separation',{'base':'Q(sqrt5)','coefficient':'F7[w]/(w^2-5)','encoding':'a+7b'})
def fig07():
 f,a=chart();roots=DATA['q11_roots'];pairs=DATA['q11_conjugate_pairs'];rr={v:i for i,v in enumerate(roots)}
 a.scatter([rr[x]for x,y in pairs],[rr[y]for x,y in pairs],s=62,color=TEAL,zorder=3)
 for i in range(15):
  for j in range(15):a.scatter([i],[j],s=14,color=PALE,zorder=1)
 a.set(xlim=(-.8,14.8),ylim=(-.8,14.8),xticks=[0,7,14],yticks=[0,7,14],xlabel='First coefficient trace label',ylabel='Conjugate trace label');a.set_title('15 conjugate pairs, compared with 225 marginal pairs',fontsize=17,color=TEAL,pad=14)
 save(f,'07_trace_correlation','q11 source trace-polynomial roots in F49 reconstructed exactly',{'root_codes':roots,'conjugate_pairs':pairs,'joint_count':15,'marginal_pair_count':225,'extra_pairs':210})
def fig08():
 f,a=canvas();title(a,'Precision has a depth and a fixed natural frame')
 for x,depth,s in[(.4,'mod 7','Cocycle classes\nα and opposite β'),(3.75,'mod 49','First digits\np and q'),(7.1,'mod 343','Further integral\nconstraints')]:card(a,x,3.9,2.5,1.5,depth+'\n'+s,size=17)
 arrow(a,(3.04,4.63),(3.6,4.63),color=TEAL);arrow(a,(6.39,4.63),(6.95,4.63),color=TEAL)
 card(a,.8,.85,8.4,1.8,'One natural lattice, frame, and reference ρ₀\nIndependent local basis changes do not supply\none global realization',size=18)
 save(f,'08_depth_frame','precision and normalization diagram',{'precisions':[7,49,343],'actual_frozen_patterns_depth':1,'scope':'shared natural-frame assumptions retained'})
def fig09():
 f,a=canvas();title(a,'Tame inertia and Frobenius must form one matrix word')
 card(a,.5,4.08,9,1.3,'$F T F^{-1} = T^{Q}$\nCompatible tame inertia and arithmetic Frobenius',size=20)
 card(a,.45,2.35,4.15,1.05,'ρ(T) = I + 7M\nM² = 0 over k',size=22)
 card(a,5.4,2.35,4.15,1.05,'M = c [θ, −θ²; 1, −θ]\nc = β(T) ≠ 0',size=19)
 text(a,5,1.05,'cp(F) − bp(T) = −hc      h = (Q−1)/7 mod 7',22,col=TEAL)
 save(f,'09_tame_packet','stipulated first-order toric packet equations',{'M':'c[[theta,-theta^2],[1,-theta]]','p_T':'theta*c','p_F':'theta*b-h','toric':'c*p(F)-b*p(T)=-h*c'})
def fig10():
 f,a=canvas();title(a,'Coefficient Frobenius preserves the full pair')
 card(a,.6,4.05,8.8,1.2,'σ(a+bw) = (a+bw)⁷ = a−bw',size=28)
 for x,s in[(.45,'Fixed part\nσ(a)=a\n𝔽₇'),(5.55,'Negated part\nσ(bw)=−bw\nw𝔽₇')]:card(a,x,1.45,4,1.8,s,size=22)
 text(a,5,.55,'Common semilinearity is an extra condition on the same frame and reference.',15,col=COPPER)
 save(f,'10_semilinearity','F49 Frobenius identity checked for all49 elements',{'elements_checked':49,'plus_dimension_F7':1,'minus_dimension_F7':1})
def fig11():
 f,a=chart();primes=P['prime_order'];z=[[int(q in S['patterns'][n]['support'])for q in primes]for n in'ABCD']
 from matplotlib.colors import ListedColormap
 a.imshow(z,cmap=ListedColormap(['white',TEAL]),vmin=0,vmax=1,aspect='auto');a.set(xticks=range(10),xticklabels=primes,yticks=range(4),yticklabels=list('ABCD'),xlabel='Rational prime in the conditional complete β-support universe',ylabel='Pattern')
 a.tick_params(axis='x',labelsize=11);a.set_title('Each frozen support contains exactly nine primes',color=TEAL,fontsize=20,pad=14)
 save(f,'11_support_sets','four conditional complete beta support sets copied and cardinality checked',{'prime_order':primes,'support_indicator':z,'cardinalities':[sum(r)for r in z]})
def fig12():
 f,a=canvas();title(a,'Four supports retain two conjugate coefficient choices')
 for i,n in enumerate('ABCD'):
  x=.35+i*2.45;u='3w'if n in'AB'else'w';card(a,x,3.25,2,2.15,f'Pattern {n}\nu = +{u}\nu = −{u}',size=21)
 card(a,.7,.6,8.6,1.75,'All eight normalized tuples have r = 6 and a₅ = 1\nNecessary system survivors\nArithmetic solutions are not constructed',size=18)
 save(f,'12_eight_patterns','Block70 stipulated normalized survivor table',{'patterns':{'A':['3w','-3w'],'B':['3w','-3w'],'C':['w','-w'],'D':['w','-w']},'ratio':6,'a5':1,'count':8,'none_eliminated':True})
def fig13():
 f,a=chart();ps=P['prime_order'];vals=[DATA['inertia_conversion'][str(q)]for q in ps]
 a.bar(range(10),vals,color=[COPPER if q%7==6 else TEAL for q in ps]);a.set(xticks=range(10),xticklabels=ps,ylim=(0,6.2),yticks=range(6),xlabel='Support prime q',ylabel='Exact conversion factor in 𝔽₇');a.tick_params(axis='x',labelsize=11)
 a.set_title('Convert frozen β-inertia to the ordinary Artin generator',fontsize=17,color=TEAL,pad=14)
 save(f,'13_artin_conversion','pinned exact inertia scale factors; bars denote residues0..6',{'primes':ps,'factors':vals,'conversion':'c_q = scale_q * s_q mod7'})
def fig14():
 f,a=canvas();title(a,'At a conductor prime, retain its own local unit')
 card(a,.4,4.3,9.2,1.05,'Norm(πq) = q     and     πq = q · uq\nThe rational prime q is the chosen uniformizer',size=22)
 card(a,.4,2.2,4.2,1.15,'Other conjugate terms\nb = 2, …, 6',size=20);card(a,5.4,2.2,4.2,1.15,'Self-conductor term\nuq is a nonzero local unit',size=18)
 text(a,5,1.05,'Dq,q = Σ (1−b) ℓq(πq(zqᵇ))  in 𝔽₇',23,col=TEAL)
 save(f,'14_self_conductor','norm-q generators and conductor Frobenius normalization',{'norm_primes':sorted(map(int,S['conductor_generators'])),'norms':P['conductor_generator_norms'],'self_term_required':True})
def fig15():
 f,a=canvas();title(a,'The bare cup equation has a restricted primitive')
 card(a,.55,4.18,8.9,1.12,'Local cup class is zero at every place in Σ\nFinite-S duality and the nonseventh unit φ',size=21)
 arrow(a,(5,4.0),(5,3.37),color=TEAL)
 card(a,1.7,1.6,6.6,1.65,'There exists one global p₀\ndp₀ = −α ∪ β',size=27)
 text(a,5,.69,'Existence does not supply its numerical values or the required affine target.',16,col=COPPER)
 save(f,'15_bare_primitive','conditional written finite-S duality theorem diagram',{'bare_primitive_exists_under_stated_hypotheses':True,'values_computed':False,'additional_ramification_for_bare_p':False})
def fig16():
 f,a=canvas();title(a,'Local ordinary characters use twenty-four coordinates')
 for x,y,w,h,s in[(.45,4.0,4.1,1.2,'2:F, 3:F, 5:F\n3 unramified coordinates'),(5.45,4.0,4.1,1.2,'7:φ, 7:3, 7:7\n3 seven-adic coordinates')]:card(a,x,y,w,h,s,size=18)
 for i in range(9):
  x=.4+i*1.04;card(a,x,2.2,.85,.75,'I  F',size=15);text(a,x+.425,1.71,str(i+1),14,col=GRAY)
 text(a,5,.6,'Nine support places × two coordinates = 18\n3 + 3 + 18 = 24 over k',23,col=TEAL)
 save(f,'16_local_coordinates','Block80 local ordinary-character coordinate list',{'fixed_unramified':3,'seven_adic':3,'support_places':9,'per_support':2,'total':24})
def fig17():
 f,a=canvas();title(a,'Fourteen reciprocity relations leave ten global directions')
 card(a,.45,3.65,3.9,2,'24 local coordinates\nL has 14 rows\nrank L = 14',size=22)
 card(a,5.65,3.65,3.9,2,'10 global parameters\nJ is 24 × 10\nrank J = 10',size=21)
 arrow(a,(5.42,4.68),(4.56,4.68),color=TEAL)
 text(a,5,2.52,'LJ = 0      and      im J = ker L',26,col=TEAL)
 card(a,.8,.35,8.4,1.65,'The exact image concerns ordinary characters z = p−p₀\nIt classifies differences\nThe affine origin remains unknown',size=17)
 save(f,'17_global_localization','four exact localization matrices independently rank/multiplication checked',{'L_shape':[14,24],'L_rank':14,'J_shape':[24,10],'J_rank':10,'H1_dimension_k':10})
def fig18():
 f,a=chart();f.subplots_adjust(right=.80);A=P['patterns']['C']['global_to_constraint_matrix'];im=a.imshow(A,cmap='YlGnBu',vmin=0,vmax=6,aspect='auto');cb=f.colorbar(im,cax=f.add_axes([.865,.21,.026,.62]),ticks=range(7));cb.set_label('Residue in 𝔽₇',fontsize=13);a.set(xticks=[0,3,6,9],xticklabels=[1,4,7,10],yticks=[0,5,6,14],yticklabels=[1,6,7,15],xlabel='Global parameter column',ylabel='Constraint row');a.axhline(5.5,color=COPPER,lw=2)
 a.set_title('A = EJ: six fixed rows and nine toric rows',fontsize=19,color=TEAL,pad=13)
 save(f,'18_toric_projection','exact PatternC15x10 finite-field matrix, residue palette0..6',{'pattern':'C','matrix':A,'fixed_rows':6,'toric_rows':9,'shape':[15,10],'rank':8})
def fig19():
 f,a=chart();ns=list('ABCD');x=np.arange(4);rankv=[P['patterns'][n]['rank']for n in ns];ker=[10-v for v in rankv];coker=[15-v for v in rankv]
 a.bar(x-.25,rankv,.25,color=TEAL,label='rank A');a.bar(x,ker,.25,color=COPPER,label='dim ker A');a.bar(x+.25,coker,.25,color='#A5BDBB',label='dim coker A');a.set(xticks=x,xticklabels=ns,ylim=(0,11),yticks=range(0,11,2),xlabel='Conditional support pattern',ylabel='Dimension over k = 𝔽₄₉');a.legend(loc='upper center',ncol=3,frameon=False,fontsize=12)
 for shift,vals in[(-.25,rankv),(0,ker),(.25,coker)]:
  for i,v in enumerate(vals):a.text(i+shift,v+.15,str(v),ha='center',fontsize=15)
 a.set_title('Homogeneous freedom and affine obstruction differ',fontsize=19,color=TEAL,pad=13)
 save(f,'19_affine_dimensions','exact rank-nullity in each supplied15x10 matrix',{'patterns':ns,'rank':rankv,'kernel':ker,'cokernel':coker})
def fig20():
 f,a=canvas();title(a,'Two added toric rows remove Pattern C’s extra directions')
 for i,row in enumerate([[3,1],[5,2]]):
  for j,v in enumerate(row):card(a,2.65+j*1.55,4.28-i*1.45,1.15,1.05,str(v),size=33)
 text(a,7.3,3.96,'det = 3·2 − 1·5\n= 1 in 𝔽₇',24,col=TEAL)
 card(a,.8,.8,8.4,1.2,'Both old plus directions are removed\nThe two remaining directions are at 307 and 1483',size=19)
 save(f,'20_pattern_C_minor','exact2x2minor in the old plus-kernel basis',{'matrix':[[3,1],[5,2]],'det_mod7':1,'old_kernel_dimension':4,'new_kernel_dimension':2,'remaining_support':[307,1483]})
def fig21():
 f,a=canvas();title(a,'A left-null basis evaluates the canonical affine obstruction')
 card(a,.4,4.03,4.05,1.65,'A z = t(p₀)\n15 equations\n10 parameters',size=20);card(a,5.55,4.18,4.05,1.3,'N A = 0\nN has 7 or 8 rows',size=23)
 text(a,5,3.17,'Stage P is solvable ⇔ N t(p₀) = 0',27,col=TEAL)
 card(a,.75,1.03,8.5,1.2,'Actual t(p₀) and N t(p₀) have not been computed\nThe finite matrices do not supply their arithmetic origin',size=18)
 save(f,'21_affine_criterion','exact criterion for stipulated affine StageP',{'criterion':'exists z with A z=t iff N t=0','left_null_dimensions':[8,8,7,8],'actual_arithmetic_target_computed':False})
def fig22():
 n='C';v=P['patterns'][n];A=v['global_to_constraint_matrix'];N=v['dual_obstruction_basis'];t=v['synthetic_nonimage_target'];z=[1]+[0]*9;shift=mv(A,z);tp=[(x-y)%7 for x,y in zip(t,shift)];obs=mv(N,t);check('synthetic origin translation control',mv(N,tp)==obs)
 f,a=canvas();title(a,'Changing the primitive moves the target inside one image coset')
 card(a,.4,4.15,4,1.2,'p₀ → p₀ + zchar\nGlobal ordinary character',size=18);card(a,5.6,4.15,4,1.2,'t → t − A z₀\nN t is unchanged',size=22)
 arrow(a,(4.56,4.75),(5.44,4.75),color=TEAL)
 card(a,.7,1.35,8.6,1.3,'Synthetic Pattern C: t = e₁ and z₀ = e₁\nN t = '+str(obs),size=20)
 text(a,5,.52,'This exact control tests origin invariance, not an actual arithmetic target.',16,col=COPPER)
 save(f,'22_origin_invariance','synthetic finite-field control with archived PatternC matrices',{'kind':'synthetic','pattern':n,'t':t,'z0':z,'translated_t':tp,'obstruction':obs,'arithmetic_authenticated':False})
def fig23():
 f,a=canvas();title(a,'Upper ramification and integral lifting remain after Stage P')
 card(a,.45,4.03,9.1,1.3,'β(T)=0 forces p(T)=0\nUpper inertia q(T) may remain nonzero',size=20)
 for x,h,s in[(.4,'upper content one','v₇(N₁₂) = 1\nN₁₁,N₂₂ ∈ 49$\\mathcal{O}$\nN₂₁ ∈ 343$\\mathcal{O}$'),(5.6,'content at least two','N ≡ 0 (mod 49)\nFirst-order inertia vanishes\nHigher digits still matter')]:
  text(a,x+2,3.28,h,20,col=TEAL);card(a,x,1.08,4,1.65,s,size=17)
 save(f,'23_upper_integral_gate','written local integral refinement at beta-unramified variable places',{'content_one':{'N12_valuation':1,'N11_min_valuation':2,'N22_min_valuation':2,'N21_min_valuation':3},'content_ge2':'all N vanish modulo49','global_upper_support_bounded':False})
def fig24():
 f,a=canvas();title(a,'The next arithmetic obligation is an actual affine class')
 for y,s,col in[(4.68,'Compute actual N t(p₀) for each residual pattern',PALE),(2.95,'If zero: construct compatible upper q\nand integral lifts',PALE),(1.22,'Resolve unrestricted supports and depths\nplus the remaining signatures','#EFE1CB')]:card(a,.75,y,8.5,1.05,s,size=19,color=col)
 arrow(a,(5,4.5),(5,4.1),dashed=True,color=COPPER);arrow(a,(5,2.77),(5,2.36),dashed=True,color=COPPER)
 text(a,5,.43,'None of these arrows is supplied by another homogeneous rank calculation.',16,col=COPPER)
 save(f,'24_research_boundary','explicit research dependency diagram, dashed implications are unproved obligations',{'next':'actual canonical affine class N t(p0)','if_nonzero':'excludes stated first-stage branch','if_zero':'opens upper q and integral compatibility','full_beal_open':True})
FIGURES={i:globals()[f'fig{i:02d}']for i in range(1,25)}
PAPER=[1,3,11,19,24]
def main():
 p=argparse.ArgumentParser();p.add_argument('--paper-only',action='store_true');p.add_argument('--result-dir');args=p.parse_args();started=time.time();audit()
 selected=PAPER if args.paper_only else list(FIGURES)
 for n in selected:FIGURES[n]()
 for key in DATA['figures']:
  if int(key[:2])in PAPER:shutil.copy2(OUT/(key+'.pdf'),SHARED/(key+'.pdf'))
 (ROOT/'data.json').write_text(json.dumps(DATA,indent=2)+'\n')
 (ROOT/'FIGURE_LAYOUT_CHECK.json').write_text(json.dumps({'all_passed':True,'figures':LAYOUT},indent=2)+'\n')
 report={'status':'bounded exact data verified','checks':CHECKS,'check_count':len(CHECKS),'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__,'runtime_seconds':time.time()-started,'exported_numbers':selected,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((ROOT/'inputs').iterdir())},'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(OUT.iterdir())if p.suffix in['.pdf','.png']},'nonclaim':'does not prove Beal, construct actual p0 or evaluate actual affine target'}
 (ROOT/'COMPUTATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 if args.result_dir:
  d=ROOT/args.result_dir;d.mkdir(parents=True,exist_ok=True)
  for name in['data.json','FIGURE_LAYOUT_CHECK.json','COMPUTATION_REPORT.json']:shutil.copy2(ROOT/name,d/name)
  assets=d/'figures';assets.mkdir(exist_ok=True)
  for key in DATA['figures']:
   for ext in['.pdf','.png']:shutil.copy2(OUT/(key+ext),assets/(key+ext))
  (d/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'Exported {len(selected)} figures. {len(CHECKS)} exact assertions, native canvas and card containment passed.')
if __name__=='__main__':main()
