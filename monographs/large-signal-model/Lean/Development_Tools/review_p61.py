from pathlib import Path
import hashlib,json

root=Path('/workspace/scratch/ea498747acd5/work/Komorebi_LSM_Lean_0.18.0')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'ContinuousPopulationBridge':'a6f3b0b484b38dfeef5e1ecd33c59c93d97d905b1bb4cacda6d879667edfa7c6','ContinuousRealizationP61':'d146f7a85d3673e2a8e59840cb342c81512985de9213aed8802590be1545ece9'}
for m,h in expected.items():assert sha(root/'KomorebiLSM'/f'{m}.lean')==h
result_path=root/'verification/development_p61/RESULT.json'
result=json.loads(result_path.read_text())
assert result['passed'] is True
checks=[
 'Supplied dimension and polynomial degree remain the actual finite coordinate and coefficient types; no global rank or degree discovery is inferred from finitely many tables',
 'The actual invertible population core derives the test coordinate equivalence and its inverse; fitted coefficients are literally reconstructedCoefficient(populationCore,populationTable)',
 'P54 reconstruction derives coefficient, full density and all-word likelihood identities without assuming the desired identification or equality of laws',
 'The P53 finite coefficient/Gram/moment certificate is attached to exactly those fitted coefficients and constructs the literal realizedInstrument',
 'The independent transformed initial PSD and mass-one check derives initial validity, all-horizon actual record probabilities and prefixes, prescribed-action probabilities and event density formula',
 'Inverse population atlas constructs the literal original-coefficient instrument and its mass row, then proves equality of actual original and fitted common-policy record measures',
 'P60 template matching constructs a finite certificate for exactly the reconstructed family; an invertible map and separate initial check are retained',
 'Exact atlas coefficients are literal conjugates; their match and actual full event-law equality are derived, with unchanged finite Gram witnesses',
 'Complete signed packet synthesis preserves the actual event measure through the proved state identity; signed packet raw measures are not claimed additive probability mixtures',
 'Individual normalized packet interpretation separately requires cone positivity and positive mass',
 'The actual partition bin map, its cell fibers, bin-history policy and complete actual pushforward equality use this same fitted instrument',
 'General positive Bochner cell averages retain exact cells, integrated mass and Lh; actual equal-interval hypotheses and genuine induced norm retain Lh/3',
 'The constant-time-family run and actual record-law bridge are proved, allowing the same fitted record measure to invoke the P59 common-cone/common-reference/common-policy budget',
 'Three semantic controls retain degree, independent initial state and separate signed-packet positivity rather than deriving False from missing imports or unknown identifiers',
]
out={'claim':'P61 conditional continuous realization with finite domain certificate','verdict':'proved as written in the registered scope','provenance':'Coordinator raw-source review of both complete 511-line sources and all three controls, separate from the author. Same collaborative model/team lineage, not external independent certification.','source_hashes':{'KomorebiLSM/'+m+'.lean':h for m,h in expected.items()},'checks':[{'obligation':x,'passed':True}for x in checks],'scope_limit':'Conditional finite dimension, polynomial degree, invertible complete population core, exact moment dictionaries, independent finite certificate and initial coverage. No empirical coverage, unrestricted geometry discovery or adequacy follows from internal validity.','execution_boundary':'Final author individual receipt is bound below. The coordinator did not rerun those commands; fresh cumulative .18 compilation, axiom audit, replay and all controls remain separately required.','author_result_sha256':sha(result_path)}
p=root/'verification/development_p61/RAW_COORDINATOR_REVIEW.json'
p.write_text(json.dumps(out,indent=2)+'\n')
mapping={'status':'complete','modules':list(expected),'source_sha256':expected,'endpoints':['Komorebi.LSM.ContinuousPopulationBridge.fitted_density_identification','Komorebi.LSM.ContinuousRealizationP61.population_realization_certificate','Komorebi.LSM.ContinuousRealizationP61.population_record_law','Komorebi.LSM.ContinuousRealizationP61.recognized_population_probability','Komorebi.LSM.ContinuousRealizationP61.population_atlas_law','Komorebi.LSM.ContinuousRealizationP61.complete_packet_law','Komorebi.LSM.ContinuousRealizationP61.positive_packet_state','Komorebi.LSM.ContinuousRealizationP61.exact_population_bins','Komorebi.LSM.ContinuousRealizationP61.population_cell_resolution','Komorebi.LSM.ContinuousRealizationP61.population_equal_interval_resolution','Komorebi.LSM.ContinuousRealizationP61.population_common_policy_budget'],'scope':'Actual supplied finite dimension and polynomial degree with an invertible complete population core derive inverse-moment fitted coefficients, full densities and word likelihoods. The independent P53 finite matrix/Gram/moment witness and transformed initial PSD/mass check for that same family yield actual all-horizon laws. Literal original/atlas event-law transport, a sufficient invertible P60 template constructor, complete signed synthesis with separate packet positivity, actual bin-policy pushforward, P58 Lh and Lh/3 resolution and P59 common-cone/reference/policy budgets are connected to the same fitted instrument. No dimension/degree discovery, empirical coverage or generating-process adequacy is inferred.'}
(p.parent/'ACCEPTED_MAPPING.json').write_text(json.dumps(mapping,indent=2)+'\n')
print(p,sha(p))
