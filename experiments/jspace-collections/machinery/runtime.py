"""Pure named operations, reusable functions, lazy choices, bounded loops. Komorebi P."""
from dataclasses import dataclass
import copy
from .values import Value, Fault, KINDS, BASE_KINDS, element_kind, digest


def named(name):
    return isinstance(name, str) and name and len(name) <= 100 and '/' not in name


@dataclass
class Operation:
    name: str
    parameters: dict
    output: str
    origin: str
    identity: str
    function: object = None
    body: dict | None = None


class Registry:
    def __init__(self): self.operations = {}

    def native(self, name, parameters, output, function, identity, origin='supplied'):
        if name in self.operations: raise Fault('registry', f'Operation already registered: {name}')
        if not named(name) or output not in KINDS or not all(named(k) and v in KINDS for k,v in parameters.items()):
            raise Fault('type', 'Invalid operation signature.')
        self.operations[name] = Operation(name, dict(parameters), output, origin, identity, function=function)

    def get(self, name):
        if not isinstance(name,str) or name not in self.operations: raise Fault('unknown_operation', f'Unknown operation: {name}')
        return self.operations[name]

    def define(self, name, parameters, body, origin='authored_function'):
        # Earlier definitions only: recursive and unresolved functions are rejected.
        body = copy.deepcopy(body)
        program = Program(body, parameters, self)
        if set(program.outputs) != {'result'}: raise Fault('signature', 'Reusable functions expose one result.')
        output = program.types[program.outputs['result']]
        dependencies = {op: self.get(op).identity for op in program.operations}
        identity = digest({'body':body, 'parameters':parameters, 'dependencies':dependencies})
        self.native(name, parameters, output, None, identity, origin)
        self.operations[name].body = body

    def definitions(self):
        return copy.deepcopy([{'name':op.name, 'parameters':op.parameters, 'body':op.body, 'origin':op.origin}
                for op in self.operations.values() if op.body is not None])

    def manifest(self):
        return copy.deepcopy({name:{'parameters':op.parameters,'output':op.output,'origin':op.origin,'identity':op.identity}
                for name,op in sorted(self.operations.items())})


