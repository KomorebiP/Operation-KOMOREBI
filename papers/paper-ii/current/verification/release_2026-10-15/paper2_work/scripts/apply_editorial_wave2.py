from pathlib import Path
import hashlib,json,difflib
R=Path('release_package/Komorebi_Paper_II_Release_2026-10-15');A=Path('paper2_work/audit');B=Path('paper2_work/editorial_before_wave2');B.mkdir(exist_ok=True)
changes=[];original={};working={}
def edit(rel,before,after,ref):
 p=R/rel
 if rel not in original: original[rel]=p.read_text();working[rel]=original[rel]
 assert working[rel].count(before)==1,(ref,working[rel].count(before))
 working[rel]=working[rel].replace(before,after)
 changes.append(dict(source=rel,audit_finding=ref,before=before,after=after))
p='editable/traditional/chapters/01_orientation.tex'
edit(p,'The exact answer is controlled by the finite module','The exact answer is controlled by the finite length module','A-CLARIFY-FINITE')
p='editable/traditional/chapters/04_arithmetic.tex'
edit(p,r'For a finite torsion $\OO$ module $G$, write',r'For a finitely generated torsion $\OO$ module $G$, write','A-CLARIFY-FINITE')
edit(p,r'The module $G_{\Lambda,\Pcal}$ is finite because $\Lambda_{\mathrm{split}}$ and $\Lambda$ are full lattices in the same vector space.',r'The gluing module $G_{\Lambda,\Pcal}$ is a finitely generated torsion $\OO$ module, hence has finite length, because $\Lambda_{\mathrm{split}}$ and $\Lambda$ are full lattices in the same vector space. To see that the split lattice is full, clear denominators of bases of the rational summands. Each $\Lambda\cap V_\alpha$ then spans $V_\alpha$, so their direct sum spans $V$.','A-CLARIFY-FINITE; A-CLARIFY-INCLUSION')
edit(p,'The length and exponent of a finite module are read directly from its Smith decomposition.','The length and exponent of a finitely generated torsion module are read directly from its Smith decomposition.','A-CLARIFY-FINITE')
edit(p,r's_{2,\Z^2}(E_+)=s_{2,\Z^2}(E_-)=1.',r's_{2,\Z_2^2}(E_+)=s_{2,\Z_2^2}(E_-)=1.','A-CLARIFY-LOCAL-LATTICE')
edit(p,'Let the residue field have size $q$, fix $L\\geq1$, and consider','Assume the residue field is finite of cardinality $q$, fix $L\\geq1$, and consider','A-CLARIFY-Q')
logs=[]
for rel,t in working.items():
 p=R/rel;back=B/rel;back.parent.mkdir(parents=True,exist_ok=True);assert not back.exists();back.write_text(original[rel]);p.write_text(t)
 logs.append({'path':rel,'before_sha256':hashlib.sha256(original[rel].encode()).hexdigest(),'after_sha256':hashlib.sha256(t.encode()).hexdigest()})
(A/'editorial_wave2.json').write_text(json.dumps({'schema':'komorebi.paper_ii.editorial_wave2.v1','status':'APPLIED_PENDING_REVIEW_AND_PDF_BUILD','audit_source':'paper2_work/audit/arithmetic_initial.json','changes':changes,'files':logs,'pdf_authoring_marker':'Already run exactly once before wave1. Not repeated.','validation':'All before fragments matched exactly once. No PDF build, final status or formal source change.'},indent=2)+'\n')
(A/'editorial_wave2.diff').write_text(''.join(''.join(difflib.unified_diff(original[rel].splitlines(True),t.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel)) for rel,t in working.items()))
print('Applied',len(changes),'arithmetic clarifications')
