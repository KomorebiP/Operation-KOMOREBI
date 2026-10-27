import pathlib,json,hashlib,re
root=pathlib.Path('/dev/shm/komorebi_core_monograph_fbc994080222')
source=root/'register_current.txt'
text=source.read_text()
meta=json.loads((root/'register_metadata.json').read_text())
rows=[
('I','Projector Resolved Seed Calculus I',[105,44,100],
 'The accepted publication covers 69 proof-level records at the scopes of its 108-record correspondence map. Accepted October 15 evidence checks 3,500 logical declarations, with runtime helpers separately inventoried. The frozen readers retain the accepted mathematical content.',
 ['The semantic record distinguishes 47 targeted new reviews from 22 retained predecessor correspondences.','Noncomputable constructions are not executable solvers.','Pinned external runtime and cache prerequisites remain.'],[]),
('II','Projector Resolved Seed Calculus II',[80,26,51],
 'The accepted contract covers all 53 enumerated proof-level source scopes, with a complete 81-record map. Its 75 production modules and 2,112 logical replays retain their October 19 evidence date. The 48 Python tests retain the successful October 20 record.',
 ['No general admissible-contour existence theorem is asserted; canonical values require the relevant admissible data.','The unrecovered historical 80-module/2,228-replay claim is not current evidence.','Retained unpacked history does not recreate a missing historical ZIP.'],[]),
('III','Projector Resolved Seed Calculus III',[99,6,26,53,2],
 'The corrected publication treats actual-range continuous packet jets and norm and composition interfaces. Its accepted formal core covers 16 production modules, 608 owned declarations and 594 logical replays. The main manuscript has 167 numbered environments, including 98 theorem-like environments and two classical standard facts, which are separate counts.',
 ['Full Lean certification of the expanded monograph remains incomplete.','Packet Taylor integral remainder and estimate, the Stirling/Touchard count, separate restricted-product/Hilbert norm corollaries and later expanded material retain reviewed ordinary-proof status.','Total iteratedFDeriv reconstruction does not assert differentiability of an arbitrary function.','The older 2,693-declaration/full-98+2 formal claim remains uncertified because matched source was not recovered.','Papers I-II dependencies remain inherited.'],[]),
('IV','Projector Resolved Seed Calculus IV',[77,28,140,5],
 'The reviewed publication retains its 68-result contract, with Standard fact 11.1 separate. Accepted October 19 evidence covers 118 production modules, 151 correspondence rows and 1,164 targets. Its formal namespace census and finite gates remain separately bounded evidence.',
 ['No universal zero simplicity, positivity of every reduced zero, full displacement expansion or zeta functional equation is asserted.','Hypotheses, branch choices, multiplicities and integer-order ranges remain in force.','Exact editable source for the selected later October 16 standalone visual PDF remains unrecovered; the selected PDF and older October 8 source are retained, with differences on pages 1, 14 and 28.','No exact rebuild of the later visual PDF is claimed.'],[]),
('V','Multiresolution Signal Calculus',[131,43,60],
 'The accepted release integrates the recovered subsidiary repair and the exactly normalized square-wave example. It preserves 83 proof environments and the documented 118/119 numbered records. The inherited finite Lean contract contains twenty results and 225 targets; broader prose proof records do not enlarge it.',
 ['The September 6 compiler evidence remains inherited; no fresh Lean run occurred in the closeout or freeze.','The 63 broader prose proof records do not enlarge formal coverage.','Separated-jump results retain their model, gap and grid assumptions.','Seventeen October 5 verification artifacts remain unrecovered and inventoried; current manuscripts, figures and original Lean sources are present.'],
 ['Stable edge-packet recovery.','The edge-packet approximation class.']),
('VI','Transfer Semigroups and Memory',[152,44,64],
 'The publication retains its mathematical body and the accepted corrected builders and guides. Its inherited formal contract covers 33 scoped endpoints, 341 targets and 47 production modules. The broader 142 theorem-like records and 140 proof bodies remain separate from that contract.',
 ['Full-paper Lean formalization is incomplete; September 6 compiler and axiom evidence remains inherited.','Two disclosure-only branch reconstructions and three fragment pins authenticate their stated inputs; the old assembled whole-file hash remains unrecovered.','Classical inputs retain their hypotheses and inherited authentication scope.','Finite-state, common-gap and fixed-partition restrictions remain.','Floating residuals are not interval certificates.'],
 ['Transfer-semigroup realization on completed state spaces.','Uniform refinement control.','Latent-packet closure for stable infinite systems.']),
('VII','Quantum Seeds and Effective Dynamics',[159,42,85],
 'The accepted publication has nine mathematical parts, six supplements, three retained alternative proofs and worked visual and Lean guides. Its inherited formal evidence supports nineteen finite items under their stated hypotheses; the expanded manuscript and physical continuum program exceed that finite contract.',
 ['The 323 named theorem declarations in 25 active modules, six constructed objects and nine dependency pins are distinct units.','Full expanded-manuscript formalization and Part II’s physical continuum program are outside the finite contract.','Bounded-operator and geometric statements retain their individual hypotheses.','The 125 older compiled-object hashes are historical; those binaries are not retained.','Accepted PDF replay compares page counts and extracted text, with byte equality recorded separately.'],
 ['Anomaly-free refinement.','Uniform Feshbach control for the proposed tower.','Lorentzian reconstruction.','An Einstein infrared limit.','A positive physical massless spin-two sector.']),
('VIII','Packet Operator Algorithms',[124,34,94],
 'The publication retains seven mathematical parts, 85 numbered records, 56 main proof bodies and six substantive proof supplements. Accepted September 6 formal evidence covers 56 finite items under their hypotheses. Its 392 theorem declarations include 373 Paper VIII declarations and nineteen reused foundation results; constructions and classical inputs remain separate.',
 ['Small-core optimality assumes supplied ordered thin-SVD equations, actual compact input ranges and the stated arbitrary ambient competitors.','General SVD existence, verified numerical QR/SVD and canonical singular-values API identification remain outside the formal contract.','No generic dense-matrix exponent, unrestricted discovery theorem, bit-complexity bound or CUDA-kernel verification is asserted.','The older 200 compiled-output hashes are historical crosslinks; compiled binaries and a standalone matched toolchain/configuration bundle are not retained.','Historical GPU timings lack complete source-array fingerprints, correctness-reference fields and timing provenance; arithmetic recalculation does not recover them.'],
 ['Unrestricted profitable structure discovery.','Compilation with nonlocal costs and overlapping candidates.','An architecture-specific packet communication theorem.']),
('IX','Euler Congruences',[232,25,139],
 'The accepted publication preserves its current written proofs and inherited arithmetic, dyadic and lifting endpoints. The historical bibliography identities, source archive and original figures were recovered within a bounded authentication scope. Expanded factorial, mixed-step, all-rank and radius developments remain written proofs, audits and bounded checks rather than newly compiled endpoints.',
 ['The inherited external Nishibuchi capstone and arithmetic/dyadic/lifting endpoints retain their exact individual scopes.','Static source, log, correspondence and axiom inventories are distinct units, not a new full-paper kernel-coverage count.','Two older scalar summaries, 380 output hashes without retained build directories, and runtime/configuration/adapter/Nishibuchi correspondence limits remain explicit.','Dyadic512 retains 4,096-bit modular precision and difference order through 128, with exact rational checks recorded separately.','Failed stronger equality candidates remain failures.','Amice analytic pullback/depleted branches, finite-field modal minimality and unrestricted infinite polyphase interfaces retain narrower qualifications.','Bibliography recovery does not verify every cited theorem application or blanket-certify historical mathematics.','Current PDF replay has matching text and page counts; byte equality requires trailer-ID normalization and raw PDF byte equality is false.'],
 ['General ordinary Euler-tail simplicity.','Remaining exact higher-difference classifications.','Broad Native13.2/13.3 programs.']),
('X','Universal Residual Seeds',[92,33,37],
 'The selected amended conditional publication has a twenty-row source contract. Its October 20 evidence includes two fresh pinned 122-module builds, 392 byte-identical generated artifacts and a full audit of 2,846 owned declarations. These accepted runs are inherited evidence for the collected edition.',
 ['The conditional 20/20 contract has independent target-family and carrier-recovery existentials, with a literal GQ arithmetic separator.','Source families, carrier presentations and constituent local comparisons remain supplied.','Identifying the witnesses and nonzero occupancy require additional premises.','Classical Inputs 3.1 and 4.1 are excluded from the twenty-row concordance.','Bounded critical-source review is not an all-20 proof audit or machine-certified prose equivalence.','The later stronger 19/20 residual attempt remains unpromoted.','The October 16-17 packages and reported 122/39 run remain unauthenticated; the recovered October 10 lineage was explicitly selected.','Accepted PDF replay has false raw-byte identity but exact page/text/86.4-dpi pixels and trailer-ID-normalized identity; production-artifact raw-byte identity is a separate result.'],
 ['Universal occupancy.','Natural finite seed rank.','Unknown carriers.','Unrestricted compatible systems.','General arithmetic attachment.']),
('XI','Tame and Wild Packet Geometry',[111,53,239,77,36],
 'The accepted publication retains its selected formal scope and separately tracked terminal and interface work. The October 18 record covers 423 selected modules, 4,342 catalogue names and 7,672 owned logical declarations, including 6,159 theorems. Conjecture 66 remains open.',
 ['The 7,672 logical declarations and 4,342 lexical catalogue names are different counts.','The repaired-terminal 51 declarations and supplied-candidate-interface one declaration remain separate.','October 18 continuations reused only authenticated successful objects from that same session; compiled objects, runtime and caches are not bundled.','The 403-page raw-versus-assembled comparison establishes assembly consistency, not a fresh isolated rebuild or universal byte identity.','The full Block 02 editable archive remains missing; its preserved reader is not a recovered unified source rebuild.','The original v0.45 receipt remains missing despite a separately repaired successful replay.'],
 ['General arithmetic realization for every admitted H1-H4 datum.','Full characterizing H5 identities for the same realized candidate.','Corrected full-character occurrence in the fixed Continuation113 candidate with the correct noncompact extension.','Actual native square/section/phase data when the stronger prescribed native contract is required.']),
('XII','Patching Support and Hecke Packets',[40,28,31],
 'The revised conditional publication supplies 49 claim links to 291 distinct production targets. Its original census of 41 complete, seven partial and one unchecked claim remains a separate historical statement. Production and teaching sources are preserved, with compiler evidence inherited.',
 ['Applications must supply actual residual/deformation data, applicable patching and full support.','Applications must supply a compatible same-field Hecke point, classicality and an attached representation.','Frobenius comparison and any required already existing compatible families must be supplied.','The conditional theorem does not establish universal supply of those arithmetic inputs.','Paper XI Conjecture 66 is not assumed proved.','The historical 96 registered modules, 1,229 public named declarations, 748 XII theorem declarations and 81 reused X theorem declarations retain their lexical/inherited meanings.','The 24 teaching modules are distinct from the 49 excerpt-directory files.','Recorded isolated rebuild equality covers three PDFs and four redrawn figure PDFs in the checked environment; it is not a cross-platform promise.','Nine deliberately excluded predecessor font binaries remain external dependencies; historical font-source access and exact-lineage limits remain explicit.'],[])
]
sections={}
parts=re.split(r'(?m)^([IVX]+)\. ([A-Z][A-Z ]+)\n',text)
for j in range(1,len(parts),3): sections[parts[j]]={'heading':parts[j+1], 'text':parts[j+2].split('\nSHARED RELEASE WORK')[0]}
papers=[]
for no,title,pages,scope,bounds,opened in rows:
 section=sections[no]
 date='2026-10-20' if no in ['I','II','III','IV','V','VI','VII'] else '2026-10-21'
 labels=['reader_1','reader_2','reader_3']
 if no=='III': labels=['main','analytic','visual','Lean','release_record']
 elif no=='IV': labels=['reader_1','reader_2','reader_3','verification_addendum']
 elif no=='XI': labels=['reader_1','reader_2','reader_3','reader_4','reader_5']
 p={'paper':no,'title':title,'register_heading':section['heading'],'frozen_package':f'Paper_{no}_Frozen_Release_{date}.zip','reader_package':f'Paper_{no}_Frozen_Readers_{date}.zip','freeze_date':date,'components':[{'register_label':lab,'pages':n} for lab,n in zip(labels,pages)],'selected_component_page_count':sum(pages),'scope_paragraph':scope,'required_boundaries':bounds,'open_research':opened,'source_section_sha256':hashlib.sha256(section['text'].encode()).hexdigest()}
 if no=='III': p['duplication']={'combined_reader_pages':186,'additional_pages_if_all_six_pdfs_are_appended':186,'rule':'Use the five components or the complete reader, not both. The complete reader repeats the same 186 pages.'}
 if no=='X': p['duplication']={'known_atlas_duplicate_pages_within_selected_readers':30,'known_duplicate_adjusted_page_count':132,'rule':'The three selected readers total 162 delivered pages, including thirty intentionally duplicated atlas pages. Identify these exact source pages before deciding whether to omit them.'}
 if no=='IX': p['excluded_from_current_count']=['Original historical 52-page reader.','Three same-basename unselected publication/build PDFs.']
 if no=='XI': p['count_caution']='The separate 403-page assembly-comparison unit is not the full 516-page delivered-reader total and does not itself establish a duplicate-page removal rule.'
 papers.append(p)
