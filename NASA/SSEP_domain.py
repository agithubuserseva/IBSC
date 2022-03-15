from CommNet_domain import *
from CDR_domain import CDR
from Module import Module
from utils import *

locations = ["near", "far", "future"]
indexs = ["1","2","3"]

argument_list = [("time", "time")]
input_list= []
rule_list =[]
defines = []
sub_actions = []

input_list.append(("init_trj", "Int"))

for i in range(1, 4):
    input_list.append(("init_trj_g{}".format(str(i)), "Int"))

for i in range(1, 3):
    input_list.append(("intent_trj_future_s_{}".format(str(i)), "Int"))

for i in range(1, 4):
    input_list.append(("intent_trj_future_g_{}_adsb".format(str(i)), "Int"))

for loc in locations:
    input_list.append(("sugg_trj_{}".format(str(loc)), "Int"))

if not EXTENDED_MODEL:
    rule_list.append(lambda GESP: forall(GESP, lambda g: AND(NOT(g.fault_communications_atc_par),
                                                             NOT(g.fault_communications_atc_tot),
                                                             NOT(g.fault_communications_adsb),
                                                             NOT(g.fault_apply_future),
                                                             NOT(g.fault_apply_far),
                                                             NOT(g.fault_apply_near)
                                                             )))

argument_list.append(("next_intent_trj_future", "TRJ-0"))


for loc in locations:
    argument_list.append(("intent_trj_{}_adsb".format(loc), "TRJ-1"))

    
for loc in locations:
    argument_list.append(("intent_trj_{}_atc".format(loc), "TRJ-1"))
    
argument_list.append(("request_GTM", "Boolean"))

defines.append(("need_GTM", lambda g: OR(g.cdr.internal_failure, g.fault_communications_adsb)))

rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_atc), IFF(g.request_GTM, g.need_GTM))))
rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_atc), IFF(g.request_GTM, g.need_GTM))))


for loc in locations:
    rule_list.append(inv_rules(lambda g, loc=loc: Implication(g.fault_communications_adsb, getattr(g, "intent_trj_{}_adsb".format(loc)) < 0)))

rule_list.append(inv_rules(lambda g: Implication(g.fault_communications_atc, g.intent_trj_near_atc < 0)))
rule_list.append(inv_rules(lambda g: Implication(g.fault_communications_atc, g.intent_trj_far_atc < 0)))

if SSEP_INT_FUTURE:
    rule_list.append(inv_rules(lambda g: Implication(g.fault_communications_atc, g.intent_trj_future_atc < 0)))

#TODO, change that
rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_adsb), forall_next_rule(g, lambda g1, g2: EQ(g1.intent_trj_near_adsb, g2.intent_trj_near)))))
rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_adsb), forall_next_rule(g, lambda g1, g2: EQ(g1.intent_trj_far_adsb, g2.intent_trj_far)))))
rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_adsb), forall_next_rule(g, lambda g1, g2: EQ(g1.intent_trj_future_adsb, g2.next_intent_trj_future)))))


if SSEP_INT_FUTURE:
    rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_atc), EQ(g.intent_trj_future_atc, g.next_intent_trj_future))))
else:
    rule_list.append(inv_rules(lambda g: EQ(g.intent_trj_future_atc, Int(-1))))

rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_atc), EQ(g.intent_trj_near_atc, g.intent_trj_near))))
rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_communications_atc), EQ(g.intent_trj_far_atc, g.intent_trj_far))))

defines.append(("int_sugg_trj_future", lambda g: g.cdr.sugg_trj_future))
defines.append(("communication_step", lambda g:  g.comm_f.communication_step))


for loc in locations:
    argument_list.append(("fault_apply_{}".format(loc), "Boolean"))

c_types = ["atc_par", "atc_tot", "adsb"]
for c in c_types:
    argument_list.append(("fault_communications_{}".format(c), "Boolean"))

for loc in locations:
    defines.append(("to_fault_apply_{}".format(loc), lambda g, loc=loc: getattr(g, "fault_apply_{}".format(loc))))

c_types = ["atc_par", "atc_tot", "adsb"]
for c in c_types:
    defines.append(("to_fault_communications_{}".format(c), lambda g: getattr(g, "fault_communications_{}".format(c))))

defines.append(("fault_communications_atc", lambda g: OR(g.fault_communications_atc_par, g.fault_communications_atc_tot)))


for loc in locations:
    argument_list.append(("intent_trj_{}".format(str(loc)), "TRJ-0"))
argument_list.append(("current_trj", "TRJ-0"))

rule_list.append(assign_init_rule(lambda g: EQ(g.current_trj, g.init_trj)))
rule_list.append(assign_init_rule(lambda g: EQ(g.intent_trj_near, g.init_trj)))
rule_list.append(assign_init_rule(lambda g: EQ(g.intent_trj_far, g.init_trj)))
if INIT_FUTURE_INTENT:
    rule_list.append(assign_init_rule(lambda g: EQ(g.intent_trj_future, g.init_trj)))

for loc in locations:
    argument_list.append(("X_intent_trj_{}".format(loc), "Int"))
    rule_list.append(inv_rules(lambda g, loc=loc: OR( EQ(getattr(g, "X_intent_trj_{}".format(loc)), Int(-1)),  next(g, lambda g1: EQ( getattr(g, "X_intent_trj_{}".format(loc)),
                                                                                                                                    getattr(g1, "intent_trj_{}".format(loc)))))))

