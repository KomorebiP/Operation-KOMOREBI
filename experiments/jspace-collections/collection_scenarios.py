"""Authored collection programs for checking the machinery. Komorebi P."""
import numpy as np
from machinery import Value,Store
from scenarios import registry as previous_registry,node,grid_case,scalar_case


def registry():
    r=previous_registry()
    r.define('keep_large',{'item':'object','minimum':'index'},{'nodes':[
        node('area','object.area',item='item'),node('keep','index.at_least',a='area',b='minimum')
    ],'outputs':{'result':'keep'}})
    return r


def collection_case():
    scene=np.zeros((7,10),int)
    scene[1,1]=scene[1,2]=scene[2,1]=2
    scene[4,4]=scene[4,5]=4;scene[1,5]=8
    inputs={'scene':Value('grid',scene),'background':Value('color',0),'connectivity':Value('index',4),
            'minimum':Value('index',2),'offset':Value('point',[0,0]),'overwrite':Value('flag',False)}
    program={'nodes':[
        node('objects','grid.components',scene='scene',background='background',connectivity='connectivity'),
        {'id':'areas','map':{'op':'object.area','items':'objects','bindings':{}}},
        {'id':'selected','filter':{'op':'keep_large','items':'objects','bindings':{'minimum':'minimum'}}},
        {'id':'shifted','map':{'op':'object.translate','items':'selected','bindings':{'offset':'offset'}}},
        {'id':'cleared','fold':{'op':'object.erase','items':'selected','state':'scene','bindings':{'background':'background'}}},
        {'id':'placed','fold':{'op':'object.paint','items':'shifted','state':'cleared','bindings':{'background':'background','overwrite':'overwrite'}}},
        node('selected_count','objects.count',items='selected'),
        node('changed','grid.changed',a='scene',b='placed'),node('change_count','mask.count',mask='changed')
    ],'outputs':{'result':'placed','original':'scene','objects':'objects','areas':'areas','selected_count':'selected_count','changed_cells':'change_count'}}
    expected=scene.copy();expected[1,1]=expected[1,2]=expected[2,1]=expected[4,4]=expected[4,5]=0
    expected[1,3]=expected[1,4]=expected[2,3]=2;expected[4,6]=expected[4,7]=4
    return program,inputs,expected


def make_bank():
    bank=Store(registry());p,v,_=grid_case();assert bank.create('grid',p,v)['status']=='committed'
    p,v=scalar_case();assert bank.create('scalar',p,v)['status']=='committed'
    p,v,_=collection_case();assert bank.create('objects',p,v)['status']=='committed'
    return bank


def proposal(bank,offset=(0,2),require_match=True):
    return {'action':'propose','workspace':'objects','expected_revision':bank.branches['objects'],
            'updates':{'offset':Value('point',list(offset)).pack()},'locked_outputs':['original'],
            'targets':{'result':Value('grid',collection_case()[2]).pack()},'require_target_match':require_match}
