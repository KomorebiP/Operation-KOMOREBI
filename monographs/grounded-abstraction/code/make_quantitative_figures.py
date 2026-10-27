"""Two analytical charts from the exact first-edition data, not empirical runs."""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'


def num(x):return float(Fraction(x))


def save(fig,name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.16,
                metadata={'Title':name,'Author':'Komorebi P.','CreationDate':None,'ModDate':None})
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',pad_inches=.16,metadata={'Date':None})
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight',pad_inches=.16)
    plt.close(fig)


def main():
    data=json.loads((ROOT/'data/quantitative_illustrations.json').read_text())
    rows=data['precision_curve']
    fig,ax=plt.subplots(figsize=(9.2,4.7))
    ax.plot([r['N'] for r in rows],[num(r['generic_bound']) for r in rows],marker='s',label='Uniform three-report allowance')
    ax.plot([r['N'] for r in rows],[num(r['maximum_actual_TV_through_3']) for r in rows],marker='o',label='Largest exact error in this sensor')
    ax.set_xscale('log',base=2);ax.set_yscale('log')
    ax.set_xlabel('Probability denominator N',fontsize=12)
    ax.set_ylabel('Total-variation error',fontsize=12)
    ax.set_title('Finite memory needs a declared horizon',fontsize=15,pad=17)
    ax.legend(loc='upper right',fontsize=10,frameon=False)
    ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    fig.subplots_adjust(left=.13,right=.97,bottom=.20,top=.86)
    fig.text(.5,.035,'Four cell masses. Exact likelihoods. All binary report histories through three updates.',ha='center',fontsize=10)
    save(fig,'finite_memory_horizon')

    rows=data['leakage_curve']
    fig,ax=plt.subplots(figsize=(9.2,4.7))
    ax.plot([r['steps'] for r in rows],[num(r['unstable']) for r in rows],marker='o',label='Hidden multiplier 2')
    ax.plot([r['steps'] for r in rows],[num(r['stable']) for r in rows],marker='s',label='Hidden multiplier 1/2')
    ax.set_yscale('log')
    ax.set_xlabel('Number of prediction steps',fontsize=12)
    ax.set_ylabel('Visible prediction error',fontsize=12)
    ax.set_title('The same small return channel has different consequences',fontsize=14,pad=17)
    ax.legend(loc='upper left',fontsize=11,frameon=False)
    ax.set_xticks(range(1,9));ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    fig.subplots_adjust(left=.13,right=.97,bottom=.20,top=.86)
    fig.text(.5,.035,'Return coupling = 1/64. At coupling exactly zero, both output errors stay zero.',ha='center',fontsize=10)
    save(fig,'observable_leakage')
    print('Generated two mathematical charts as PDF, SVG, and PNG from exact rational data.')

if __name__=='__main__':main()
