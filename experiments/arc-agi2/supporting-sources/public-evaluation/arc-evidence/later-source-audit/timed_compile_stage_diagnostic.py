"""Instrument one separate frozen compile call; never write scan checkpoints."""
import datetime
import faulthandler
import json
import resource
import sys
import time
from pathlib import Path

WORKSPACE = Path('/workspace/scratch/40dd7e475149')
SOURCE = WORKSPACE / 'arc-fullbank/block17'
EVIDENCE = WORKSPACE / 'arc-evidence/later-source-audit'
TASK_ID = '3e6067c3'
sys.path.insert(0, str(SOURCE))
import engine


def main():
    challenges = engine.read(WORKSPACE / 'arc-offline-data/arc-agi_evaluation_challenges.json')
    task = engine.sanitize(challenges[TASK_ID])
    assert all(set(test) == {'input'} for test in task['test'])
    report = {
        'task_id_for_external_diagnostic_only': TASK_ID,
        'task_id_passed_to_compiler': False,
        'task_semantic_hash': engine.contract.digest(task),
        'code_hash': engine.code_hash(),
        'bank_hash': engine.bank_hash(),
        'compile_call': 'engine.compile_record(sanitized_task, include_new=True)',
        'instrumentation': 'faulthandler.dump_traceback_later(60, repeat=True, exit=False)',
        'separate_compile_process': True,
        'main_worker_or_checkpoint_changes': False,
        'query_solutions_opened': False,
        'extra_temporary_cpu_use': True,
        'attribution_limit': 'This new diagnostic call does not establish the current stack of any original live scan worker.',
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    report_path = EVIDENCE / 'timed_compile_stage_diagnostic_report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    started = time.monotonic()
    cpu_started = time.process_time()
    exit_code = 0
    with (EVIDENCE / 'timed_compile_stage_diagnostic_stacks.log').open('w') as stack_log:
        faulthandler.dump_traceback_later(60, repeat=True, file=stack_log, exit=False)
        try:
            record = engine.compile_record(task, include_new=True)
            engine.verify(record)
            report.update(outcome='completed', diagnostic_record_hash=record['content_hash'],
                          diagnostic_candidate_count=len(record['candidates']),
                          diagnostic_receipt_count=len(record['receipts']),
                          record_admitted_to_main_census=False,
                          record_payload_written=False)
        except KeyboardInterrupt:
            report.update(outcome='interrupted_by_owned_session_ctrl_c',
                          diagnostic_record_hash=None, record_admitted_to_main_census=False)
            exit_code = 130
        except BaseException as error:
            report.update(outcome='diagnostic_exception', exception_type=type(error).__name__,
                          exception_message=str(error), record_admitted_to_main_census=False)
            exit_code = 1
        finally:
            faulthandler.cancel_dump_traceback_later()
            report.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          wall_seconds=time.monotonic() - started,
                          own_process_cpu_seconds=time.process_time() - cpu_started,
                          own_process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report_path': str(report_path), 'outcome': report['outcome'],
                      'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
