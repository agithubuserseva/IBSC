
from CommNet_domain import COMMON_PHASE
from model_config import *
from utils import *
from Module import Module


#init

argument_list = [("time", "time")]
input_list= []
rule_list =[]
defines = []
sub_actions = []

#input
input_list.append(("init_trj", "Int"))
input_list.append(("sugg_trj_near", "Int"))
input_list.append(("sugg_trj_far", "Int"))
input_list.append(("sugg_trj_future", "Int"))

if not EXTENDED_MODEL:
    rule_list.append(lambda GESP: forall(GESP, lambda g: AND(NOT(g.fault_communications_atc_par),
                                                             NOT(g.fault_communications_atc_tot),
                                                             NOT(g.fault_communications_adsb),
                                                             NOT(g.fault_apply_future),
                                                             NOT(g.fault_apply_far),
                                                             NOT(g.fault_apply_near)
                                                             )))


if not GSEP_ADSB_OUT:
    defines.append(("intent_trj_near_adsb", lambda g: Int(-1)))
    defines.append(("intent_trj_far_adsb", lambda g: Int(-1)))
    defines.append(("intent_trj_future_adsb", lambda g: Int(-1)))
else:
    argument_list.append(("intent_trj_near_adsb", "TRJ-1"))
    argument_list.append(("intent_trj_far_adsb", "TRJ-1"))
    argument_list.append(("intent_trj_future_adsb", "TRJ-1"))

    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g:
                        AND(Iff(g.fault_communications_adsb, g.intent_trj_near_adsb < 0),
                            Iff(g.fault_communications_adsb, g.intent_trj_far_adsb < 0),
                            Iff(g.fault_communications_adsb, g.intent_trj_future_adsb < 0))
                        ))
    rule_list.append(lambda GSEP_AIR: forall([GSEP_AIR, GSEP_AIR], lambda g1, g2: Implication(is_next(g1, g2),
                        AND(OR(g1.fault_communications_adsb, EQ(g1.intent_trj_near_adsb  , g2.intent_trj_near_adsb)),
                            OR(g1.fault_communications_adsb, EQ(g1.intent_trj_far_adsb  , g2.intent_trj_far_adsb)),
                            OR(g1.fault_communications_adsb, EQ(g1.intent_trj_future_adsb  , g2.intent_trj_future_adsb))))
                        ))



argument_list.append(("intent_trj_near_atc", "TRJ-1"))
argument_list.append(("intent_trj_far_atc", "TRJ-1"))
argument_list.append(("intent_trj_future_atc", "TRJ-1"))

defines.append(("communication_step", lambda g: g.comm_f.communication_step))

rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g:
                        AND(Iff(g.fault_communications_atc, g.intent_trj_near_atc < 0),
                            Iff(g.fault_communications_atc, g.intent_trj_near_atc < 0),
                            Iff(g.fault_communications_atc, g.intent_trj_near_atc < 0))
                        ))



argument_list.append(("fault_apply_future", "Boolean"))
argument_list.append(("fault_apply_far", "Boolean"))
argument_list.append(("fault_apply_near", "Boolean"))
argument_list.append(("fault_communications_atc_par", "Boolean"))
argument_list.append(("fault_communications_atc_tot", "Boolean"))
argument_list.append(("fault_communications_adsb", "Boolean"))

defines.append(("to_fault_apply_future", lambda g: g.fault_apply_future))
defines.append(("to_fault_apply_far", lambda g: g.fault_apply_far))
defines.append(("to_fault_apply_near", lambda g: g.fault_apply_near))
defines.append(("to_fault_communications_atc_par", lambda g: g.fault_communications_atc_par))
defines.append(("to_fault_communications_atc_tot", lambda g: g.fault_communications_atc_tot))
defines.append(("to_fault_communications_adsb", lambda g: g.fault_communications_adsb))

defines.append(("fault_communications_atc", lambda g: OR(g.fault_communications_atc_par, g.fault_communications_atc_tot)))

if not GSEP_ADSB_OUT:
    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: NOT(g.fault_communications_adsb)))

argument_list.append(("intent_trj_near", "TRJ-0"))
argument_list.append(("intent_trj_far", "TRJ-0"))
argument_list.append(("intent_trj_future", "TRJ-0"))
argument_list.append(("current_trj", "TRJ-0"))



rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(init(g), EQ(g.current_trj, g.init_trj))))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(init(g), EQ(g.intent_trj_near, g.init_trj))))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(init(g), EQ(g.intent_trj_far, g.init_trj))))

if INIT_FUTURE_INTENT:
    rule_list.append(
        lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(init(g), EQ(g.intent_trj_future, g.init_trj))))



argument_list.append(("X_intent_trj_near", "TRJ-1"))
argument_list.append(("X_intent_trj_far", "TRJ-1"))
argument_list.append(("X_intent_trj_future", "TRJ-1"))
argument_list.append(("X_current_trj", "TRJ-1"))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: OR(EQ(g.X_intent_trj_near, Int(-1)), next(g, lambda g1: EQ(g.X_intent_trj_near, g1.intent_trj_near )))))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: OR(EQ(g.X_intent_trj_far, Int(-1)), next(g, lambda g1: EQ(g.X_intent_trj_far, g1.intent_trj_far )))))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: OR(EQ(g.X_intent_trj_future, Int(-1)), next(g, lambda g1: EQ(g.X_intent_trj_future, g1.intent_trj_future )))))
rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: OR(EQ(g.X_current_trj, Int(-1)), next(g, lambda g1: EQ(g.X_current_trj, g1.current_trj )))))


