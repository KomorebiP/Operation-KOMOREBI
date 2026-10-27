"""Authored machinery demonstrations, not learned solvers. Komorebi P."""
import numpy as np
from machinery import Value, Store
from machinery.operations import base_registry


def node(name,operation,**bindings): return {'id':name,'op':operation,'args':bindings}


def registry():
    r = base_registry()
    parameters = {'scene':'grid','source_color':'color','target_color':'color','zero':'color','turns':'index','transparent':'flag'}
    r.define('copy_pattern',parameters,{'nodes':[
        node('source_mask','grid.color_mask',scene='scene',color='source_color'),
        node('source_box','mask.bounds',mask='source_mask'),
        node('patch','grid.crop',scene='scene',region='source_box'),
        node('turned','grid.rotate',patch='patch',turns='turns'),
        node('target_mask','grid.color_mask',scene='scene',color='target_color'),
        node('destination','mask.origin',mask='target_mask'),
        node('cleared','grid.paint',scene='scene',mask='target_mask',color='zero'),
        node('placed','grid.paste',scene='cleared',patch='turned',at='destination',transparent='transparent')
    ],'outputs':{'result':'placed'}})
    r.define('advance',{'state':'scalar','delta':'scalar'},{'nodes':[
        node('next','learned.channel_91',a='state',b='delta')
    ],'outputs':{'result':'next'}})
    return r


def grid_case():
    scene = np.zeros((7,10),dtype=int)
    scene[1,1] = scene[2,1] = scene[2,2] = 2
    scene[3,6] = 3; scene[0,9] = 8
    inputs = {'scene':Value('grid',scene),'source_color':Value('color',2),'target_color':Value('color',3),
              'zero':Value('color',0),'turns':Value('index',1),'transparent':Value('flag',True),'enabled':Value('flag',True)}
    program = {'nodes':[
        node('copy','copy_pattern',**{k:k for k in inputs if k!='enabled'}),
        {'id':'chosen','select':{'condition':'enabled','then':'copy','else':'scene'}},
        node('changed','grid.changed',a='scene',b='chosen'),
        node('change_count','mask.count',mask='changed')
    ],'outputs':{'result':'chosen','original':'scene','changed_mask':'changed','changed_cells':'change_count'}}
    expected = scene.copy(); expected[3,6] = 0
    expected[3,7] = expected[4,6] = expected[4,7] = 2
    return program,inputs,expected


def scalar_case():
    inputs = {'a':Value('scalar',-3.),'b':Value('scalar',2.),'start':Value('scalar',1.),
              'delta':Value('scalar',.25),'count':Value('index',4)}
    program = {'nodes':[
        node('product','learned.channel_42',a='a',b='b'),
        node('a_is_greater','number.greater',a='a',b='b'),
        {'id':'maximum','select':{'condition':'a_is_greater','then':'a','else':'b'}},
        {'id':'rollout','repeat':{'op':'advance','state':'start','count':'count','bindings':{'delta':'delta'}}}
    ],'outputs':{'product':'product','maximum':'maximum','accumulated':'rollout'}}
    return program,inputs


def make_bank():
    bank = Store(registry())
    program,inputs,_ = grid_case(); assert bank.create('grid',program,inputs)['status']=='committed'
    program,inputs = scalar_case(); assert bank.create('scalar',program,inputs)['status']=='committed'
    return bank
