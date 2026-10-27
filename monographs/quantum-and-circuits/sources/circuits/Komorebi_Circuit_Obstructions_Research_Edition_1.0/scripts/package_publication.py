"""Stage and hash the complete source-preserving publication set."""
from pathlib import Path
import shutil,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
NAME='Komorebi_Circuit_Obstructions_Research_Edition_1.0'
DEST=ROOT/'release'/NAME

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copytree(source,dest):
    shutil.copytree(source,dest,dirs_exist_ok=True,
      ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git'))

def main():
    if DEST.exists():shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for name in ['source','historical_companion','manuscripts','figures','scripts']:
        copytree(ROOT/name,DEST/name)
    (DEST/'output').mkdir()
    for name in ['Komorebi_Circuit_Obstructions_Main_Paper.pdf',
                 'Komorebi_Circuit_Obstructions_Visual_Guide.pdf',
                 'Komorebi_Circuit_Obstructions_Lean_Guide.pdf']:
        shutil.copy2(ROOT/'output'/name,DEST/'output'/name)
    for name in ['README.md','EDITION_NOTES.md']:
        shutil.copy2(ROOT/name,DEST/name)
    originals=DEST/'originals';originals.mkdir()
    original_source=ROOT/'downloads'
    if not original_source.exists():original_source=ROOT/'originals'
    for p in sorted(original_source.iterdir()):
        if p.is_file():shutil.copy2(p,originals/p.name)
    reviews=DEST/'reviews';reviews.mkdir()
    for p in sorted((ROOT/'reviews').glob('*')):
        if p.is_file():shutil.copy2(p,reviews/p.name)
        elif p.name.startswith('render_'):
            (reviews/p.name).mkdir()
            for q in p.glob('contact-*.png'):shutil.copy2(q,reviews/p.name/q.name)
    build=DEST/'build';build.mkdir()
    for name in ['main','visual','lean']:
        (build/name).mkdir()
        for q in (ROOT/'build'/name).glob('*.log'):
            shutil.copy2(q,build/name/q.name)
    files=sorted(p for p in DEST.rglob('*') if p.is_file())
    manifest={'schema':'komorebi.circuit.publication-manifest.v1',
              'edition':'1.0','baseline':'v1.2.0','date':'2026-10-07',
              'files':[{'path':p.relative_to(DEST).as_posix(),'bytes':p.stat().st_size,
                        'sha256':sha(p)} for p in files],
              'excludes':['PUBLICATION_MANIFEST.json','PUBLICATION_MANIFEST.sha256'],
              'meaning':'Content consistency, not author authentication or a proof certificate'}
    mp=DEST/'PUBLICATION_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2))
    (DEST/'PUBLICATION_MANIFEST.sha256').write_text(sha(mp)+'  PUBLICATION_MANIFEST.json\n')
    z=ROOT/'output/Komorebi_Circuit_Obstructions_Complete_Publication_Set_2026-10-07.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as f:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():f.write(p,p.relative_to(DEST.parent))
    with zipfile.ZipFile(z) as f:
        if f.testzip() is not None:raise ValueError('ZIP CRC failure')
        if len(f.namelist())!=len(files)+2:raise ValueError('ZIP member count mismatch')
        for entry in manifest['files']:
            b=f.read(NAME+'/'+entry['path'])
            if len(b)!=entry['bytes'] or hashlib.sha256(b).hexdigest()!=entry['sha256']:
                raise ValueError('Manifest mismatch: '+entry['path'])
    # No self-hash is placed inside the ZIP.
    (z.with_suffix('.zip.sha256')).write_text(sha(z)+'  '+z.name+'\n')
    print(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'sha256':sha(z),
                      'manifested_files':len(files),'zip_members':len(files)+2,
                      'verified_members':len(files),'crc':'PASS'},indent=2))

if __name__=='__main__':main()
