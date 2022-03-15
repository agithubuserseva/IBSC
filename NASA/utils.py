

import sys
sys.path.append('../Analyzer')
from type_constructor import add_timed_obj, get_timed_obj
from logic_operator import *

def DIFFERENT_FROM(args, head=None):
    if head == None:
        head = args[0]
    if args == []:
        return TRUE()
    else:
        return AND([NotEquals(head, ele) for ele in args if ele != head])

def ALL_DIFFERENT(args):
    if args == []:
        return TRUE()
    else:
        head = args[0]
        rest = args[1:]
        return AND(DIFFERENT_FROM(rest, head), ALL_DIFFERENT(rest))

#a dictionary used to keep track of next element
next_dict = {}
prev_dict = {}
def is_next(g1, g2):
    return EQ(g1.time + Int(1), g2.time)

def previous(g, func):
    prev_obj = prev_dict.get(g, None)
    circuit = exist(type(g), lambda g2: AND(is_next(g2, g), func(g2)))
    if prev_obj is None:
        sub_input_subs = {}
        sub_input_subs["time"] = (g.time - Int(1))
        prev_obj = type(g)(temp = True, input_subs = sub_input_subs)
        #prev_obj.time = g.time - Int(1)
        #prev_obj.sync_time()
        prev_dict[g] = prev_obj
        next_dict[prev_obj] = g
    else:
        if prev_obj in type(g).collect_list:
            circuit.act_include = prev_obj

    circuit.act_non_include = prev_obj
    return circuit

def next(g, func):
    next_obj = next_dict.get(g, None)
    circuit = exist(type(g), lambda g2: AND(is_next(g, g2), func(g2)))
    if next_obj is None:
        sub_input_subs = {}
        sub_input_subs["time"] = (g.time + Int(1))
        next_obj = type(g)(temp = True, input_subs =sub_input_subs)
        #next_obj.time = (g.time + Int(1))
        #next_obj.sync_time()
        next_dict[g] = next_obj
        prev_dict[next_obj] = g
    else:
        if next_obj in type(g).collect_list:
            circuit.act_include = next_obj
    circuit.act_non_include = next_obj
    return circuit

def define_next(g, name, value_func, default_value):
    return OR(EQ(getattr(g, name), default_value), next(g, value_func))

def init(g):
    return EQ(g.time, Int(0))

def assign_init_rule(func):
    return lambda Type: forall(Type, lambda g: Implication(init(g), func(g)))

def assign_next_rule(func):
    return lambda Type: forall([Type, Type], lambda g1, g2: Implication(is_next(g1, g2), func(g1, g2)))

def inv_rules(func):
    return lambda Type: forall(Type, func)

def forall_next_rule(g, func):
    return forall(type(g), lambda g1: Implication(is_next(g,g1), func(g, g1)))

def name_match_define(source, target):
    if type(target) == type(""):
        return (source, lambda g: getattr(g, target))
    else:
        return (source, lambda g: target)

def name_match_define_or(source, targets):
    return (source, lambda g: OR([getattr(g, target) for target in targets]))



def create_func(g, name_tokens):
    assert name_tokens != []
    result = g
    for token in name_tokens:
        result = getattr(result, token)

    return result


def make_input_list(parm_names):
    result_list = []
    for name in parm_names:
        if type(name) != type(""):
            result_list.append(lambda g, name =name: name)
        else:
            name_tokens = name.split('.')
            result_list.append(lambda g, name_tokens=name_tokens: create_func(g, name_tokens))
    return result_list

def count(exprs):
    if exprs == []:
        return Int(0)
    else:
        head = exprs[0]
        return ITE(head, Int(0), Int(1)) + count(exprs[1:])

def same_time_events(g, target_Type, req =None):
    current_frame = get_timed_obj(g.time)
    if target_Type in current_frame:
        target_object = current_frame[target_Type]
        if req is None:
            return target_object.presence
        else:
            return AND(target_object.presence, req(target_object))
    else:
        sub_input_subs = {}
        sub_input_subs["time"] = g.time
        target_object = target_Type(temp = False, input_subs=sub_input_subs )
        #target_object.time = g.time
        #target_object.presence = g.presence
        #add_timed_obj(g.time, target_object)
        if req is None:
            req = lambda g: TRUE()

        circuit = exist(target_Type, lambda g2: AND(EQ(g2.time, g.time ), req(g2)))
        circuit.act_non_include = target_object
        return circuit


