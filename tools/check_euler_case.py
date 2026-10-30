"""Check the worked Euler page, accepted finite evidence, and optional library route."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'examples/euler_packets.py'
PAGE = ROOT/'docs/demonstrations/EULER_PACKETS.md'
RUN = ROOT/'verification/euler-packets/run-007'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_example():
    spec=importlib.util.spec_from_file_location('euler_worked_case',SCRIPT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_library(example, math_root, git, computed=None):
    expected=json.loads((ROOT/'manifests/reader-site-libraries.json').read_bytes())['math']['revision']
    revision=subprocess.check_output([git,'rev-parse','HEAD'],cwd=math_root,text=True).strip()
    # Documentation-only checkout changes are allowed, but every tracked source
    # must still match the website's pinned revision. Imported untracked sources
    # are rejected below as well.
    subprocess.run([git,'diff','--exit-code',expected,'--','src'],cwd=math_root,check=True,capture_output=True)
    raw=subprocess.check_output([git,'ls-tree','-r','--name-only',expected,'src'],cwd=math_root,text=True)
    before={p:digest(math_root/p) for p in raw.splitlines() if p.endswith('.py') and (math_root/p).is_file()}
    sys.path.insert(0,str(math_root/'src'))
    from komorebi_math.sequences import reciprocal_coefficients as integral
    from komorebi_math.analytic.reciprocal import reciprocal_coefficients as analytic
    from komorebi_math.arithmetic.euler import EulerLocalCoordinates, signed_euler_number
    from komorebi_math.coordinates.polynomials import (
        euler_to_fibonacci_transform, fibonacci_companion_power,
        secant_euler_from_fibonacci_coordinates, fibonacci_polynomial_family,
        euler_polynomial_family)
    from komorebi_math.coordinates.calculus import (
        integral_coordinate_operator, derivative_coordinate_operator)
    from komorebi_math.arithmetic.recurrence import LinearRecurrence
    from komorebi_math.analytic.appell import congruential_inverse
    from komorebi_math.arithmetic.hurwitz import hurwitz_inverse, hurwitz_product
    from komorebi_math.coordinates.combinatorial import stirling_first_signed, stirling_second
    from komorebi_math.coordinates.formal import FormalCoordinateChange
    from komorebi_math.coordinates.recurrence import (
        analyze_recurrence_coordinates, euler_fibonacci_coordinates,
        recurrence_analysis_transform, recurrence_synthesis_transform,
        variation_of_constants_prefix)
    import numpy
    checks=0
    for spacing in range(2,7):
        for parameter in (0,1,2,3):
            reference=example.reciprocal_recurrence(spacing,parameter,11)
            assert tuple(reference)==integral(spacing,11,power=parameter)
            checks+=11
        for parameter in (F(-2),F(-1),F(0),F(1,2),F(1),F(2),F(3)):
            reference=example.reciprocal_recurrence(spacing,parameter,11)
            assert tuple(reference)==analytic(spacing,parameter,10)
            checks+=11
    local_checks=dict(values=0,truncations=0,row_weights=0)
    for prime in (2,3,5,7):
        coordinates=EulerLocalCoordinates(prime)
        kernel=example.local_kernel(prime,11)
        inverse_kernel=example.local_inverse_kernel(prime,11)
        for index in range(11):
            degree=2*index
            source=example.local_source(prime,degree)
            terms=example.local_terms(prime,index)
            expected_value=sum(terms)
            assert coordinates.source(degree)==source
            assert coordinates.kernel(index)==kernel[index]
            assert coordinates.inverse_kernel(index)==inverse_kernel[index]
            assert coordinates.reconstruct(degree)==expected_value
            assert coordinates.inverse_reconstruct_source(degree)==source
            local_checks['values']+=5
            for depth in range(index+1):
                result=coordinates.truncate(degree,depth)
                partial=sum(terms[:depth+1])
                assert result.value==partial
                assert result.error==expected_value-partial
                assert result.certificate.valid
                if depth==index:
                    assert result.modulus is None
                else:
                    assert result.modulus==prime**(4*depth+3 if prime==2 else 2*depth+2)
                local_checks['truncations']+=2
                assert coordinates.row_weight(degree,depth)==example.valuation(terms[depth],prime)
                local_checks['row_weights']+=1
    computed=example.compute() if computed is None else computed
    fib=computed['fibonacci']
    connection=euler_to_fibonacci_transform(12).matrix
    fib_checks=dict(connection_entries=0,polynomial_companion_entries=0,
                    centered_euler_values=0,recurrence_matrix_entries=0,
                    recurrence_round_trips=0,full_index_records=0)
    for i in range(13):
        for j in range(13):
            assert connection[i][j]==F(fib['polynomial_connection'][i][j])
            fib_checks['connection_entries']+=1
    even=[(-1)**n*value for n,value in enumerate(example.reciprocal_recurrence(2,1,26))]
    full=[F(0) if n%2 else even[n//2] for n in range(26)]
    assert full[:5]!=even[:5]
    for n in range(13):
        mat=fibonacci_companion_power(n)
        for i in range(2):
            for j in range(2):
                assert tuple(mat[i][j])==tuple(map(F,fib['polynomial_companion_powers'][n][i][j]))
                fib_checks['polynomial_companion_entries']+=1
        assert secant_euler_from_fibonacci_coordinates(n)==full[n]
        fib_checks['centered_euler_values']+=1
    for length in range(2,27):
        for values in (even[:length],full[:length]):
            record=analyze_recurrence_coordinates(values,(1,1))
            expected_coordinates=tuple(values[:2])+tuple(values[i+2]-values[i+1]-values[i] for i in range(length-2))
            assert record.coordinates()==expected_coordinates
            assert record.reconstruct()==tuple(values)
            assert variation_of_constants_prefix(record)==tuple(values)
            fib_checks['recurrence_round_trips']+=3
        assert euler_fibonacci_coordinates(length).coordinates()==analyze_recurrence_coordinates(full[:length],(1,1)).coordinates()
        fib_checks['full_index_records']+=1
        # Check every entry of the accepted 16-term matrices against the library.
        if length==16:
            for api,key in ((recurrence_analysis_transform,'recurrence_analysis'),
                            (recurrence_synthesis_transform,'recurrence_synthesis')):
                matrix=api((1,1),length).matrix
                for i in range(length):
                    for j in range(length):
                        assert matrix[i][j]==F(fib[key][i][j])
                        fib_checks['recurrence_matrix_entries']+=1
    literature=computed['literature']
    lit_checks=dict(packet_values=0,packet_state_coordinates=0,jump_entries=0,calculus_entries=0)
    fib_values=[0,1]
    for _ in range(1400):
        fib_values.append(fib_values[-1]+fib_values[-2])
    recurrence=LinearRecurrence((1,1),(0,1))
    for step in range(1,13):
        jump=recurrence.jump_matrix(step)
        expected_jump=literature['jumps'][step]
        for i in range(2):
            for j in range(2):
                assert jump[i,j]==expected_jump[1-i][1-j]
                lit_checks['jump_entries']+=1
        for address in range(step):
            packet=recurrence.residue_packet(step,address)
            for k in range(10):
                assert packet.term(k)==fib_values[step*k+address]
                lit_checks['packet_values']+=1
                for i,value in enumerate(packet.state(k)):
                    assert value==fib_values[step*k+address+i]
                    lit_checks['packet_state_coordinates']+=1
    for row in literature['dyadic_factors']:
        step,divisor=row['step'],row['divisor']
        jump=recurrence.jump_matrix(step)
        for i in range(2):
            for j in range(2):
                assert jump[i,j]==int(i==j)+divisor*row['factor'][1-i][1-j]
                lit_checks['jump_entries']+=1
    for degree in range(9):
        record=literature['calculus'][str(degree)]
        matrices=[(integral_coordinate_operator(fibonacci_polynomial_family(),degree).matrix,record['integral']),
                  (derivative_coordinate_operator(fibonacci_polynomial_family(),degree+1).matrix,
                   record['derivative']+[['0']*(degree+2)]),
                  (derivative_coordinate_operator(euler_polynomial_family(),degree+1).matrix,
                   record['euler_derivative']+[['0']*(degree+2)])]
        for actual,wanted in matrices:
            for i,row in enumerate(actual):
                for j,value in enumerate(row):
                    assert value==F(wanted[i][j])
                    lit_checks['calculus_entries']+=1
    atlas=computed['atlas']
    atlas_checks=dict(quartic_values=0,hurwitz_values=0,stirling_entries=0,
                      formal_values=0,formal_substitution_entries=0)
    for address in range(4):
        actual=congruential_inverse(4,address,23)
        for n,value in enumerate(actual):
            assert value==F(atlas['quartic'][address][n])
            atlas_checks['quartic_values']+=1
    for mode in atlas['modes']:
        prime=mode['prime']
        q=[int(n%2==0) for n in range(25)]
        actual=hurwitz_inverse(q,24,modulus=prime)
        product=hurwitz_product(q,actual,degree=24,modulus=prime)
        for n in range(25):
            assert actual[n]==mode['values'][n]
            assert product[n]==int(n==0)
            atlas_checks['hurwitz_values']+=2
    for n in range(17):
        for k in range(17):
            assert stirling_first_signed(n,k)==atlas['stirling_first'][n][k]
            assert stirling_second(n,k)==atlas['stirling_second'][n][k]
            atlas_checks['stirling_entries']+=2
    from math import factorial
    log=(F(0),)+tuple(F((-1)**(n+1),n) for n in range(1,17))
    chart=FormalCoordinateChange('log(1+T)',log)
    for coefficients,wanted in (
        ([F(atlas['full_euler'][n],factorial(n)) for n in range(17)],atlas['logarithmic_ordinary']),
        ([F(atlas['full_euler'][n+1],factorial(n)) for n in range(17)],atlas['derivative_pullback'])):
        for value,expected_value in zip(chart.pullback_coefficients(coefficients),wanted):
            assert value==F(expected_value)
            atlas_checks['formal_values']+=1
    for n,value in enumerate(chart.inverse().coefficients):
        assert value==(F(0) if n==0 else F(1,factorial(n)))
        atlas_checks['formal_values']+=1
    substitution=chart.substitution_transform().matrix
    for n in range(17):
        for k in range(17):
            assert substitution[n][k]*factorial(n)/factorial(k)==atlas['stirling_first'][n][k]
            atlas_checks['formal_substitution_entries']+=1
    edge_checks=dict(partials=0,errors=0,row_weights=0,kernel_values=0)
    dyadic=EulerLocalCoordinates(2)
    for row in computed['edge']['rows']:
        r,x,n=row['r'],row['x'],row['N']
        if not ((r<=8 and x<=4) or (r in (15,31) and x<=2)):
            continue
        partial=dyadic.reconstruct(2*n,depth=r-1)
        assert partial==F(row['partial'])
        edge_checks['partials']+=1
        assert signed_euler_number(2*n)-partial==F(row['tail'])
        edge_checks['errors']+=1
        for offset,weight in enumerate(row['omitted_weights']):
            assert dyadic.row_weight(2*n,r+offset)==weight
            edge_checks['row_weights']+=1
    for r,value in computed['edge']['kernel'].items():
        assert dyadic.kernel(int(r))==F(value)
        edge_checks['kernel_values']+=1
    sources=[]
    for name,module in sorted(sys.modules.items()):
        filename=getattr(module,'__file__',None)
        if not name.startswith('komorebi_math') or not filename:
            continue
        path=Path(filename).resolve()
        assert path.is_relative_to(math_root), 'Unexpected package source: '+str(path)
        relative=path.relative_to(math_root).as_posix()
        assert relative in before, 'Untracked imported library source: '+relative
        after=digest(path)
        assert before[relative]==after, 'Library source changed during comparison: '+relative
        sources.append(dict(path=relative,sha256=after,sha256_before=before[relative]))
    return dict(status='PASS',checkout_revision=revision,source_revision=expected,
                tracked_sources_match_pin=True,coefficient_comparisons=checks,
                numpy_version=numpy.__version__,imported_sources=sources,
                local_charts=[2,3,5,7],local_even_degree=[0,20],
                local_comparisons=local_checks,local_chart_comparisons=sum(local_checks.values()),
                fibonacci_comparisons=fib_checks,fibonacci_total_comparisons=sum(fib_checks.values()),
                literature_comparisons=lit_checks,literature_total_comparisons=sum(lit_checks.values()),
                atlas_comparisons=atlas_checks,atlas_total_comparisons=sum(atlas_checks.values()),
                edge_comparisons=edge_checks,edge_total_comparisons=sum(edge_checks.values()),
                scope='Exact numeric library outputs in the declared finite range. Not a proof of the complete Python implementation.')


def check(math_root=None,git='git'):
    example=load_example()
    accepted=json.loads((RUN/'results.json').read_bytes())
    manifest=json.loads((RUN/'manifest.json').read_bytes())
    assert manifest['run']['status']=='completed' and manifest['run']['exit_status']==0
    assert accepted['source_sha256']==digest(SCRIPT)
    source_record=next(item for item in manifest['input_artifacts'] if item['path']=='examples/euler_packets.py')
    assert source_record['sha256']==source_record['sha256_after']==digest(SCRIPT)
    for result in manifest['outputs']:
        assert digest(ROOT/result['path'])==result['sha256'],result['path']
    fresh=example.compute()
    semantic=lambda r:{k:v for k,v in r.items() if k!='python'}
    assert semantic(fresh)==semantic(accepted), 'The accepted finite output is stale'
    text=PAGE.read_text(encoding='utf-8')
    marker=re.search(r'<!-- euler-expected-output -->\s*```text\n(.*?)```',text,re.S)
    assert marker
    completed=subprocess.run([sys.executable,'-B',str(SCRIPT)],check=True,capture_output=True,text=True,timeout=60)
    assert completed.stdout==marker[1], 'Printed program output differs from the worked page'
    assert text.count(r'\[')==text.count(r'\]')
    assert text.count(r'\(')==text.count(r'\)')
    assert 'A000364' in text and 'A211212' in text

    tap_script=ROOT/'examples/euler_polyphase_taps.py'
    tap_spec=importlib.util.spec_from_file_location('euler_tap_split',tap_script)
    tap_module=importlib.util.module_from_spec(tap_spec)
    tap_spec.loader.exec_module(tap_module)
    tap_result=tap_module.compute()
    assert tap_result==json.loads((ROOT/'verification/euler-packets/polyphase-taps-002/results.json').read_bytes())
    tap_marker=re.search(r'<!-- euler-tap-expected-output -->\s*```text\n(.*?)```',text,re.S)
    assert tap_marker
    tap_cli=subprocess.run([sys.executable,'-B',str(tap_script)],check=True,capture_output=True,text=True,timeout=30)
    assert tap_cli.stdout==tap_marker[1], 'Printed tap-split output differs from the worked page'

    # A nonzero infinite vector has zero sampled output although square leading
    # blocks have nonzero diagonal. Check complete finite rows, not square cuts.
    for order in range(12):
        weights=example.transfer_row(2,0,order)
        values=[0]+[(-2)**j for j in range(1,len(weights))]
        assert sum(w*v for w,v in zip(weights,values))==0
        assert weights[order]==2**order
    index_values=example.reciprocal_recurrence(2,1,28)
    index_values=[example.as_integer((-1)**n*v) for n,v in enumerate(index_values)]
    index_cases=0
    for prime in (3,5,7):
        for degree in range(2,14,2):
            difference=index_values[(degree+prime*(prime-1))//2]-index_values[degree//2]
            assert difference % (prime*prime)==0
            index_cases+=1
    assert (index_values[3]-index_values[0]) % 3 != 0

    # A separate check of the packet elimination and displayed Schur coefficients.
    from math import factorial
    length=12
    c=[F(1,factorial(4*n)) for n in range(length)]
    d=[-F(1,factorial(4*n+2)) for n in range(length)]
    eliminated=example.mul(example.mul(d,example.inverse(c,length),length),d,length)
    effective=example.add(c,example.scale(example.shift(eliminated,1,length),-1),length)
    determinant=example.add(example.mul(c,c,length),example.scale(example.shift(example.mul(d,d,length),1,length),-1),length)
    assert effective[:3]==[F(1),-F(5,24),F(73,8064)]
    assert eliminated[:2]==[F(1,4),-F(13,1440)]
    assert example.mul(effective,c,length)==determinant
    a=example.inverse(effective,length)
    restored_b=example.scale(example.mul(example.mul(example.inverse(c,length),d,length),a,length),-1)
    scalar=example.reciprocal_recurrence(2,1,24)
    for n in range(length):
        assert a[n]*factorial(4*n)==scalar[2*n]
        assert restored_b[n]*factorial(4*n+2)==scalar[2*n+1]

    result=dict(status='PASS',python=platform.python_version(),script_sha256=digest(SCRIPT),
                manuscript_sha256=digest(PAGE),accepted_manifest_sha256=digest(RUN/'manifest.json'),
                finite_results_reproduced=True,displayed_cli_matches=True,
                schur_packet_coefficients=24,schur_displayed_coefficients=True,
                sampling_infinite_kernel_rows=12,
                euler_index_supercongruence_cases=index_cases,euler_zero_index_counterexample=True,
                library_comparison=check_library(example,math_root,git,fresh) if math_root else None,
                polyphase_taps=dict(signal_cases=tap_result['finite_checks']['signal_comparisons'],
                                    impulse_cases=tap_result['finite_checks']['impulse_comparisons'],
                                    displayed_cli_matches=True,missing_advance_control=tap_result['missing_advance']),
                scope='Executed finite calculations, displayed-output correspondence and source identities. Written proof self-review is separate.')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--math-root',type=Path)
    parser.add_argument('--git',default='git')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(args.math_root.resolve() if args.math_root else None,args.git)
    if args.output:
        if args.output.exists():
            raise FileExistsError('Choose a new result file')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'library_comparison'}},sort_keys=True))
    if result['library_comparison']:
        print(json.dumps({k:v for k,v in result['library_comparison'].items() if k!='imported_sources'},sort_keys=True))


if __name__=='__main__':
    main()
