from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1]
mods=json.loads((root/'evidence/modules.json').read_text(encoding="utf-8"))
base=['Basic','Minimal','Menu','Conservation','Transport','ConstrainedMinimal','Search','Arithmetic','Nonlinear','Examples']
general=['RationalCertificates','ConstructiveMatrix','Wire','RationalMenuCover','BranchCertificate']
records=[]
for module in mods:
    f=root/'lean/KomorebiRepair'/(module.replace('.','/')+'.lean');namespace=[]
    for i,line in enumerate(f.read_text(encoding="utf-8").splitlines(),1):
        match=re.match(r'^namespace\s+(\S+)',line)
        if match:namespace.append(match[1])
        match=re.match(r'^end(?:\s+\S+)?\s*$',line)
        if match and namespace:namespace.pop()
        match=re.match(r'^(?:@\[[^\]]*\]\s*)?theorem\s+(\w+)',line)
        if match:records.append({'name':'.'.join(namespace+[match[1]]),'file':str(f.relative_to(root)),
          'line':i,'module':module,'layer':'baseline' if module in base else ('general' if module in general else 'concrete')})
(root/'docs/theorem_registry.json').write_text(json.dumps({'theorems':records},indent=2), encoding="utf-8")
(root/'lean/AxiomAudit.lean').write_text('import KomorebiRepair\nset_option pp.fullNames true\n'+''.join('#print axioms '+r['name']+'\n' for r in records), encoding="utf-8")
print({'total':len(records),'baseline':sum(x['layer']=='baseline' for x in records),'general_new':sum(x['layer']=='general' for x in records),'concrete_new':sum(x['layer']=='concrete' for x in records)})
