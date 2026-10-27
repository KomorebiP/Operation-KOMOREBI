"""Python / Matplotlib atlas. One axes per figure, no generated artwork.

The plots use Matplotlib's default color cycle and default colormap.
Line styles, hatching, and labelled boundaries supplement the default colors.
"""
from __future__ import annotations
from pathlib import Path
from math import cos, sin, pi
import base64
import csv
import io
import json
import textwrap
from typing import Callable

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from PIL import Image
from model import run_story, validate, controlled_access_cases

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'Companion concept: Self-Improving Intelligence v1.0, Sections 7 and 31. New illustrative model: code/model.py.'


def wrap(text: str, n: int) -> str:
    return '\n'.join(textwrap.fill(line, n) for line in text.split('\n'))


def text(ax, x, y, s, size=14, **kw):
    return ax.text(x,y,s,ha=kw.pop('ha','center'),va=kw.pop('va','center'),fontsize=size,**kw)


def box(ax,x,y,w,h,title,body='',size=15,heavy=False,dashed=False,header=False):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.045,rounding_size=0.12',
                    fill=False,linewidth=2.1 if heavy else 1.05,linestyle='--' if dashed else '-')
    ax.add_patch(p)
    if body or header:
        text(ax,x+w/2,y+h-.32,title,size,weight='bold')
        if body:
            text(ax,x+w/2,y+h/2-.16,body,size-2,linespacing=1.45)
    else:
        text(ax,x+w/2,y+h/2,title,size,weight='bold')
    return p


def arrow(ax,start,end,label='',rad=0.0,heavy=False,dashed=False,label_pos=None,size=11):
    p=FancyArrowPatch(start,end,connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',
                      mutation_scale=15 if heavy else 11,linewidth=2.3 if heavy else 1.1,
                      linestyle='--' if dashed else '-')
    ax.add_patch(p)
    if label:
        x,y=label_pos if label_pos else ((start[0]+end[0])/2,(start[1]+end[1])/2+.22)
        text(ax,x,y,label,size)
    return p


def page(i,title,subtitle,caption,source=SOURCE,kind='diagram'):
    fig=plt.figure(figsize=(14,8.75),dpi=120)
    fig.text(.048,.979,'OPERATION KOMOREBI  /  AGENT DYNAMICS',fontsize=9,ha='left',va='top',weight='bold')
    fig.text(.048,.935,title,fontsize=27,ha='left',va='top',weight='bold')
    fig.text(.048,.870,subtitle,fontsize=12.5,ha='left',va='top')
    if kind=='3d':
        ax=fig.add_axes([.045,.20,.66,.64],projection='3d')
    elif kind=='chart':
        ax=fig.add_axes([.085,.25,.84,.51])
    else:
        ax=fig.add_axes([.04,.205,.92,.62])
        ax.set(xlim=(0,14),ylim=(0,7));ax.set_axis_off()
    fig.text(.048,.130,wrap(caption,139),fontsize=11.2,ha='left',va='top',linespacing=1.48)
    fig.text(.048,.045,wrap(source,157),fontsize=8,ha='left',va='bottom')
    fig.text(.95,.045,f'{i:02d}  /  14',fontsize=9,ha='right',va='bottom')
    return fig,ax


def chart_finish(ax):
    ax.tick_params(labelsize=10)
    ax.grid(True,axis='y',alpha=.22)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def architecture():
    fig,ax=page(1,'An agent acts across a boundary',
        'Outside: observations and consequences. Inside: retained state, predictions, comparisons, and decisions.',
        'Solid arrows carry observations or actions. Dashed arrows carry internal revision or remembered evidence. These are functional roles, not measured neural modules. The toy implementation makes belief, memory, and action checks explicit.')
    box(ax,.2,1.3,2.7,4.5,'WORLD','Signals\nOther agents\nResources\nConsequences',size=17)
    box(ax,3.75,.6,10.0,6.1,'',dashed=True)
    text(ax,8.75,6.33,'AGENT  /  private computational state',15,weight='bold')
    for x,title,body in [(4.05,'Perception','receive a report'),(7.35,'World model','retain compatible cases'),(10.65,'Prediction','anticipate the next report')]:
        box(ax,x,4.5,2.8,1.25,title,body,size=15)
    for x,title,body in [(4.05,'Memory','receipts + older episodes'),(7.35,'Revision','refilter or change scope'),(10.65,'Decision gate','test the proposed action')]:
        box(ax,x,2.05,2.8,1.3,title,body,size=15)
    arrow(ax,(2.95,5.08),(4.01,5.08),'observe',size=10)
    arrow(ax,(6.9,5.08),(7.31,5.08))
    arrow(ax,(10.2,5.08),(10.61,5.08))
    arrow(ax,(5.45,4.46),(5.45,3.40),'store',label_pos=(4.87,3.9),dashed=True)
    arrow(ax,(8.75,3.41),(8.75,4.44),'new state',label_pos=(8.10,3.9),dashed=True)
    arrow(ax,(12.05,4.46),(12.05,3.70),dashed=True)
    arrow(ax,(12.05,3.70),(9.8,3.70),dashed=True)
    arrow(ax,(9.8,3.70),(9.8,3.41),dashed=True)
    text(ax,10.76,4.01,'prediction vs. report',11)
    arrow(ax,(6.9,2.7),(7.31,2.7),dashed=True)
    arrow(ax,(10.2,2.7),(10.61,2.7))
    arrow(ax,(12.1,2.0),(12.1,1.15))
    arrow(ax,(12.1,1.15),(1.55,1.15),'action crosses back into the world',label_pos=(7.4,1.39),heavy=True)
    arrow(ax,(1.55,1.15),(1.55,1.28))
    return fig