class Program:
    def __init__(self, specification, inputs, registry):
        if not isinstance(specification, dict) or set(specification) != {'nodes','outputs'}:
            raise Fault('schema', 'A program has nodes and named outputs.')
        if not inputs or not all(named(k) and v in KINDS for k,v in inputs.items()):
            raise Fault('type', 'Invalid input signature.')
        if not isinstance(specification['nodes'], list) or len(specification['nodes']) > 256:
            raise Fault('budget', 'A graph permits at most 256 nodes.')
        self.nodes = {}; self.outputs = specification['outputs']; self.operations = set()
        self.types = dict(inputs); self.dependencies = {}
        if not isinstance(self.outputs, dict) or not self.outputs or not all(named(k) for k in self.outputs):
            raise Fault('schema', 'At least one named output is required.')
        for node in specification['nodes']:
            if not isinstance(node, dict) or not named(node.get('id')): raise Fault('schema', 'Node requires an id.')
            name = node['id']
            if name in self.nodes or name in inputs: raise Fault('binding', f'Duplicate binding: {name}')
            self.nodes[name] = node
        visiting = set()

        def infer(name):
            if not isinstance(name, str): raise Fault('binding', 'Bindings refer to named values.')
            if name in self.types: return self.types[name]
            if name not in self.nodes: raise Fault('binding', f'Missing binding: {name}')
            if name in visiting: raise Fault('cycle', f'Cyclic dependency involving {name}')
            visiting.add(name); node = self.nodes[name]
            if set(node) == {'id','op','args'}:
                op = registry.get(node['op']); self.operations.add(op.name)
                args = node['args']
                if not isinstance(args, dict) or set(args) != set(op.parameters):
                    raise Fault('binding', f'{name} needs named arguments {list(op.parameters)}')
                for key, ref in args.items():
                    if infer(ref) != op.parameters[key]: raise Fault('type', f'{name}.{key} expects {op.parameters[key]}')
                kind = op.output; deps = list(args.values())
            elif set(node) == {'id','select'}:
                spec = node['select']
                if not isinstance(spec,dict) or set(spec) != {'condition','then','else'}: raise Fault('schema','Invalid choice.')
                if infer(spec['condition']) != 'flag': raise Fault('type','A choice requires a Boolean condition.')
                kind = infer(spec['then'])
                if kind != infer(spec['else']): raise Fault('type','Both choice branches must have the same type.')
                deps = list(spec.values())
            elif set(node) == {'id','repeat'}:
                spec = node['repeat']
                if not isinstance(spec,dict) or set(spec) != {'op','state','count','bindings'}: raise Fault('schema','Invalid repeat.')
                op = registry.get(spec['op']); self.operations.add(op.name)
                if 'state' not in op.parameters or op.parameters['state'] != op.output:
                    raise Fault('type','Repeated operation must preserve the state type.')
                if infer(spec['state']) != op.output or infer(spec['count']) != 'index':
                    raise Fault('type','Repeat needs matching state and an integer count.')
                if not isinstance(spec['bindings'],dict) or set(spec['bindings']) != set(op.parameters)-{'state'}:
                    raise Fault('binding','Invalid repeat arguments.')
                for key,ref in spec['bindings'].items():
                    if infer(ref) != op.parameters[key]: raise Fault('type',f'Repeat argument {key} has the wrong type.')
                kind = op.output; deps = [spec['state'],spec['count'],*spec['bindings'].values()]
            elif len(node)==2 and set(node)-{'id'} in ({'map'},{'filter'},{'fold'}):
                mode=next(k for k in node if k!='id'); spec=node[mode]
                fields={'op','items','bindings'} | ({'state'} if mode=='fold' else set())
                if not isinstance(spec,dict) or set(spec)!=fields: raise Fault('schema',f'Invalid {mode} node.')
                item_type=element_kind(infer(spec['items']))
                if item_type is None: raise Fault('type',f'{mode} requires a typed collection.')
                op=registry.get(spec['op']);self.operations.add(op.name)
                if op.parameters.get('item')!=item_type: raise Fault('type','Collection item argument has the wrong type.')
                reserved={'item'}
                if mode=='fold':
                    reserved.add('state');kind=infer(spec['state'])
                    if op.parameters.get('state')!=kind or op.output!=kind: raise Fault('type','Fold must preserve its accumulator type.')
                elif mode=='filter':
                    if op.output!='flag': raise Fault('type','A filter predicate must return a flag.')
                    kind='list['+item_type+']'
                else:
                    if op.output not in BASE_KINDS: raise Fault('type','Nested collections are not supported.')
                    kind='list['+op.output+']'
                if not isinstance(spec['bindings'],dict) or set(spec['bindings'])!=set(op.parameters)-reserved:
                    raise Fault('binding',f'Invalid {mode} bindings.')
                for key,ref in spec['bindings'].items():
                    if infer(ref)!=op.parameters[key]:raise Fault('type',f'{mode} argument {key} has the wrong type.')
                deps=[spec['items'],*spec['bindings'].values()]+([spec['state']] if mode=='fold' else [])
            else: raise Fault('schema', f'Invalid node form: {name}')
            self.types[name] = kind; self.dependencies[name] = deps; visiting.remove(name)
            return kind

        for name in self.nodes: infer(name)
        for ref in self.outputs.values(): infer(ref)