data={
 'schema':'komorebi.core.monograph-editorial-inventory/1',
 'source':{k:meta[k] for k in ['name','library_file_id','file_id','version_id','modified_at','size_bytes']},
 'source_local_reconstruction_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'source_note':'Derived only from the current version-17 register read. Local text reconstruction restores one final newline; hashes of register sections are editorial provenance, not claims about original source-package bytes.',
 'selection_policy':'Use the twelve frozen reader sets, retaining paper-local hypotheses, claim numbering and inherited evidence scope. Do not promote a later duplicate upload or unselected build artifact to the selected edition.',
 'shared_front_matter':[
  'This collected edition presents the twelve frozen core publications within their accepted publication, formal and conditional scopes. Their distribution freezes were completed on 20-21 October 2026.',
  'Collection and layout do not constitute a fresh full proof audit or a new execution of the twelve Lean projects. Recorded compiler, finite-computation and rebuild evidence retains its original date and exact scope.',
  'Publication completion does not imply that every English proof is formalized, every conjecture is solved or every historical archive is recovered. Each part states its own assumptions, formal coverage and remaining research.',
  'Original software and machine-readable material use MIT. Original writing, figures and editable writing sources use CC BY 4.0. Third-party and font terms remain separate and must accompany the collected edition.',
  'The wider Komorebi Space, Realization Calculus companions, Proof-Path Theory, machine-theory and software projects are outside this twelve-paper closeout.'
 ],
 'page_accounting':{
  'selected_component_pages_excluding_the_duplicate_III_complete_reader':sum(p['selected_component_page_count'] for p in papers),
  'known_internal_X_atlas_duplicate_pages':30,
  'known_duplicate_adjusted_pages':sum(p['selected_component_page_count'] for p in papers)-30,
  'all_selected_pdf_pages_if_III_components_and_complete_reader_are_both_counted':sum(p['selected_component_page_count'] for p in papers)+186,
  'qualification':'3047 is the sum of selected component readers using III once. 3017 removes only the register-explicit thirty-page X atlas overlap. This is not a fresh global page-identity or semantic-deduplication audit. Front matter, separators and additional editorial pages are not included.',
  'component_label_note':'Reader names are not given by the register for most parts. Generic reader_n labels preserve the register order without inventing role-to-file mappings; resolve exact filenames and roles from each selected reader archive.'
 },
 'papers':papers
}
out=root/'editorial/core_inventory.json';out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
assert len(papers)==12
assert data['page_accounting']['selected_component_pages_excluding_the_duplicate_III_complete_reader']==3047
print(json.dumps({'output':str(out),'papers':len(papers),'selected_component_pages':3047,'known_duplicate_adjusted_pages':3017,'bytes':out.stat().st_size}))
