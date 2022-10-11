from pysmt.shortcuts import *

from type_constructor import Action, UnionAction

import itertools
controll_varaible_eq = dict()
controll_varaible_eq_r = dict()
raw_control_variable = set()
controll_variable = set()
controll_variable_scope = dict()
control_var_sym = dict()

learned_inv = []
model_action_mapping = dict()
class Control_Tree():

    def __init__(self, control_vs, trees, name="control_v"):
        self.control_vs = control_vs
        self.trees = trees
        self.name = name


    def add_child(self, child_vs, child_trees):
        self.control_vs += child_vs
        self.trees += child_trees

def look_for_child_control_variable(formula):
   collection = set()
   fv = get_free_variables(formula)
   for v in fv:
       if v.symbol_name().startswith("control_v_"):
           collection.add(v)
   return collection


def build_tree(control_vs, args):
    trees = []
    for control_v, arg in zip(control_vs, args):

            control_set = look_for_child_control_variable(arg)
            tree= set()
            for child in control_set:
                ct = controll_variable_scope.get(child, None)
                if ct is not None:
                    tree.add(ct)
            trees.append(tree)

            controll_varaible_eq[arg] = control_v
            controll_varaible_eq_r[control_v] = arg


    c_tree = Control_Tree(control_vs, trees)
    for control_v in control_vs:
        controll_variable_scope[control_v] = c_tree


    controll_variable.add(c_tree)
    for child_ts in trees:
        for child_t in child_ts:
            if (child_t in controll_variable):
                controll_variable.remove(child_t)



def build_symmetry_mapping(constraints):
    cs = [look_for_child_control_variable(cons) for cons in constraints]
    collections =[]
    for control_v in cs:
        index = 0
        while len(control_v) > 0:
            if len(collections) <= index:
                sym = set()
                collections.append(sym)
            else:
                sym = collections[index]
            sym.add(control_v.pop())
            index += 1

    for col in collections:
        sym_set = col
        for v in col:
            sym_res = control_var_sym.get(v, None)
            if sym_res is not None:
                sym_set = sym_set.union(sym_res)
        for v in col:
            control_var_sym[v] = sym_set

        new_constraint = [controll_varaible_eq_r[v] for v in col]
        build_symmetry_mapping(new_constraint)


def get_symmetry(assignments):
    new_constraint = set()
    for ass in assignments:
        sym_set = control_var_sym.get(ass, None)
        if sym_set is not None:
            new_con = Or(sym_set)
            if new_con not in new_constraint:
                new_constraint.add(Or(sym_set))
                continue
        new_constraint.add(ass)

    return list(new_constraint)

def symmetry_sub(formula):
    result =[]
    for f in formula:
        if f.is_symbol():
            convs = look_for_child_control_variable(f )
            res = get_symmetry(convs)
            f = substitute(f, dict([(con, res) for con, res in zip(convs,res)]))
        result.append(f)
    return result



try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

class illFormedFormulaException(Exception):
    pass

def _polymorph_args_to_tuple( args, should_tuple=False):
    """ Helper function to return a tuple of arguments from args.

    This function is used to allow N-ary operators to express their arguments
    both as a list of arguments or as a tuple of arguments: e.g.,
       And([a,b,c]) and And(a,b,c)
    are both valid, and they are converted into a tuple (a,b,c) """

    if len(args) == 1 and isinstance(args[0], Iterable):
        args = args[0]
    if should_tuple:
        return tuple(args)
    else:
        return list(tuple(args))


def encode(formula, assumption=False, include_new_act=False, exception=None, disable=None):
    if isinstance(formula, Operator):
        res = formula.encode(assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable)
        if formula.subs is not None:
            for target, src in formula.subs.items():
                res = target.sym_subs(src, encode(res, assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable))
        return res
    else:
        return formula

def invert(formula):
    if isinstance(formula, Operator):
        res = formula.invert()
        res.subs = formula.subs
        return res
    else:
        return Not(formula)

def DNF(formula):
    dnfs = to_DNF(formula)
    return [AND(dnf)for dnf in dnfs]

