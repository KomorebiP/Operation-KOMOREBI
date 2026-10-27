"""Population moment learning and fixed-template recognition without a generator import."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from continuous_reference import load_json,fit_population_moments,recognize_template,certificate_from_template,verify_certificate,encode


def main():
    fitted=fit_population_moments(load_json(ROOT/'examples/continuous_population_tables.json'))
    template=load_json(ROOT/'examples/continuous_template.json')
    T=recognize_template(fitted,template)
    certificate=certificate_from_template(fitted,template,T)
    verified=verify_certificate(certificate)
    p,z=verified.condition_at('direct','1/2')
    q,z=verified.condition_at('rotated','-1/2',z)
    destination=ROOT/'certificates/continuous_psd_certificate.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(certificate,indent=2)+'\n')
    report={'core_determinant':str(fitted['core_determinant']),
            'moment_gram_determinant':str(fitted['moment_gram_determinant']),
            'alignment':encode(T),'certificate':verified.verification,
            'densities_wrt_du_over_2':[str(p),str(q)],'joint_density':str(p*q),
            'final_test_state':encode(z),
            'point_probabilities':'Zero for this nonatomic model. Listed values are densities.',
            'learning_scope':'Known degree and rank, exact population tables, supplied structural template.'}
    (ROOT/'verification/continuous_example.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