def coupling():
    fig,ax=page(2,'Two agents do not share a mind',
        'Distinct evidence produces distinct private states. Messages can bring those states into agreement.',
        'At event 11, A retains locations {2, 5}; B still retains {0, 2, 5, 7}. A must send its middle-bit receipt before B can make the same update. Reliable transport and truthful reports are explicit assumptions, not achievements inferred from the diagram.')
    box(ax,.35,1.65,4.1,4.95,'AGENT A','',size=17,heavy=True,header=True)
    box(ax,9.55,1.65,4.1,4.95,'AGENT B','',size=17,heavy=True,header=True)
    for x,label,poss in [(2.4,'High and middle bit access',(2,5)),(11.6,'Low bit + calibration access',(0,2,5,7))]:
        text(ax,x,5.83,label,12)
        for j in range(8):
            px=x-1.54+j*.44
            ax.add_patch(Circle((px,4.82),.145,fill=j in poss,linewidth=1.1))
            text(ax,px,4.37,str(j),10)
        text(ax,x,3.64,'Private belief + receipt history',12,weight='bold')
        text(ax,x,2.82,'A message changes the belief only\nwhen it contributes applicable evidence.',11,linespacing=1.5)
    box(ax,5.37,3.35,3.26,1.85,'RECEIPT r11','middle bit = 1\nissuer A  /  current episode',size=14)
    arrow(ax,(4.52,4.38),(5.3,4.38),dashed=True,heavy=True)
    arrow(ax,(8.7,4.38),(9.48,4.38),dashed=True,heavy=True)
    text(ax,7,5.68,'PUBLIC MESSAGE CHANNEL',11,weight='bold')
    box(ax,5.15,.24,3.7,1.30,'ENVIRONMENT','source + sensor convention',size=14)
    arrow(ax,(5.1,.9),(2.43,1.6),label='private observation',label_pos=(2.8,.73),rad=-.1,size=10)
    arrow(ax,(8.9,.9),(11.57,1.6),label='private observation',label_pos=(11.2,.73),rad=.1,size=10)
    text(ax,7,2.40,'No direct link joins the\nagents\' unreported internal states.',12,linespacing=1.5)
    return fig


