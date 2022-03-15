import copy
from collections import Iterable

from pysmt.shortcuts import *
from pysmt import fnode
from pysmt.typing import STRING, INT, REAL

request_action_map = dict()
attribute_variable_map = dict()

exception_map = dict()

def _polymorph_args_to_tuple( args):
    """ Helper function to return a tuple of arguments from args.

    This function is used to allow N-ary operators to express their arguments
    both as a list of arguments or as a tuple of arguments: e.g.,
       And([a,b,c]) and And(a,b,c)
    are both valid, and they are converted into a tuple (a,b,c) """

    if len(args) == 1 and isinstance(args[0], Iterable):
        args = args[0]
    return list(tuple(args))

def _set_value(cur, name_tokens, value):
    if len(name_tokens) == 1:
        setattr(cur, name_tokens[0], value)
    else:
        new_cur = getattr(cur, name_tokens[0])
        _set_value(new_cur, name_tokens[1:], value)

def set_value(g, names, value):
    name_tokens = names.split('.')
    return _set_value(g, name_tokens, value)

def get_variables_by_type(type_name):
    return attribute_variable_map.get(type_name, set())

def add_variable_by_type(type_name, variable):
    target = get_variables_by_type(type_name)
    target.add(variable)
    attribute_variable_map[type_name] = target

def get_action_name(action_id):
    if action_id == 1:
        return "access"
    elif action_id == 2:
        return "disclose"

def union(*arg):
    args = _polymorph_args_to_tuple(arg)
    result = []
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, Action):
            result.append(arg)
        elif isinstance(arg, UnionAction):
            result += list(arg.actions)
        else:
            assert False

    return UnionAction(result)

class UnionAction():
    def __init__(self, args):
        self.actions = set(args)




class Action():
    presence_counter = 0
    sym_presence = Symbol("action_presence", typename=BOOL)

    def __init__(self):
        value = self.get_counter_update()
        self.presence = Symbol("action_presence_{}".format(value), typename=BOOL)
        self.card = Symbol("action_card_{}".format(value), typename=INT)
        self.cardinality_constraint = And(Iff(self.presence, Equals(self.card, Int(1))),
                                          Iff(Not(self.presence), Equals(self.card, Int(0))))
        self.sym_constraint = set()

    def get_counter_update(self):
        presence_counter = Action.presence_counter
        Action.presence_counter += 1
        return presence_counter

    def _comparsion(self, other, OP):

        if isinstance(other, Action):
            return OP(self.time, other.time)
        else:
            return OP(self.time, other)

    def __gt__(self, other):
        return self._comparsion(other, GT)

    def __ge__(self, other):
        return self._comparsion(other, GE)

    def __lt__(self, other):
        return self._comparsion(other, LT)

    def __le__(self, other):
        return self._comparsion(other, LE)



def create_type(type_name, type_dict = dict(), upper_bound=None, lower_bound=None, var_type=INT, enum = None):
    def num_constraint(var):
        if var_type == REAL:
            constructor = Real
        else:
            constructor = Int
        constraint = []
        if not upper_bound is None:
            constraint.append(LE(var, constructor(upper_bound)))
        if not lower_bound is None:
            constraint.append(GE(var, constructor(lower_bound)))
        return And(constraint)
    def string_constraint(var):
        if enum is None:
            return TRUE()
        else:
            constraint = []
            for item in enum:
                if isinstance(item, str):
                    item = String(item)
                constraint.append(Equals(var, item))
            return And(constraint)

    constraint = lambda var: TRUE()

    if var_type == INT or var_type == REAL:
        constraint = num_constraint
    elif var_type == STRING:
        constraint = string_constraint

    type_dict[type_name] = (var_type, constraint)
    return type_name

def get_value_from_node(model, node):
    if isinstance(node, fnode.FNode):
        return model.get_py_value(node)
    else:
        return  node

def get_or_create(model, key, map, key_type):
    v_map = map.get(key_type, None)
    if v_map is None:
        return key
    else:
        inv_map = {get_value_from_node(model, v): k for k, v in v_map.items()}
        value = inv_map.get(key, None)
        if value is None:
            value = key
            v_map[value] = key

    return value

def create_pair_action(action_name, attributes, constraint_dict):
    action_new_name = "Requested_"+action_name
    action_class = create_action(action_name, attributes, constraint_dict)
    request_class = create_action(action_new_name, attributes, constraint_dict)
    request_action_map[action_class] = request_class
    request_action_map[request_class] = action_class
    return request_class, action_class


def snap_shot(act_type):
    act_type.snap_shot = copy.copy(act_type.collect_list)


Delayed_Constraints = []
Timed_dict = {}
def get_timed_obj(time_var):
    if time_var in Timed_dict:
        return Timed_dict.get(time_var)
    assert False

def add_timed_obj(time_var, obj):
    if time_var in Timed_dict:
        Timed_dict[time_var][type(obj)] = obj
    else:
        new_set = {}
        new_set[type(obj)] = obj
        Timed_dict[time_var] = new_set

