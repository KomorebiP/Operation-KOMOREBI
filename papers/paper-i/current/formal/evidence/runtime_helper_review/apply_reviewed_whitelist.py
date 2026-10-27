#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,re,shutil
root=Path(__file__).resolve().parents[3];review=Path(__file__).resolve().parent
source=root/'release_package/Komorebi_Paper_I_Release_2026-10-15/formal/current'
audits=[root/'release_work/runtime/release_audit',root/'release_package/Komorebi_Paper_I_Release_2026-10-15/formal/scripts/release_audit']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((review/'inventory.json').read_text());parents=json.loads((review/'parent_bodies.json').read_text());sep=json.loads((review/'dependency_separation.json').read_text())
assert inv['exit']==parents['exit']==sep['exit']==0
assert 'DIAGNOSTIC_COMPLETE OWNED 3513 PARTIAL 13 UNSAFE 0 LOGICAL_HELPER_REFERENCES 0' in (review/'dependency_separation.log').read_text()
assert len(inv['helpers'])==13 and len(parents['helpers'])==6
pmap={x['name']:x for x in parents['helpers']}
reasons={
 'Komorebi.PaperIRelease.CategoryExport.evaluate':'Structural recursion on Expression. Recursive calls use direct expression subterms; logical definition uses Expression.brecOn.',
 'Komorebi.PaperIRelease.CategoryExport.evaluateTransported':'Structural recursion on Expression. Recursive calls use direct expression subterms; logical definition uses Expression.brecOn.',
 'Komorebi.PaperIRelease.operatorWord':'Structural recursion on List; recursive call uses the tail. Logical definition uses List.brecOn.',
 'Komorebi.PaperIRelease.StrictPath':'Structural recursion on natural path length; recursive call replaces n+1 by n. Logical definition uses Nat.brecOn, including when the return value is Prop.',
 'Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap':'Structural source recursion on TypedPath; recursive call uses direct subpath. Logical auxiliary uses WellFounded.Nat.fix with sizeOf the typed path.',
 'Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word':'Structural source recursion on TypedPath; recursive call uses direct subpath. Logical auxiliary uses WellFounded.Nat.fix with sizeOf the typed path.'}
helpers=[]
for h in sorted(inv['helpers'],key=lambda x:x['name']):
 assert h['partial'] and not h['unsafe'] and h['kind']=='definition'
 assert set(h['axioms'])<={'propext','Classical.choice','Quot.sound'}
 p=h['name'].removesuffix('._unsafe_rec');row={**h,'parent':p,'classification':'compiler-generated partial runtime implementation; excluded from logical replay'}
 if p in pmap:
  pr=pmap[p];assert not pr['partial'] and not pr['unsafe'] and pr['runtime_helper_references']==[]
  row.update(review_origin='new release helper reviewed against frozen source and compiled logical parent',termination_review=reasons[p],logical_parent=pr)
 else:row.update(review_origin='inherited Block08 exact-name inventory; source unchanged',termination_review='Existing accepted helper classification retained; final diagnostic reconfirms flags, axioms and logical separation.')
 helpers.append(row)
