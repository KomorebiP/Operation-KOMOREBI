#!/usr/bin/env python3
"""Bind the twelve selected editions to their publication components."""
from pathlib import Path
import hashlib, json, shutil
import fitz
from rebrand_components import rebrand_component
from book_component_adapter import adapt_component, normalize_preserved_palette
from book_layout import make_layout
from atlas_book_routes import normalize_atlas_routes

ROOT = Path(__file__).resolve().parent

DESCRIPTIONS = {
 'I': 'Seeds, operators and projectors provide the linear language of the series. Exact packet coordinates make the generated objects and the maps between them visible.',
 'II': 'Refinement towers compare packet descriptions across levels. Weighted transfers and integral separation show which structures survive a change of resolution.',
 'III': 'Typed operations extend the linear language to nonlinear coordinates, analytic packet jets and obstruction theory. The analytic supplement develops the continuous packet-jet claims.',
 'IV': 'A cyclic analytic family connects coefficient selection, differential transport, reciprocal polynomials and spectral zero data.',
 'V': 'Signal models move through filters, packet trees and reconstruction maps. Exact coordinates and singular packets distinguish representation from approximation and recovery.',
 'VI': 'Evolution, probability and conditioning share a transfer language. Eliminating hidden states produces memory terms whose hypotheses remain part of the model.',
 'VII': 'Quantum seeds generate spaces through an operator grammar. Symmetry, circuits, geometric transport and quantum channels lead to finite effective dynamics and bounded refinement questions.',
 'VIII': 'Structured packet representations remove work before execution. Exact compilation connects algebraic structure, recompression, precision and stated hardware observations.',
 'IX': 'Euler congruences are developed through completion, factorial strengthening and dyadic geometry. The accompanying guides connect exact statements, bounded examples and formal coverage.',
 'X': 'Residual seeds, deformation forests and transport categories organize conditional system completion. Supplied arithmetic and carrier data remain explicit inputs.',
 'XI': 'Tame and wild packet geometry organizes the local arithmetic constructions. The research companions retain both restricted progress and the unresolved obligations of Conjecture 66.',
 'XII': 'Patching support and compatible Hecke packets complete a conditional arithmetic argument. Each application must supply the geometric, automorphic and representation-theoretic inputs that the theorem uses.'
}
BOUNDARIES = {
 'I': 'The correspondence concerns the stated proof-level constructions. Noncomputable existence results do not provide executable solvers.',
 'II': 'Canonical values are defined for admissible data. A general existence theorem for admissible contours remains a separate question.',
 'III': 'Expanded ordinary proofs and the bounded Lean core have different coverage. The packet Taylor estimates, counting arguments and later extensions retain their stated ordinary-proof status. Arbitrary differentiability is not asserted.',
 'IV': 'The analytic statements retain their branch choices, multiplicities and integer-order hypotheses. Universal zero simplicity and a zeta functional equation remain outside these results.',
 'V': 'Separated-jump results require the stated model, gap and grid assumptions. Stable edge-packet recovery and the broader approximation class remain open.',
 'VI': 'Finite-state, common-gap and fixed-partition restrictions remain explicit. Completion, uniform refinement control and stable infinite latent-packet closure remain open. Floating residuals are not interval certificates.',
 'VII': 'The finite formal contract does not certify the full continuum physics program. Anomaly-free refinement, uniform Feshbach control, Lorentzian reconstruction and the proposed gravitational limits remain open.',
 'VIII': 'Small-core optimality uses supplied ordered thin-SVD equations and actual compact ranges. General numerical SVD verification, unrestricted discovery and CUDA-kernel verification require further results.',
 'IX': 'The arithmetic, dyadic and lifting results have distinct hypotheses. General Euler-tail simplicity and the broader native and polyphase extensions remain open.',
 'X': 'The target family and recovered carrier are independent existential outputs. Identifying them and proving nonzero occupancy require additional premises. Source families, carrier presentations and local comparisons remain supplied.',
 'XI': 'Conjecture 66 remains open. Its unresolved requirements concern general arithmetic realization, H5 for the same candidate, corrected full-character occurrence and actual native data under the stronger contract.',
 'XII': 'Actual residual and deformation data, applicable patching and full support, a compatible same-field Hecke point, classicality and an attached representation are required. Comparisons of compatible families assume those families already exist. Chapter XI\'s Conjecture 66 is not assumed proved.'
}
ROLES = {'traditional':'Mathematical text','machine_native':'Computational formulation','visual':'Visual studies',
         'lean':'Formal companion','analytic_supplement':'Analytic supplement','release_record':'Release record',
         'verification_closeout':'Verification closeout','research_progress':'Research companion',
         'research_atlas':'Research atlas','conjecture_progress':'Research companion','conjecture_atlas':'Research atlas'}