def draw_state(ax,s):
    """One synchronized view, all elements in one coordinate system."""
    ax.set(xlim=(0,16),ylim=(0,8));ax.set_axis_off()
    t=s['t'];truth=s['truth']
    box(ax,.28,1.36,3.45,5.90,'ENVIRONMENT',size=16,heavy=s['active']=='world',header=True)
    text(ax,2,6.65,'Viewer-only truth',10)
    cx,cy,r=2.0,4.80,1.05
    for j in range(8):
        a=pi/2-2*pi*j/8
        x,y=cx+r*cos(a),cy+r*sin(a)
        ax.add_patch(Circle((x,y),.23,fill=False,linewidth=3.2 if j==truth['target'] else .9))
        text(ax,x,y,str(j),11,weight='bold' if j==truth['target'] else 'normal')
    text(ax,2,4.79,'source\nlocation',11)
    text(ax,2,3.18,f'Sensor orientation: {truth["theta"]}',12,weight='bold')
    text(ax,2,2.51,'No direct truth feed\nto either agent',11,linespacing=1.6)
    text(ax,2,1.82,'Service completed' if t==17 else 'World awaits a command',10)
    for who,x in [('A',5.00),('B',10.45)]:
        st=s[who]; active=s['active']==who and s['channel'] in ('observation','check')
        box(ax,x,4.03,4.87,3.23,f'AGENT {who}',size=16,heavy=active,header=True)
        text(ax,x+2.43,6.63,f'Private belief  /  episode {st["epoch"]}',11)
        bx=x+.5; by=4.75; barw=.32; gap=.50
        for j,v in enumerate(st['p']):
            if v:
                ax.add_patch(Rectangle((bx+j*gap,by),barw,.98*v,alpha=.85,
                                      hatch='//' if who=='B' else None))
            text(ax,bx+j*gap+barw/2,by-.20,str(j),9)
        ax.plot([bx-.05,bx+7*gap+barw+.05],[by,by],linewidth=.65)
        text(ax,x+2.43,5.97,f'{len(st["locations"])} possible location{"s" if len(st["locations"]) != 1 else ""}  |  H = {st["entropy"]:.1f} bits',11)
        text(ax,x+2.43,4.22,f'{len(st["receipt_ids"])} active receipt{"s" if len(st["receipt_ids"]) != 1 else ""}  /  {st["archive_size"]} archived',9.6)
    # Active arrows follow the event channel. Idle routes remain visibly possible.
    arrow(ax,(3.8,6.11),(4.92,6.11),heavy=s['channel']=='observation' and s['active']=='A')
    arrow(ax,(3.70,7.54),(12.86,7.54),heavy=s['channel']=='observation' and s['active']=='B')
    arrow(ax,(12.86,7.54),(12.86,7.30),heavy=s['channel']=='observation' and s['active']=='B')
    text(ax,8.6,7.79,'external sensor observations',10)
    left=(7.25,3.73);right=(12.94,3.73)
    if s['active']=='B>A':
        arrow(ax,right,left,heavy=True,dashed=True)
    else:
        arrow(ax,left,right,heavy=s['channel']=='message',dashed=True)
    text(ax,10.1,3.51,'explicit message transport',10)
    box(ax,5.00,1.36,10.32,1.99,'ACTION / EVIDENCE CHECK',size=14,heavy=s['channel'] in ('action','check'),header=True)
    if t==6:
        main='Old certainty remains, but its sensor premise is now false.'
        sub='The viewer can see the change. The agents have not observed it yet.'
    elif t==7:
        main='A rejects the old prediction. B has not received that news.'
        sub='Belief expansion and the episode-reset rule are supplied mechanisms.'
    elif t==17:
        main=f'ISSUED: route service to bay {truth["target"]}.  CONFIRMED.'
        sub='The physical response closes this illustrated perception-action loop.'
    elif s['A']['ready']:
        main=f'A can justify bay {s["A"]["action"]} under its current model.'
        sub='A proposed command is not an external action until it is actually issued.'
    else:
        main='WAIT: the remaining cases do not yet justify one location.'
        sub='Investigate or communicate. Do not convert uncertainty into a false commitment.'
    text(ax,10.16,2.41,main,12.4,weight='bold')
    text(ax,10.16,1.81,sub,10.4)
    arrow(ax,(5.65,4.0),(5.65,3.37),heavy=s['channel']=='check')
    arrow(ax,(5.0,1.10),(2.0,1.10),heavy=s['channel']=='action')
    arrow(ax,(2.0,1.10),(2.0,1.32),heavy=s['channel']=='action')
    text(ax,9.55,.74,'External actions affect the world; observations and messages update private state.',11)


def state_plate(story):
    fig,ax=page(3,'A live view of internal and external state',
        'Event 12: both agents agree about the uncertainty, but neither can yet select the right action.',
        'The animation uses this same layout at all 18 events. Histogram heights are computed probabilities, not decorative activations. The outlined world location is shown to the reader only; the agents receive bit reports and explicit messages.')
    draw_state(ax,story[12]);return fig


def beliefs(story):
    fig,ax=page(4,'The representation changes over time',
        'A\'s complete belief over source location, not a single confidence score.',
        'Each column sums to one. Initial observations narrow the support. At event 7, a contradiction triggers a supplied model-reset rule and uncertainty expands. Calibration later resolves what ordinary readings cannot. Intensity is probability from 0 to 1.',kind='chart')
    matrix=np.asarray([s['A']['p'] for s in story]).T
    ax.imshow(matrix,origin='lower',aspect='auto',vmin=0,vmax=1,interpolation='nearest')
    ax.set(xticks=range(18),yticks=range(8),xlabel='Event index',ylabel='Candidate source location')
    ax.set_xticks(np.arange(-.5,18,1),minor=True);ax.set_yticks(np.arange(-.5,8,1),minor=True)
    ax.grid(which='minor',linewidth=.5,alpha=.2);ax.tick_params(which='minor',length=0)
    for x,label in [(0,'PRIOR'),(5,'IDENTIFIED'),(8,'NEW SCOPE'),(12,'AMBIGUOUS'),(16,'CALIBRATED')]:
        ax.text(x,8.05,label,ha='center',va='bottom',fontsize=9,weight='bold')
    return fig