def to_DNF(formula):
    if isinstance(formula, Operator):
        return formula.to_DNF()
    else:
        return [simplify(formula)]

def to_CNF(formula):
    if isinstance(formula, Operator):
        return formula.to_CNF()
    else:
        return [simplify(formula)]


def sub(formula, source, target):
    if isinstance(formula, Operator):
        formula.sub(source, target)
        return formula
    else:
        return target.sym_subs(source, formula)


def slicing(formula, actions, reverse=False):
    if isinstance(formula, Operator):
        return formula.slicing(actions, reverse = reverse)
    else:
        bounded_variables = []
        fb = get_free_variables(formula)
        for action in actions:
            bounded_variables += action.get_all_variables()

        if len(set(fb) - set(bounded_variables)) == 0:
            if reverse:
                return None
            else:
                return formula
        else:
            if reverse:
                return formula
            else:
                return None


def update_context_map(context_map, action, context):
    attribute_of_interests = action.extract_mentioned_attributes(context)
    action_type = type(action)
    res = context_map.get( action_type, set())
    res  = res.union(attribute_of_interests)
    context_map[action_type] = res
    return context_map

def merge_context_map(map1, map2):
    for key, value in map2.items():
        m1_value = map1.get(key, set())
        map1[key] = m1_value.union(value)


    return map1






def get_func_args(func):
    assert isinstance(func, type(get_func_args))
    return func.__code__.co_varnames



def exist(Action_Class, func):
    if isinstance(Action_Class, type([])):
        func_vars=  list(get_func_args(func))
        #assert len(Action_Class) == len(func_vars)
        assert len(Action_Class) > 0
        if len(Action_Class) == 1:
            return exist(Action_Class[0], func)
        else:
            new_func = lambda x: exist(Action_Class[1:], lambda *args: func(x, *args))
            return exist(Action_Class[0], new_func)
    elif isinstance(Action_Class, type):
        return Exists(Action_Class, Function(func))
    elif isinstance(Action_Class, UnionAction):
        return OR([Exists(AC, Function(func)) for AC in Action_Class.actions])
    else:
        raise AssertionError

def forall(Action_Class, func):
    if isinstance(Action_Class, type([])):
        func_vars=  list(get_func_args(func))
        assert len(Action_Class) == len(func_vars)
        assert len(Action_Class) > 0
        if len(Action_Class) == 1:
            return forall(Action_Class[0], func)
        else:
            new_func = lambda x: forall(Action_Class[1:], lambda *args: func(x, *args))
            return forall(Action_Class[0], new_func)
    elif isinstance(Action_Class, type):
        return Forall(Action_Class, Function(func))
    elif isinstance(Action_Class, UnionAction):
        return AND([Forall(AC, Function(func)) for AC in Action_Class.actions])
    else:
        raise AssertionError


def Implication(l, r):
    return OR(NOT(l), r)

class Operator():
   def __init__(self):
       self.subs = {}

   def encode(self, assumption= False, include_new_act=False, exception=None, disable=None):
       return

   def invert(self):
       return self

   def sub(self, source, target):
       if self.subs is None:
            self.subs = {target: source}
       else:
            self.subs.update({target: source})

   def to_DNF(self):
       pass

   def to_CNF(self):
       pass

   def slicing(self, actions, reverse = False):
       pass

def NOT(arg, polarity = True):
    if arg is None or arg == []:
        return TRUE()
    else:
        if isinstance(arg, Operator):
            return C_NOT(arg, polarity)
        else:
            return Not(arg)


class C_NOT(Operator):
    def __init__(self, arg, polarity=True):
        super().__init__()
        self.arg = arg
        self.polarity = polarity
        self.ops = None

    def encode(self, assumption=False, include_new_act=False, exception = None, disable=None):
        if self.polarity:
            return encode(invert(self.arg), assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable)
        else:
            return encode(self.arg, assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable)

    #if invert the not, then you get the argument
    def invert(self):
        #self.polarity = not self.polarity
        if self.ops is None:
            self.ops = C_NOT(self.arg, not self.polarity)
        return self.ops

    def to_DNF(self):
        if self.polarity:
            return to_DNF(invert(self.arg))
        else:
            return to_DNF(self.arg)

    def to_CNF(self):
        if self.polarity:
            return to_CNF(invert(self.arg))
        else:
            return to_CNF(self.arg)

    def slicing(self, actions, reverse = False):
        if self.polarity:
            return slicing(invert(self.arg), actions, reverse = reverse)
        else:
            return slicing(self.arg, actions, reverse = reverse)

    def generalize_encode(self, context=[]):
        return encode(self)

