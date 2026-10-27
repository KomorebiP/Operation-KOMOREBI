"""Preserve existing arithmetic evidence across the final I04 label revision.

This performs source/data/hash checks only. It does not rerun the arithmetic
witnesses or change their original manifest, logs, or numerical results.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
E = ROOT/'evidence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prior_script = E/'layout_refresh_i04/verified_prior_script.py'
    prior_audit_path = E/'layout_refresh_i04/verified_prior_audit.json'
    current_script = ROOT/'figures_i_iii.py'
    current_audit_path = E/'figures_i_iii_audit.json'
    audit = json.loads(current_audit_path.read_text())
    before = json.loads(prior_audit_path.read_text())
    revision = audit['label_only_updates'][-1]
    assert revision['figure']=='I04_exponential_system'
    stripped = dict(audit)
    stripped.pop('label_only_updates')
    stripped['figures']['I04_exponential_system']['pdf_sha256'] = revision['previous_pdf_sha256']
    assert stripped == before
    mathematical_old = dict(before['figures']['I04_exponential_system'])
    mathematical_new = dict(audit['figures']['I04_exponential_system'])
    mathematical_old.pop('pdf_sha256');mathematical_new.pop('pdf_sha256')
    assert mathematical_old == mathematical_new
    assert sha(ROOT/'figures/I04_exponential_system.pdf') == revision['new_pdf_sha256']
    assert audit['figures']['I04_exponential_system']['pdf_sha256'] == revision['new_pdf_sha256']

    # Undo only the standalone-render extraction and the two presentation
    # strings, then require byte equality with the previously pinned source.
    source = current_script.read_text()
    match = re.search(r'\ndef figure_I04\(\):\n    """[^\n]+"""\n(.*?)\ndef figures_I\(\):',source,re.S)
    assert match
    body = match.group(1).rstrip('\n')
    for new,old in zip(revision['new_titles'],revision['old_titles']):
        assert new in body
        body = body.replace(new,old)
    normalized = source[:match.start()]+'\n'+source[match.end()-len('\ndef figures_I():'):]
    assert normalized.count('    figure_I04()\n')==1
    normalized = normalized.replace('    figure_I04()\n',body+'\n',1)
    variants = (normalized,normalized.replace('\n\ndef figures_I():','\ndef figures_I():',1))
    assert prior_script.read_text() in variants
    # The isolated block's private numerical locals are not consumed later.
    later = source[source.index('    figure_I04()\n')+len('    figure_I04()\n'):source.index('\ndef figures_II():')]
    for name in ('sections','derivatives','lhs','rhs','tails','uu'):
        assert not re.search(r'\b'+name+r'\b',later),name

    base_path = E/'independent_arithmetic_final_snapshot/manifest.json'
    base = json.loads(base_path.read_text())
    assert base['run']['exit_status']==0
    original_results = E/'independent_arithmetic_final_snapshot/results.json'
    expected_outputs = {item['path']:item['sha256'] for item in base['outputs']}
    assert sha(original_results)==expected_outputs[str(original_results.relative_to(ROOT))]
    for item in base['input_artifacts']:
        if item['path']=='evidence/figures_i_iii_audit.json':
            assert sha(prior_audit_path)==item['sha256_after']
        else:
            assert sha(ROOT/item['path'])==item['sha256_after'],item['path']
    assert json.loads(original_results.read_text())['all_passed']
    result={'all_passed':True,'role':'provenance-only preservation; no arithmetic recomputation',
        'base_computation_manifest':str(base_path.relative_to(ROOT)),
        'base_computation_manifest_sha256':sha(base_path),
        'base_computation_results':str(original_results.relative_to(ROOT)),
        'base_computation_results_sha256':sha(original_results),
        'actual_computation_script_and_chapter_unchanged':True,
        'all_36_arithmetic_audit_entries_and_checks_preserved':True,
        'source_normalizes_exactly_to_prior_script':True,
        'I04_mathematical_facts':mathematical_new,
        'presentation_changes':{'old_titles':revision['old_titles'],'new_titles':revision['new_titles'],
            'standalone_render_function_extracted':True,
            'previous_pdf_sha256':revision['previous_pdf_sha256'],'new_pdf_sha256':revision['new_pdf_sha256']},
        'arithmetic_witnesses_rerun':False,'unrelated_computations_rerun':False}
    target=E/'independent_arithmetic_presentation_refresh/results.json'
    target.parent.mkdir(exist_ok=True,parents=True)
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all_passed':True,'arithmetic_recomputed':False}))


if __name__=='__main__':
    main()