evidencefiles=['Inventory.lean','inventory.log','inventory.json','ParentBodies.lean','parent_bodies.log','parent_bodies.json','DependencySeparation.lean','dependency_separation.log','dependency_separation.json']
receipt={'schema':'paper-i-reviewed-runtime-helpers/1','status':'REVIEWED','scope':'Exact-name runtime classification only. No new axiom, proof declaration, or production-source change. The final strict audit and kernel replay must still pass.','helper_count':13,'inherited_helper_count':7,'new_helper_count':6,'diagnostic_owned_count':3513,'diagnostic_logical_count':3500,'diagnostic_unsafe_count':0,'diagnostic_logical_references_to_helpers':0,'helpers':helpers,'source_modules':[{'module':m,'source':str(Path(*m.split('.')).with_suffix('.lean')),'sha256':sha((source/Path(*m.split('.'))).with_suffix('.lean'))} for m in sorted({x['module'] for x in helpers})],'evidence':[{'path':'helper_review_evidence/'+f,'sha256':sha(review/f)} for f in evidencefiles],'independent_review':'The independent package auditor inspected all six source parents and the logical-dependency separation diagnostic and endorsed the exact six additions; original seven retained.','limits':['Generated runtime implementations are not kernel proof terms and remain excluded from logical replay.','Logical parents and all logical declarations remain subject to exact-name wholeclosure kernel replay.','Every unlisted partial declaration and every unsafe declaration must still be rejected.']}
for audit in audits:
 before=review/('before_staged' if '/release_package/' in str(audit) else 'before_runtime');before.mkdir(exist_ok=True)
 for name in ['OwnedAudit.template.lean','verify_release.py']:shutil.copy2(audit/name,before/name)
 dest=audit/'helper_review_evidence';dest.mkdir(exist_ok=True)
 for f in evidencefiles:shutil.copy2(review/f,dest/f)
 (audit/'reviewed_runtime_helpers.json').write_text(json.dumps(receipt,indent=2)+'\n')
 p=audit/'OwnedAudit.template.lean';s=p.read_text();s=re.sub(r'let generatedRuntime : Array Name := #\[[^\n]*\]','let generatedRuntime : Array Name := #['+', '.join('`'+h['name'] for h in helpers)+']',s);p.write_text(s)
 p=audit/'verify_release.py';s=p.read_text();s=s.replace('The seven inventoried generated partial runtime helpers are excluded from logical proof replay.','The exact reviewed generated partial runtime helpers are inventoried separately and excluded from logical proof replay; the actual count is recorded below.')
 s=s.replace("        binding=json.loads((audit/'runtime_bindings.json').read_text())", """        helper_review=json.loads((audit/'reviewed_runtime_helpers.json').read_text())
        assert helper_review['status']=='REVIEWED'
        reviewed_helpers=helper_review['helpers'];reviewed_names={h['name'] for h in reviewed_helpers}
        assert len(reviewed_names)==len(reviewed_helpers)==helper_review['helper_count']
        template_text=(audit/'OwnedAudit.template.lean').read_text()
        whitelist_text=re.search(r'let generatedRuntime : Array Name := (#\\[[^\\n]*\\])',template_text).group(1)
        assert set(re.findall(r'`([\\w.]+)',whitelist_text))==reviewed_names
        manifest_modules={r['module'] for r in rows}
        for item in helper_review['source_modules']:
            if item['module'] in manifest_modules:assert sha(root/item['source'])==item['sha256'],item['module']
        for item in helper_review['evidence']:assert sha(audit/item['path'])==item['sha256'],item['path']
        report['reviewed_runtime_helpers_receipt_sha256']=sha(audit/'reviewed_runtime_helpers.json')
        report['reviewed_runtime_helper_count']=len(reviewed_names)
        binding=json.loads((audit/'runtime_bindings.json').read_text())""")
 s=s.replace("'module_count':len(reuse)}", "'module_count':len(reuse),'scope':b.get('scope'),'component_schema':b.get('schema'),'parent_audit':b.get('parent_audit')}\n            assert len(reuse)==b.get('fresh_production_module_count',len(reuse))")
 s=s.replace("        (out/'owned_declarations.json').write_text", """        expected_runtime_names={h['name'] for h in reviewed_helpers if h['module'] in mods}
        actual_runtime_names={r['name'] for r in owned if r['runtime_only']}
        assert actual_runtime_names==expected_runtime_names,{'unexpected_runtime':sorted(actual_runtime_names-expected_runtime_names),'missing_reviewed_runtime':sorted(expected_runtime_names-actual_runtime_names)}
        report['runtime_exact_reviewed_name_match']=True
        (out/'owned_declarations.json').write_text""")
 p.write_text(s)
 (audit/'reviewed_runtime_helpers.json').write_text(json.dumps(receipt,indent=2)+'\n')
(review/'reviewed_runtime_helpers.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Whitelist receipt SHA256',sha(review/'reviewed_runtime_helpers.json'))
print('Updated audit-only files in both runtime and staged release. No production source changes.')