def uncertainty(story):
    fig,ax=page(5,'Uncertainty contracts, expands, then resolves',
        'Private state can diverge temporarily even when both agents use the same update rule.',
        'Entropy is calculated from each exact location distribution: H = -sum p log2 p. The rise at events 7-8 is the supplied response to a model contradiction, not evidence that more data inherently makes Bayesian inference worse. The stale belief at event 6 illustrates a missing premise.',kind='chart')
    t=[s['t'] for s in story]
    ax.step(t,[s['A']['entropy'] for s in story],where='post',marker='o',label='Agent A')
    ax.step(t,[s['B']['entropy'] for s in story],where='post',marker='s',linestyle='--',label='Agent B')
    ax.set(xlim=(-.3,17.3),ylim=(-.15,3.85),xticks=range(18),yticks=(0,1,2,3),xlabel='Event index',ylabel='Location uncertainty (bits)')
    ax.legend(loc='upper left',ncol=2,frameon=False)
    for x,y,label in [(3,1,'messages\ncombine evidence'),(7,3,'impossible report\ntriggers reset'),(12,1,'ordinary reports\nreach a limit'),(14,0,'calibration')]:
        ax.annotate(label,xy=(x,y),xytext=(x+(.5 if x<13 else -.8),y+.65),fontsize=10,
                    ha='left' if x<13 else 'right',arrowprops={'arrowstyle':'->','linewidth':.9})
    chart_finish(ax);return fig


def prediction(story):
    obs=[s for s in story if s['observation']]
    fig,ax=page(6,'A prediction error is an internal event',
        'The sensor supplies a report. The agent compares it with a prediction made before receiving it.',
        'At event 7, A predicts report 1 with probability one and receives 0. That is a contradiction within this noiseless finite model. It triggers model expansion, not a conclusion that one particular physical cause has been identified. Calibration is a different observation channel.',kind='chart')
    xs=np.arange(len(obs))
    ax.plot(xs,[s['observation']['predicted_one'] for s in obs],marker='o',linestyle='--',label='Pre-observation probability of report 1')
    ax.plot(xs,[s['observation']['observed'] for s in obs],marker='s',linestyle='none',markersize=8,label='Actual binary report')
    labels=[f'{s["active"]}: {"cal" if s["observation"]["receipt"]["kind"]=="calibration" else "bit "+str(s["observation"]["receipt"]["bit"])}\nt={s["t"]}' for s in obs]
    ax.set(xticks=xs,xticklabels=labels,ylim=(-.12,1.4),yticks=(0,.5,1),ylabel='Probability or report value')
    ax.legend(loc='upper left',frameon=False,fontsize=10)
    k=next(i for i,s in enumerate(obs) if s['t']==7)
    ax.annotate('Predicted 1; received 0',xy=(k,0),xytext=(k+.5,.25),fontsize=11,
                arrowprops={'arrowstyle':'->','linewidth':1.2})
    chart_finish(ax);return fig


def trajectory(story):
    fig,ax=page(7,'An actual three-dimensional state trajectory',
        'The coordinates are expected source bits, calculated from each agent\'s probability distribution.',
        'This is a genuine 3D projection of the explicit belief state, not an invented neural embedding. It is lossy: the uniform prior and the later 50/50 belief over locations 2 and 5 have the same centroid. The full belief heatmap distinguishes them.',kind='3d')
    bits=np.array([[(j>>2)&1,(j>>1)&1,j&1] for j in range(8)])
    for j,b in enumerate(bits):
        ax.scatter(*b,s=28)
        ax.text(*(b+.022),str(j),fontsize=10)
    for i in range(8):
        for j in range(i+1,8):
            if np.sum(np.abs(bits[i]-bits[j]))==1:
                ax.plot(*np.stack([bits[i],bits[j]]).T,linestyle=':',linewidth=.7,alpha=.2)
    # Reset to the default cycle after drawing the reference cube.
    ax.set_prop_cycle(None)
    # One uninterrupted line per agent; markers expose repeated and shared states.
    for who,marker,style in [('A','o','-'),('B','s','--')]:
        v=np.asarray([s[who]['p'] for s in story])@bits
        ax.plot(v[:,0],v[:,1],v[:,2],marker=marker,linestyle=style,linewidth=2.1,label=f'Agent {who}')
    ax.set(xlabel='Expected high bit',ylabel='Expected middle bit',zlabel='Expected low bit',
           xlim=(-.06,1.09),ylim=(-.06,1.09),zlim=(-.06,1.09),xticks=(0,.5,1),yticks=(0,.5,1),zticks=(0,.5,1))
    ax.view_init(elev=24,azim=-56);ax.set_box_aspect((1,1,1));ax.legend(loc='upper left',frameon=False)
    fig.text(.73,.72,'READ THE GEOMETRY',fontsize=12,weight='bold')
    fig.text(.73,.66,'Corners = definite locations.\n\nInterior points = belief centroids.\n\nThe paths move as evidence\narrives or the model resets.\n\nA shared point need not mean\na shared full representation.',fontsize=12,linespacing=1.7,va='top')
    return fig