def should_use_gate(args):
    for arg in args:
        if isinstance(arg, Operator):
            return True
    return False

def AND( *args):
    c_args = _polymorph_args_to_tuple(args)
    if c_args == [] or args is None:
        return TRUE()
    else:
        if should_use_gate(c_args):
            return C_AND(c_args)
        else:
            return And(_polymorph_args_to_tuple(args, should_tuple=True))


class C_AND(Operator):
    def __init__(self, *args):
        super().__init__()
        self.arg_list = _polymorph_args_to_tuple(args)
        self.op = None


    def encode(self, assumption=False, include_new_act=False, exception = None, disable=None):
        result_list =[]
        for arg in self.arg_list:
            result_list.append(encode(arg, assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable))
        return And(result_list)


    def invert(self):
        if self.op is None:
            arg_list = []
            for arg in self.arg_list:
                arg_list.append(invert(arg))
            self.op = OR(arg_list)
            self.op.op = self
        return self.op

    def to_DNF(self):
        sub_DNFS = [to_DNF(arg) for arg in self.arg_list ]
        dnfs = []
        for sub_dnf in sub_DNFS:
            if dnfs == []:
                dnfs = sub_dnf
            else:
                if sub_dnf == []:
                    continue
                else:
                    temp = []
                    for dnf in dnfs:
                        for sub in sub_dnf:
                            temp.append(AND(dnf, sub))
                    dnfs  = temp
        return dnfs

    def to_CNF(self):
        res = []
        for arg in self.arg_list:
            res += to_CNF(arg)
        return res

    def slicing(self, actions, reverse = False):
        sub_slices = [slicing(arg, actions, reverse = reverse) for arg in self.arg_list]
        sub_slices = [res for res in sub_slices if res is not None]
        return AND(sub_slices)

def OR( *args):
    c_args = _polymorph_args_to_tuple(args)
    if c_args == [] or args is None:
        return FALSE()
    else:
        if should_use_gate(c_args):
            return C_OR(c_args)
        else:
            return Or(_polymorph_args_to_tuple(args, should_tuple=True))


class C_OR(Operator):
    def __init__(self, *args):
        super().__init__()
        self.arg_list = _polymorph_args_to_tuple(args)
        self.op = None

    def encode(self, assumption=False, include_new_act=False, exception=None, disable=None):
        result_list =[]
        for arg in self.arg_list:
            result_list.append(encode(arg, assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable))
        if assumption:
            return _OR(result_list)
        else:
            return Or(result_list)

    def invert(self):
        if self.op is None:
            arg_list = []
            for arg in self.arg_list:
                arg_list.append(invert(arg))
            self.op = AND(arg_list)
            self.op.op = self
        return self.op

    def to_DNF(self):
        res = []
        for arg in self.arg_list:
            res += to_DNF(arg)
        return res


    def to_CNF(self):
        sub_CNFS = [to_CNF(arg) for arg in self.arg_list ]
        cnfs = []
        for sub_cnf in sub_CNFS:
            if cnfs == []:
                cnfs = sub_cnf
            else:
                if sub_cnf == []:
                    continue
                else:
                    temp = []
                    for cnf in cnfs:
                        for sub in sub_cnf:
                            temp.append(OR(cnf, sub))
                    cnfs  = temp
        return cnfs

    def slicing(self, actions, reverse=False):
        sub_slices = [slicing(arg, actions, reverse = reverse) for arg in self.arg_list]
        sub_slices = [res for res in sub_slices if res is not None]
        return OR(sub_slices)


