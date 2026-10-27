"""Release-candidate regression guards, independent of the Lean proof count."""
from __future__ import annotations
import ast, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))


class EncodingPolicyTests(unittest.TestCase):
    def source_calls(self):
        for folder in ('python','scripts','tests'):
            for f in sorted((ROOT/folder).rglob('*.py')):
                for n in ast.walk(ast.parse(f.read_text(encoding='utf-8'))):
                    if isinstance(n,ast.Call):yield f,n
    def test_path_text_encodings_are_explicit(self):
        misses=[]
        for f,n in self.source_calls():
            if isinstance(n.func,ast.Attribute) and n.func.attr in ('read_text','write_text'):
                if 'encoding' not in {k.arg for k in n.keywords}:misses.append((str(f),n.lineno))
        self.assertEqual(misses,[])
    def test_text_subprocess_encodings_are_explicit(self):
        misses=[]
        for f,n in self.source_calls():
            if isinstance(n.func,ast.Attribute) and n.func.attr=='run':
                kws={k.arg:k.value for k in n.keywords}
                if isinstance(kws.get('text'),ast.Constant) and kws['text'].value is True and 'encoding' not in kws:
                    misses.append((str(f),n.lineno))
        self.assertEqual(misses,[])
    def test_python310_syntax_only(self):
        # Parsing is not a CPython 3.10 runtime-support claim.
        for folder in ('python','scripts'):
            for f in (ROOT/folder).rglob('*.py'):
                with self.subTest(file=f.name):ast.parse(f.read_text(encoding='utf-8'),feature_version=(3,10))
    def test_no_math_source_version_change(self):
        mods=json.loads((ROOT/'evidence/modules.json').read_text(encoding='utf-8'))
        for mod in mods:
            rel='lean/KomorebiRepair/'+mod.replace('.','/')+'.lean'
            with self.subTest(module=mod):
                self.assertEqual((ROOT/rel).read_bytes(), (ROOT/'provenance/v0.5.0'/rel).read_bytes())



class LocaleRegressionTests(unittest.TestCase):
    @unittest.skipUnless(os.name=='posix','POSIX C-locale reproduction, not Windows certification')
    def test_export_under_ascii_locale(self):
        with tempfile.TemporaryDirectory() as td:
            env=dict(os.environ,LC_ALL='C',LANG='C',PYTHONUTF8='0',PYTHONCOERCECLOCALE='0',PYTHONPATH=str(ROOT/'python'))
            cmd=[sys.executable,'-X','utf8=0','-m','repair_certificates','export',
                str(ROOT/'examples/worked_input.json'),str(ROOT/'examples/worked_certificate.json'),td]
            p=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            text=(Path(td)/'Certificate.lean').read_text(encoding='utf-8')
            self.assertIn('\u2227',text)
            self.assertIn('original_equations_checked',text)
    def test_wire_utf8_roundtrip(self):
        import repair_certificates as C
        p=C.read_json(ROOT/'examples/worked_input.json');c=C.read_json(ROOT/'examples/worked_certificate.json')
        text=C.emit_certificate(p,c,'Roundtrip','Input')
        self.assertEqual(text.encode('utf-8').decode('utf-8'),text)
        self.assertIn('\u2115',text)


class AcceptanceReceiptTests(unittest.TestCase):
    def test_missing_wheel_is_failure_not_success(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'receipt'
            p=subprocess.run([sys.executable,str(ROOT/'scripts/platform_acceptance.py'),
                '--wheel',str(Path(td)/'missing.whl'),'--output',str(out)],
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(p.returncode,1)
            data=json.loads((out/'platform_report.json').read_text(encoding='utf-8'))
            self.assertEqual(data['status'],'FAIL')
            self.assertFalse(data['network_access_requested'])
    def test_existing_acceptance_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            mark=Path(td)/'keep.txt';mark.write_text('unchanged',encoding='utf-8')
            p=subprocess.run([sys.executable,str(ROOT/'scripts/platform_acceptance.py'),'--output',td],
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(p.returncode,2)
            self.assertEqual(mark.read_text(encoding='utf-8'),'unchanged')
            self.assertFalse((Path(td)/'platform_report.json').exists())
    def test_version_agrees_with_source(self):
        import komorebi_repair as K
        self.assertEqual(K.__version__,(ROOT/'VERSION').read_text(encoding='utf-8').strip())
    def test_source_scripts_do_not_request_network(self):
        # The supported acceptance path fixes pip's no-index/no-deps options.
        src=(ROOT/'scripts/platform_acceptance.py').read_text(encoding='utf-8')
        self.assertIn("'--no-index'",src)
        self.assertIn("'--no-deps'",src)
        self.assertIn("PIP_NO_INDEX='1'",src)




@unittest.skipUnless(os.name=='posix','Pinned Linux-kit command-path test')
class RuntimePinTests(unittest.TestCase):
    def fake_kit_check(self, wrong_commit):
        import shlex
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);kit=base/'kit';kit.mkdir();repo=base/'not-the-pinned-mathlib';repo.mkdir()
            # A real local git commit, deliberately different from the required pin.
            for argv in (["git","init",str(repo)],
                         ["git","-C",str(repo),"-c","user.name=Release test","-c","user.email=test@example.invalid","commit","--allow-empty","-m","deliberately wrong fixture"]):
                q=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',timeout=20)
                self.assertEqual(q.returncode,0,q.stderr)
            commit='0'*40 if wrong_commit else '6a10ac8c22beadecabdbb0919c2b50214762f91d'
            script='#!/bin/sh\ncase "$1" in\nattach) mkdir -p "$2/.lake/packages"; ln -s '+shlex.quote(str(repo))+' "$2/.lake/packages/mathlib" ;;\nlean) echo "Lean (version 4.34.0-rc2, commit '+commit+')" ;;\n*) exit 91 ;;\nesac\n'
            (kit/'run.sh').write_text(script,encoding='utf-8')
            out=base/'evidence'
            q=subprocess.run([sys.executable,str(ROOT/'scripts/certify_one.py'),
                str(ROOT/'examples/worked_input.json'),'--kit',str(kit),'--output',str(out)],
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(q.returncode,1,q.stdout+q.stderr)
            rec=json.loads((out/'result.json').read_text(encoding='utf-8'))
            self.assertEqual(rec['status'],'UNRESOLVED_VERIFICATION_FAILURE')
            expected='Wrong Lean runtime pin' if wrong_commit else 'Wrong Mathlib pin'
            self.assertEqual(rec['error'],expected)
            self.assertFalse(any(x['label'].startswith('compile_') for x in rec['commands']))
    def test_matching_version_wrong_commit_rejected(self):self.fake_kit_check(True)
    def test_matching_lean_wrong_mathlib_rejected(self):self.fake_kit_check(False)


if __name__=='__main__':unittest.main()