if S_COMM_FAILURE_G_ATC > 0:
    argument_list.append(("count_f_comm_atc", "CFG_ATC"))
    rule_list.append(assign_init_rule(lambda g: EQ(g.count_f_comm_atc, Int(0))))
    rule_list.append(assign_next_rule(lambda g1, g2: OR(EQ(g2.count_f_comm_atc, g1.count_f_comm_atc + 1),
                                                        EQ(g2.count_f_comm_atc, g1.count_f_comm_atc),
                                                        EQ(g2.count_f_comm_atc, Int(0)),
                                                        )))
    argument_list.append(("allowed_f_comm_atc", "Boolean"))
    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: IFF(g.allowed_f_comm_atc, next(g, lambda g1: EQ(g1.count_f_comm_atc, g.count_f_comm_atc + 1))) ))
    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(NOT(g.allowed_f_comm_atc), NOT(g.fault_communications_atc_par)) ))

if S_COMM_FAILURE_G_ADSB > 0:
    argument_list.append(("count_f_comm_adsb", "CFG_ADSB"))
    rule_list.append(assign_init_rule(lambda g: EQ(g.count_f_comm_adsb, Int(0))))
    rule_list.append(assign_next_rule(lambda g1, g2: OR(EQ(g2.count_f_comm_adsb, g1.count_f_comm_adsb + 1),
                                                        EQ(g2.count_f_comm_adsb, g1.count_f_comm_adsb),
                                                        EQ(g2.count_f_comm_adsb, Int(0)),
                                                        )))

    argument_list.append(("allowed_f_comm_adsb", "Boolean"))
    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: IFF(g.allowed_f_comm_adsb, next(g, lambda g1: EQ(
        g1.allowed_f_comm_adsb, g.allowed_f_comm_adsb + 1)))))
    rule_list.append(lambda GSEP_AIR: forall(GSEP_AIR, lambda g: Implication(NOT(g.allowed_f_comm_adsb),
                                                                             NOT(g.fault_communications_adsb))))


rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.current_trj, ITE(g1.communication_step, g1.current_trj,
                                                                        ITE(g1.fault_apply_near, g2.current_trj,
                                                                            ITE(g1.fault_communications_atc, g2.intent_trj_near, g1.sugg_trj_near)
                                                                        )))))



rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_near, ITE(g1.fault_apply_near, g2.intent_trj_near,
                                                                        ITE(g1.fault_communications_atc, ITE(g1.communication_step, g1.intent_trj_near, g1.intent_trj_far),
                                                                             g1.sugg_trj_near
                                                                        )))))

rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_far, ITE(g1.fault_apply_far, g2.intent_trj_far,
                                                                        ITE(g1.fault_communications_atc, ITE(g1.communication_step, g1.intent_trj_far, g1.intent_trj_future),
                                                                             g1.sugg_trj_far
                                                                        )))))

rule_list.append(assign_next_rule(lambda g1, g2: EQ(g2.intent_trj_future, ITE(g1.fault_apply_future, g2.intent_trj_future,
                                                                        ITE(g1.fault_communications_atc, g1.intent_trj_future,
                                                                             g1.sugg_trj_near
                                                                        )))))

rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

def create_sub_actions(name):
    sub_class_list = []
    CP = COMMON_PHASE.create_instance("{}_CP".format(name))
    sub_class_list.append(("comm_f", CP, None))
    return sub_class_list


GSEP = Module("GSEP", input_list, argument_list, defines, rule_list, create_sub_actions)



locations = ["near", "far", "future"]
types = ["g", "s"]
index = ["1", "2", "3"]

input_list =[]
argument_list = [("time", "time")]
rule_list = []
defines = []
input_list.append(("init_trj", "Int"))
for loc in locations:
    defines.append(name_match_define("to_fault_apply_{}".format(loc), FALSE()))

defines.append(name_match_define("to_fault_communications_atc_par", FALSE()))
defines.append(name_match_define("fault_communications_atc", FALSE()))
defines.append(name_match_define("fault_communications_atc_par", FALSE()))

defines.append(name_match_define("to_fault_communications_atc_tot", FALSE()))
defines.append(name_match_define("fault_communications_atc_tot", FALSE()))
defines.append(name_match_define("to_fault_communications_adsb", FALSE()))
defines.append(name_match_define("fault_communications_adsb", FALSE()))

defines.append(name_match_define("current_trj", "init_trj" ))
for loc in locations:
    defines.append(name_match_define("intent_trj_{}".format(loc), "init_trj" ))

for loc in locations:
    defines.append(name_match_define("intent_trj_{}_atc".format(loc), "init_trj" ))

defines.append(name_match_define("intent_trj_future_adsb", Int(-1)))

for loc in locations:
    defines.append(name_match_define("X_intent_trj_{}".format(loc), "init_trj" ))


defines.append(name_match_define("X_current_trj", "init_trj"))
rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

GSEP_disabled = Module("GSEP_disabled", input_list, argument_list, defines, rule_list, sub_action_generator=None)