class Function(Operator):

    def __init__(self, procedure, polarity= True):
        #create an concrete input based_on the type
        super().__init__()
        self.procedure = procedure
        self.polarity = polarity
        self.evaulated = []
        self.result_cache = dict()

    def evaulate(self, input, assumption=False):
        cache = self.result_cache.get(input, None)
        if cache is None:
            cache = self.procedure(input)
            self.result_cache[input] =cache

        if self.polarity:
           res= cache
        else:
            res= invert(cache)
        if assumption:
            self.evaulated.append(res)
        return res

    #check the slide effects
    def invert(self):
        return Function(self.procedure, polarity= not self.polarity)

temp_count = 0
def add_def(s, fml):
    global temp_count
    name = Symbol("def_{}".format(temp_count))
    temp_count+=1
    s.add_assertion(Iff(name, fml))
    return name

def relax_core(s, core, Fs):
    prefix = TRUE()
    Fs -= { f for f in set(core) }
    for i in range(len(core)-1):
        prefix = add_def(s, And(core[i], prefix))
        Fs |= { add_def(s, Or(prefix, core[i+1])) }

def get_assumption_core(solver):
    assumptions = solver.z3.unsat_core()
    pysmt_assumptions = [solver.converter.back(t) for t in assumptions]
    return pysmt_assumptions


def maxsat(s, Fs, round = -1, namespace=None):
    cost = 0
    Fs0 = Fs.copy()
    while not s.solve(Fs):
        #print("cost {}".format(cost))
        cost += 1
        #print("try to get assumption")
        core = [f for f in get_assumption_core(s) if f in Fs]
        if round >= 0 and namespace is not None:
            for f in core:
                act = namespace.get(f, None)
                if act is not None:
                    minimize_memory[namespace[f]] = round
        #print("relaxing core")
        relax_core(s, core, Fs)
        #print("next")
    model = s.get_model()
    return cost, { f for f in Fs0 if not model.get_py_value(f) }, model

def maxsat_model(s, Fs):
    cost = 0
    Fs0 = Fs.copy()
    while not s.solve(Fs):
        # print("cost {}".format(cost))
        cost += 1
        # print("try to get assumption")
        core = [f for f in get_assumption_core(s) if f in Fs]
        # print("relaxing core")
        relax_core(s, core, Fs)
        # print("next")
    model = s.get_model()
    return model, { f for f in Fs0 if not model.get_py_value(f) }

def mini_solve(solver, actions):
    constraints = []
    type_constraints = {}
    intermediate = {}
    name_space = {}
    visited_acts = dict()

    solver.push()
    soft_constraints = set()

    for act in actions:
        choice_list = []
        act_type = type(act)
        hold_act, choice_constraint = type_constraints.get(act_type, (None, None))
        if choice_constraint is not None:
            choice_constraint = hold_act.sym_subs(act, choice_constraint)
        else:
            visited_temp_act = visited_acts.get(act_type, [])
            for t_action in visited_temp_act:
                choice_list.append(act.build_eq_constraint(t_action))

            choice_constraint = Implies(act.presence, Or(choice_list))
            type_constraints[act_type] = (act, choice_constraint)

        name_str = str(act)
        fresh_var = Symbol("{}".format(name_str))
        solver.add_assertion(Iff(fresh_var, choice_constraint))
        soft_constraints.add(fresh_var)
        name_space[fresh_var] = act
        intermediate[act] = fresh_var

        result = visited_acts.get(act_type, None)
        if result is None:
            visited_acts[act_type] = [act]
        else:
            visited_acts[act_type].append(act)

    model, available = maxsat_model(solver, soft_constraints)
    solver.pop()
    return model


minimize_memory = dict()

