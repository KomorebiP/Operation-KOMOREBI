#!/usr/bin/env python3
"""Emit typed source expression data for an independently defined Lean evaluator.

Uses the frozen Block19 source selector, not its arithmetic term printer.
The AST parser/selection/emitter remain trusted; Lean checks interpretation
against the separately emitted and already refined source operations.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
from bind_python_source import ROOT, HASHES, mask_sources


def string(s):
    return json.dumps(s, ensure_ascii=False)


def nat(n):
    if isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 0:
        return f"(.literal {n.value})"
    if isinstance(n, ast.Name):
        return f"(.variable {string(n.id)})"
    if isinstance(n, ast.BinOp):
        op = {ast.Add:"add",ast.Sub:"sub",ast.Mult:"mul",ast.Pow:"pow"}.get(type(n.op))
        if op:
            return f"(.{op} {nat(n.left)} {nat(n.right)})"
    raise ValueError("Unsupported natural expression: "+ast.dump(n))


def rat(n):
    if isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 0:
        return f"(.literal {n.value})"
    if isinstance(n, ast.Name):
        return f"(.variable {string(n.id)})"
    if isinstance(n, ast.BinOp):
        if isinstance(n.op, ast.Pow):
            return f"(.pow {rat(n.left)} {nat(n.right)})"
        op = {ast.Add:"add",ast.Sub:"sub",ast.Mult:"mul",ast.Div:"div"}.get(type(n.op))
        if op:
            return f"(.{op} {rat(n.left)} {rat(n.right)})"
    if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name):
        # partial[] is an evaluated two-entry list, not a change of syntax.
        return f"(.entry {string(n.value.id)} {nat(n.slice)})"
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and not n.keywords:
        name=n.func.id
        if name=="Q" and len(n.args)==1:
            return rat(n.args[0])
        if name=="Q" and len(n.args)==2:
            return f"(.div {rat(n.args[0])} {rat(n.args[1])})"
        if name=="factorial" and len(n.args)==1:
            return f"(.factorial {nat(n.args[0])})"
        if name=="comb" and len(n.args)==2:
            return f"(.choose {nat(n.args[0])} {nat(n.args[1])})"
        if name=="max" and len(n.args)==2:
            return f"(.maximum {rat(n.args[0])} {rat(n.args[1])})"
    raise ValueError("Unsupported rational expression: "+ast.dump(n))


def value(n):
    if isinstance(n, ast.Name) and n.id=="last":
        return f"(.integer {nat(n)})"
    if isinstance(n, ast.Tuple) and len(n.elts)==2:
        return f"(.tuple {value(n.elts[0])} {value(n.elts[1])})"
    return f"(.rational {rat(n)})"


def generate(coupled, family):
    patterns,holes=mask_sources(coupled,family)
    expected=json.loads((ROOT/'tools/python_refinement/source_patterns.json').read_text(encoding='utf-8'))
    if patterns!=expected:
        raise ValueError("Unsupported statement/control change")
    lines=['import CoupledExpressionSemantics','','/-! Generated typed expression data; do not hand-edit. -/','',
           'namespace Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions.Source','']
    for name in ('product','q_power','r_power','weight_u','weight_v','ordinary','partial_term','seed','update','outer_default','tail','steps_default','bits_default','last_default'):
        is_nat=name in ('q_power','r_power','steps_default','bits_default','last_default')
        kind,emit=('NatExpr',nat) if is_nat else ('RatExpr',rat)
        lines.append(f'def {name} : {kind} := {emit(holes[name])}')
    d=holes['dictionary']
    if not isinstance(d,ast.Dict):raise ValueError('Literal dictionary required')
    fields=[]
    for k,v in zip(d.keys,d.values,strict=True):
        if not isinstance(k,ast.Constant) or type(k.value)is not str:raise ValueError('Literal key required')
        fields.append(f'({string(k.value)}, {value(v)})')
    lines += ['', 'def dictionary : List (String × ValueExpr) :=', '  ['+',\n   '.join(fields)+']', '',
              'end Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions.Source','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--output',type=Path)
    args=p.parse_args()
    raw={name:(ROOT/name).read_bytes() for name in HASHES}
    for name,data in raw.items():
        if hashlib.sha256(data).hexdigest()!=HASHES[name]:raise ValueError('Pinned source changed: '+name)
    code=generate(raw['research/coupled_lab.py'].decode('utf-8'),raw['research/family_lab.py'].decode('utf-8')).encode('utf-8')
    target=ROOT/'lean/CoupledSourceExpressions.lean'
    if args.write:target.write_bytes(code)
    if target.read_bytes()!=code:raise ValueError('Expression artifact differs from source')
    report={'status':'passed','source_hashes':HASHES,'expression_artifact_sha256':hashlib.sha256(code).hexdigest(),
            'emitter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'trust_boundary':'Parser, source selector and expression-data emitter; operator interpretation and lowering comparisons are checked by Lean. Statement/control template and Python primitive implementations remain trusted.'}
    if args.output:
        if args.output.exists():p.error('--output must be new')
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report))


if __name__=='__main__':main()