def ambiguity(story):
    fig,ax=page(8,'Two worlds produce the same ordinary reports',
        'At event 12, both explanations fit every reported source bit.',
        'Location 2 has ordinary bit pattern 010 with orientation 0. Location 5 has bit pattern 101 with orientation 1, producing the same reported 010. Both posterior entries are exactly 1/2. A repeated ordinary reading cannot distinguish them.',kind='chart')
    joint=np.zeros((2,8));cases=story[12]['A']['cases']
    for j,theta in cases:joint[theta,j]=1/len(cases)
    ax.imshow(joint,aspect='auto',origin='lower',interpolation='nearest',vmin=0,vmax=.5)
    ax.set(xticks=range(8),yticks=(0,1),yticklabels=('Orientation 0','Orientation 1'),xlabel='Candidate source location')
    ax.set_xticks(np.arange(-.5,8,1),minor=True);ax.grid(which='minor',linewidth=.6,alpha=.2);ax.tick_params(which='minor',length=0)
    for j,theta in cases:ax.text(j,theta,'1/2',ha='center',va='center',fontsize=25,weight='bold')
    ax.text(2,1.68,'(source 2, orientation 0)',ha='center',fontsize=11)
    ax.text(5,1.68,'(source 5, orientation 1)',ha='center',fontsize=11)
    return fig


def calibration(story):
    fig,ax=page(9,'More of the same is not a new distinction',
        'A new evidence channel resolves a problem that repeated ordinary observations leave unchanged.',
        'These are joint (source, orientation) hypotheses after the reset. The repeated high-bit reading at event 13 leaves both possibilities intact. The calibration at event 14 reduces B to one case, and its message lets A make the same update at event 15.',kind='chart')
    sub=story[8:16];xs=[s['t'] for s in sub]
    ax.step(xs,[s['A']['n_cases'] for s in sub],where='post',marker='o',label='Agent A')
    ax.step(xs,[s['B']['n_cases'] for s in sub],where='post',marker='s',linestyle='--',label='Agent B')
    ax.set(xlim=(7.8,15.2),ylim=(.5,10),xticks=xs,yticks=(1,2,4,8),xlabel='Event index',ylabel='Compatible source / orientation pairs')
    ax.legend(frameon=False,ncol=2,loc='upper right')
    ax.annotate('Repeat: no reduction',xy=(13,2),xytext=(11.4,5.0),fontsize=12,arrowprops={'arrowstyle':'->'})
    ax.annotate('Calibration\nthen communication',xy=(14,1),xytext=(14.0,6.4),ha='center',fontsize=12,arrowprops={'arrowstyle':'->'})
    chart_finish(ax);return fig


def timeline(story):
    fig,ax=page(10,'External events and internal reactions are interleaved',
        'An event raster reveals who observes, who communicates, and when an action actually reaches the world.',
        'Circles are scheduled observable operations, squares are messages, and the final star is the external service command. Event 6 changes the world without directly changing either belief. The next report is what causes A to revise. Time here is event order, not measured seconds.',kind='chart')
    lanes={'World change':5,'A observes':4,'B observes':3,'Message channel':2,'Action check':1,'External action':0}
    for label,y in lanes.items():ax.axhline(y,linewidth=.55,alpha=.2)
    for label,channel,active,marker in [('World change','world','', 'D'),('A observes','observation','A','o'),('B observes','observation','B','o'),('Message channel','message','','s'),('Action check','check','','^'),('External action','action','','*')]:
        inds=[s['t'] for s in story if s['channel']==channel and (not active or s['active']==active)]
        ax.plot(inds,[lanes[label]]*len(inds),linestyle='none',marker=marker,markersize=14 if marker=='*' else 9)
    ax.set(xlim=(-.4,17.5),ylim=(-.6,5.8),xticks=range(18),yticks=list(lanes.values()),yticklabels=list(lanes),xlabel='Event index')
    ax.annotate('unannounced\norientation change',xy=(6,5),xytext=(3.5,5.40),fontsize=10,ha='center',arrowprops={'arrowstyle':'->'})
    for t,label in [(3,'both ways'),(8,'reset notice'),(12,'new evidence'),(15,'calibration')]:
        ax.text(t,2.33,label,fontsize=9,ha='center',rotation=0)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    return fig