def get_temp_act_constraint_minimize(solver, rules, force_no_duplicate=False, inductive_assumption_table=None, addition_actions = None, round = -1, disable_minimization = False):
    should_block = True
    #short cut
    if (len(Exists.Temp_ACTs) == 1 or disable_minimization):
        unqiue_act = set()
        for act in Exists.Temp_ACTs:
            exist_obj = Exists.Temp_ACTs.get(act)
            unqiue_act.add((act, exist_obj))
        include_new_actions(unqiue_act, rules, should_block, inductive_assumption_table)
        return

    constraints = []
    type_constraints = {}
    intermediate = {}
    name_space = {}
    visited_acts = dict()
    if addition_actions is None:
        addition_actions = []

    force_no_duplicate = force_no_duplicate or addition_actions == []

    test_actions = addition_actions + list(Exists.Temp_ACTs)
    solver.push()
    soft_constraints = set()
    for act in test_actions:
        #update round info
        if round >= 0:
            old_round = minimize_memory.get(act, -1)
            if old_round < 0:
                minimize_memory[act] = round

        choice_list = []
        act_type = type(act)
        hold_act, choice_constraint = type_constraints.get(act_type, (None, None))
        if choice_constraint is not None and addition_actions == []:
            choice_constraint = hold_act.sym_subs(act, choice_constraint)
        else:
            if addition_actions == []:
                for t_action in act_type.collect_list:
                    choice_list.append(act.build_eq_constraint(t_action))

            if force_no_duplicate:
                visited_temp_act = visited_acts.get(act_type, [])
                for t_action in visited_temp_act:
                    choice_list.append(act.build_eq_constraint(t_action))

            choice_constraint = Implies(act.presence, Or(choice_list))
            type_constraints[act_type] = (act, choice_constraint)
        name_str = str(act)
        fresh_var = Symbol("{}".format(name_str))
        solver.add_assertion(Iff(fresh_var, choice_constraint))
        soft_constraints.add(fresh_var)
        name_space[fresh_var] = act
        intermediate[act] = fresh_var
        #sum = Plus(sum, fresh_var)

        if force_no_duplicate:
            result = visited_acts.get(act_type, None)
            if result is None:
                visited_acts[act_type]= [act]
            else:
                visited_acts[act_type].append(act)

    #filtering phase
    filtering_threshold = 5
    filtered_soft_constraints = set()

    if round >= 0 and not force_no_duplicate:
        for act, fresh_var in intermediate.items():
            if minimize_memory.get(act, -1) >= round -filtering_threshold:
                filtered_soft_constraints.add(fresh_var)

        #print("diff {} {}".format(len(soft_constraints), len(filtered_soft_constraints)))
        cost, available, model = maxsat(solver, filtered_soft_constraints)
        unqiue_act = []
        if len(available) >= 1:
            #print("filtered successful")
            for node in available:
                act = name_space[node]
                exist_obj = Exists.Temp_ACTs.get(act)
                if exist_obj is not None:
                    unqiue_act.append((act, exist_obj))

            # now include the temp actions into the universe, this may introduce duplicate actions
            include_new_actions(unqiue_act, rules, should_block, inductive_assumption_table)
            solver.pop()
            return model
    #print("filtered unsuccessful")
    cost, available, model = maxsat(solver, soft_constraints, round, name_space)
    if force_no_duplicate:
        print("current domain {}".format(len(available)))
    unqiue_act = []
    assert len(available) >= 1
    for node in available:
        act = name_space[node]
        exist_obj = Exists.Temp_ACTs.get(act)
        if exist_obj is not None:
            unqiue_act.append((act, exist_obj))

    # now include the temp actions into the universe, this may introduce duplicate actions
    include_new_actions(unqiue_act, rules, should_block, inductive_assumption_table)
    solver.pop()

    return model

