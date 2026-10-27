import json
from pathlib import Path

import numpy as np
import pytest

from komorebi_pr_lasm import (
    analyze_signal, PolyphaseFIR, StreamingFIR, polyphase_analyze, polyphase_synthesize,
    save_signal_archive, load_signal_archive,
)


@pytest.mark.parametrize('length',[1,2,3,7,16,31,64,257,1024])
@pytest.mark.parametrize('modulus',[1,2,3,4,7])
def test_1d_exact_reconstruction_without_padding(length,modulus):
    x=np.random.default_rng(length).normal(size=length)
    analysis=analyze_signal(x,modulus=modulus)
    assert analysis.length==length
    assert max(analysis.reconstruction_residuals().values())<1e-12
    assert np.array_equal(polyphase_synthesize(polyphase_analyze(x,modulus),length,modulus),x)


@pytest.mark.parametrize('modulus',[1,2,3,4,7])
@pytest.mark.parametrize('tap_length',[1,2,3,8,15])
def test_fir_transfer_blocks_match_direct_full_convolution(modulus,tap_length):
    rng=np.random.default_rng(modulus*100+tap_length)
    taps=rng.normal(size=tap_length);bank=PolyphaseFIR(taps,modulus)
    for r in range(modulus):
        for s in range(modulus):
            for m in range(bank.blocks.shape[2]):
                k=modulus*m+r-s
                assert bank.blocks[r,s,m]==(taps[k] if 0<=k<tap_length else 0.)
    for length in [1,3,16,79]:
        x=rng.normal(size=length)
        assert np.allclose(bank.apply(x),np.convolve(x,taps),atol=5e-13,rtol=5e-13)


def test_fir_composition_preserves_order_and_full_tail():
    x=np.arange(15.)
    a=PolyphaseFIR([1,2,-1],3);b=PolyphaseFIR([.5,-.25],3)
    assert np.allclose(a.compose(b).apply(x),a.apply(b.apply(x)),atol=1e-12)
    with pytest.raises(ValueError): a.compose(PolyphaseFIR([1],2))


@pytest.mark.parametrize('tap_length',[1,2,7,25])
def test_streaming_chunk_boundaries_and_reset(tap_length):
    rng=np.random.default_rng(tap_length);x=rng.normal(size=87);h=rng.normal(size=tap_length)
    expected=np.convolve(x,h)
    for cuts in [[0,87],[0,1,2,3,4,87],[0,7,18,21,66,87]]:
        stream=StreamingFIR(h)
        assert stream.process([]).size==0
        parts=[stream.process(x[a:b]) for a,b in zip(cuts,cuts[1:])]
        parts.append(stream.flush())
        assert np.allclose(np.concatenate(parts),expected,rtol=1e-13,atol=1e-13)
        assert stream.flush().size==0
        with pytest.raises(ValueError):stream.process([1])
        stream.reset()
        assert np.allclose(np.concatenate([stream.process(x),stream.flush()]),expected,atol=1e-13)


def test_streaming_is_causal_not_future_leaking():
    h=[1,-2,1];a=StreamingFIR(h);b=StreamingFIR(h)
    prefix=np.arange(30.)
    assert np.array_equal(a.process(prefix),b.process(prefix))
    assert not np.array_equal(a.process(np.zeros(5)),b.process(np.ones(5)))


def test_empty_stream_has_no_tail():
    s=StreamingFIR([1,2]);assert s.flush().size==0


@pytest.mark.parametrize('value',[[],[np.nan],[np.inf],[1j],[[1,2]]])
def test_signal_runtime_invalid_inputs_rejected(value):
    with pytest.raises(ValueError):analyze_signal(value)
    with pytest.raises(ValueError):PolyphaseFIR(value)


def test_signal_archive_roundtrip_and_corruption_detection(tmp_path):
    x=np.random.default_rng(3).normal(size=60)
    a=analyze_signal(x,modulus=7,maximum_depth=4)
    path=save_signal_archive(a,tmp_path/'coordinates.npz')
    b=load_signal_archive(path)
    assert b.modulus==7 and b.effective_depth==2
    assert np.array_equal(a.spatial,b.spatial)
    assert np.array_equal(a.fourier,b.fourier)
    with np.load(path,allow_pickle=False) as stored:
        metadata=stored['metadata'].copy();signal=stored['signal'].copy()
    signal[0]+=1
    np.savez_compressed(path,signal=signal,metadata=metadata)
    with pytest.raises(ValueError,match='checksum'):load_signal_archive(path)


def test_archive_rejects_extra_entries_objects_unknown_schema_and_limits(tmp_path):
    path=tmp_path/'bad.npz'
    np.savez(path,signal=np.arange(4.),metadata=np.array('{}'),extra=np.ones(1))
    with pytest.raises(ValueError):load_signal_archive(path)
    np.savez(path,signal=np.array([object()],dtype=object),metadata=np.array('{}'))
    with pytest.raises(ValueError):load_signal_archive(path)
    a=analyze_signal(np.arange(32.));save_signal_archive(a,path)
    with pytest.raises(ValueError,match='limit'):load_signal_archive(path,maximum_bytes=2)
    with np.load(path,allow_pickle=False) as stored:
        m=json.loads(str(stored['metadata']));signal=stored['signal'].copy()
    m['schema_version']=999
    np.savez(path,signal=signal,metadata=np.asarray(json.dumps(m)))
    with pytest.raises(ValueError,match='schema'):load_signal_archive(path)
