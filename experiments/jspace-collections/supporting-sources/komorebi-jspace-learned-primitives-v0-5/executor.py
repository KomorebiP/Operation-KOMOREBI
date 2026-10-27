"""Executable expressions using only validated neural calls. Komorebi P.

Operand order is retained. No multiplication, addition, subtraction, square,
or power opcode is available to this language. Numerical computation inside
the learned kernels, including their supplied activations, remains necessary.
"""
import json
import numpy as np

def key(expr):return json.dumps(expr,separators=(',',':'))

class Executor:
    def __init__(self,catalog):self.catalog=catalog

    def evaluate(self,expr,xy):
        xy=np.asarray(xy,float)
        if expr=='x':return xy[...,0]
        if expr=='z':return xy[...,1]
        if isinstance(expr,list) and len(expr)==4 and expr[0]=='call':
            return self.catalog.call(expr[1],self.evaluate(expr[2],xy),self.evaluate(expr[3],xy))
        raise ValueError('Only input terminals and registered primitive calls are executable.')

    def enumerate(self,xy,max_calls=3):
        """Enumerate ordered programs. No algebraic equivalence is assumed."""
        xy=np.asarray(xy);levels=[[('x',xy[:,0]),('z',xy[:,1])]];records=[]
        for count in range(1,max_calls+1):
            level=[]
            for left_count in range(count):
                right_count=count-1-left_count
                for op in self.catalog.accepted:
                    for a,av in levels[left_count]:
                        for b,bv in levels[right_count]:
                            expr=['call',op,a,b];value=self.catalog.call(op,av,bv)
                            level.append((expr,value));records.append({'expression':expr,'values':value,'calls':count})
            levels.append(level)
        return records

    def discover(self,xy,outputs,max_calls=3,tolerance=1e-6):
        records=self.enumerate(xy,max_calls);errors=np.array([np.max(abs(r['values']-outputs)) for r in records])
        feasible=np.flatnonzero(errors<=tolerance)
        if not len(feasible):return {'status':'no_fitting_program','best_error':float(errors.min()),'checked':len(records)}
        chosen=int(feasible[0]);r=records[chosen]
        return {'status':'fitted','expression':r['expression'],'calls':r['calls'],
                'max_demonstration_error':float(errors[chosen]),'fitting_programs':len(feasible),'checked':len(records),
                'kernel_identity':self.catalog.kernels.identity(),'claim':'Finite demonstration fit, pending independent validation.'}
