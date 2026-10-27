#!/usr/bin/env python3
"""Four source-aligned vector diagrams for Paper XII. No empirical data.
Generated diagrams replace crossed arrows and distinguish the five-gate theorem
from propagation in two already existing families. No arithmetic input is inferred.
"""
import argparse, datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'svg.hashsalt':'paper-xii-1.0.0'})
dt=datetime.datetime(2026,10,10,tzinfo=datetime.timezone.utc)
def new(height=4.5):
 f,ax=plt.subplots(figsize=(9,height));ax.set_xlim(0,11);ax.set_ylim(0,5.5);ax.axis('off');f.subplots_adjust(left=0,right=1,bottom=0,top=1);return f,ax
def box(ax,x,y,w,h,text,size=12):
 ax.add_patch(Rectangle((x,y),w,h,fill=False,linewidth=1));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size)
def arrow(ax,x,y,xx,yy):ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops={'arrowstyle':'->','lw':1.1})
def save(f,name,title):
 f.savefig(a.output.parent/name,metadata={'Title':title,'Author':'Komorebi P.','CreationDate':dt,'ModDate':dt});plt.close(f)
# Three factor projections leave the source vertically, never through another label.
f,ax=new();ax.text(5.5,5.12,'Artin decomposition and the associated module packets',ha='center',fontsize=15)
box(ax,3.8,3.82,3.4,.7,r'$T\ \cong\ T_1\times T_2\times T_3$',14)
ax.plot([5.5,5.5],[3.82,3.43],linewidth=1);ax.plot([1.9,9.1],[3.43,3.43],linewidth=1)
for i,c in enumerate([1.9,5.5,9.1],1):
 arrow(ax,c,3.43,c,2.97);box(ax,c-1.2,2.23,2.4,.74,f'local algebra $T_{i}$',12)
 arrow(ax,c,2.23,c,1.72);box(ax,c-1.2,.92,2.4,.78,rf'$e_{i}V\ \cong\ V_{{\mathfrak{{m}}_{i}}}$',14)
ax.text(5.5,.40,'Each packet can be zero. Nonzero packets may retain nilpotent Hecke operators.',ha='center',fontsize=11)
save(f,'09_hecke_artin_packets.pdf','Paper XII Theorem 8.2: canonical Artin packets')
# Shared Frobenius data specify independent coefficient-place problems.
f,ax=new();ax.text(5.5,5.12,'One supplied Frobenius spine, several coefficient places',ha='center',fontsize=15)
box(ax,3.5,3.87,4,.65,r'supplied polynomials $P_v(X)\in L[X]$',13)
ax.plot([5.5,5.5],[3.87,3.5],linewidth=1);ax.plot([1.85,9.15],[3.5,3.5],linewidth=1)
for i,c in enumerate([1.85,5.5,9.15],1):
 arrow(ax,c,3.5,c,3.05);box(ax,c-1.45,2.03,2.9,1.0,rf'coefficient place $\lambda_{i}$'+'\nfinite occupied classes',12)
 arrow(ax,c,2.03,c,1.55);box(ax,c-1.45,.80,2.9,.73,'continuous realization\nunder Theorem 10.5',11.5)
ax.text(5.5,.30,'Every column needs its own coefficient, occupancy, continuity, and relation inputs.',ha='center',fontsize=11)
save(f,'14_companion_spine.pdf','Paper XII Theorem 10.5: conditional coefficient-place completion')
# No direct unsupported arrow from support to arithmetic realization.
f,ax=new();ax.text(5.5,5.10,'Support supplies a fiber, not an arithmetic realization',ha='center',fontsize=15)
box(ax,.15,3.42,2.7,.86,'supported point $x$\ncompatible Hecke point $y$',11.5)
box(ax,4.10,3.42,2.8,.86,'nonzero Hecke fiber\nand selected eigensystem',11.5)
box(ax,8.13,3.42,2.72,.86,'occurring classical object\nwith attached representation',11)
arrow(ax,2.86,3.85,4.09,3.85);ax.text(3.47,4.08,'support',ha='center',fontsize=10.5)
arrow(ax,6.91,3.85,8.12,3.85);ax.text(7.51,4.08,'classicality',ha='center',fontsize=10.5)
box(ax,1.45,1.95,8.1,.70,'Common Frobenius polynomials + continuity + density + Brauer-Nesbitt',11.5)
arrow(ax,9.48,3.40,9.48,2.67);arrow(ax,5.5,1.94,5.5,1.48)
box(ax,2.55,.62,5.9,.86,r'$\rho_x^{\mathrm{ss}}\ \cong\ \rho_{\pi}$'+'\nThe same specialization and the same occurring object',12)
ax.text(5.5,.20,'Irreducibility identifies the original specialization, not only its semisimplification.',ha='center',fontsize=11)
save(f,'16_pointwise_automorphy.pdf','Paper XII Theorems 9.3 and 9.4: support versus realization')
# Final diagram: separate the optional propagation theorem from the five gates.
f,ax=new(9*4.8/11);ax.set_ylim(0,4.8)
ax.text(5.5,4.5,'Five gates for one fixed deformation point',ha='center',va='center',fontsize=15)
labels=[('1  Residual','occupied problem\nand universal data'),('2  Patching','full support\nand control maps'),('3  Comparison','support inclusion\nfor actual carriers'),('4  Fiber','compatible point y\nand nonzero fiber'),('5  Realization','classicality and\nGalois comparison')]
for i,(title,body) in enumerate(labels):
 x=.12+2.19*i;ax.add_patch(Rectangle((x,2.65),1.99,1.23,fill=False,linewidth=1))
 ax.text(x+.995,3.62,title,ha='center',va='center',fontsize=11.8,fontweight='bold');ax.text(x+.995,3.12,body,ha='center',va='center',fontsize=11.4)
 if i<4:arrow(ax,x+1.99,3.27,x+2.18,3.27)
ax.text(5.5,2.23,'The conclusion identifies the specialization at that same point.',ha='center',fontsize=12)
ax.add_patch(Rectangle((.8,.69),9.4,.93,fill=False,linewidth=1))
ax.text(5.5,1.31,'Additional propagation step',ha='center',fontsize=12,fontweight='bold')
ax.text(5.5,.93,'Two existing compatible families + the same automorphic object + one common spine',ha='center',fontsize=11.2)
arrow(ax,5.5,2.09,5.5,1.64)
ax.text(5.5,.25,'Neither full support nor this diagram constructs missing companions.',ha='center',fontsize=11.5)
save(f,a.output.name,'Paper XII Theorem 12.6: five gates and separate propagation')
