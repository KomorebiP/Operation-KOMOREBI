import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from primitive_environment import CHANNELS,dataset,higher_targets
from primitive_model import Kernels,Catalog
from executor import Executor
from primitive_workspace import PrimitiveWorkspace
from geometry import BehaviorGeometry
from workspace import Workspace

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x,cls.y=dataset(503,256);v,t=dataset(504,128)
        cls.kernels=Kernels(CHANNELS,activation='square');cls.kernels.refit_readout(cls.x,cls.y)
        cls.catalog=Catalog.validate(cls.kernels,v,t);cls.executor=Executor(cls.catalog)
        cls.core=Workspace.load('baseline/model_0.npz')
        cls.geometry=BehaviorGeometry.from_dict(json.loads(Path('baseline/geometry_0.json').read_text()))
        # Adapter inferred from valid paired-output examples, not a new result.
        rng=np.random.default_rng(891);a=rng.normal(size=(64,2));b=np.stack([a[:,0],a[:,0]-a[:,1],a[:,0]+a[:,1]],axis=1)
        cls.adapter=np.linalg.lstsq(a,b,rcond=None)[0].T

    def test_gradients(self):
        for activation in ['tanh','square']:
            m=Kernels(CHANNELS,seed=81,activation=activation)
            _,grad=m.loss_grad(self.x[:11],self.y[:,:11])
            for name,index in [('W',(1,0,3)),('b',(1,4)),('v',(1,2)),('skip',(1,0)),('c',(1,))]:
                old=m.p[name][index];eps=1e-6
                m.p[name][index]=old+eps;a=m.loss_grad(self.x[:11],self.y[:,:11])[0]
                m.p[name][index]=old-eps;b=m.loss_grad(self.x[:11],self.y[:,:11])[0]
                m.p[name][index]=old
                self.assertAlmostEqual((a-b)/(2*eps),grad[name][index],places=7)

    def test_validation_rejects_outside_activation_family(self):
        self.assertEqual(self.catalog.accepted,CHANNELS[:3])
        self.assertGreater(self.catalog.receipt['heldout_max_errors'][CHANNELS[3]],.05)

    def test_no_named_product_opcode(self):
        with self.assertRaises(ValueError):self.executor.evaluate(['mul','x','z'],self.x)
        with self.assertRaises(ValueError):self.executor.evaluate(['square','x'],self.x)

    def test_unvalidated_operation_cannot_execute(self):
        with self.assertRaises(ValueError):self.executor.evaluate(['call',CHANNELS[3],'x','z'],self.x)

    def test_operand_order(self):
        forward=self.executor.evaluate(['call',CHANNELS[0],'x','z'],self.x)
        reverse=self.executor.evaluate(['call',CHANNELS[0],'z','x'],self.x)
        np.testing.assert_allclose(forward,-reverse,atol=1e-10)
        self.assertGreater(float(np.max(abs(forward-reverse))),1.)

    def test_composition_from_neural_calls(self):
        xy=self.x[:16];target=higher_targets(xy)[0]
        r=self.executor.discover(xy,target,max_calls=2)
        self.assertEqual(r['status'],'fitted')
        np.testing.assert_allclose(self.executor.evaluate(r['expression'],self.x),higher_targets(self.x)[0],atol=1e-8)

    def test_readout_uses_observations(self):
        rng=np.random.default_rng(5);m=Kernels(CHANNELS,activation='square')
        shuffled=self.y[:,rng.permutation(len(self.x))];m.refit_readout(self.x,shuffled)
        v,t=dataset(774,256);c=Catalog.validate(m,v,t)
        self.assertEqual(c.accepted,[])

    def test_kernel_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'m.npz';self.kernels.save(p);m=Kernels.load(p)
            self.assertEqual(m.identity(),self.kernels.identity())
            np.testing.assert_array_equal(m.predict(self.x),self.kernels.predict(self.x))

    def test_workspace_growth_and_edit(self):
        b=PrimitiveWorkspace(self.core,self.geometry,self.executor,self.adapter)
        b.add('old',np.random.default_rng(97).normal(size=24));old=b.state('old');outputs=b.read('old',self.x).copy()
        expr=['call',CHANNELS[1],'x',['call',CHANNELS[1],'x','x']]
        target=2*self.x[:,0]+higher_targets(self.x)[0]
        self.assertEqual(b.install('new',expr,self.x,target)['status'],'committed')
        b.fork('new','trial');before=b.read('trial',self.x);b.edit_amplitude('trial',.5)
        expected=.5*higher_targets(self.x)[0]
        np.testing.assert_allclose(b.read('trial',self.x)-before,np.broadcast_to(expected,before.shape),atol=1e-8)
        self.assertTrue(b.undo('trial'));np.testing.assert_array_equal(b.read('trial',self.x),before)
        self.assertEqual(b.state('old'),old);np.testing.assert_array_equal(b.read('old',self.x),outputs)

    def test_saved_workspace_rejects_changed_primitive_meaning(self):
        b=PrimitiveWorkspace(self.core,self.geometry,self.executor,self.adapter);b.add('A',np.zeros(24))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bank.json';b.save(p)
            loaded=PrimitiveWorkspace.load(p,self.core,self.geometry,self.executor)
            self.assertEqual(loaded.to_dict(),b.to_dict())
            m=copy.deepcopy(self.kernels);m.p['v'][1,0]+=.01
            altered=Executor(Catalog(m,self.catalog.accepted,{'status':'controlled_mutation'}))
            with self.assertRaises(ValueError):PrimitiveWorkspace.load(p,self.core,self.geometry,altered)

if __name__=='__main__':unittest.main()
