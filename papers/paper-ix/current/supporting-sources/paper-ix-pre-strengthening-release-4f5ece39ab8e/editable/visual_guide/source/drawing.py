#!/usr/bin/env python3
"""Deterministic, editable TikZ plates. Geometry samples are distinct from exact-check evidence."""
from __future__ import annotations
import json, math
from pathlib import Path
from models import *
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics'

def F(x):return f'{float(x):.6f}'.rstrip('0').rstrip('.') or '0'
def tex(x):
    x=Q(x)
    if x.denominator==1:return str(x.numerator)
    sign='- ' if x<0 else ''
    return sign+r'\frac{'+str(abs(x.numerator))+'}{'+str(x.denominator)+'}' 
class Plate:
    def __init__(self,name,title):
        self.name=name;self.title=title;self.parts=[r'\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth,line cap=round,line join=round]',r'\path[use as bounding box] (0,-.6) rectangle (14,4.8);']
    def add(self,t):self.parts.append(t)
    def text(self,x,y,t,opts=''):
        self.add(r'\node[font=\small,align=center'+(','+opts if opts else '')+'] at ('+F(x)+','+F(y)+') {'+t+'};')
    def line(self,x1,y1,x2,y2,opts=''):
        self.add(r'\draw['+opts+'] ('+F(x1)+','+F(y1)+') -- ('+F(x2)+','+F(y2)+');')
    def rect(self,x,y,w,h,opts='draw,fill=black!7'):
        self.add(r'\path['+opts+'] ('+F(x)+','+F(y)+') rectangle ('+F(x+w)+','+F(y+h)+');')
    def circ(self,x,y,r=.11,opts='fill=black'):
        self.add(r'\path['+opts+'] ('+F(x)+','+F(y)+') circle ('+F(r)+');')
    def axes(self,x,y,w,h,xmax,ymax,xticks=(),yticks=(),xlabel='',ylabel='',xmin=0,ymin=0):
        def pt(a,b):return (x+w*(float(a)-xmin)/(xmax-xmin),y+h*(float(b)-ymin)/(ymax-ymin))
        for a in xticks:
            xx,_=pt(a,ymin);self.line(xx,y,xx,y+h,'black!13,line width=.25pt');self.line(xx,y-.06,xx,y+.06);self.text(xx,y-.26,str(a),'font=\\scriptsize')
        for b in yticks:
            _,yy=pt(xmin,b);self.line(x,yy,x+w,yy,'black!13,line width=.25pt');self.text(x-.16,yy,str(b),'anchor=east,font=\\scriptsize')
        self.line(x,y,x+w+.12,y,'->,line width=.6pt');self.line(x,y,x,y+h+.12,'->,line width=.6pt')
        if xlabel:self.text(x+w/2,y-.55,xlabel,'font=\\scriptsize')
        if ylabel:self.text(x,y+h+.4,ylabel,'anchor=west,font=\\scriptsize')
        return pt
    def curve(self,pt,xs,ys,style='line width=1.1pt'):
        coords=[]
        for a,b in zip(xs,ys):
            xx,yy=pt(a,b)
            if not(math.isfinite(xx) and math.isfinite(yy)):raise ValueError('Nonfinite plotting coordinate')
            coords.append('('+F(xx)+','+F(yy)+')')
        self.add(r'\draw['+style+'] plot coordinates {'+' '.join(coords)+'};')
    def matrix(self,x,y,A,cell=.68,rows=None,cols=None,title='',cellw=None):
        cw=cell if cellw is None else cellw
        if title:self.text(x+len(A[0])*cw/2,y+.7,title,'font=\\small')
        for i in range(len(A)):
            for j in range(len(A[0])):
                self.rect(x+j*cw,y-(i+1)*cell,cw,cell,'draw=black!30,fill='+('white' if A[i][j]==0 else 'black!8'))
                self.text(x+(j+.5)*cw,y-(i+.5)*cell,'$'+tex(A[i][j])+'$','font=\\small')
        if rows:
            for i,a in enumerate(rows):self.text(x-.15,y-(i+.5)*cell,a,'anchor=east,font=\\scriptsize')
        if cols:
            for j,a in enumerate(cols):self.text(x+(j+.5)*cw,y+.23,a,'font=\\scriptsize')
    def bars(self,x,y,vals,labels,width=4.4,height=2.7,maxv=1,title='',annotate=True):
        n=len(vals);pitch=width/n;bw=pitch*.52
        self.line(x,y,x+width,y,'line width=.6pt')
        if title:self.text(x+width/2,y+height+.75,title)
        for j,v in enumerate(vals):
            hh=float(v)/float(maxv)*height;xx=x+(j+.24)*pitch
            self.rect(xx,y,bw,hh,'draw=black,fill=black!12,line width=.6pt')
            self.text(xx+bw/2,y-.3,labels[j],'font=\\scriptsize')
            if annotate:self.text(xx+bw/2,y+hh+.22,'$'+tex(v)+'$','font=\\scriptsize')
    def finish(self):
        self.add(r'\end{tikzpicture}');(OUT/(self.name+'.tex')).write_text('\n'.join(self.parts)+'\n');return {'name':self.name,'title':self.title,'kind':'editable TikZ vector drawing','numerical_geometry_only':True}

def seq(a,b,n=101):return [a+(b-a)*i/(n-1) for i in range(n)]

