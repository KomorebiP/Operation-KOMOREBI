#!/usr/bin/env python3
"""Three bounded exact finite illustrations. Rational data are computed before plotting."""
from pathlib import Path
from fractions import Fraction
import argparse,json,hashlib,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
META={'CreationDate':datetime.datetime(2026,10,9,tzinfo=datetime.timezone.utc),'ModDate':datetime.datetime(2026,10,9,tzinfo=datetime.timezone.utc),'Creator':'Matplotlib / exact finite models'}
def frac(q):
    q=Fraction(q)
    return str(q.numerator) if q.denominator==1 else str(q.numerator)+'/'+str(q.denominator)
def rank(a):
    a=[[Fraction(x) for x in row] for row in a]; row=0
    for col in range(len(a[0])):
        pivot=next((i for i in range(row,len(a)) if a[i][col]),None)
        if pivot is None:continue
        a[row],a[pivot]=a[pivot],a[row]
        q=a[row][col];a[row]=[x/q for x in a[row]]
        for i in range(len(a)):
            if i!=row:
                q=a[i][col];a[i]=[x-q*y for x,y in zip(a[i],a[row])]
        row+=1
        if row==len(a):break
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=ROOT/'monograph_figures')
    args=parser.parse_args();out=args.output_directory.resolve();out.mkdir(parents=True,exist_ok=True)
    c1=[[1,0,0],[0,0,0]];c2=[[1,0,0],[0,1,0]];c3=[[0,0,1],[0,0,0]]
    seed={'d':2,'m':3,'C1':c1,'C2':c2,'C3':c3,'single_ranks':[rank(c1),rank(c2)],'single_orbit_dimensions':[2*rank(c1),2*rank(c2)],'combined_row_rank':rank(c2+c3),'combined_orbit_dimension':2*rank(c2+c3),'ambient_dimension':6,'minimum_seed_count':2}
    h=[[2,1],[1,3]];schur=Fraction(2)-Fraction(1,3)
    inverse={'H':h,'retained_coordinate':0,'eliminated_block':'3','determinant':'5','schur_complement_of_H':frac(schur),'effective_inverse':frac(1/schur),'full_inverse':[['3/5','-1/5'],['-1/5','2/5']],'inverse_of_compressed_H':'1/2','inverse_discrepancy':frac(Fraction(3,5)-Fraction(1,2))}
    channel={'P':[[1,0],[0,0]],'Z':[[1,0],[0,-1]],'normalized_kraus_squared_weights':['3/4','1/4'],'unnormalized_error_squared_weights':['3','1'],'normalized_kraus_gram_scale':'1','unnormalized_error_gram_scale':'4','normalized_output_trace':'1','unnormalized_output_trace':'4','scope':'Output scaling for this one code state only. No general recovery assertion.'}
    data={'schema':'komorebi.paper_vii.exact_monograph_models.v1','scope':'Three exact finite pedagogical models. No continuum or universal claim.','models':{'seed_support':seed,'block_inverse':inverse,'channel_scale':channel}}
    (out/'exact_models.json').write_text(json.dumps(data,indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.facecolor':'white'})
    teal='#245D60';orange='#B57D51';light='#DCE7E7'
    fig,ax=plt.subplots(1,2,figsize=(9,4),gridspec_kw={'width_ratios':[1,1.2]})
    ax[0].axis('off')
    text='C1 = [[1, 0, 0], [0, 0, 0]]\n\nC2 = [[1, 0, 0], [0, 1, 0]]\n\nC3 = [[0, 0, 1], [0, 0, 0]]\n\nC2 and C3 cover all 3 columns.'
    ax[0].text(.02,.91,text,va='top',linespacing=1.6,fontsize=10,fontfamily='DejaVu Sans Mono')
    vals=seed['single_orbit_dimensions']+[seed['combined_orbit_dimension']]
    ax[1].bar(['C1','C2','C2 + C3'],vals,color=[light,teal,orange],width=.6)
    for i,v in enumerate(vals):ax[1].text(i,v+.12,str(v),ha='center',fontweight='bold')
    ax[1].set_ylim(0,7);ax[1].set_yticks(range(0,7,2));ax[1].set_ylabel('Algebraic orbit dimension');ax[1].axhline(6,color='#6B777C',ls='--',lw=1)
    ax[1].text(-.40,6.08,'full space',ha='left',fontsize=9,color='#536568');fig.suptitle('Seed rank measures the available multiplicity support',x=.07,ha='left',fontsize=13,fontweight='bold');fig.tight_layout(rect=[0,0,1,.90]);fig.savefig(out/'exact_seed_support.pdf',metadata=META);plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(9,4))
    ax[0].axis('off');ax[0].text(.04,.9,'H = [[2, 1], [1, 3]]\n\nSchur complement of H:\n\n2 - 1/3 = 5/3\n\nRetained entry of H inverse:\n\n(5/3) inverse = 3/5',ha='left',va='top',linespacing=1.3,fontfamily='DejaVu Sans Mono',fontsize=11)
    values=[Fraction(1,2),Fraction(3,5),Fraction(3,5)];ax[1].bar(['Compressed\ninverse','Schur\ninverse','Full inverse\nentry'],[float(x) for x in values],color=[orange,teal,light],width=.6)
    for i,v in enumerate(values):ax[1].text(i,float(v)+.025,frac(v),ha='center',fontweight='bold')
    ax[1].set_ylim(0,.75);ax[1].set_ylabel('Inverse response');ax[1].set_yticks([0,.25,.5,.75]);fig.suptitle('Block inversion includes the discarded coordinate',x=.07,ha='left',fontsize=13,fontweight='bold');fig.tight_layout(rect=[0,0,1,.90]);fig.savefig(out/'exact_feshbach_compression.pdf',metadata=META);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));x=np.arange(2);p=[Fraction(3,4),Fraction(3)];q=[Fraction(1,4),Fraction(1)]
    ax.bar(x,[float(v) for v in p],label='I contribution',color=teal,width=.5)
    ax.bar(x,[float(v) for v in q],bottom=[float(v) for v in p],label='Z contribution',color=orange,width=.5)
    for i in range(2):
        ax.text(i,float(p[i])/2,frac(p[i]),ha='center',va='center',color='white',fontweight='bold');ax.text(i,float(p[i]+q[i]/2),frac(q[i]),ha='center',va='center',color='white',fontweight='bold');ax.text(i,float(p[i]+q[i])+.13,'trace '+frac(p[i]+q[i]),ha='center',fontweight='bold')
    ax.set_xticks(x,['Normalized channel','Unnormalized error map']);ax.set_ylabel('Output trace on the code state P');ax.set_ylim(0,4.8);ax.set_xlim(-.7,1.7);ax.legend(loc='upper left',frameon=False);fig.suptitle('Relative weights alone do not fix normalization',x=.075,ha='left',fontsize=13,fontweight='bold');fig.tight_layout(rect=[0,0,1,.90]);fig.savefig(out/'exact_channel_scale.pdf',metadata=META);plt.close(fig)
    manifest={'schema':'komorebi.paper_vii.exact_monograph_figures.v1','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'models_sha256':hashlib.sha256((out/'exact_models.json').read_bytes()).hexdigest(),'figures':[{ 'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.glob('*.pdf'))]}
    (out/'generation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
