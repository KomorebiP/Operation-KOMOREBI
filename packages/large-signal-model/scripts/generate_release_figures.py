"""Regenerate separate Matplotlib figures from source calculations and audit ledgers.

No synthetic results are substituted for measured benchmark rows. The signal plots
are explicitly illustrative deterministic signals. Uses Matplotlib defaults.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from komorebi_pr_lasm import analyze_signal, PolyphaseFIR, StreamingFIR, best_basis, l1_packet_cost


def main() -> None:
    out=ROOT/'docs'/'figures';out.mkdir(parents=True,exist_ok=True)
    ledger={}
    def plot(title,xlabel,ylabel,size=(7.6,3.7)):
        fig=plt.figure(figsize=size,layout='constrained')
        ax=fig.add_subplot(111)
        ax.set(title=title,xlabel=xlabel,ylabel=ylabel)
        return fig,ax
    def save(fig,name):
        fig.savefig(out/f'{name}.png',dpi=190)
        fig.savefig(out/f'{name}.pdf')
        plt.close(fig)
    n=np.arange(256)
    x=np.sin(2*np.pi*7*n/256)+.35*np.sin(2*np.pi*41*n/256)
    x[96:160]+=.8
    a=analyze_signal(x,modulus=4,maximum_depth=6)
    ledger['illustrative_signal']={'samples':256,'definition':'sin(2*pi*7*n/256)+0.35*sin(2*pi*41*n/256)+0.8*indicator(96<=n<160)',
                                   'reconstruction_residuals':a.reconstruction_residuals()}
    fig,ax=plot('One signal, complete reconstruction','Sample index','Amplitude')
    ax.plot(n,x,label='Source',linewidth=1.3)
    ax.plot(n,a.reconstruct('packets'),label='Packet synthesis',linestyle='--',linewidth=1.)
    ax.legend(loc='upper right',fontsize=9)
    save(fig,'01_reconstruction')
    fig,ax=plot('Full Fourier coordinates: positive-frequency view','Cycles per sample','Unitary coefficient magnitude')
    f=np.fft.rfftfreq(len(x))
    ax.plot(f,np.abs(np.fft.rfft(x,norm='ortho')),linewidth=1.2)
    ax.set_xlim(0,.5)
    save(fig,'02_fourier')
    fig,ax=plot('Residue channels preserve every sample','Lane index q','Amplitude + display offset')
    for phase,lane in a.polyphase.items():
        ax.plot(np.arange(len(lane)),lane+3*phase,marker='.',markersize=3,linewidth=.8,label=f'Phase {phase}, offset {3*phase}')
    ax.legend(fontsize=8,loc='upper right')
    save(fig,'03_polyphase')
    # The supplied additive l1 cost with packet penalty 0.5 chooses a complete finite antichain.
    selection=best_basis(a.packets, cost=l1_packet_cost, packet_penalty=0.5)
    ordered=sorted(selection.paths)
    energy=[float(np.sum(a.packets.coefficients[p]**2)) for p in ordered]
    fig,ax=plot('Energy retained by the selected complete packet basis','Selected packet (left-to-right path order)','Squared coefficient norm')
    ax.bar(np.arange(len(energy)),energy)
    if len(energy)<=22:
        ax.set_xticks(np.arange(len(energy)),[p or 'root' for p in ordered],rotation=60,ha='right',fontsize=8)
    ledger['packet_basis']={'paths':ordered,'energy':energy,'total_energy':sum(energy),'source_energy':float(x@x)}
    save(fig,'04_packets')
    h=np.array([.25,.5,.25])
    y=PolyphaseFIR(h,modulus=4).apply(x)
    fig,ax=plot('Finite FIR filtering includes the complete tail','Sample index','Amplitude')
    ax.plot(n,x,label='Source',linewidth=.85)
    ax.plot(np.arange(len(y)),y,label='Full convolution',linewidth=1.25)
    ax.legend(fontsize=9)
    ledger['fir']={'taps':h.tolist(),'input_length':len(x),'output_length':len(y),'max_error_vs_direct':float(np.max(np.abs(y-np.convolve(x,h))))}
    save(fig,'05_fir')
    stream=StreamingFIR(h);cuts=[0,31,96,101,180,256]
    ys=np.concatenate([stream.process(x[i:j]) for i,j in zip(cuts,cuts[1:])]+[stream.flush()])
    fig,ax=plot('Chunk boundaries do not reset filter history','Sample index','Amplitude')
    ax.plot(np.arange(len(y)),y,label='Batch',linewidth=1.2)
    ax.plot(np.arange(len(ys)),ys,linestyle='--',label='Stream + tail',linewidth=1.)
    for c in cuts[1:-1]:
        ax.axvline(c,linestyle=':',linewidth=.65)
    ax.legend(fontsize=9)
    ledger['stream']={'boundaries':cuts,'max_error_vs_batch':float(np.max(np.abs(ys-y)))}
    save(fig,'06_streaming')
    rows=json.loads((ROOT/'verification/current_benchmark/operator_benchmark.json').read_text())
    fig,ax=plot('Held-out state prediction: seven controlled mechanisms','Scenario','State RMSE',size=(7.6,4.0))
    z=np.arange(len(rows));width=.38
    ax.bar(z-width/2,[r['baseline_state_rmse'] for r in rows],width,label='Single linear portfolio')
    ax.bar(z+width/2,[r['lasm_state_rmse'] for r in rows],width,label='Typed portfolio',hatch='//')
    ax.set_xticks(z,[r['scenario'].replace('-', '\n',1) for r in rows],fontsize=8)
    ax.legend(fontsize=9)
    ledger['benchmark']={'source':'verification/current_benchmark/operator_benchmark.json','rows':rows}
    save(fig,'07_operator_benchmark')
    sweep=json.loads((ROOT/'verification/current_stress/operator_cases.json').read_text())
    fig,ax=plot('Five-seed synthetic state prediction','Case grouped by seed (seven families per seed)','PR-LASM / baseline RMSE')
    ax.scatter(np.arange(1,len(sweep)+1),[r['state_rmse_ratio'] for r in sweep],s=22,label='One held-out case')
    ax.axhline(1.,linestyle='--',linewidth=1.,label='Equal to baseline')
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=9)
    ledger['operator_sweep']={'source':'verification/current_stress/operator_cases.json','ratios':[r['state_rmse_ratio'] for r in sweep]}
    save(fig,'08_multiseed')
    summary=json.loads((ROOT/'verification/current_stress/summary.json').read_text())
    control=summary['negative_control']
    fig,ax=plot('Negative control: corrupt the training correspondence','Training pairing','Unseen-test RMSE (log scale)')
    ax.bar(['Intact pairing','Permuted targets'],[control['normal_rmse'],control['shuffled_rmse']])
    ax.set_yscale('log')
    ledger['negative_control']=control
    save(fig,'09_negative_control')
    (out/'figure_data.json').write_text(json.dumps(ledger,indent=2,allow_nan=False)+'\n')
    print(f'Generated 9 separate figure pairs and their source ledger in {out}')


if __name__=='__main__':
    main()
