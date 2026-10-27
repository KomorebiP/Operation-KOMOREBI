"""Admission boundaries for the corrected runtime; not model attestation."""
from __future__ import annotations

from copy import deepcopy
from numbers import Real
from typing import Any, Mapping
import json
import re
import numpy as np

from .adapters.base import LatentReasonerAdapter
from .schemas import AuditConfig, TraceObservation


class AdapterValidationError(ValueError):
    """Adapter evidence is inadmissible; no acceptance result may be emitted."""


def finite_array(value: Any, name: str) -> np.ndarray:
    try:
        array = np.asarray(value)
        if array.dtype.kind not in 'iuf' or array.ndim == 0 or not array.size:
            raise AdapterValidationError(f'{name} must be a nonempty real numeric array')
        if not np.all(np.isfinite(array)):
            raise AdapterValidationError(f'{name} contains non-finite values')
        converted = np.asarray(array, dtype=np.float64)
        if not np.all(np.isfinite(converted)):
            raise AdapterValidationError(f'{name} cannot be represented as finite float64 values')
        return converted
    except (TypeError, OverflowError) as exc:
        raise AdapterValidationError(f'{name} is not a valid numeric array') from exc


def check_observation(observation: TraceObservation, *, num_latents: int, latent: bool) -> TraceObservation:
    loss = observation.answer_loss
    if isinstance(loss, (bool, np.bool_)) or not isinstance(loss, Real) or not np.isfinite(loss):
        raise AdapterValidationError('Answer loss must be a finite real scalar')
    finite_array(observation.answer_logits, 'answer logits')
    if latent:
        trace = finite_array(observation.trace, 'latent trace')
        if trace.ndim != 2 or trace.shape[0] != num_latents:
            raise AdapterValidationError('Latent trace shape does not match the configured step count')
    return observation


REAL_TEXT_FIELDS = ('adapter', 'external_repository', 'checkpoint_repo', 'checkpoint_filename', 'base_model')
REAL_HEX_FIELDS = {'external_commit': 40, 'checkpoint_revision': 40, 'base_model_revision': 40,
                   'source_verification_sha256': 64, 'checkpoint_sha256': 64, 'base_model_tree_sha256': 64}


def fingerprint_kind(fingerprint: Mapping[str, Any], expected: Mapping[str, Any] | None, num_latents: int) -> str:
    """Require explicit provenance; a matching record is not independent attestation."""
    if not isinstance(fingerprint, Mapping) or not fingerprint:
        raise AdapterValidationError('Missing adapter fingerprint')
    if not isinstance(fingerprint.get('adapter'), str) or not fingerprint['adapter'].strip():
        raise AdapterValidationError('Missing adapter identity')
    if type(fingerprint.get('num_latents')) is not int or fingerprint['num_latents'] != num_latents:
        raise AdapterValidationError('Fingerprint latent-step count differs from the configuration')
    marker = fingerprint.get('engineered_positive_control')
    if marker is True:
        if fingerprint.get('evidence_kind', 'engineered_fixture') != 'engineered_fixture':
            raise AdapterValidationError('Contradictory engineered/real provenance')
        return 'engineered_fixture'
    if marker is not False or fingerprint.get('evidence_kind') != 'real_checkpoint':
        raise AdapterValidationError('Unknown provenance: real-checkpoint evidence must be explicit')
    for field in REAL_TEXT_FIELDS:
        if not isinstance(fingerprint.get(field), str) or not fingerprint[field].strip():
            raise AdapterValidationError(f'Missing real-model identity field: {field}')
    for field, size in REAL_HEX_FIELDS.items():
        value = fingerprint.get(field)
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{'+str(size)+'}', value) is None:
            raise AdapterValidationError(f'Missing or invalid pinned digest: {field}')
    if not isinstance(expected, Mapping):
        raise AdapterValidationError('Real-model admission requires a precommitted expected fingerprint')
    for field in (*REAL_TEXT_FIELDS, *REAL_HEX_FIELDS, 'num_latents', 'engineered_positive_control', 'evidence_kind'):
        if field not in expected or type(expected[field]) is not type(fingerprint[field]) or expected[field] != fingerprint[field]:
            raise AdapterValidationError(f'Fingerprint differs from the precommitted record: {field}')
    return 'real_checkpoint'


class ValidatedAdapter(LatentReasonerAdapter):
    def __init__(self, wrapped: LatentReasonerAdapter, config: AuditConfig, expected_fingerprint=None):
        config.validate()
        self.wrapped = wrapped
        self.num_latents = config.num_latents
        try:
            self._fingerprint = deepcopy(dict(wrapped.model_fingerprint()))
        except (TypeError, ValueError) as exc:
            raise AdapterValidationError('Adapter fingerprint must be a mapping') from exc
        self.evidence_kind = fingerprint_kind(self._fingerprint, expected_fingerprint, self.num_latents)
        # Freeze the serialized identity too, rejecting non-JSON or NaN metadata.
        try:
            self._identity = json.dumps(self._fingerprint, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError) as exc:
            raise AdapterValidationError('Fingerprint must contain finite JSON metadata') from exc

    def _check_identity(self):
        try:
            current = json.dumps(dict(self.wrapped.model_fingerprint()), sort_keys=True, allow_nan=False)
        except (ValueError, TypeError) as exc:
            raise AdapterValidationError('Adapter identity became invalid') from exc
        if current != self._identity:
            raise AdapterValidationError('Adapter identity changed during execution')

    def _observe(self, call, *args, latent=True):
        self._check_identity()
        observation = call(*args)
        self._check_identity()
        return check_observation(observation, num_latents=self.num_latents, latent=latent)

    def capture(self, task):
        return self._observe(self.wrapped.capture, task)

    def score_with_trace(self, task, trace):
        array = finite_array(trace, 'supplied trace')
        if array.ndim != 2 or array.shape[0] != self.num_latents:
            raise AdapterValidationError('Supplied trace has the wrong shape')
        observation = self._observe(self.wrapped.score_with_trace, task, trace)
        if np.shape(observation.trace) != array.shape:
            raise AdapterValidationError('Scored trace shape differs from supplied trace')
        return observation

    def supports_mode(self, mode):
        return self.wrapped.supports_mode(mode)

    def capture_mode(self, task, mode):
        return self._observe(self.wrapped.capture_mode, task, mode, latent=(mode == 'latent'))

    def generate_mode(self, task, mode):
        return self._observe(self.wrapped.generate_mode, task, mode, latent=(mode == 'latent'))

    def model_fingerprint(self):
        self._check_identity()
        return deepcopy(self._fingerprint)

    def close(self):
        self.wrapped.close()


def validated_adapter(adapter, config, *, expected_fingerprint=None):
    if isinstance(adapter, ValidatedAdapter):
        if adapter.num_latents != config.num_latents:
            raise AdapterValidationError('Validated adapter configuration changed')
        if expected_fingerprint is not None:
            fingerprint_kind(adapter.model_fingerprint(), expected_fingerprint, config.num_latents)
        return adapter
    return ValidatedAdapter(adapter, config, expected_fingerprint)
