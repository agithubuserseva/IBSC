from logic_operator import *
from type_constructor import snap_shot
from trace_ult import print_trace
import copy

'''
Check the validity of a trace implied by the model from
solving a given set of constraints. Stop at the 
first rule that is violated by the trace 
'''
action_iteration_bound = 1000
def get_all_actions(ACTION):
    res = []
    for ACT in ACTION:
        res += ACT.collect_list
    return res


def complete_clear_actions(ACTION):
    for ACT in ACTION:
        ACT.collect_list.clear()
        ACT.temp_collection_set = set()
        ACT.syn_collect_list.clear()
        ACT.additional_constraint.clear()
        ACT.snap_shot.clear()
        ACT.EQ_CLASS = [set()]
        #TODO, may need to clear indexs

def clear_Exist_cache():
    Exists.Temp_ACTs.clear()
    Exists.new_included.clear()
    Exists.hint_barrier = False

def clear_all(ACTION, rules=None):
    complete_clear_actions(ACTION)
    clear_Exist_cache()
    if rules is not None:
        clear_rules(rules)

def clear_rules(rules):
    for rule in rules:
        if isinstance(rule, Exists):
            rule.act_include= None
            rule.act_non_include = None
            rule.func.result_cache.clear()
        if isinstance(rule, Forall):
            rule.func.result_cache.clear()





considered_object = set()
considered_constraint = []
def get_all_constraint(ACTION, full=True):
    global considered_constraint
    res_constraint = []
    for ACT in ACTION:
        for act in ACT.collect_list:
            if act not in considered_object:
                for delayed_func in act.delayed_constraint:
                    result = delayed_func()
                    considered_constraint.append(result)
                    if not full:
                        res_constraint.append(result)

                considered_constraint.append(act.constraint)
                if not full:
                    res_constraint.append(act.constraint)
                considered_object.add(act)
        for act in ACT.temp_collection_set:
            if act not in considered_object:
                for delayed_func in act.delayed_constraint:
                    result = delayed_func()
                    considered_constraint.append(result)
                    if not full:
                        res_constraint.append(result)

                considered_constraint.append(act.constraint)
                if not full:
                    res_constraint.append(act.constraint)
                considered_object.add(act)
    if full:
        return considered_constraint
    else:
        return res_constraint



def clear_actions(Action):
    #Action.collect_list.clear()
    Action.syn_collect_list.clear()

def clear_all_action(ACTION):
    for Action in ACTION:
        clear_actions(Action)


def snap_shot_all(ACTION):
    for Act in ACTION:
        snap_shot(Act)

def action_changed(ACTION):
    changed = []
    for Act in ACTION:
        if len(Act.snap_shot) < len(Act.collect_list):
            changed.append(Act)
    return changed

def check_trace(model, complete_rules, rules, stop_at_first = True):
    solver = Solver()
    #assert(len(Forall.pending_defs) == 0)
    parital_model =  [EqualsOrIff(k, v) for k, v in model]
    solver.add_assertion(And(parital_model))
    result = set()
    for rule in complete_rules:
        if rule in rules:
            continue
        else:
            solver.push()
            constraint = encode(rule, include_new_act=False, disable=True)
            solver.add_assertion(constraint)
            solver.add_assertion(And(get_temp_act_constraints(checking=True)))
            solved = solver.solve()
            solver.pop()
            if not solved:
                result.add(rule)
                if stop_at_first:
                    return result
    return result

def check_property_expanding(property, rules, ACTION, state_action):
    application_rounds = 1
    while application_rounds < action_iteration_bound:
        s = Solver("z3")
        cur_round = 0
        should_coutinue = True
        print(application_rounds)
        while (cur_round < 1 and should_coutinue):
            prop = encode(property, include_new_act=True)
            while (action_changed()):
                snap_shot_all()
                prop = encode(property, include_new_act=True)

            results = []
            for p in rules:
                results.append(encode(p, include_new_act=True))
            cur_round += 1
            should_coutinue = action_changed()

        while (action_changed()):
            snap_shot_all()
            prop = encode(property, include_new_act=True)
            results = []
            for p in rules:
                results.append(encode(p, include_new_act=False))

        s.push()
        s.add_assertion(And([prop] + results + get_all_constraint()))
        s.push()
        s.add_assertion(And(get_temp_act_constraints()))
        solved = s.solve()
        if solved:
            print_trace(s.get_model(), ACTION, state_action)
            return
        else:
            s.pop()
            solved = s.solve()
            if solved:
                print("need to increase domain")
                application_rounds += 1
            else:
                print("unsat")
                return
    # print(serialize(result))
    print("reaching limit, unsat")


