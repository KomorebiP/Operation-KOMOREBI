import unittest
import numpy as np

from streaming_skat import (
    orthonormalize_covariates,
    full_factor,
    stream_sample_gram,
    stream_kernel_action,
    stream_A_times_V,
    stream_AT_times_U,
    stream_dual_action,
    tiled_sample_gram,
)


class StreamingSKATTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(123)
        cls.n=96; cls.m=311; cls.s=5
        maf=rng.uniform(.005,.25,cls.m)
        cls.G=rng.binomial(2,maf[None,:],size=(cls.n,cls.m)).astype(float)
        cls.w=(1-maf)**24
        X=np.column_stack([np.ones(cls.n),rng.normal(size=cls.n),rng.normal(size=cls.n)])
        cls.Q=orthonormalize_covariates(X)
        cls.A=full_factor(cls.G,cls.w,cls.Q)
        cls.K=cls.A@cls.A.T
        cls.rng=rng

    def test_stream_gram(self):
        K2=stream_sample_gram(self.G,self.w,self.Q,variant_block=37)
        self.assertLess(np.linalg.norm(K2-self.K)/np.linalg.norm(self.K),1e-12)

    def test_kernel_action(self):
        V=self.rng.normal(size=(self.n,self.s))
        got=stream_kernel_action(self.G,self.w,self.Q,V,variant_block=41)
        ref=self.K@V
        self.assertLess(np.linalg.norm(got-ref)/np.linalg.norm(ref),1e-12)

    def test_A_action(self):
        V=self.rng.normal(size=(self.m,self.s))
        got=stream_A_times_V(self.G,self.w,self.Q,V,variant_block=43)
        ref=self.A@V
        self.assertLess(np.linalg.norm(got-ref)/np.linalg.norm(ref),1e-12)

    def test_AT_action(self):
        U=self.rng.normal(size=(self.n,self.s))
        got=stream_AT_times_U(self.G,self.w,self.Q,U,variant_block=47)
        ref=self.A.T@U
        self.assertLess(np.linalg.norm(got-ref)/np.linalg.norm(ref),1e-12)

    def test_dual_action(self):
        V=self.rng.normal(size=(self.m,self.s))
        got=stream_dual_action(self.G,self.w,self.Q,V,variant_block=53)
        ref=self.A.T@(self.A@V)
        self.assertLess(np.linalg.norm(got-ref)/np.linalg.norm(ref),1e-12)

    def test_tiled_gram(self):
        got=tiled_sample_gram(
            self.G,self.w,self.Q,
            variant_block=61,
            sample_tile=23,
        )
        self.assertLess(np.linalg.norm(got-self.K)/np.linalg.norm(self.K),1e-12)


if __name__=="__main__":
    unittest.main(verbosity=2)