def get_temp_act_constraint_minimize_old(solver, rules, force_no_duplicate=False, inductive_assumption_table=None, addition_actions = None):
    should_block = True
    #short cut
    if (len(Exists.Temp_ACTs) == 1):
        unqiue_act = set()
        for act in Exists.Temp_ACTs:
            exist_obj = Exists.Temp_ACTs.get(act)
            unqiue_act.add((act, exist_obj))
        include_new_actions(unqiue_act, rules, should_block, inductive_assumption_table)
        return

    constraints = []
    type_constraints = {}
    intermediate = {}
    sum = Int(0)
    visited_acts = dict()
    if addition_actions is None:
        addition_actions = []

    test_actions = addition_actions + list(Exists.Temp_ACTs)
    solver.push()
    for act in test_actions:
        choice_list = []
        act_type = type(act)
        hold_act, choice_constraint = type_constraints.get(act_type, (None, None))
        if choice_constraint is not None and addition_actions == []:
            choice_constraint = hold_act.sym_subs(act, choice_constraint)
        else:
            if addition_actions == []:
                for t_action in act_type.collect_list:
                    choice_list.append(act.build_eq_constraint(t_action))

            if force_no_duplicate:
                visited_temp_act = visited_acts.get(act_type, [])
                for t_action in visited_temp_act:
                    choice_list.append(act.build_eq_constraint(t_action))

            choice_constraint = Implies(act.presence, Or(choice_list))
            type_constraints[act_type] = (act, choice_constraint)

        fresh_var = Ite(choice_constraint, Int(1), Int(0))
        intermediate[act] = fresh_var
        sum = Plus(sum, fresh_var)

        if force_no_duplicate:
            result = visited_acts.get(act_type, None)
            if result is None:
                visited_acts[act_type]= [act]
            else:
                visited_acts[act_type].append(act)

    max = len(test_actions)
    min = 0
    current = max -1
    old = max
    round = 0
    model = None
    target_sum = Symbol("target_sum", typename=INT)
    solver.add_assertion(Equals(sum, target_sum))
    while (current < max and current != old):
        round += 1
        solver.push()
        solver.add_assertion(GE(target_sum, Int(current)))
        solved = solver.solve()
        if solved:
            model = solver.get_model()
            #print("diff {}".format(current - solver.get_model().get_py_value(sum)))
            current = solver.get_model().get_py_value(sum)
            old = current
            min = current
            current = (current + max) // 2
            if inductive_assumption_table is None:
                if False:
                   break

        else:
            old = current
            max = current
            current = current - 1

        solver.pop()

    unqiue_act = set()
    for act in Exists.Temp_ACTs:
        true_res = model.get_py_value(Equals(intermediate[act], Int(1)))
        res = model.get_py_value(act.presence) and not true_res
        if res:
            exist_obj = Exists.Temp_ACTs.get(act)
            unqiue_act.add((act, exist_obj))
    # now include the temp actions into the universe, this may introduce duplicate actions
    include_new_actions(unqiue_act, rules, should_block, inductive_assumption_table)
    solver.pop()

    return constraints




def include_new_actions(unqiue_act, rules, should_block = False, inductive_assumption_table = None):
    for act, exist_obj in unqiue_act:
        print(exist_obj.input_type)
        Exists.Temp_ACTs.pop(act)
        act.make_permanent()
        new_action = act
        exist_obj.act_include = new_action
        Exists.new_included.add(new_action)
        #should we add inductive assumption
        if inductive_assumption_table is not None and should_block:
            # now check if the blocking clause is given
            blocking_clause = exist_obj.blocking_clause
            if blocking_clause is not None:
                assumption = blocking_clause(new_action)
                inductive_assumption_table[assumption] = {new_action}
                rules.add(assumption)

def get_temp_act_constraints(checking = False):
    constraints = []
    type_constraints = {}
    if checking:
        compare_dict = Exists.check_ACTS
    else:
        compare_dict = Exists.Temp_ACTs

    for act in compare_dict:
        choice_list = []
        act_type = type(act)
        hold_act, choice_constraint = type_constraints.get(act_type, (None, None))
        if choice_constraint is not None:
            choice_constraint = hold_act.sym_subs(act, choice_constraint)
        else:
            for t_action in act_type.collect_list:
                choice_list.append(act.build_eq_constraint(t_action))

            choice_constraint = Implies(act.presence, Or(choice_list))
            type_constraints[act_type] = (act, choice_constraint)

        constraints.append(choice_constraint)

    if checking:
        compare_dict.clear()
    return constraints

