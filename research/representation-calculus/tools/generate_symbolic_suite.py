"""Generate a symbolic Lean instance for each frozen v0.2 matrix certificate."""
from pathlib import Path
from hashlib import sha256
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from export_symbolic_lean import emit, canonical

def main():
    items=[]
    for src in sorted((ROOT/'certificates').glob('*.source.json')):
        tag=src.name.removesuffix('.source.json')
        cp=src.with_name(tag+'.certificate.json')
        spec=json.loads(src.read_text());cert=json.loads(cp.read_text())
        ns='Large' if tag=='scrambled_128bit' else 'Case'+''.join(part.capitalize() for part in tag.split('_'))
        module='GeneratedLarge' if tag=='scrambled_128bit' else 'Symbolic_'+tag
        output=ROOT/'formalization'/(module+'.lean')
        text=emit(spec,cert,ns);output.write_text(text)
        items.append({'tag':tag,'module':module,'namespace':f'Komorebi.Representation.Symbolic.{ns}',
            'source':str(src.relative_to(ROOT)),'certificate':str(cp.relative_to(ROOT)),
            'source_sha256':sha256(src.read_bytes()).hexdigest(),'certificate_sha256':sha256(cp.read_bytes()).hexdigest(),
            'canonical_source_sha256':sha256(canonical(spec)).hexdigest(),
            'generated':str(output.relative_to(ROOT)),'generated_sha256':sha256(text.encode()).hexdigest(),
            'modulus':spec['p']**spec['r'],'source_dimension':spec['dimension'],'target_coordinates':cert['dimension'],
            'raw_test_count':len(cert['raw_tests']),'state_enumeration_used':False})
    (ROOT/'evidence/SYMBOLIC_EXPORTS.json').write_text(json.dumps(items,indent=2)+'\n')
    print(json.dumps({'exported':len(items),'total_source_bytes':sum((ROOT/i['generated']).stat().st_size for i in items),'state_enumeration_used':False},indent=2))
if __name__=='__main__':main()