class Runner:
    def __init__(self, registry, max_steps=2048, max_repeat=64, max_depth=16):
        self.registry = registry; self.max_steps = max_steps
        self.max_repeat = max_repeat; self.max_depth = max_depth
        self.cache = {}

    def run(self, specification, inputs):
        self.trace = []; self.values = {}; self.steps = 0; self.location = 'root'
        self.cache_hits = 0; self.native_executions = 0
        identity = digest(self.registry.manifest())
        try:
            result = self._graph(specification, inputs, 'root', 0)
            status = {'status':'ok','outputs':{k:v.pack() for k,v in result.items()}}
        except Fault as exc:
            status = {'status':'failed','error':{'code':exc.code,'message':str(exc),'location':self.location},'outputs':{}}
        return {**status, 'trace':copy.deepcopy(self.trace), 'values':{k:v.pack() for k,v in self.values.items()},
                'steps':self.steps,'native_executions':self.native_executions,'cache_hits':self.cache_hits,
                'registry_identity':identity}

    def _tick(self, path):
        self.location = path; self.steps += 1
        if self.steps > self.max_steps: raise Fault('budget','Execution step limit exceeded.')

    def _call(self, name, arguments, path, depth):
        self._tick(path)
        if depth > self.max_depth: raise Fault('budget','Function nesting limit exceeded.')
        op = self.registry.get(name)
        if set(arguments) != set(op.parameters) or any(arguments[k].kind != kind for k,kind in op.parameters.items()):
            raise Fault('type', f'Invalid arguments for {name}')
        cached = False
        if op.body is not None:
            value = self._graph(op.body, arguments, path, depth+1)['result']
        else:
            key = digest({'operation':op.identity,'name':name,'args':{k:v.pack() for k,v in arguments.items()}})
            if key in self.cache:
                value = self.cache[key]; cached = True; self.cache_hits += 1
            else:
                self.native_executions += 1
                try: value = op.function(**arguments)
                except Fault: raise
                except (ValueError, TypeError, IndexError, OverflowError) as exc:
                    raise Fault('operation', f'{name}: {exc}') from exc
                if not isinstance(value, Value) or value.kind != op.output: raise Fault('type','Invalid operation result.')
                self.cache[key] = value
        self.trace.append({'path':path,'event':'call','operation':name,'origin':op.origin,
                           'operation_identity':op.identity,'arguments':{k:v.pack() for k,v in arguments.items()},
                           'result':value.pack(),'cached':cached})
        return value

    def _graph(self, specification, inputs, prefix, depth):
        program = Program(specification, {k:v.kind for k,v in inputs.items()}, self.registry)
        available = dict(inputs)
        for k,v in inputs.items(): self.values[prefix+'/'+k] = v

        def resolve(name):
            if name in available: return available[name]
            node = program.nodes[name]; path = prefix+'/'+name; self._tick(path)
            if 'op' in node:
                arguments = {k:resolve(ref) for k,ref in node['args'].items()}
                value = self._call(node['op'], arguments, path, depth)
            elif 'select' in node:
                s = node['select']; condition = resolve(s['condition']).data
                chosen = s['then'] if condition else s['else']; skipped = s['else'] if condition else s['then']
                self.trace.append({'path':path,'event':'select','condition':condition,'chosen':chosen,'skipped':skipped})
                value = resolve(chosen)
            elif 'repeat' in node:
                s = node['repeat']; count = resolve(s['count']).data
                if not 0 <= count <= self.max_repeat: raise Fault('budget',f'Repeat count must be 0..{self.max_repeat}.')
                value = resolve(s['state'])
                bindings = {k:resolve(ref) for k,ref in s['bindings'].items()} if count else {}
                for i in range(count):
                    value = self._call(s['op'], {'state':value,**bindings},path+f'/step_{i}',depth+1)
                    self.values[path+f'/step_{i}'] = value
                self.trace.append({'path':path,'event':'repeat','iterations':count})
            else:
                mode=next(k for k in node if k!='id');spec=node[mode];items=resolve(spec['items'])
                value=resolve(spec['state']) if mode=='fold' else None
                bindings={k:resolve(ref) for k,ref in spec['bindings'].items()} if items.data else {}
                outputs=[];decisions=[]
                for i,item in enumerate(items.data):
                    args={'item':item,**bindings}
                    if mode=='fold':args['state']=value
                    observed=self._call(spec['op'],args,path+f'/item_{i}',depth+1)
                    self.values[path+f'/item_{i}']=observed
                    if mode=='fold':value=observed
                    elif mode=='map':outputs.append(observed)
                    else:
                        decisions.append(observed.data)
                        if observed.data:outputs.append(item)
                if mode!='fold':value=Value(program.types[name],outputs)
                record={'path':path,'event':mode,'items':len(items.data)}
                if mode=='filter':record.update(kept=len(outputs),decisions=decisions)
                self.trace.append(record)
            available[name] = value; self.values[path] = value
            return value

        return {k:resolve(ref) for k,ref in program.outputs.items()}