def analyzing_temp_act(model):
    unqiue_act = set()
    for act in Exists.Temp_ACTs:
        act_type = type(act)
        if model.get_py_value(act.presence):
            res = True
            for t_action in act_type.collect_list:
                if act.model_equal(model, t_action):
                    print("find non-unique")
                    res = False
                    break
            if res:
                exist_obj = Exists.Temp_ACTs.get(act)
                unqiue_act.add((act,exist_obj))
    #now include the temp actions into the universe
    for act, exist_obj in unqiue_act:
        Exists.Temp_ACTs.pop(act)
        new_action =  exist_obj.input_type()
        exist_obj.act_include = new_action
        Exists.new_included.add(new_action)






class Exists(Operator):
    Temp_ACTs = dict()
    check_ACTS = dict()
    new_included = set()

    def __init__(self, input_type, func):
        super().__init__()
        if not isinstance(func, Function):
            raise illFormedFormulaException("Exists: {} is not a Function".format(func))
        self.input_type = input_type
        self.func = func
        self.act_include = None
        self.act_non_include =None
        self.op = None
        self.blocking_clause = None

    def encode(self, assumption=False, include_new_act = False, exception = None, disable=None):

        if not include_new_act:
            if self.act_include is not None:
                action = self.act_include
            else:
                if self.act_non_include is None:
                    self.act_non_include = self.input_type(temp = True)
                action = self.act_non_include
        else:
            if self.act_include is None:
                self.act_include = self.input_type()
            action = self.act_include


        base_constraint = encode(AND(self.func.evaulate(action, assumption=assumption), action.presence),
            assumption=assumption, include_new_act=include_new_act, exception=exception, disable=disable)
        if include_new_act:
            Exists.new_included.add(action)
        elif not include_new_act and action == self.act_non_include and action != self.act_include:
            if disable:
                Exists.check_ACTS[action] = self
            else:
                #exist_obj = Exists.Temp_ACTs.get(action, None)
                #assert exist_obj is None or exist_obj == self
                Exists.Temp_ACTs[action] = self

        return base_constraint


    def invert(self):
        if self.op is None:
            self.op = Forall(self.input_type, invert(self.func))
            self.op.op = self
        return self.op

    def generalize_encode(self):
        action = self.input_type(temp=True)
        return

    def to_DNF(self):
        raise NotImplementedError("DNF for quantified formula is not ready")


def add_forall_defs(solver):
    for constraint in Forall.pending_defs:
        solver.add_assertion(constraint)
    #Forall.pending_defs.clear()


class Forall(Operator):
    count = 0
    pending_defs = set()
    def __init__(self, input_type, func):
        super().__init__()
        if not isinstance(func, Function):
            raise illFormedFormulaException("Exists: {} is not a Function".format(func))
        self.input_type = input_type
        self.func = func
        self.op = None
        self.var = Symbol("forall_{}".format(Forall.count))
        self.considered = set()
        Forall.count += 1


    def encode(self, assumption = False, include_new_act=False, exception=None, disable=None):
        constraint = []
        # base construction
        consider_exception = not exception is None
        for action in self.input_type.snap_shot:
            if (not consider_exception) or (not action in exception):
                base_constraint = encode(Implication(action.presence,  self.func.evaulate(action)) ,  assumption = assumption, include_new_act=include_new_act, exception=exception, disable=disable)
                if not disable:
                    if action not in self.considered:
                        Forall.pending_defs.add(Implies(self.var, base_constraint))
                        self.considered.add(action)
                    else:
                        #assert (Implies(self.var, base_constraint) in Forall.pending_defs)
                        #print("weird")
                        pass
                else:
                    constraint.append(base_constraint)
        if not disable:
            return self.var
        else:
            return And(constraint)

    def invert(self):
        if self.op is None:
            self.op = Exists(self.input_type, invert(self.func))
            self.op.op = self
        return self.op

    def to_DNF(self):
        raise NotImplementedError("DNF for quantified formula is not ready")




def create_control_variable(arg):
    s = controll_varaible_eq.get(arg)
    if s is None:
        s = Symbol("control_v_{}".format(len(raw_control_variable)))
        raw_control_variable.add(s)
    return s



