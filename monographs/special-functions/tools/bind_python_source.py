#!/usr/bin/env python3
"""Check/regenerate the closed-fragment Python-to-Lean source binding.

The parser, binder and interpretation of supported Python constructs are part
of the stated trust boundary. This tool is not a verified Python compiler.
Every non-documentation statement in each selected function is shape-checked;
all holed arithmetic, defaults and dictionary values are actually translated.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORT = Path(__file__).resolve().parent / "python_refinement"
HASHES = {
    "research/coupled_lab.py": "dff2a80db6f459e52dda45bc3399e0be45edf287df2efbeb1a56b57d38dfe20a",
    "research/family_lab.py": "7b546c1cd3159bb59634a3306c116719cd8d8d368c0046af90270c709b08cc8e",
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def selected_functions(text, names):
    module = ast.parse(text)
    result = {}
    for name in names:
        found = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(found) != 1:
            raise ValueError("Expected exactly one function: "+name)
        fn = copy.deepcopy(found[0])
        if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) and isinstance(fn.body[0].value.value, str):
            fn.body.pop(0)
        result[name] = fn
    return result


def mask_sources(coupled, family):
    functions = selected_functions(coupled, ("_index", "scales", "coupled_odd_derivatives", "disk_majorant", "certified_evaluation"))
    functions.update(selected_functions(family, ("ordinary_taylor_coefficients",)))
    holes = {}
    def hole(owner, key, label):
        if isinstance(owner, list):
            holes[label] = owner[key]
            owner[key] = ast.Constant(value="SOURCE_HOLE:"+label)
        else:
            holes[label] = getattr(owner, key)
            setattr(owner, key, ast.Constant(value="SOURCE_HOLE:"+label))
    # Exact positions are guarded by the complete masked AST comparison below.
    derivative = functions["coupled_odd_derivatives"]
    product = derivative.body[3].body[0].value
    for i, label in enumerate(("product", "q_power", "r_power")):
        hole(product.elt.elts, i, label)
    for position, label in ((1, "weight_u"), (2, "weight_v")):
        hole(derivative.body[3].body[position].value.args[0].args[0], "elt", label)
    majorant = functions["disk_majorant"]
    hole(majorant.body[9], "value", "seed")
    hole(majorant.body[10].body[0], "value", "update")
    hole(majorant.args.kw_defaults, 0, "steps_default")
    hole(majorant.args.kw_defaults, 1, "bits_default")
    evaluation = functions["certified_evaluation"]
    hole(evaluation.body[4].value, "orelse", "outer_default")
    hole(evaluation.body[7].value.elt.args[0], "elt", "partial_term")
    hole(evaluation.body[9], "value", "tail")
    hole(evaluation.body[10], "value", "dictionary")
    hole(evaluation.args.defaults, 0, "last_default")
    hole(functions["ordinary_taylor_coefficients"].body[0].value, "elt", "ordinary")
    patterns = {name: ast.dump(fn, annotate_fields=True, include_attributes=False)
                for name, fn in functions.items()}
    return patterns, holes


class Arithmetic:
    def __init__(self, rational=None, natural=None, arrays=None):
        self.rational = rational or {}
        self.natural = natural or {}
        self.arrays = arrays or {}

    def nat(self, node):
        if isinstance(node, ast.Name) and node.id in self.natural:
            return self.natural[node.id]
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value >= 0:
            return str(node.value)
        if isinstance(node, ast.BinOp):
            op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Pow: "^"}.get(type(node.op))
            if op:
                return "("+self.nat(node.left)+op+self.nat(node.right)+")"
        raise ValueError("Unsupported natural expression: "+ast.dump(node))

    def rat(self, node):
        if isinstance(node, ast.Name) and node.id in self.rational:
            return self.rational[node.id]
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return str(node.value)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                return "("+self.rat(node.left)+"^"+self.nat(node.right)+")"
            op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}.get(type(node.op))
            if op:
                return "("+self.rat(node.left)+op+self.rat(node.right)+")"
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            if node.value.id in self.arrays:
                return "("+self.arrays[node.value.id]+"["+self.nat(node.slice)+"]?).getD 0"
            if node.value.id == "partial" and isinstance(node.slice, ast.Constant) and type(node.slice.value) is int and node.slice.value in (0, 1):
                return ("u", "v")[node.slice.value]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            name = node.func.id
            if name == "comb" and len(node.args) == 2:
                return "(("+self.nat(node.args[0])+").choose "+self.nat(node.args[1])+" : ℚ)"
            if name == "factorial" and len(node.args) == 1:
                return "(("+self.nat(node.args[0])+").factorial : ℚ)"
            if name == "Q" and len(node.args) == 1:
                return self.rat(node.args[0])
            if name == "Q" and len(node.args) == 2:
                return "("+self.rat(node.args[0])+"/"+self.rat(node.args[1])+")"
            if name == "max" and len(node.args) == 2:
                return "(max "+self.rat(node.args[0])+" "+self.rat(node.args[1])+")"
        raise ValueError("Unsupported rational expression: "+ast.dump(node))

    def value(self, node):
        if isinstance(node, ast.Name) and node.id == "last":
            return ".integer (N : ℤ)"
        if isinstance(node, ast.Tuple) and len(node.elts) == 2:
            return ".tuple ("+self.value(node.elts[0])+") ("+self.value(node.elts[1])+")"
        return ".rational "+self.rat(node)


def declarations(holes):
    product = Arithmetic(natural={"n": "n", "i": "i.val"}, arrays={"u": "uv.1", "v": "uv.2"})
    weight = Arithmetic(rational={"c": "t.1", "q": "q", "r": "r"}, natural={"i": "t.2.1", "j": "t.2.2"})
    other_weight = Arithmetic(rational={"c": "t.1", "a": "q", "b": "r"}, natural={"i": "t.2.1", "j": "t.2.2"})
    weight_text = weight.rat(holes["weight_u"])
    if weight_text != other_weight.rat(holes["weight_v"]):
        raise ValueError("The two rows do not use the same weighted-products template")
    ordinary = Arithmetic(rational={"a": "a"}, natural={"n": "n"})
    partial = Arithmetic(rational={"c": "c", "x": "x"}, natural={"n": "n"})
    bound = Arithmetic(rational={"x": "x", "bound": "bound"})
    outer = Arithmetic(rational={"x": "x"})
    tail = Arithmetic(rational={"majorant": "B", "x": "x", "s": "s"}, natural={"last": "N"})
    dictionary = Arithmetic(rational={"x": "x", "s": "s", "majorant": "B", "tail": "t"})
    d = holes["dictionary"]
    if not isinstance(d, ast.Dict) or any(not isinstance(k, ast.Constant) or type(k.value) is not str for k in d.keys):
        raise ValueError("Return must be a literal dictionary with string keys")
    fields = ["("+json.dumps(k.value)+", "+dictionary.value(v)+")" for k, v in zip(d.keys, d.values, strict=True)]
    if len(set(k.value for k in d.keys)) != len(d.keys):
        raise ValueError("Duplicate dictionary key")
    constants = {}
    for label in ("steps_default", "bits_default", "last_default"):
        n = holes[label]
        if not isinstance(n, ast.Constant) or type(n.value) is not int or n.value < 0:
            raise ValueError("Natural resource/index default required")
        constants[label] = str(n.value)
    return {
        "products": "def products (n : ℕ) (uv : Arrays) : List Product :=\n  List.ofFn (fun i : Fin n =>\n    ("+product.rat(holes["product"])+", "+product.nat(holes["q_power"])+", "+product.nat(holes["r_power"])+"))\n\n",
        "weighted": "def weighted (q r : ℚ) (terms : List Product) : ℚ :=\n  (terms.map (fun t => "+weight_text+")).sum\n\n",
        "ordinary": "def ordinary (row : List ℚ) : List ℚ :=\n  row.mapIdx (fun n a => "+ordinary.rat(holes["ordinary"])+")\n\n",
        "partialSum": "def partialSum (row : List ℚ) (x : ℚ) : ℚ :=\n  ((ordinary row).mapIdx (fun n c => "+partial.rat(holes["partial_term"])+")).sum\n\n",
        "seed": "def seed (x : ℚ) : ℚ := "+bound.rat(holes["seed"])+"\n",
        "update": "def update (x bound : ℚ) : ℚ := "+bound.rat(holes["update"])+"\n\n",
        "defaultSteps": "def defaultSteps : ℕ := "+constants["steps_default"]+"\n",
        "defaultBits": "def defaultBits : ℕ := "+constants["bits_default"]+"\n",
        "defaultLast": "def defaultLast : ℕ := "+constants["last_default"]+"\n",
        "outerRadius": "def outerRadius (x : ℚ) (s : Option ℚ) : ℚ := s.getD "+outer.rat(holes["outer_default"])+"\n",
        "tail": "def tail (B x s : ℚ) (N : ℕ) : ℚ := "+tail.rat(holes["tail"])+"\n\n",
        "resultDictionary": "def resultDictionary (x : ℚ) (N : ℕ) (s B : ℚ) (u v : ℚ) : Dictionary :=\n  let t := tail B x s N\n  ["+",\n   ".join(fields)+"]\n\n",
    }


def generate(coupled, family, require_hash=True):
    if require_hash:
        for name, value in (("research/coupled_lab.py", coupled), ("research/family_lab.py", family)):
            if sha_bytes(value.encode("utf-8")) != HASHES[name]:
                raise ValueError("Pinned source bytes changed: "+name)
    actual, holes = mask_sources(coupled, family)
    expected = json.loads((SUPPORT/"source_patterns.json").read_text(encoding="utf-8"))
    if actual != expected:
        changed = sorted(k for k in actual if actual.get(k) != expected.get(k))
        raise ValueError("Unsupported control/data-flow change: "+", ".join(changed))
    template = (SUPPORT/"CoupledPythonSource.template").read_text(encoding="utf-8")
    for name, declaration in declarations(holes).items():
        token = "{{"+name+"}}"
        if template.count(token) != 1:
            raise ValueError("Template must contain exactly one "+token)
        template = template.replace(token, declaration)
    if "{{" in template:
        raise ValueError("Unexpanded source template hole")
    return template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the bound Lean translation")
    parser.add_argument("--output", type=Path, help="Fresh binding receipt path")
    args = parser.parse_args()
    coupled = (ROOT/"research/coupled_lab.py").read_bytes().decode("utf-8")
    family = (ROOT/"research/family_lab.py").read_bytes().decode("utf-8")
    generated = generate(coupled, family).encode("utf-8")
    target = ROOT/"lean/CoupledPythonSource.lean"
    if args.write:
        target.write_bytes(generated)
    if target.read_bytes() != generated:
        raise ValueError("Source-generated Lean translation differs from the checked artifact")
    report = {"status": "passed", "source_hashes": HASHES,
              "translation_sha256": sha_bytes(generated),
              "binder_sha256": sha_bytes(Path(__file__).read_bytes()),
              "patterns_sha256": sha_bytes((SUPPORT/"source_patterns.json").read_bytes()),
              "template_sha256": sha_bytes((SUPPORT/"CoupledPythonSource.template").read_bytes()),
              "trust_boundary": "Python AST parser and closed-fragment binder/template; exact rational/integer/stdlib and container primitives. No verified compiler or CPython implementation claim."}
    if args.output:
        if args.output.exists():
            parser.error("--output must be a new path")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