def ablation(story):
    fig,ax=page(11,'Remove a channel; the internal endpoint changes',
        'Controlled access comparison using the same post-change source and the same available private observations.',
        'Without messages, A has high and middle bits while B has the low bit and calibration. Each retains four possible source locations. With all messages but no calibration, both retain two. These are exact information-access comparisons, not training runs or general performance scores.',kind='chart')
    controls=controlled_access_cases();names=list(controls)
    counts={who:[len({c[0] for c in controls[name][who]}) for name in names] for who in ('A','B')}
    y=np.arange(3)
    ax.barh(y-.17,counts['A'],height=.3,label='Agent A')
    ax.barh(y+.17,counts['B'],height=.3,label='Agent B',hatch='//')
    for i in range(3):
        for offset,who in [(-.17,'A'),(.17,'B')]:ax.text(counts[who][i]+.10,i+offset,str(counts[who][i]),va='center',fontsize=12)
    ax.set(yticks=y,yticklabels=names,xlim=(0,5),xticks=(0,1,2,3,4),xlabel='Possible source locations at the endpoint')
    ax.invert_yaxis();ax.legend(frameon=False,ncol=2,loc='lower right');chart_finish(ax)
    return fig


def gate(story):
    fig,ax=page(12,'Waiting is part of the action policy',
        'Agreement about uncertainty is not permission to choose an arbitrary member of it.',
        'The gate checks every case in the agent\'s current support. This is not a probability threshold or a moral authority claim. At event 12, locations 2 and 5 remain possible; after calibration, only 5 remains. Correctness still depends on the actual world belonging to the model family.')
    box(ax,.25,3.8,3.5,2.0,'CURRENT BELIEF','{(2, 0), (5, 1)}\nTwo different action targets',size=16)
    box(ax,5.0,3.75,4.0,2.1,'ONE ACTION FOR ALL?','Every surviving case must\njustify the same command.',size=16,heavy=True)
    box(ax,10.25,4.20,3.5,1.2,'NO: WAIT',size=17)
    box(ax,10.25,1.25,3.5,1.7,'YES: ISSUE BAY 5','Only after calibration\nand evidence delivery',size=15)
    arrow(ax,(3.82,4.75),(4.92,4.75),heavy=True)
    arrow(ax,(9.08,4.75),(10.17,4.75),heavy=True)
    arrow(ax,(7.0,3.67),(10.17,2.1),'after calibration: {(5, 1)}',label_pos=(9.33,3.2),rad=.12,size=11)
    text(ax,12.0,3.64,'request new evidence',11)
    box(ax,.25,.85,7.5,1.65,'THE CHECK IS ALSO AN INTERNAL OPERATION',
        'A confident guess, a verified action, and an issued command\nare different events in the computational record.',size=14)
    return fig


def levels():
    fig,ax=page(13,'State updating is not the same as self-improvement',
        'The animation implements the upper loop. The lower loop is a proposed extension, not a hidden result.',
        'The toy agents update beliefs and replace a contradicted model scope using supplied rules. They do not learn a new query policy, alter source code, or improve their own learner. The manuscript studies additional finite mechanisms for compiler and rule acquisition; those experiments are not being rerun here.',source='Source: Self-Improving Intelligence v1.0, Sections 1, 23, 31. Atlas distinction; no claim of observed neural self-improvement.')
    text(ax,.3,6.35,'FAST LOOP  /  executed in this model',14,ha='left',weight='bold')
    for x,title,body in [(.35,'Observe','receive evidence'),(4.95,'Update state','refine beliefs'),(9.55,'Select / check','justify an action')]:
        box(ax,x,4.50,4.1,1.4,title,body,size=16)
    arrow(ax,(4.50,5.2),(4.88,5.2),heavy=True);arrow(ax,(9.10,5.2),(9.48,5.2),heavy=True)
    text(ax,7.0,3.70,'Persistent belief change can occur while the update algorithm stays fixed.',12)
    text(ax,.3,2.75,'SLOW LOOP  /  proposed learning extension',14,ha='left',weight='bold')
    for x,title,body in [(.35,'Propose a new method','encoder, query policy, operator'),(4.95,'Test the same contract','new tasks + complete costs'),(9.55,'Retain a checked change','then reassess future learning')]:
        box(ax,x,.85,4.1,1.4,title,body,size=14,dashed=True)
    arrow(ax,(4.50,1.55),(4.88,1.55),dashed=True);arrow(ax,(9.10,1.55),(9.48,1.55),dashed=True)
    return fig