def _OR(*args):
    arg_list = _polymorph_args_to_tuple(args)
    if len(arg_list) == 0:
        return FALSE()
    if len(arg_list) == 1:
        return arg_list[0]
    if TRUE() in arg_list:
        return TRUE()
    filtered_args = [arg for arg in arg_list if arg != FALSE()]
    control_sym = [create_control_variable(arg) for arg in filtered_args]
    build_tree(control_sym, filtered_args)
    return Or(control_sym)


def next(Action_class, idenifier_func, func, current_time = Int(0)):
    return (exist(Action_class, lambda act: AND(func(act),
                                                act > current_time,
                                                NOT(exist(Action_class, lambda act1:
                                                         AND(act1 > current_time,
                                                                act1 < act,
                                                                 idenifier_func(act1, act)
                                                             )
                                                          ))
                                                )))

def previous(Action_class, idenifier_func, func, current_time = Int(0)):
    return (exist(Action_class, lambda act: AND(func(act),
                                                act < current_time,
                                                NOT(exist(Action_class, lambda act1:
                                                         AND(act1 < current_time,
                                                                act1 > act,
                                                                 idenifier_func(act1, act)
                                                             )
                                                          ))
                                                )))

def current(Action_class, idenifier_func, func, current_time = Int(0)):
    return (exist(Action_class, lambda act: AND(func(act),
                                                act <= current_time,
                                                NOT(exist(Action_class, lambda act1:
                                                         AND(act1 <= current_time,
                                                                act1 >= act,
                                                                 idenifier_func(act1, act),
                                                                NOT(act.build_eq_constraint(act1))
                                                             )
                                                          ))
                                                )))

def eventually(Action_class, func, current_time = Int(0)):
    circuit = exist(Action_class, lambda act: AND(func(act), act >= current_time))
    circuit.blocking_clause = lambda act1: Implication(act1.presence,
                                                       forall(Action_class, lambda act: Implication(act1 > act,
                                                                                                    NOT(func(act)))))
    return circuit

def once(Action_class, func, current_time):
    circuit = exist(Action_class, lambda act: AND(func(act), act <= current_time))
    circuit.blocking_clause = lambda act1: Implication(act1.presence, forall(Action_class, lambda act: Implication(act1 < act,
                                                                                                                   NOT(func(act)))) )
    return circuit

def until(EAction, func, Faction, func1, current_time):
    circut = exist(EAction, lambda eaction: AND(func(eaction),
                                                eaction >= current_time,
                                                NOT(exist(Faction, lambda faction : AND(func1(faction),
                                                                                        faction < eaction,
                                                                                        faction >= current_time)))))
    circut.blocking_clause = lambda act1 : Implication(act1.presence, NOT(exist(EAction, lambda eaction: AND(func(eaction),
                                                eaction > act1,
                                                NOT(exist(Faction, lambda faction : AND(func1(faction),
                                                                                        faction < eaction,
                                                                                        faction >= act1)))))))

    return circut


def since(EAction, func, Faction, func1, current_time):
    circut = exist(EAction, lambda eaction: AND(func(eaction),
                                                eaction <= current_time,
                                                NOT(exist(Faction, lambda faction : AND(func1(faction),
                                                                                        faction > eaction,
                                                                                        faction <= current_time)))))
    circut.blocking_clause = lambda act1 : Implication(act1.presence, NOT(exist(EAction, lambda eaction: AND(func(eaction),
                                                eaction < act1,
                                                NOT(exist(Faction, lambda faction : AND(func1(faction),
                                                                                        faction > eaction,
                                                                                        faction <= act1)))))))

    return circut

def ITE(cond, left, right):
    return Ite(cond, left, right)

def IFF(left, right):
    if isinstance(left, Operator) or isinstance(right, Operator):
        return AND(Implication(left, right), Implication(right,left))
    return Iff(left, right)

def EQ(left, right):
    if isinstance(left, Action) and isinstance(right, Action):
        return left.build_eq_constraint(right)
    return Equals(left, right)

def NEQ(left, right):
    if isinstance(left, Action) and isinstance(right, Action):
        return Not(left.build_eq_constraint(right))
    return NotEquals(left, right)