argument_list.append(("X_current_trj", "Int"))
rule_list.append(inv_rules(lambda g: OR(EQ(getattr(g, "X_current_trj"), Int(-1)),  next(g, lambda g1: EQ( getattr(g, "X_current_trj"),
                                                                                                                                getattr(g1, "current_trj"))))))


if S_COMM_FAILURE_G_ATC > 0: 
    argument_list.append(("count_f_comm_atc", "S_COMM_FAILURE_G_ATC-0"))

    rule_list.append(assign_init_rule(lambda g: EQ(g.count_f_comm_atc, Int(0))))

    rule_list.append(assign_next_rule(lambda g1, g2: OR(EQ(g2.count_f_comm_atc, g1.count_f_comm_atc + 1),
                                                        EQ(g2.count_f_comm_atc, g1.count_f_comm_atc),
                                                        EQ(g2.count_f_comm_atc, Int(0)),
                                                        )))

    argument_list.append(("allowed_f_comm_atc", "Boolean"))
    rule_list.append(lambda SSEP: forall(SSEP, lambda g: IFF(g.allowed_f_comm_atc, next(g, lambda g1: EQ(
        g1.count_f_comm_atc, g.count_f_comm_atc + 1)))))
    rule_list.append(lambda SSEP: forall(SSEP, lambda g: Implication(NOT(g.allowed_f_comm_atc),
                                                                             NOT(g.fault_communications_atc_par))))
    
if S_COMM_FAILURE_G_ADSB > 0:
    argument_list.append(("count_f_comm_adsb", "S_COMM_FAILURE_G_ADSB-0"))

    rule_list.append(assign_init_rule(lambda g: EQ(g.count_f_comm_adsb, Int(0))))
    rule_list.append(assign_next_rule(lambda g1, g2: OR(EQ(g2.count_f_comm_adsb, g1.count_f_comm_adsb + 1),
                                                        EQ(g2.count_f_comm_adsb, g1.count_f_comm_adsb),
                                                        EQ(g2.count_f_comm_adsb, Int(0)),
                                                        )))

    argument_list.append(("allowed_f_comm_adsb", "Boolean"))
    rule_list.append(lambda SSEP: forall(SSEP, lambda g: IFF(g.allowed_f_comm_adsb, next(g, lambda g1: EQ(
        g1.count_f_comm_adsb, g.count_f_comm_adsb + 1)))))
    rule_list.append(lambda SSEP: forall(SSEP, lambda g: Implication(NOT(g.allowed_f_comm_adsb),
                                                                     NOT(g.fault_communications_adsb))))








#TODO
###-- behavioral definition of the GSEP aircraft --

###-- Position --
rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.current_trj,
                                                    ITE(g1.communication_step, g1.current_trj,
                                                        ITE(g1.fault_apply_near, g2.current_trj,
                                                            ITE(g1.fault_communications_atc, g2.intent_trj_near, g1.sugg_trj_near))
                                                    ))))

rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_near,
                                                    ITE(g1.fault_apply_near, g2.intent_trj_near,
                                                        ITE(g1.fault_communications_atc, ITE(g1.communication_step, g1.intent_trj_near, g1.intent_trj_far),
                                                            g1.sugg_trj_near))
                                                    )))

rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_far,
                                                    ITE(g1.fault_apply_far, g2.intent_trj_far,
                                                        ITE(g1.fault_communications_atc, ITE(g1.communication_step, g1.intent_trj_far, g1.intent_trj_future),
                                                            g1.sugg_trj_far))
                                                    )))

rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_future,
                                                    ITE(g1.fault_apply_far, g2.intent_trj_future, g1.next_intent_trj_future)
                                                    )))

rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

rule_list.append(inv_rules(lambda g: EQ(g.next_intent_trj_future, ITE(g.fault_communications_atc,
                                                                      g.intent_trj_future,
                                                                      ITE(g.request_GTM, g.sugg_trj_future, g.cdr.sugg_trj_future)))))

def create_sub_actions(name):
    sub_class_list = []
    cdr = CDR.create_instance("{}_CDR".format(name))
    cdr_argument_dict = {}
    for i in range(1,4):
        cdr_argument_dict["intent_trj_future_g_{}".format(str(i))] = lambda g, i=i: getattr(g, "intent_trj_future_g_{}_adsb".format(str(i)))

    for i in range(1,3):
        cdr_argument_dict["intent_trj_future_s_{}".format(str(i))] = lambda g, i=i: getattr(g, "intent_trj_future_s_{}".format(str(i)))

    sub_class_list.append(("cdr", cdr, cdr_argument_dict))

    CP = COMMON_PHASE.create_instance("{}_CP".format(name))
    sub_class_list.append(("comm_f", CP, None))

    return sub_class_list

'''
for i in range(1, 1000):
    pass
for loc in range(1, 1000):
    pass
for t in range(1, 1000):
    pass

for type in range(1, 1000):
    pass

for air1 in range(1, 1000):
    pass

for air2 in range(1, 1000):
    pass
'''
rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

SSEP = Module("SSEP", input_list, argument_list, defines, rule_list, sub_action_generator=create_sub_actions)