def contract():
    fig,ax=page(14,'What these displays mean',
        'A visual model can be expressive without claiming access to an unmeasured mind.',
        'The source manuscript remains unchanged. The atlas extends its hidden-case and sensor-convention examples into a new scripted two-agent illustration. All frames, charts, and 3D coordinates are regenerated from code. No AI-generated pictorial asset is used.',source='References: Self-Improving Intelligence v1.0, Sections 7, 9, 24, 31. Canonical model, schedule, checks and CSV/JSON are included.')
    items=[('WORLD','A fixed location j in 0,...,7 within each episode.\nThe sensor convention changes once between investigations.'),
           ('OBSERVATION',r'$o=\operatorname{bit}_q(j)\;\mathrm{XOR}\;\theta$'+'\nA calibration directly reports the orientation.'),
           ('INTERNAL STATE','Uniform probability on the cases compatible with active receipts.\nOld receipts are archived when the supplied reset rule is used.'),
           ('COMMUNICATION','Reliable delivery, honest receipts, explicit episode notices.\nSharing is not independent remeasurement.'),
           ('DECISION','Issue a command only when all remaining locations agree.\nThe scripted schedule makes one final external commitment.'),
           ('LIMIT','No neural training, real activation telemetry, consciousness claim,\nor general guarantee for arbitrary environmental change.')]
    for k,(h,b) in enumerate(items):
        y=6.03-k*1.00
        text(ax,.30,y,h,12,ha='left',weight='bold')
        text(ax,3.12,y,b,12,ha='left',linespacing=1.5)
        if k<5:ax.plot([.3,13.5],[y-.46,y-.46],linewidth=.5,alpha=.25)
    return fig


PLATE_BUILDERS=[('01_agent_boundary',lambda s:architecture()),
                ('02_private_and_shared_state',lambda s:coupling()),
                ('03_synchronized_agent_view',state_plate),
                ('04_belief_heatmap',beliefs),('05_uncertainty_trace',uncertainty),
                ('06_prediction_and_feedback',prediction),('07_internal_trajectory_3d',trajectory),
                ('08_model_ambiguity',ambiguity),('09_calibration_changes_the_state',calibration),
                ('10_interaction_timeline',timeline),('11_access_comparison',ablation),
                ('12_action_gate',gate),('13_inference_and_learning',lambda s:levels()),
                ('14_model_contract',lambda s:contract())]


