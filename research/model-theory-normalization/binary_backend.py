"""Bit-list reference arithmetic and its explicit gate/cell model.

Least significant bit first. Arithmetic cores use Boolean gates, not native
integer multiplication or division. Encoding/decoding and Python list/index
management are outside the gate/cell model, and are reported separately.
This is a tested port of the Lean algorithms, not verified code extraction.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import Any, Sequence
import hashlib,json

Word = tuple[int, ...]

def encode(n: int) -> Word:
    if type(n) is not int or n < 0:
        raise ValueError('encode requires a nonnegative integer')
    out=[]
    while n:
        out.append(n & 1); n >>= 1
    return tuple(out)

def decode(a: Word) -> int:
    n=0
    for bit in reversed(a): n=(n<<1)|bit
    return n

def validate(a: Sequence[int]) -> Word:
    if any(type(x) is not int or x not in (0,1) for x in a):
        raise ValueError('word must contain integer bits 0 or 1')
    return tuple(a)

def pad(a: Word,n: int)->Word:
    return a+(0,)*max(0,n-len(a))

def add_eval(a: Word,b: Word,c: int=0)->tuple[Word,int]:
    if c not in (0,1): raise ValueError('carry must be a bit')
    out=[];n=max(len(a),len(b))
    for i in range(n):
        x=a[i] if i<len(a) else 0;y=b[i] if i<len(b) else 0
        u=x^y;out.append(u^c);c=(x&y)|(u&c)
    out.append(c)
    return tuple(out),10*n+1

def sub_eval(a: Word,b: Word,c: int=0)->tuple[tuple[Word,int],int]:
    if len(a)!=len(b):raise ValueError('subtractor requires equal widths')
    if c not in (0,1):raise ValueError('borrow must be a bit')
    out=[]
    for x,y in zip(a,b):
        u=x^y;out.append(u^c);c=((1-x)&y)|((1-u)&c)
    return (tuple(out),c),12*len(a)+1

def mul_eval(a: Word,b: Word)->tuple[Word,int]:
    out=();cost=1
    for bit in reversed(a):
        shifted=(0,)+out;cost+=2
        if bit:
            out,c=add_eval(b,shifted);cost+=c
        else:out=shifted
    return out,cost

def div_eval(a: Word,b: Word)->tuple[tuple[Word,Word],int]:
    if not any(b):raise ZeroDivisionError('zero or padded-zero divisor')
    quotient=();remainder=();cost=1
    for bit in reversed(a):
        u=(bit,)+remainder;w=max(len(u),len(b))
        x,y=pad(u,w),pad(b,w)
        (diff,borrow),subcost=sub_eval(x,y)
        quotient=(1-borrow,)+quotient
        remainder=x if borrow else diff
        cost+=2*w+subcost+3
    return (quotient,remainder),cost

def zero_eval(a: Word)->tuple[bool,int]:
    z=1
    for b in a:z=z&(1-b)
    return bool(z),4*len(a)+1

@dataclass(frozen=True)
class Signed:
    negative: bool
    magnitude: Word
    @staticmethod
    def of_int(n:int)->'Signed':
        if type(n) is not int:raise ValueError('integer required')
        return Signed(n<0,encode(abs(n)))
    def value(self)->int:
        m=decode(self.magnitude)
        return -m if self.negative else m

def difference_eval(a:Word,b:Word)->tuple[Signed,int]:
    width=max(len(a),len(b));x,y=pad(a,width),pad(b,width)
    (diff,borrow),cost=sub_eval(x,y);cost+=2*width+1
    if borrow:
        (diff,_),c=sub_eval(y,x);cost+=c
    return Signed(bool(borrow),diff),cost

def signed_add_eval(a:Signed,b:Signed)->tuple[Signed,int]:
    if a.negative==b.negative:
        z,c=add_eval(a.magnitude,b.magnitude)
        return Signed(a.negative,z),c+2
    if a.negative:
        z,c=difference_eval(b.magnitude,a.magnitude)
    else:
        z,c=difference_eval(a.magnitude,b.magnitude)
    return z,c+2

def signed_sub_eval(a:Signed,b:Signed)->tuple[Signed,int]:
    z,c=signed_add_eval(a,Signed(not b.negative,b.magnitude))
    return z,c+1

def signed_mul_eval(a:Signed,b:Signed)->tuple[Signed,int]:
    z,c=mul_eval(a.magnitude,b.magnitude)
    return Signed(a.negative ^ b.negative,z),c+1

def signed_div_eval(a:Signed,b:Word)->tuple[tuple[Signed,Word],int]:
    zero,checkcost=zero_eval(b)
    if zero:raise ZeroDivisionError('positive divisor required')
    (q,r),cost=div_eval(a.magnitude,b);cost+=checkcost+1
    if not a.negative:return (Signed(False,q),r),cost
    zero,zcost=zero_eval(r);cost+=zcost
    if zero:return (Signed(True,q),r),cost
    q,c=add_eval(q,(),1);cost+=c
    width=max(len(b),len(r));(r,borrow),c=sub_eval(pad(b,width),pad(r,width))
    if borrow:raise ArithmeticError('restoring remainder invariant failed')
    cost+=2*width+c
    return (Signed(True,q),r),cost

def residue_mul_eval(a:Word,b:Word,m:Word)->tuple[Word,int]:
    p,pc=mul_eval(a,b);(_,r),dc=div_eval(p,m)
    return r,pc+dc

def residue_add_eval(a:Word,b:Word,m:Word)->tuple[Word,int]:
    s,sc=add_eval(a,b);(_,r),dc=div_eval(s,m)
    return r,sc+dc

@dataclass
class BitMeter:
    """Drop-in scalar interface for the unchanged v0.9 imperative port.

    `units` retains the old arithmetic-event count. `gate_cell_units` is a
    DIFFERENT counter, computed by the bit circuits and explicit sign wrappers.
    Control, queue and conversion overhead are not misrepresented as included.
    """
    counts: Counter=field(default_factory=Counter)
    bit_counts: Counter=field(default_factory=Counter)
    conversion_input_bits:int=0
    conversion_output_bits:int=0
    maximum_operand_bits:int=0
    maximum_output_storage_bits:int=0
    samples:list=field(default_factory=list)
    trace_hash:Any=field(default_factory=hashlib.sha256,repr=False)
    keep_samples:int=24
    @property
    def units(self)->int:return sum(self.counts.values())
    @property
    def gate_cell_units(self)->int:return sum(self.bit_counts.values())
    def record(self,op:str,args:tuple[int,...],out:Any,cost:int,storage:int=0)->Any:
        self.counts[op]+=1;self.bit_counts[op]+=cost
        widths=[abs(x).bit_length() for x in args]
        self.conversion_input_bits+=sum(widths)
        self.conversion_output_bits+=abs(int(out)).bit_length()
        self.maximum_operand_bits=max([self.maximum_operand_bits]+widths)
        self.maximum_output_storage_bits=max(self.maximum_output_storage_bits,storage)
        rec=[op,list(args),out,cost,storage]
        self.trace_hash.update((json.dumps(rec,separators=(',',':'))+'\n').encode())
        if len(self.samples)<self.keep_samples:self.samples.append(rec)
        return out
    def charge(self,op:str,value:Any)->Any:
        # These are scalar extraction and constructor tests, not bit arithmetic.
        if op not in ('residue_lift','option_test'):raise ValueError('unpriced primitive '+op)
        return self.record(op,(int(value),),value,max(1,abs(int(value)).bit_length()))
    def add(self,a:int,b:int)->int:
        z,c=signed_add_eval(Signed.of_int(a),Signed.of_int(b));return self.record('integer_add',(a,b),z.value(),c,len(z.magnitude))
    def sub(self,a:int,b:int)->int:
        z,c=signed_sub_eval(Signed.of_int(a),Signed.of_int(b));return self.record('integer_sub',(a,b),z.value(),c,len(z.magnitude))
    def mul(self,a:int,b:int)->int:
        z,c=signed_mul_eval(Signed.of_int(a),Signed.of_int(b));return self.record('integer_mul',(a,b),z.value(),c,len(z.magnitude))
    def div(self,a:int,b:int)->int:
        if b<=0:raise ValueError('positive divisor contract')
        (q,r),c=signed_div_eval(Signed.of_int(a),encode(b));return self.record('integer_div',(a,b),q.value(),c,len(q.magnitude)+len(r))
    def rem(self,a:int,b:int)->int:
        if b<=0:raise ValueError('positive divisor contract')
        (q,r),c=signed_div_eval(Signed.of_int(a),encode(b));return self.record('integer_rem',(a,b),decode(r),c,len(q.magnitude)+len(r))
    def abs(self,a:int)->int:
        z=Signed.of_int(a);return self.record('integer_abs',(a,),decode(z.magnitude),1,len(z.magnitude))
    def neg(self,a:int)->int:
        z=Signed.of_int(a);q=Signed(not z.negative,z.magnitude);return self.record('integer_neg',(a,),q.value(),1,len(q.magnitude))
    def zero(self,a:int)->bool:
        z,c=zero_eval(Signed.of_int(a).magnitude);return self.record('zero_compare',(a,),z,c)
    def nonneg(self,a:int)->bool:
        z=Signed.of_int(a);return self.record('sign_compare',(a,),not z.negative,1)
    def rmul(self,a:int,b:int,m:int)->int:
        if not 0<=a<m or not 0<=b<m:raise ValueError('canonical residues required')
        z,c=residue_mul_eval(encode(a),encode(b),encode(m));return self.record('residue_mul',(a,b,m),decode(z),c,len(z))
    def radd(self,a:int,b:int,m:int)->int:
        if not 0<=a<m or not 0<=b<m:raise ValueError('canonical residues required')
        z,c=residue_add_eval(encode(a),encode(b),encode(m));return self.record('residue_add',(a,b,m),decode(z),c,len(z))
    def report(self)->dict[str,Any]:
        return {'arithmetic_events':self.units,'gate_cell_units':self.gate_cell_units,
          'events_by_opcode':dict(sorted(self.counts.items())),
          'gate_cell_by_opcode':dict(sorted(self.bit_counts.items())),
          'conversion_input_bits':self.conversion_input_bits,'conversion_output_bits':self.conversion_output_bits,
          'maximum_operand_bits':self.maximum_operand_bits,'maximum_output_storage_bits':self.maximum_output_storage_bits,
          'trace_sha256':self.trace_hash.hexdigest(),'samples':self.samples}