def digest(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    builds = json.loads((ROOT/'component_builds.json').read_text())
    if isinstance(builds,dict):builds=builds['components']
    by_name={x['baseline_filename']:x for x in builds}
    metadata=json.loads((ROOT/'editorial/book_parts_metadata.json').read_text())
    book=ROOT/'book';book.mkdir(exist_ok=True)
    frozen=ROOT/'frozen_readers';frozen.mkdir(exist_ok=True)
    compiled=ROOT/'compiled';compiled.mkdir(exist_ok=True)
    cursor=10;parts=[];branding=[];adaptations={}
    for part in metadata['parts']:
        roman=part['paper'];targetpart=compiled/roman;targetpart.mkdir(exist_ok=True)
        row={'paper':roman,'title':part['title'],'subtitle':part['subtitle'],
             'description':DESCRIPTIONS[roman],'boundary':BOUNDARIES[roman],
             'divider_index':cursor,'folio':cursor-11,'components':[]}
        cursor+=1
        for src in part['components']:
            filename=src['filename'];b=by_name.pop(filename)
            original=Path(src['source_path']);original_target=frozen/filename
            if not original.exists(): original=original_target
            assert digest(original)==src['source_pdf_sha256']
            if original.resolve()!=original_target.resolve(): shutil.copy2(original,original_target)
            p=Path(b['output_pdf']);p=p if p.is_absolute() else ROOT/p
            dest=targetpart/filename
            if p.resolve()!=dest.resolve():shutil.copy2(p,dest)
            treatment=rebrand_component(dest)
            cid=roman+'_'+src['role']
            adaptations[cid]=adapt_component(dest,cid,preserved=b['build_kind']=='preserved_pdf')
            adaptations[cid]['palette']=normalize_preserved_palette(dest,cid)
            branding.append({'component':roman+'_'+src['role'],'path':str(dest.relative_to(ROOT)),**treatment})
            with fitz.open(dest) as d:pages=len(d)
            row['components'].append({'id':roman+'_'+src['role'],
                'paper':roman,'role':src['role'],'short_role':ROLES.get(src['role'],src['navigation_title']),
                'title':ROLES.get(src['role'],src['navigation_title']),'deck':src.get('deck',''),
                'path':str(dest.relative_to(ROOT)),'sha256':digest(dest),
                'baseline_path':str(original_target.relative_to(ROOT)),
                'baseline_sha256':src['source_pdf_sha256'],
                'baseline_pages':src['source_page_count'],'pages':pages,
                'index_start':cursor,'page_start':cursor-11,'page_end':cursor-12+pages,
                'build_kind':b['build_kind'],'display_branding':treatment['status'],'aliases':b.get('aliases',[]),
                'numeric_remotes_edition':b.get('numeric_remotes_edition','current' if b.get('remotes_rebound') else 'frozen'),
                'preserved_page_spans':b.get('preserved_page_spans',[]),
                'warnings':b.get('warnings',[])})
            cursor+=pages
        parts.append(row)
    if by_name:raise ValueError('Unexpected component results: '+str(list(by_name)))
    (book/'display_adaptations.json').write_text(json.dumps({'components':adaptations},indent=2,ensure_ascii=False)+'\n')
    (book/'adapted_parts.json').write_text(json.dumps({'parts':parts},indent=2,ensure_ascii=False)+'\n')
    record=make_layout(parts,adaptations)
    normalize_atlas_routes(record)
    (book/'build_spec.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    (book/'branding_treatment.json').write_text(json.dumps({'components':branding},indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'parts':len(parts),'components':sum(len(x['components']) for x in parts),
                      'pages':record['expected_total_pages'],'build_kinds':{k:sum(c['build_kind']==k for p in parts for c in p['components'])
                      for k in ['source_retypeset','preserved_pdf','mixed']}},indent=2))

if __name__=='__main__':main()