def render_atlas() -> dict:
    for d in ('data','plates','frames','validation'):(ROOT/d).mkdir(parents=True,exist_ok=True)
    story=run_story()
    (ROOT/'data'/'agent_trace.json').write_text(json.dumps(story,indent=2),encoding='utf-8')
    (ROOT/'validation'/'model_checks.json').write_text(json.dumps(validate(),indent=2),encoding='utf-8')
    with (ROOT/'data'/'agent_trace.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['event','agent','epoch','entropy_bits','possible_locations','joint_cases','ready','active_receipts','title'])
        writer.writeheader()
        for s in story:
            for a in ('A','B'):
                st=s[a]
                writer.writerow({'event':s['t'],'agent':a,'epoch':st['epoch'],'entropy_bits':st['entropy'],
                                 'possible_locations':';'.join(map(str,st['locations'])),'joint_cases':st['n_cases'],
                                 'ready':st['ready'],'active_receipts':len(st['receipt_ids']),'title':s['title']})
    pdf=ROOT/'Agent_Dynamics_Python_Visual_Atlas.pdf'
    with PdfPages(pdf,metadata={'Title':'Agent Dynamics: Internal State and External Interaction',
                               'Author':'Komorebi P. / Operation Komorebi',
                               'Subject':'Python-generated analytical visual companion; explicit two-agent toy model.'}) as out:
        for name,fn in PLATE_BUILDERS:
            fig=fn(story)
            fig.savefig(ROOT/'plates'/f'{name}.svg')
            fig.savefig(ROOT/'plates'/f'{name}.png',dpi=145)
            out.savefig(fig)
            plt.close(fig)
    return {'pdf':str(pdf),'pages':len(PLATE_BUILDERS),'model_assertions':validate()['assertions']}


def render_animation() -> dict:
    story=run_story();images=[];embedded=[]
    for s in story:
        fig=plt.figure(figsize=(14,9),dpi=110)
        fig.text(.035,.97,'AGENTS IN MOTION  /  INTERNAL STATE + EXTERNAL FEEDBACK',fontsize=10,weight='bold',va='top')
        fig.text(.035,.922,f'{s["t"]:02d}  {s["title"]}',fontsize=20,weight='bold',va='top')
        ax=fig.add_axes([.025,.16,.95,.68]);draw_state(ax,s)
        fig.text(.035,.102,wrap(s['detail'],128),fontsize=11.5,va='top',linespacing=1.45)
        fig.text(.035,.025,'Computed toy-model trace. Supplied schedule and update rules. No neural activity measurements.',fontsize=9)
        b=io.BytesIO();fig.savefig(b,format='png',dpi=110);plt.close(fig)
        raw=b.getvalue();(ROOT/'frames'/f'event_{s["t"]:02d}.png').write_bytes(raw)
        images.append(Image.open(io.BytesIO(raw)).convert('RGB'))
        embedded.append('data:image/png;base64,'+base64.b64encode(raw).decode('ascii'))
    gif=ROOT/'Agent_Dynamics_Animated.gif'
    images[0].save(gif,save_all=True,append_images=images[1:],loop=0,
                   duration=[1500 if i in (0,6,7,12,14,17) else 1000 for i in range(18)],optimize=False)
    labels=[s['title'] for s in story]
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Dynamics - Python Visual Player</title>
<style>body{font-family:system-ui,sans-serif;max-width:1300px;margin:1.2rem auto;padding:0 1rem;line-height:1.5}h1{margin-bottom:.25rem}img{display:block;width:100%;height:auto}button,select{font:inherit;padding:.45rem .8rem}input{width:min(60vw,650px)}.controls{display:flex;gap:.8rem;align-items:center;flex-wrap:wrap}small{display:block;margin:1rem 0}details{margin-top:1rem}</style>
<h1>Agent Dynamics</h1><p>An offline, Python-rendered visual player. Observe both private belief states and the external events that change them.</p>
<div class="controls"><button id="play">Play</button><button id="back">Previous</button><button id="next">Next</button>
<input type="range" id="time" min="0" max="17" value="0" aria-label="Event index"><span id="label"></span>
<select id="speed" aria-label="Playback speed"><option value="1400">Slow</option><option value="850">Medium</option><option value="450">Fast</option></select></div>
<img id="frame" alt="Synchronized world and two-agent belief states">
<small>The location shown inside the environment is viewer-only truth. Agents receive only explicit observations and messages. The reset and communication schedule are supplied, not learned. There are no network calls.</small>
<details><summary>What changes at the turning point?</summary><p>A report contradicts A's current model. A expands its candidate set, archives stale receipts, and explicitly informs B. The two agents eventually narrow the possibilities to two source/sensor pairs. Repetition leaves that ambiguity intact; a separately available calibration resolves it. This illustrates belief revision, not recursive improvement of the update algorithm.</p></details>
<script>const frames=__FRAMES__, labels=__LABELS__;let t=0,timer=null;const el=id=>document.getElementById(id);
function show(){el('frame').src=frames[t];el('time').value=t;el('label').textContent=(t+1)+' / '+frames.length;el('frame').alt='Event '+t+': '+labels[t];}
function stop(){if(timer)clearInterval(timer);timer=null;el('play').textContent='Play';}
function start(){stop();el('play').textContent='Pause';timer=setInterval(()=>{t=(t+1)%frames.length;show()},Number(el('speed').value));}
el('play').onclick=()=>timer?stop():start();el('back').onclick=()=>{stop();t=(t+frames.length-1)%frames.length;show()};el('next').onclick=()=>{stop();t=(t+1)%frames.length;show()};el('time').oninput=e=>{stop();t=Number(e.target.value);show()};el('speed').onchange=()=>{if(timer)start()};show();</script></html>'''
    html=html.replace('__FRAMES__',json.dumps(embedded)).replace('__LABELS__',json.dumps(labels))
    player=ROOT/'Agent_Dynamics_Interactive.html';player.write_text(html,encoding='utf-8')
    return {'gif':str(gif),'html':str(player),'frames':len(images)}

if __name__=='__main__':
    print(render_atlas())
    print(render_animation())
