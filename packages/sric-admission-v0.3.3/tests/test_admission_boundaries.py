from dataclasses import replace
from pathlib import Path
import json
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.audit import run_causal_audit
from sric_real_lrm.dataset import deterministic_calibration_audit_split
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.pipeline import run_block24_pipeline
from sric_real_lrm.schemas import AuditConfig
from sric_real_lrm.sealing import verify_seal
from sric_real_lrm.hashing import sha256_object
from sric_real_lrm.validation import AdapterValidationError, fingerprint_kind, validated_adapter


class CorruptAdapter(FakeProcedureLatentAdapter):
    def __init__(self, *, field='answer_logits', value=None, task_id=None, arm='capture'):
        super().__init__();self.field=field;self.value=value;self.task_id=task_id;self.arm=arm
    def corrupt(self, task, obs):
        if self.task_id is None or task.task_id==self.task_id:
            return replace(obs,**{self.field:self.value})
        return obs
    def capture(self, task):
        obs=super().capture(task)
        return self.corrupt(task,obs) if self.arm=='capture' else obs
    def score_with_trace(self, task, trace):
        obs=super().score_with_trace(task,trace)
        return self.corrupt(task,obs) if self.arm=='score' else obs


class FingerprintAdapter(FakeProcedureLatentAdapter):
    def __init__(self, fingerprint): super().__init__();self.fingerprint=fingerprint
    def model_fingerprint(self): return self.fingerprint


def real_metadata():
    # Schema/control fixture only. These are deliberately not model receipts.
    return {'adapter':'IdentitySchemaFixture','external_repository':'test/repo','checkpoint_repo':'test/weights',
            'checkpoint_filename':'fixture','base_model':'fixture','external_commit':'a'*40,
            'checkpoint_revision':'b'*40,'base_model_revision':'c'*40,'source_verification_sha256':'d'*64,
            'checkpoint_sha256':'e'*64,'base_model_tree_sha256':'f'*64,'num_latents':6,
            'engineered_positive_control':False,'evidence_kind':'real_checkpoint'}


class AdmissionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full=AuditConfig.load(ROOT/'configs/fake_fixture.json')
        cls.fast=replace(cls.full,bootstrap_replicates=4,semantic_escalation=False,truncation=False,run_mode_controls=False)
        cls.records=make_fixture_records(48)
        cls.split=deterministic_calibration_audit_split(cls.records,seed=cls.fast.seed,calibration_fraction=cls.fast.causal_calibration_fraction)

    def test_original_full_fixture_remains_synthetic(self):
        result=run_block24_pipeline(FakeProcedureLatentAdapter(),self.records,self.full)
        self.assertEqual(result['overall_status'],'CAUSALLY_VALIDATED')
        self.assertFalse(result['claim_boundary']['real_checkpoint_evidence'])
        self.assertEqual(result['semantic_escalation']['selected']['rank'],3)
        json.dumps(result,allow_nan=False)

    def test_empty_logits_rejected_in_capture_and_score(self):
        for arm in ['capture','score']:
            with self.subTest(arm=arm),self.assertRaises(AdapterValidationError):
                run_block24_pipeline(CorruptAdapter(value=np.array([]),arm=arm),self.records,self.fast)

    def test_nan_rejected_at_every_calibration_and_audit_position(self):
        for support in ['calibration','audit']:
            for task in self.split[support]:
                with self.subTest(support=support,task=task.task_id),self.assertRaises(AdapterValidationError):
                    run_block24_pipeline(CorruptAdapter(value=np.array([np.nan,0.0]),task_id=task.task_id),self.records,self.fast)

    def test_nonfinite_scored_logits_and_losses_rejected(self):
        for field,values in [('answer_logits',[np.array([np.nan,0.0]),np.array([np.inf,0.0]),np.array([-np.inf,0.0])]),('answer_loss',[np.nan,np.inf,-np.inf])]:
            for value in values:
                with self.subTest(field=field,value=str(value)),self.assertRaises(AdapterValidationError):
                    run_block24_pipeline(CorruptAdapter(field=field,value=value,arm='score'),self.records,self.fast)

    def test_bad_clean_loss_and_trace_rejected(self):
        for field,value in [('answer_loss',np.nan),('trace',np.zeros((0,32))),('trace',np.full((6,32),np.nan)),('trace',np.zeros((5,32)))]:
            with self.subTest(field=field,shape=np.shape(value)),self.assertRaises(AdapterValidationError):
                run_block24_pipeline(CorruptAdapter(field=field,value=value),self.records,self.fast)

    def test_finite_replay_mismatch_still_rejected(self):
        result=run_block24_pipeline(CorruptAdapter(value=np.array([1000.0,0.0]),task_id=self.split['audit'][1].task_id),self.records,self.fast)
        self.assertEqual(result['overall_status'],'ADAPTER_INVALID')
        self.assertEqual(result['semantic_escalation']['status'],'SEMANTIC_ESCALATION_NOT_ADMISSIBLE')

    def test_standalone_causal_api_cannot_bypass_observation_checks(self):
        with self.assertRaises(AdapterValidationError):
            run_causal_audit(CorruptAdapter(value=np.array([])),self.records,self.fast)

    def test_missing_or_unknown_identity_rejected_before_model_execution(self):
        for fp in [{},{'adapter':'unknown','num_latents':6},{'adapter':'unknown','num_latents':6,'engineered_positive_control':False},
                   {'adapter':'unknown','num_latents':6,'engineered_positive_control':'true'}]:
            adapter=FingerprintAdapter(fp)
            with self.subTest(fp=fp),patch.object(adapter,'capture',side_effect=AssertionError('should not execute')):
                with self.assertRaises(AdapterValidationError):run_block24_pipeline(adapter,self.records,self.fast)

    def test_real_identity_requires_matching_precommitted_record(self):
        fp=real_metadata()
        for expected in [None,{},dict(fp,checkpoint_sha256='0'*64)]:
            with self.subTest(expected=expected),self.assertRaises(AdapterValidationError):fingerprint_kind(fp,expected,6)
        self.assertEqual(fingerprint_kind(fp,dict(fp),6),'real_checkpoint')

    def test_missing_or_invalid_real_digest_rejected(self):
        for key in ['checkpoint_sha256','base_model_tree_sha256','source_verification_sha256','external_commit']:
            for value in [None,'','bad']:
                fp=dict(real_metadata(),**{key:value})
                with self.subTest(key=key,value=value),self.assertRaises(AdapterValidationError):fingerprint_kind(fp,fp,6)

    def test_conflicting_provenance_and_boolean_step_count_rejected(self):
        for fp in [dict(real_metadata(),engineered_positive_control=True),dict(real_metadata(),num_latents=True)]:
            with self.subTest(fp=fp),self.assertRaises(AdapterValidationError):fingerprint_kind(fp,fp,6)

    def test_identity_change_before_capture_rejected(self):
        adapter=FakeProcedureLatentAdapter();wrapped=validated_adapter(adapter,self.fast)
        adapter.seed+=1
        with self.assertRaises(AdapterValidationError):wrapped.capture(self.records[0])

    def test_identity_change_during_capture_rejected(self):
        adapter=FakeProcedureLatentAdapter();wrapped=validated_adapter(adapter,self.fast)
        original=adapter.capture
        def changed(task):
            observation=original(task);adapter.seed+=1;return observation
        with patch.object(adapter,'capture',side_effect=changed),self.assertRaises(AdapterValidationError):
            wrapped.capture(self.records[0])

    def test_mode_control_observations_are_validated(self):
        adapter=FakeProcedureLatentAdapter();wrapped=validated_adapter(adapter,self.fast)
        bad=replace(adapter.capture(self.records[0]),answer_logits=np.array([]))
        for method in ['capture_mode','generate_mode']:
            with self.subTest(method=method),patch.object(adapter,method,return_value=bad),self.assertRaises(AdapterValidationError):
                getattr(wrapped,method)(self.records[0],'direct')

    def test_cli_fixture_seal_run_and_receipt(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            tmp=Path(tmp);data=tmp/'tasks.json';seal=tmp/'seal.json';result=tmp/'result.json'
            commands=[['make-fixture','--output',str(data),'--count','48'],
                      ['stage-fake','--data',str(data),'--output',str(seal)],
                      ['run-fake','--data',str(data),'--seal',str(seal),'--output',str(result)],
                      ['verify-result',str(result)]]
            for command in commands:
                completed=subprocess.run([sys.executable,'-B','-m','sric_real_lrm',*command],cwd=ROOT,capture_output=True,text=True,timeout=20)
                self.assertEqual(completed.returncode,0,completed.stderr)
            payload=json.loads(result.read_text())
            self.assertEqual(payload['overall_status'],'CAUSALLY_VALIDATED')
            self.assertFalse(payload['claim_boundary']['real_checkpoint_evidence'])
            self.assertFalse(payload['execution_boundary']['real_checkpoint_used'])
            prior=json.loads(seal.read_text());prior.pop('runtime_edition')
            prior['seal_sha256']=sha256_object({k:v for k,v in prior.items() if k!='seal_sha256'})
            with self.assertRaisesRegex(ValueError,'fresh seal'):verify_seal(prior)


if __name__=='__main__':unittest.main(verbosity=2)