def inductive_checking(property, rules, complete_rules, ACTION, state_action, minimized = False):
    snap_shot_all(ACTION)
    application_rounds = 0
    inductive_assumption_table= dict()
    prop = encode(property, include_new_act=False)

    new_rules = set(rules)
    should_calibrate = True
    s = Solver("z3")
    s.add_assertion(prop)
    while application_rounds < action_iteration_bound:
        print(application_rounds)
        while (action_changed(ACTION) or should_calibrate):
            should_calibrate = False
            snap_shot_all(ACTION)
            encode(property, include_new_act=False)
            for p in rules:
                temp_res = encode(p, include_new_act=False)
                if p in new_rules:
                    s.add_assertion(temp_res)

        new_rules.clear()
        print("end encoding")
        s.add_assertion(And(get_all_constraint(ACTION, full=False)))
        add_forall_defs(s)
        solved = s.solve()
        if solved:
            s.push()
            s.add_assertion(And(get_temp_act_constraints()))
            solved = s.solve()
            if solved:
                model = s.get_model()
                print_trace(model, ACTION, state_action)
                # check trace
                res = check_trace(model, complete_rules, rules, stop_at_first=True)
                if len(res) == 0:
                    print("find trace")
                    print_trace(model, ACTION, state_action)
                    return False
                else:
                    print("need to add more rules")
                    rules = rules.union(res)
                    new_rules = res
                    should_calibrate = True
                    s.pop()
            else:
                s.pop()
                if minimized:
                    print("start minimizing")
                    old_rule = copy.copy(rules)
                    get_temp_act_constraint_minimize(s, rules, force_no_duplicate=True,
                                                     inductive_assumption_table=inductive_assumption_table,
                                                     addition_actions=None, round = application_rounds)
                    new_rules = rules - old_rule
                else:
                    model = s.get_model()
                    analyzing_temp_act(model)
                print("need to increase domain")
                application_rounds += 1
        else:
            print("unsat")
            return True
    # print(serialize(result))
    print("reaching limit, bounded unsat")
    return True

def prove_by_induction(property, rules, complete_rules, ACTION, state_action, minimized = False):
    #first check init
    res = inductive_checking(property, rules, complete_rules, ACTION, state_action, minimized)

    clear_all(ACTION, list(rules) + [property])
    return res

def check_property_refining(property, rules, complete_rules, ACTION, state_action, minimized = False, vol_bound = 500, disable_minimization = False, min_solution = False, final_min_solution = False):
    current_min_solution = False
    out_of_bound_warning = False
    application_rounds = 1
    prop = encode(property, include_new_act=True)
    while (action_changed(ACTION)):
        snap_shot_all(ACTION)
        prop = encode(property, include_new_act=True)


    new_rules = set(rules)
    should_calibrate = True
    s = Solver("z3", unsat_cores_mode=None)
    s.add_assertion(prop)
    while application_rounds < action_iteration_bound:
        print(application_rounds)
        while (action_changed(ACTION) or should_calibrate):
            should_calibrate = False
            snap_shot_all(ACTION)
            encode(property, include_new_act=False)
            for p in rules:
                temp_res = encode(p, include_new_act=False)
                if p in new_rules:
                    s.add_assertion(temp_res)

        new_rules.clear()
        #print("end encoding")
        s.add_assertion(And(get_all_constraint(ACTION, full=False)))
        add_forall_defs(s)

        if current_min_solution:
            solved = True
        else:
            solved = s.solve()

        if solved:
            save_model = s.get_model()
            s.push()
            s.add_assertion(And(get_temp_act_constraints()))

            if current_min_solution:
                solved = True
            else:
                solved = s.solve()

            if solved:
                if not current_min_solution:
                    model = s.get_model()
                    print_trace(model, ACTION, state_action)
                    #check trace
                    res = check_trace(model, complete_rules, rules, stop_at_first=True)
                else:
                    res = []
                if len(res) == 0:
                    if final_min_solution:
                        model = mini_solve(s, get_all_actions(ACTION))
                    print("find trace")
                    vol = print_trace(model, ACTION, state_action)
                    print("vol: {}".format(str(vol)))

                    if min_solution or (out_of_bound_warning and vol > vol_bound):
                        s.pop()
                        model = get_temp_act_constraint_minimize(s, rules, force_no_duplicate=True, addition_actions=get_all_actions(ACTION), round=application_rounds, disable_minimization=disable_minimization)
                        new_vol = print_trace(model, ACTION, state_action, should_print=False)
                        if new_vol > vol_bound:
                            print("bounded UNSAT")
                            return
                        if new_vol >= vol:
                            print("opt size is {}".format(vol))
                            print("solution is opt")
                            return
                        else:
                            print("A better result may exist")
                            current_min_solution = True
                    else:
                        return
                else:
                    print("need to add more rules")
                    rules = rules.union(res)
                    new_rules = res
                    should_calibrate = True
                    s.pop()
            else:
                s.pop()
                if minimized:
                    print("start minimizing")
                    if out_of_bound_warning:
                        addition_actions = get_all_actions(ACTION)
                    else:
                        addition_actions = None

                    new_model = get_temp_act_constraint_minimize(s, rules, force_no_duplicate=True, addition_actions=addition_actions, round=application_rounds, disable_minimization=disable_minimization)
                    if new_model is None:
                        new_volume = print_trace(save_model, ACTION, state_action, should_print=False)
                    else:
                        new_volume = print_trace(new_model, ACTION, state_action, should_print=False) + 1

                    if new_volume > vol_bound:
                        if out_of_bound_warning:
                            print("bounded UNSAT")
                            return
                        else:
                            print("entering strict min search mode")
                            out_of_bound_warning = True
                else:
                    model = s.get_model()
                    analyzing_temp_act(model)

                print("need to increase domain")
                application_rounds += 1


        else:
            print("domain size {}".format(str(len(get_all_actions(ACTION)))))
            print("unsat")
            return
    # print(serialize(result))
    print("reaching limit, bounded unsat")