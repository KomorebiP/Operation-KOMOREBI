#!/usr/bin/env python3
"""Replay preserved August math code with only output destinations remapped.

Three module-level OUT assignments are changed in the execution AST, not in
stored source files. The odd-prime script's audit() is called directly so its
historical cwd output cannot overwrite evidence. No mathematics is edited.
"""
import argparse,ast,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--odd',action='store_true');a=p.parse_args()
    tree=ast.parse(a.source.read_text(),filename=str(a.source))
    remapped=0
    if not a.odd:
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OUT' for t in node.targets):
                node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(a.out.resolve()))],keywords=[]);remapped+=1
        assert remapped==1
    ast.fix_missing_locations(tree)
    scope={'__name__':'__series06_replay__','__file__':str(a.source.resolve())}
    exec(compile(tree,str(a.source),'exec'),scope)
    if a.odd:
        result=scope['audit']();a.out.write_text(json.dumps(result,indent=2)+'\n')
    else:result=json.loads(a.out.read_text())
    assert result['passed']
    print('PASS: finite legacy assertions;',len(result['checks']),'grouped checks; OUT remaps',remapped)
if __name__=='__main__':main()
