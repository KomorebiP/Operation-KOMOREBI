from pathlib import Path
import sys, time, json
from dataclasses import asdict
from decimal import Decimal
import numpy as np
from scipy.linalg import hadamard
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine'))
from interval_kcos import scaled_chi_square_target_point, even_df_scaled_chi_square_logsf_interval
from accuracy_driven import certified_positive_logsf
from verified_spectrum import certified_float64_factor_logsf
from directed_accuracy import interval_endpoint_strings
rows=[]
start=time.perf_counter()
q=scaled_chi_square_target_point(-5000,coefficient_decimal='0.02',df=80,working_dps=260,output_digits=220)
options=dict(initial_K=32,initial_L='8',initial_interval_dps=50,max_K=16384,max_L=24,max_interval_dps=180,working_dps=260)
r=certified_positive_logsf(q,['0.02']*80,relative_accuracy='1e-18',**options)
exact=even_df_scaled_chi_square_logsf_interval(q,coefficient_decimal='0.02',df=80,interval_dps=140)
lo,hi=map(Decimal,interval_endpoint_strings(r.log10_interval))
elo,ehi=map(Decimal,interval_endpoint_strings(exact['log10_interval']))
contained=lo<=elo and ehi<=hi
row={'case':'scaled_chi2_80_near_1e-5000','q_exact_decimal':q,'coefficient_exact_decimal':'0.02','df':80,'requested_relative_accuracy':'1e-18','options':options,'result':asdict(r),'independent_exact_erlang_log10_interval':exact['log10_interval'],'independent_control_interval_fully_contained':contained,'runtime_seconds':time.perf_counter()-start}
rows.append(row)
print('deep_control',r.certified,'upper_relative_ratio',r.achieved_relative_ratio_minus_one,'erlang_contained',contained,'seconds',row['runtime_seconds'],flush=True)
assert r.certified and contained and Decimal(r.achieved_relative_ratio_minus_one)<=Decimal('1e-18')
start=time.perf_counter()
n=64
Q=hadamard(n,dtype=np.float64)/8
singular=np.repeat(np.array([1,.75,.5,.25]),16)
A=Q*singular[None,:]
options=dict(relative_accuracy='1e-12',initial_candidate_digits=50,max_candidate_digits=80,candidate_step=30,interval_dps=65,tail_accuracy_fraction='0.05',tail_kwargs=dict(initial_K=64,initial_L='10',initial_interval_dps=50,max_K=4096,max_L=18,max_interval_dps=120,working_dps=170))
r=certified_float64_factor_logsf('131.33201485100517',A,**options)
known=[Decimal('1')]*16+[Decimal('0.5625')]*16+[Decimal('0.25')]*16+[Decimal('0.0625')]*16
s=r.spectral_enclosure
contained=all(Decimal(lo)<=e<=Decimal(hi) for lo,hi,e in zip(s.lower,s.upper,known))
row={'case':'binary64_dense_64_matrix_tail_near_1e-16','factor_construction':'hadamard(64)/8 times repeated singular values [1,0.75,0.5,0.25], 16 copies each; all entries exact binary64 dyadics','q_exact_decimal':'131.33201485100517','shape':[64,64],'options':options,'result':asdict(r),'all_known_exact_eigenvalues_contained':contained,'runtime_seconds':time.perf_counter()-start}
rows.append(row)
print('matrix_control',r.certified,'upper_relative_ratio',r.achieved_relative_ratio_minus_one,'eigenvalues_contained',contained,'seconds',row['runtime_seconds'],flush=True)
assert r.certified and contained and Decimal(r.achieved_relative_ratio_minus_one)<=Decimal('1e-12')
Path(sys.argv[1]).write_text(json.dumps({'controls':rows,'all_passed':True},indent=2)+'\n')
