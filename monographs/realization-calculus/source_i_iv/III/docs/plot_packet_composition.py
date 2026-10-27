from pathlib import Path
from math import comb
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Stirling partitions and independent intermediate packet labels.
S={(0,0):1}
for n in range(1,7):
    for k in range(1,n+1): S[(n,k)] = k*S.get((n-1,k),0)+S.get((n-1,k-1),0)
ns=list(range(1,7))
fig,axs=plt.subplots(1,2,figsize=(11,4))
for M in (1,2,3):
    vals=[sum(S[(n,k)]*M**k for k in range(1,n+1)) for n in ns]
    axs[0].plot(ns,vals,marker='o',label=f'{M} intermediate packets')
axs[0].set_yscale('log');axs[0].set_xticks(ns)
axs[0].set_ylabel('Decorated terms (log scale)')
axs[0].set_xlabel('Derivative order n')
axs[0].grid(axis='y',alpha=.2)
axs[0].legend(fontsize=8)
byk=[S[(4,k)]*2**k for k in range(1,5)]
axs[1].bar([1,2,3,4],byk)
for k,v in enumerate(byk,1): axs[1].annotate(str(v),(k,v),ha='center',va='bottom')
axs[1].set_xticks([1,2,3,4]);axs[1].set_xlabel('Number of blocks in a partition of 4')
axs[1].set_ylabel('Term count at two intermediate packets')
axs[1].set_title(f'Fourth derivative: {sum(byk)} terms before pruning')
axs[1].set_ylim(0,max(byk)*1.18)
fig.suptitle('Finite packet labels decorate classical set partitions',fontsize=13)
fig.tight_layout()
for suffix in ('pdf','png'):
    fig.savefig(Path(__file__).with_name('decorated_partition_terms.'+suffix),dpi=160,bbox_inches='tight')
plt.close(fig)
print('Generated figure with exact integer Stirling counts:', byk)