#sub_action = [("name", "type", "mapping")]
def create_action(action_name, attributes, constraint_dict, sub_actions = None, defines = None, inputs = None, abstraction=None):
    if inputs is not None:
        attributes = attributes + inputs
    index_map = dict([(att_name, 0) for att_name, attr_type in attributes])
    temp_index_map = dict([(att_name, 0) for att_name, attr_type in attributes])
    args_to_type = dict(attributes)
    attr_order = [attr_name for attr_name, _ in attributes]
    if sub_actions is None:
        sub_action_names = []
    else:
        sub_action_names = [sub_name for (sub_name, _, _) in sub_actions]

    def __init__(self, permanent=True, temp = False, input_subs = None):
        super(type(self), self).__init__()
        self.constraint = []
        self.delayed_constraint =[]
        if input_subs is None:
            input_subs  = {}
        '''
        if "time" in input_subs:
            value = input_subs.get("time")
            setattr(self, "time", value)
        '''

        if "presence" in input_subs:
            value = input_subs.get("presence")
            setattr(self, "presence", value)

        for attr, attr_type in attributes:
            var_type, type_constraint = constraint_dict.get(attr_type, lambda _: TRUE())
            if attr in input_subs:
                value = input_subs.get(attr)
                setattr(self, attr, value)
                self.constraint.append(type_constraint(getattr(self, attr)))
            else:
                if temp:
                    variable = Symbol("{}_{}_{}_temp".format(action_name, attr, self.get_index_update(attr, temp=True)), typename=var_type)
                    setattr(self, attr, variable)
                    self.constraint.append(type_constraint(getattr(self, attr)))

                else:
                    variable = Symbol("{}_{}_{}".format(action_name, attr, self.get_index_update(attr)), typename=var_type)
                    setattr(self, attr, variable)
                    self.constraint.append(type_constraint(getattr(self,attr)))

        if sub_actions is not None:
            for act_name, action_type, variable_mapping in sub_actions:
                # now set up the mapping
                sub_input_subs = {}
                sub_input_subs["time"] = self.time
                sub_input_subs["presence"] = self.presence
                sub_exception_subs = {}
                if variable_mapping is not None:
                    if type(variable_mapping) == type([]):
                        child_input = action_type.type_inputs
                        assert len(child_input) == len(variable_mapping)
                        for i in range(len(child_input)):
                            input_var = child_input[i][0]
                            value_func = variable_mapping[i]
                            try:
                                value = value_func(self)
                                sub_input_subs[input_var] = value
                                #setattr(sub_action_obj, input_var, value_func(self))
                            except AttributeError:
                                sub_exception_subs[input_var] = value_func
                    else:
                        for key, value_func in variable_mapping.items():
                            try:
                                sub_input_subs[key] =  value_func(self)
                                #setattr(sub_action_obj, key, value_func(self))
                            except AttributeError:
                                sub_exception_subs[key] = value_func

                sub_action_obj = action_type(temp=temp, input_subs=sub_input_subs)
                #sub_action_obj.time = self.time  # sync in time
                #sub_action_obj.presence = self.presence  # syn in presence
                #add the failed assignment as constraints
                for key, value_func in sub_exception_subs.items():
                    self.delayed_constraint.append(lambda key=key, current=sub_action_obj, parent =self, value_func = value_func :
                                                   Equals(getattr(current, key), value_func(parent)))
                setattr(self, act_name, sub_action_obj)

        if defines is not None:
            for name, value_func in defines:
                set_value(self, name, value_func(self))
                #setattr(self, name, value_func(self))

        if not temp:
            type(self).collect_list.append(self)
        else:
            type(self).temp_collection_set.add(self)

        self.constraint = Implies(self.presence, And(self.constraint))
        if hasattr(self, "time"):
            add_timed_obj(self.time, self)

    def make_permanent(self):
        if self in type(self).temp_collection_set:
            type(self).collect_list.append(self)
            type(self).temp_collection_set.remove(self)

        for child_action_name in type(self).sub_action_names:
            getattr(self, child_action_name).make_permanent()

    def sync_time(self):
        for child_action_name in type(self).sub_action_names:
            getattr(self,child_action_name).time = self.time
            getattr(self, child_action_name).sync_time()

    def get_index_update(self, key, temp= False):
        if temp:
            target_map = type(self).temp_index_map
        else:
            target_map = type(self).index_map
        if (key not in  target_map.keys()):
            print("strange update")
            return
        res = target_map.get(key, 0)
        target_map[key] = res + 1
        return res

    def sym_subs(self, other, context):
        subs_dict = dict([(getattr(self, attr), getattr(other, attr)) for attr, _ in attributes ] + [(self.presence, other.presence)])
        return substitute(context, subs_dict)

    def build_eq_constraint(self, other, consider_time = True, exceptions=None):
        if exceptions is None:
            exceptions = set()
        if not consider_time:
            exceptions.add("time")
        if type(self) != type(other):
            return FALSE()
        if self == other:
            return TRUE()
        else:
            constraint = []
            for key in type(self).index_map.keys():
                if key in exceptions:
                    continue
                constraint.append(EqualsOrIff(getattr(self, key), getattr(other, key)))
            constraint.append(EqualsOrIff(self.presence, other.presence))
            return And(constraint)

    def context_dependent_variable(self, conext):
        fb = get_free_variables(conext)
        dependent = []
        for attr, _ in attributes:
            if getattr(self, attr) in fb:
                dependent.append(getattr(self, attr))
        return dependent

    def get_all_variables(self):
        res = [ getattr(self, attr) for attr, _ in attributes]
        res.append(self.presence)
        return res


    def __repr__(self):
        pars = "({})".format(', '.join([str(getattr(self, attr)) for attr, _ in attributes if attr != "time"]))
        if hasattr(self, "time"):
            time_s = "@{time} {action_name}".format(time = self.time, action_name = action_name)
        else:
            time_s = ""
        return time_s+pars

    def print_with_context(self, context_map):
        interests = context_map.get(type(self), set())
        important_args = ["?{}:Nat".format(getattr(self, attr) ) for attr, _ in attributes if attr in interests]
        content = (' '.join(important_args)) if len(important_args) > 0 else  "..."
        pars = "{action_name} {content}".format(action_name = action_name.upper()   , content = content)
        #time_s = "@{time} {action_name}".format(time=self.time if self.time in context else "*", action_name=action_name)
        return pars

    def extract_mentioned_attributes(self, context):
        return  set([attr for attr, _ in attributes  if getattr(self, attr) in context])

    def get_record(self, model, debug=True):
        if debug:
            pars = "({})".format(', '.join(
                ["{}={}".format(str(getattr(self, attr)), str(model.get_py_value(getattr(self, attr)))) for attr, _ in attributes if
                 attr != "time"]))
            time_s = "@{time} {action_name} = {action_id} ".format(time=model.get_py_value(self.time), action_name=action_name, action_id = self.presence)
            return time_s + pars
        else:
            pars = "({})".format(', '.join(["{}={}".format(attr, str(model.get_py_value(getattr(self, attr)))) for attr, _ in attributes if attr != "time"]))
            time_s = "@{time} {action_name}".format(time=model.get_py_value(self.time), action_name=action_name)
            return time_s+pars

    def model_equal(self, model, other):
        if model.get_py_value(self.presence) != model.get_py_value(other.presence):
            return False
        for attr, _ in attributes:
            if model.get_py_value(getattr(self, attr)) != model.get_py_value(getattr(other, attr)):
                return False
        return True

    def get_model_record(self, model, translation_map,  is_readable=False, is_abstract= False):
        def map(var):
            if is_abstract and var.is_symbol():
                name ="{}_abstracted".format(var.symbol_name())
                exists =  get_env().formula_manager.symbols.get(name, None)
                if  exists  is None:
                    return  var
                else:
                    return exists
            else:
                return var


        divider = ' ' if is_readable else ' !IDS_OF '
        time_divider = " " if is_readable else ' !IDS_OF '
        pars = "{})".format(divider.join(["({}, {})".format(attr.upper(),
                                                                 str(get_or_create(model, model.get_py_value(map(getattr(self, attr))),
                                                                                   translation_map,
                                                                                   type(self).args_to_type.get(attr)))) for attr, _ in attributes if attr != "time"]))
        time_s = "{action_name}{div1}(TIME, {time}){div2}".format(div1 = time_divider, div2= divider, time=model.get_py_value(map(self.time)), action_name=action_name)
        return time_s+pars


    action_class = type(action_name, (Action,),{
        "action_name": action_name,
        "args_to_type": args_to_type,
        "index_map": index_map,
        "temp_index_map": temp_index_map,
        "sub_action_names": sub_action_names,
        "attr_order": attr_order,
        "type_inputs": inputs,
        "collect_list" : [],
        "temp_collection_set": set(),
        "syn_collect_list": [],
        "additional_constraint" : [],
        "snap_shot":[],
        "EQ_CLASS" : [set()],
        "Uncollected" : set(),
        "__init__": __init__,
        "get_index_update": get_index_update,
        "make_permanent": make_permanent,
        "sync_time":sync_time,
        "sym_subs": sym_subs,
        "context_dependent_variable": context_dependent_variable,
        "get_all_variables": get_all_variables,
        "__repr__": __repr__,
        "print_with_context": print_with_context,
        "extract_mentioned_attributes": extract_mentioned_attributes,
        "get_record": get_record,
        "get_model_record": get_model_record,
        "build_eq_constraint": build_eq_constraint,
        "model_equal":model_equal,
         "inv": []
    })
    return action_class

def get_varaible(var):
    if var.is_symbol():
        return Symbol("{}_abstracted".format(var.symbol_name()), INT)
    else:
        res = exception_map.get(var, None)
        if res is not None:
            return res
        else:
            abstracted_symbol= Symbol("{}_abstracted".format(len(exception_map.keys())), INT)
            exception_map[var] = abstracted_symbol
            return abstracted_symbol



