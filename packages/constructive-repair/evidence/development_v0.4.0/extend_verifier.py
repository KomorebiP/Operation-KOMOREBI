from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/verify_release.py';s=p.read_text()
s=s.replace("'komorebi.repair.verification.v0.3.0'","'komorebi.repair.verification.v0.4.0'")
s=s.replace("[p/'KomorebiRepair.lean',p/'AxiomAudit.lean',p/'InputEcho.lean']", "[p/'KomorebiRepair.lean',p/'AxiomAudit.lean',p/'InputEcho.lean',p/'MenuInputEcho.lean']")
s=s.replace("check('baseline_ten_modules_unchanged',unchanged)", """check('baseline_ten_modules_unchanged',unchanged)
        with zipfile.ZipFile(ROOT/'inherited/Komorebi_Constructive_Repair_v0.3.0.zip') as z:
            oldmods=json.loads(z.read('Komorebi_Constructive_Repair_v0.3.0/evidence/modules.json'))
            old_same=all((p/'KomorebiRepair'/(x.replace('.','/')+'.lean')).read_bytes()==
                z.read('Komorebi_Constructive_Repair_v0.3.0/lean/KomorebiRepair/'+x.replace('.','/')+'.lean') for x in oldmods)
        check('all_v0_3_modules_unchanged',old_same,len(oldmods))""")
marker="        result.update(status='PASS',proof_modules=len(mods)"
assert marker in s
insert="""        # Fresh v0.4.0 menu-source binding, scoped rejection and exact tests.
        menu_controls=json.loads((ROOT/'evidence/menu_rejection_index.json').read_text())
        for c in menu_controls:
            rc,txt=run('menu_negative_'+c['name'],lake('env','lean','-j1','-DwarningAsError=true','menu_negative_controls/'+c['name']+'.lean'))
            check('menu_rejection_'+c['name'],rc is not None and rc>0 and 'Type mismatch' in txt and '= false' in txt and '= true' in txt and 'failed to synthesize' not in txt and 'does not exist' not in txt)
        rc,txt=run('menu_input_echo',lake('env','lean','MenuInputEcho.lean'))
        check('menu_input_echo_executed',rc==0)
        mrows=[json.loads(x) for x in txt.splitlines() if x.startswith('{')]
        mind=json.loads((ROOT/'evidence/menu_export_index.json').read_text())
        check('menu_echo_count',len(mrows)==len(mind))
        import rational_menu as M
        for x,echo in zip(mind,mrows):
            orig=read_json(ROOT/x['input']);c=read_json(ROOT/x['certificate'])
            check('menu_binding_'+x['namespace'],M.check_echo(orig,echo) and digest(orig)==x['problem_sha256'])
            M.check_certificate(orig,c)
        check('all_shipped_menu_certificates',True,len(mind))
        rc,txt=run('menu_python_unittest',[sys.executable,'-m','unittest','-v','test_rational_menu'],cwd=ROOT/'python')
        check('menu_python_unittest',rc==0 and 'Ran 50 tests' in txt and 'OK' in txt)
        for ln in (ROOT/'evidence/menu_case_records.jsonl').read_text().splitlines():
            x=json.loads(ln);M.check_certificate(x['problem'],x['certificate'])
        check('menu_all_recorded_identities_rechecked',True,120)
        result.update(menu_exported_problems=len(mind),menu_paired_rejections=len(menu_controls),
            v0_4_new_general_theorems=sum(r['module']=='RationalMenuCover' for r in registry),
            menu_optimal_exports=sum(x['kind']=='optimal_menu' for x in mind),
            menu_no_repair_exports=sum(x['kind']=='no_admissible_repair' for x in mind))
"""
s=s.replace(marker,insert+marker)
p.write_text(s)
