#!/usr/bin/env python3
"""Build only the executable data-certificate backend from trusted Lean sources."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
for source in ['AVOC/CertificateLogic.lean','AVOC/ArtifactBinding.lean','AVOC/CertificateCodec.lean','AVOC/BindingCodec.lean','tools/CertificateMain.lean']:
    subprocess.run([sys.executable,str(root/'tools/lean_one.py'),source,'--log','results/backend_build/'+Path(source).stem+'.log'],cwd=root,check=True)
print('Data-certificate backend built. No arbitrary candidate Lean source is executed.')
