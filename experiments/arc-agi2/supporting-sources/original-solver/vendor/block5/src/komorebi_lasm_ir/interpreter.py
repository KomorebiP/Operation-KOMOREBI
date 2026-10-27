"""Resource-bounded interpreter for LASM Program IR v2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, Sequence

import numpy as np

from .nodes import (
    AllNode, AnyNode, ArgExtremeNode, CallNode, CartesianMapNode, CaseNode,
    CountNode, Expression, FilterNode, FoldNode, HoleNode, IfNode, InputNode,
    LetNode, LiteralNode, MapNode, PackNode, RenderNode, RepeatUntilStableNode,
    SelectNode, SortNode, TileNode, VariableNode,
)
from .program import Program, StaticLimits
from .registry import OperatorRegistry


class ExecutionError(RuntimeError):
    pass


class ExecutionLimitError(ExecutionError):
    pass


class AmbiguityError(ExecutionError):
    pass


class NonConvergenceError(ExecutionError):
    pass


@dataclass(frozen=True)
class ExecutionLimits:
    maximum_evaluations: int = 50_000
    maximum_operator_cost: int = 50_000
    maximum_collection_items: int = 2_048
    maximum_fixed_point_steps: int = 900
    maximum_grid_cells: int = 3_600

    def __post_init__(self) -> None:
        for name,value in self.__dict__.items():
            if isinstance(value,bool) or int(value)<=0:
                raise ValueError(f"{name} must be a positive integer")


@dataclass
class ExecutionTrace:
    evaluations: int = 0
    operator_cost: int = 0
    operator_calls: dict[str,int] = field(default_factory=dict)
    fixed_point_iterations: int = 0
    collection_visits: int = 0
    branch_decisions: list[str] = field(default_factory=list)

    def to_record(self) -> dict[str,object]:
        return {
            "evaluations":self.evaluations,
            "operator_cost":self.operator_cost,
            "operator_calls":dict(sorted(self.operator_calls.items())),
            "fixed_point_iterations":self.fixed_point_iterations,
            "collection_visits":self.collection_visits,
            "branch_decisions":list(self.branch_decisions),
        }


class RuntimeAdapter(Protocol):
    def collection(self,value:object)->tuple[object,...]: ...
    def equal(self,left:object,right:object)->bool: ...
    def monotone_leq(self,left:object,right:object)->bool: ...
    def order_key(self,value:object)->object: ...
    def render(self,canvas:object,items:object,color:object|None,mode:str)->object: ...
    def pack(self,items:object,background:object,axis:str,gap:int,normalize:bool)->object: ...
    def tile(self,tile:object,rows:int,columns:int)->object: ...
    def validate_result(self,value:object,limits:ExecutionLimits)->object: ...


class DefaultRuntimeAdapter:
    def collection(self,value:object)->tuple[object,...]:
        if isinstance(value,tuple):return value
        if isinstance(value,list):return tuple(value)
        raise TypeError(f"runtime value {type(value)!r} is not a collection")

    def equal(self,left:object,right:object)->bool:
        if isinstance(left,np.ndarray) or isinstance(right,np.ndarray):
            return bool(np.array_equal(np.asarray(left),np.asarray(right)))
        return left==right

    def monotone_leq(self,left:object,right:object)->bool:
        if isinstance(left,np.ndarray) or isinstance(right,np.ndarray):
            a,b=np.asarray(left),np.asarray(right)
            return a.shape==b.shape and bool(np.all(np.logical_or(~a.astype(bool),b.astype(bool))))
        if isinstance(left,(tuple,list)) and isinstance(right,(tuple,list)):
            return set(left).issubset(set(right))
        return left==right

    def order_key(self,value:object)->object:
        if isinstance(value,np.generic):return value.item()
        return value

    def render(self,canvas:object,items:object,color:object|None,mode:str)->object:
        raise TypeError("the default runtime has no render semantics")

    def pack(self,items:object,background:object,axis:str,gap:int,normalize:bool)->object:
        raise TypeError("the default runtime has no pack semantics")

    def tile(self,tile:object,rows:int,columns:int)->object:
        a=np.asarray(tile)
        if a.ndim!=2:raise TypeError("tile input must be a two-dimensional grid")
        return np.tile(a,(rows,columns))

    def validate_result(self,value:object,limits:ExecutionLimits)->object:
        if isinstance(value,np.ndarray) and value.ndim==2 and value.size>limits.maximum_grid_cells:
            raise ExecutionLimitError("grid cell budget exceeded")
        return value


@dataclass(frozen=True)
class ExecutionResult:
    value: object
    trace: ExecutionTrace


class Interpreter:
    def __init__(self,registry:OperatorRegistry,*,adapter:RuntimeAdapter|None=None,limits:ExecutionLimits=ExecutionLimits()) -> None:
        self.registry=registry
        self.adapter=adapter or DefaultRuntimeAdapter()
        self.limits=limits

    def _tick(self,trace:ExecutionTrace,amount:int=1)->None:
        trace.evaluations+=amount
        if trace.evaluations>self.limits.maximum_evaluations:
            raise ExecutionLimitError("evaluation budget exceeded")

    def _visit_collection(self,trace:ExecutionTrace,size:int)->None:
        trace.collection_visits+=size
        if size>self.limits.maximum_collection_items or trace.collection_visits>self.limits.maximum_evaluations:
            raise ExecutionLimitError("collection visit budget exceeded")

    def _eval(self,node:Expression,inputs:Mapping[str,object],env:Mapping[str,object],trace:ExecutionTrace)->object:
        self._tick(trace)
        if isinstance(node,InputNode):
            try:return inputs[node.name]
            except KeyError as error:raise ExecutionError(f"missing runtime input {node.name!r}") from error
        if isinstance(node,LiteralNode):return node.value
        if isinstance(node,VariableNode):
            try:return env[node.name]
            except KeyError as error:raise ExecutionError(f"unbound runtime variable {node.name!r}") from error
        if isinstance(node,HoleNode):raise ExecutionError(f"cannot execute unfilled hole {node.name!r}")
        if isinstance(node,LetNode):
            value=self._eval(node.value,inputs,env,trace)
            nested=dict(env);nested[node.name]=value
            return self._eval(node.body,inputs,nested,trace)
        if isinstance(node,CallNode):
            definition=self.registry.resolve(node.operator)
            args=[self._eval(arg,inputs,env,trace) for arg in node.arguments]
            trace.operator_cost+=int(definition.cost)
            if trace.operator_cost>self.limits.maximum_operator_cost:raise ExecutionLimitError("operator cost budget exceeded")
            trace.operator_calls[node.operator]=trace.operator_calls.get(node.operator,0)+1
            return self.adapter.validate_result(definition.function(*args),self.limits)
        if isinstance(node,IfNode):
            predicate=bool(self._eval(node.predicate,inputs,env,trace))
            trace.branch_decisions.append("if:true" if predicate else "if:false")
            return self._eval(node.when_true if predicate else node.when_false,inputs,env,trace)
        if isinstance(node,CaseNode):
            for index,branch in enumerate(node.branches):
                if bool(self._eval(branch.predicate,inputs,env,trace)):
                    trace.branch_decisions.append(f"case:{index}")
                    return self._eval(branch.result,inputs,env,trace)
            trace.branch_decisions.append("case:default")
            return self._eval(node.default,inputs,env,trace)
        if isinstance(node,MapNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            out=[]
            for value in values:
                nested=dict(env);nested[node.variable]=value
                out.append(self._eval(node.body,inputs,nested,trace))
            return tuple(out)
        if isinstance(node,FilterNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            out=[]
            for value in values:
                nested=dict(env);nested[node.variable]=value
                if bool(self._eval(node.predicate,inputs,nested,trace)):out.append(value)
            return tuple(out)
        if isinstance(node,SelectNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            winners=[]
            for value in values:
                nested=dict(env);nested[node.variable]=value
                if bool(self._eval(node.predicate,inputs,nested,trace)):winners.append(value)
            if not winners:raise AmbiguityError("select has no matching candidate")
            if node.require_unique and len(winners)!=1:raise AmbiguityError("select is ambiguous")
            return winners[0]
        if isinstance(node,AnyNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            for value in values:
                nested=dict(env);nested[node.variable]=value
                if bool(self._eval(node.predicate,inputs,nested,trace)):return True
            return False
        if isinstance(node,AllNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            for value in values:
                nested=dict(env);nested[node.variable]=value
                if not bool(self._eval(node.predicate,inputs,nested,trace)):return False
            return True
        if isinstance(node,CountNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            if node.predicate is None:return len(values)
            assert node.variable is not None
            count=0
            for value in values:
                nested=dict(env);nested[node.variable]=value
                count+=int(bool(self._eval(node.predicate,inputs,nested,trace)))
            return count
        if isinstance(node,FoldNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            accumulator=self._eval(node.initial,inputs,env,trace)
            for value in values:
                nested=dict(env);nested[node.item_variable]=value;nested[node.accumulator_variable]=accumulator
                accumulator=self._eval(node.body,inputs,nested,trace)
            return accumulator
        if isinstance(node,CartesianMapNode):
            left=self.adapter.collection(self._eval(node.left,inputs,env,trace))
            right=self.adapter.collection(self._eval(node.right,inputs,env,trace))
            self._visit_collection(trace,len(left)+len(right)+len(left)*len(right))
            output=[]
            for left_value in left:
                for right_value in right:
                    nested=dict(env);nested[node.left_variable]=left_value;nested[node.right_variable]=right_value
                    output.append(self._eval(node.body,inputs,nested,trace))
            return tuple(output)
        if isinstance(node,ArgExtremeNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            if not values:raise AmbiguityError("arg-extreme selector has no candidates")
            keyed=[]
            for value in values:
                nested=dict(env);nested[node.variable]=value
                keyed.append((self.adapter.order_key(self._eval(node.key,inputs,nested,trace)),value))
            extreme=(min if node.order=="minimum" else max)(key for key,_ in keyed)
            winners=[value for key,value in keyed if key==extreme]
            if node.require_unique and len(winners)!=1:raise AmbiguityError("arg-extreme selector is tied")
            return winners[0]
        if isinstance(node,SortNode):
            values=self.adapter.collection(self._eval(node.collection,inputs,env,trace));self._visit_collection(trace,len(values))
            keyed=[]
            for index,value in enumerate(values):
                nested=dict(env);nested[node.variable]=value
                key=self.adapter.order_key(self._eval(node.key,inputs,nested,trace))
                keyed.append((key,index,value))
            keyed.sort(key=lambda item:(item[0],item[1]),reverse=node.descending)
            return tuple(item[2] for item in keyed)
        if isinstance(node,RepeatUntilStableNode):
            if node.maximum_steps>self.limits.maximum_fixed_point_steps:raise ExecutionLimitError("fixed-point budget exceeds runtime limit")
            state=self._eval(node.seed,inputs,env,trace)
            for _ in range(node.maximum_steps):
                nested=dict(env);nested[node.state_variable]=state
                updated=self._eval(node.body,inputs,nested,trace)
                trace.fixed_point_iterations+=1
                if node.monotone and not self.adapter.monotone_leq(state,updated):raise ExecutionError("declared monotone fixed point regressed")
                if self.adapter.equal(state,updated):return state
                state=updated
            raise NonConvergenceError("fixed-point program did not stabilize within its declared budget")
        if isinstance(node,RenderNode):
            canvas=self._eval(node.canvas,inputs,env,trace);items=self._eval(node.items,inputs,env,trace)
            color=None if node.color is None else self._eval(node.color,inputs,env,trace)
            return self.adapter.validate_result(self.adapter.render(canvas,items,color,node.mode),self.limits)
        if isinstance(node,PackNode):
            items=self._eval(node.items,inputs,env,trace);background=self._eval(node.background,inputs,env,trace)
            return self.adapter.validate_result(self.adapter.pack(items,background,node.axis,node.gap,node.normalize),self.limits)
        if isinstance(node,TileNode):
            tile=self._eval(node.tile,inputs,env,trace);rows=int(self._eval(node.rows,inputs,env,trace));columns=int(self._eval(node.columns,inputs,env,trace))
            if rows<=0 or columns<=0:raise ExecutionError("tile counts must be positive")
            return self.adapter.validate_result(self.adapter.tile(tile,rows,columns),self.limits)
        raise ExecutionError(f"unsupported expression node {type(node)!r}")

    def execute(self,program:Program,inputs:Mapping[str,object],*,allow_holes:bool=False)->ExecutionResult:
        program.validate(self.registry,allow_holes=allow_holes,limits=StaticLimits(maximum_fixed_point_steps=self.limits.maximum_fixed_point_steps))
        expected={item.name for item in program.inputs}
        if set(inputs)!=expected:raise ExecutionError(f"runtime inputs do not match program signature: expected={sorted(expected)}, got={sorted(inputs)}")
        trace=ExecutionTrace()
        value=self._eval(program.root,inputs,{},trace)
        return ExecutionResult(self.adapter.validate_result(value,self.limits),trace)


__all__=[
    "AmbiguityError","DefaultRuntimeAdapter","ExecutionError","ExecutionLimitError",
    "ExecutionLimits","ExecutionResult","ExecutionTrace","Interpreter",
    "NonConvergenceError","RuntimeAdapter",
]
