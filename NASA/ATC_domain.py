from model_config import *
from pysmt.shortcuts import *
from CommNet_domain import *
from utils import *



inputs = []
argument_list=  []
rule_list = []
defines =[]

locations = ["near", "far", "future"]
index = ["1", "2", "3"]
types = ["g", "s"]
for type in types:
    for i in range(1,4):
        inputs.append(("init_{}_ac{}".format(type, str(i)), "Int"))

for type in types:
    for i in range(1,4):
        for loc in locations:
            inputs.append(("intent_{}_ac{}_{}".format(type, str(i), loc), "Int"))

for i in range(1,4):
    inputs.append(("s_ac{}_rec_request_GTM".format(str(i)), "Boolean"))

for type in types:
    for i in range(1,4):
        inputs.append(("fault_communication_{}_ac{}".format(type, str(i)), "Boolean"))

if not EXTENDED_MODEL:
    rule_list.append(lambda ATC: forall(ATC, lambda g: AND(NOT(g.atc_near_resolution_failure),
                                                       NOT(g.atc_far_resolution_failure),
                                                       NOT(g.atc_future_resolution_failure)
                                                       )))


def create_sub_actions(name):
    sub_class_list = []
    CP = COMMON_PHASE.create_instance("{}_CP".format(name))
    sub_class_list.append(("comm_f", CP, None))
    return sub_class_list


defines.append(("communication_step", lambda g: g.comm_f.communication_step))

for i in index:
    for loc in locations:
        defines.append(("ex_intent_g_ac{}_{}".format(i, loc), lambda g, i=i, loc=loc: getattr(g, "intent_g_ac{}_{}".format(i, loc))))

    defines.append(
        ("s_ac{}_request_GTM".format(i), lambda g, i=i: ITE(getattr(g, "fault_communication_s_ac{}".format(i)), FALSE(), getattr(g, "s_ac{}_rec_request_GTM".format(i)))))

if ENABLE_3_GSEP or  ENABLE_3_GSEP_1_SSEP or ENABLE_2_GSEP_2_SSEP or ENABLE_1_GSEP_3_SSEP or  ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_g_ac1_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_g_ac1_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc: EQ(getattr(g, "prev_sugg_g_ac1_{}".format(loc)), getattr(g, "init_g_ac1"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc: EQ(getattr(g1, "prev_sugg_g_ac1_{}".format(loc)), getattr(g, "sugg_g_ac1_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_g_ac1_future"), getattr(g, "init_g_ac1"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_g_ac1_future"),ITE(NOT(g.fault_communication_g_ac1), g.sugg_g_ac1_future,
                                                                       g.prev_sugg_g_ac1_future))))
else:
    for loc in locations:
        defines.append(("sugg_g_ac1_{}".format(loc), lambda g: g.init_g_ac1))
        defines.append(("prev_sugg_g_ac1_{}".format(loc), lambda g: g.init_g_ac1))


if ENABLE_3_GSEP or  ENABLE_3_GSEP_1_SSEP or ENABLE_2_GSEP_2_SSEP or ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_g_ac2_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_g_ac2_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc: EQ(getattr(g, "prev_sugg_g_ac2_{}".format(loc)), getattr(g, "init_g_ac2"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc: EQ(getattr(g1, "prev_sugg_g_ac2_{}".format(loc)), getattr(g, "sugg_g_ac2_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_g_ac2_future"), getattr(g, "init_g_ac2"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_g_ac2_future"),ITE(NOT(g.fault_communication_g_ac2), g.sugg_g_ac2_future,
                                                                       g.prev_sugg_g_ac2_future))))
else:
    for loc in locations:
        defines.append(("sugg_g_ac2_{}".format(loc), lambda g: g.init_g_ac2))
        defines.append(("prev_sugg_g_ac2_{}".format(loc), lambda g: g.init_g_ac2))


if ENABLE_3_GSEP or  ENABLE_3_GSEP_1_SSEP or ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_g_ac3_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_g_ac3_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc: EQ(getattr(g, "prev_sugg_g_ac3_{}".format(loc)), getattr(g, "init_g_ac3"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc: EQ(getattr(g1, "prev_sugg_g_ac3_{}".format(loc)), getattr(g, "sugg_g_ac3_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_g_ac3_future"), getattr(g, "init_g_ac3"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_g_ac3_future"),ITE(NOT(g.fault_communication_g_ac3), g.sugg_g_ac3_future,
                                                                       g.prev_sugg_g_ac3_future))))
else:
    for loc in locations:
        defines.append(("sugg_g_ac3_{}".format(loc), lambda g: g.init_g_ac3))
        defines.append(("prev_sugg_g_ac3_{}".format(loc), lambda g: g.init_g_ac3))


####

if ENABLE_3_GSEP_1_SSEP or  ENABLE_2_GSEP_2_SSEP or ENABLE_1_GSEP_3_SSEP or ENABLE_3_SSEP or  ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_s_ac1_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_s_ac1_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc: EQ(getattr(g, "prev_sugg_s_ac1_{}".format(loc)), getattr(g, "init_s_ac1"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc: EQ(getattr(g1, "prev_sugg_s_ac1_{}".format(loc)), getattr(g, "sugg_s_ac1_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_s_ac1_future"), getattr(g, "init_s_ac1"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_s_ac1_future"),ITE(NOT(g.fault_communication_s_ac1), g.sugg_s_ac1_future,
                                                                       g.prev_sugg_s_ac1_future))))
else:
    for loc in locations:
        defines.append(("sugg_s_ac1_{}".format(loc), lambda g: g.init_s_ac1))
        defines.append(("prev_sugg_s_ac1_{}".format(loc), lambda g: g.init_s_ac1))


if ENABLE_2_GSEP_2_SSEP or  ENABLE_1_GSEP_3_SSEP or ENABLE_3_SSEP or ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_s_ac2_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_s_ac2_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc : EQ(getattr(g, "prev_sugg_s_ac2_{}".format(loc)), getattr(g, "init_s_ac2"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc : EQ(getattr(g1, "prev_sugg_s_ac2_{}".format(loc)), getattr(g, "sugg_s_ac2_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_s_ac2_future"), getattr(g, "init_s_ac2"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_s_ac2_future"),ITE(NOT(g.fault_communication_s_ac2), g.sugg_s_ac2_future,
                                                                       g.prev_sugg_s_ac2_future))))
else:
    for loc in locations:
        defines.append(("sugg_s_ac2_{}".format(loc), lambda g: g.init_s_ac2))
        defines.append(("prev_sugg_s_ac2_{}".format(loc), lambda g: g.init_s_ac2))


if ENABLE_1_GSEP_3_SSEP or  ENABLE_3_SSEP or ENABLE_3_GSEP_3_SSEP:

    for loc in locations:
        argument_list.append(("sugg_s_ac3_{}".format(loc), "TRJ-0"))

    if COMM_FAILURE_AWARE:
        for loc in locations:
            argument_list.append(("prev_sugg_s_ac3_{}".format(loc), "TRJ-0"))

        for loc in ["near", "far"]:
            rule_list.append(assign_init_rule(lambda g, loc=loc: EQ(getattr(g, "prev_sugg_s_ac3_{}".format(loc)), getattr(g, "init_s_ac3"))))
            rule_list.append(assign_next_rule(lambda g, g1, loc=loc: EQ(getattr(g1, "prev_sugg_s_ac3_{}".format(loc)), getattr(g, "sugg_s_ac3_{}".format(loc)))))

        rule_list.append(assign_init_rule(lambda g: EQ(getattr(g, "prev_sugg_s_ac3_future"), getattr(g, "init_s_ac3"))))
        rule_list.append(assign_next_rule(
            lambda g, g1: EQ(getattr(g1, "prev_sugg_s_ac3_future"),ITE(NOT(g.fault_communication_s_ac3), g.sugg_s_ac3_future,
                                                                       g.prev_sugg_s_ac3_future))))
else:
    for loc in locations:
        defines.append(("sugg_s_ac3_{}".format(loc), lambda g: g.init_s_ac3))
        defines.append(("prev_sugg_s_ac3_{}".format(loc), lambda g: g.init_s_ac3))


for loc in locations:
    argument_list.append(("atc_{}_resolution_failure".format(loc), "Boolean"))
    defines.append(("to_atc_{}_resolution_failure".format(loc), lambda g, loc=loc: getattr(g, "atc_{}_resolution_failure".format(loc))))

for t in types:
    for i in index:
        for loc in locations:
            defines.append(("ex_sugg_{}_ac{}_{}".format(t, i, loc), lambda g, t=t, i=i, loc=loc: ITE(getattr(g, "fault_communication_{}_ac{}".format(t, i)), Int(-1), getattr(g, "sugg_{}_ac{}_{}".format(t, i, loc)))))



if COMM_FAILURE_AWARE:
    for loc in ["near", "far"]:
        for t in types:
            for i in index:
                target = "sugg_{}_ac{}_{}".format(t, i, loc)
                fault = "fault_communication_{}_ac{}".format(t, i)
                if loc == "near":
                    obj1 = "prev_sugg_{}_ac{}_far".format(t, i)
                    obj2 = "prev_sugg_{}_ac{}_near".format(t, i)
                elif loc == "far":
                    obj1 = "prev_sugg_{}_ac{}_future".format(t, i)
                    obj2 = "prev_sugg_{}_ac{}_far".format(t, i)
                obj3 = "sugg_{}_ac{}_{}".format(t, i, loc)

                rule_list.append(lambda ATC: forall(ATC, lambda g,
                                                            target=target, fault=fault, obj1=obj1, obj2=obj2, obj3=obj3:
                                                                  EQ(getattr(g, target),
                                                                  ITE(AND(getattr(g, fault), NOT(g.communication_step)),
                                                                      getattr(g, obj1), ITE(AND(getattr(g, fault), g.communication_step), getattr(g, obj2), getattr(g, obj3))
                                                                      )
                                                                  )))

    for t in ["g"]:
        for i in index:
            target = "sugg_{}_ac{}_future".format(t, i)
            fault = "fault_communication_{}_ac{}".format(t, i)
            o1 = "prev_sugg_{}_ac{}_future".format(t, i)
            o2 = "sugg_{}_ac{}_future".format(t, i)

            rule_list.append(lambda ATC: forall(ATC, lambda g, target=target,
            fault = fault,o1=o1, o2= o2: EQ(getattr(g, target),
                                                              ITE(getattr(g, fault),
                                                                  getattr(g, o1),
                                                                  getattr(g, o2)
                                                                  )
                                                              )))
    if SSEP_INT_FUTURE:
        for i in index:
            target = "sugg_s_ac{}_future".format(i)
            fault = "fault_communication_s_ac{}".format( i)
            o1 = "prev_sugg_s_ac{}_future".format(i)
            o2 = "intent_s_ac{}_future".format(i)
            o3 = "sugg_s_ac{}_future".format(i)

            rule_list.append(lambda ATC: forall(ATC, lambda g, target=target, fault=fault,
            o1=o1, o2=o2,o3=o3: EQ(getattr(g, target),
                                                              ITE(getattr(g, fault),
                                                                  getattr(g, o1), ITE(NOT(getattr(g, "s_ac{}_request_GTM".format(i))), getattr(g, o2), getattr(g, o3))
                                                                  )
                                                              )))

def find_all_selections(g, loc):
    signal = []
    for i in range(1,4):
        for type in ["s", "g"]:
            signal.append(getattr(g, "sugg_{}_ac{}_{}".format(type, str(i), loc)))
    return signal



def window_management_rules(g):
    i = None
    m_rules = []
    near_rules = []
    near_signal = find_all_selections(g, "near")
    for type in ["g", "s"]:
        for id in range(1,4):
            near_rules.append(Implication(NOT(getattr(g, "fault_communication_{}_ac{}".format(type, str(id)))),
                                       DIFFERENT_FROM(near_signal, getattr(g, "sugg_{}_ac{}_near".format(type, str(id)))))
                                       )
    m_rules.append(Implication(NOT(getattr(g, "atc_near_resolution_failure")), AND(near_rules)))

    far_rules = []
    far_signal = find_all_selections(g, "far")
    for type in ["g", "s"]:
        for id in range(1,4):
            far_rules.append(Implication(NOT(getattr(g, "fault_communication_{}_ac{}".format(type, str(id)))),
                                       DIFFERENT_FROM(far_signal, getattr(g, "sugg_{}_ac{}_far".format(type, str(id)))))
                                       )
    m_rules.append(Implication(NOT(getattr(g, "atc_far_resolution_failure")), AND(far_rules)))

    future_signal = find_all_selections(g, "future")
    future_rules = []
    for id in range(1, 4):
        future_rules.append(Implication(NOT(getattr(g, "fault_communication_g_ac{}".format( str(id)))),
                                     DIFFERENT_FROM(future_signal, getattr(g, "sugg_g_ac{}_future".format( str(id)))))
                         )
    m_rules.append(Implication(NOT(getattr(g, "atc_future_resolution_failure")), AND(future_rules)))

    future_rules = []
    for id in range(1, 4):
        future_rules.append(Implication(NOT(getattr(g, "s_ac{}_request_GTM".format(str(id)))),
                                        DIFFERENT_FROM(future_signal,
                                                       getattr(g, "sugg_s_ac{}_future".format(str(id)))))
                            )
    m_rules.append(Implication(NOT(getattr(g, "atc_future_resolution_failure")), AND(future_rules)))

    if SSEP_INT_FUTURE:
        for id in range(1,4):
            m_rules.append(Implication(AND(NOT(getattr(g, "s_ac{}_request_GTM".format(str(id)))),
                                           NOT(getattr(g, "fault_communication_s_ac{}".format(str(id))))),
                                        EQ(getattr(g, "sugg_s_ac{}_future".format(str(id))), getattr(g, "intent_s_ac{}_future".format(str(id))))
                                       ))
    else:
        for id in range(1,4):
            m_rules.append(Implication(AND(NOT(getattr(g, "s_ac{}_request_GTM".format(str(id)))),
                                           NOT(getattr(g, "fault_communication_s_ac{}".format(str(id))))),
                                        EQ(getattr(g, "sugg_s_ac{}_future".format(str(id))), getattr(g, "init_s_ac{}".format(str(id))))
                                       ))

    return AND(m_rules)

rule_list.append(inv_rules(window_management_rules))





aircraft_type = ["G1", "G2", "G3", "S1", "S2", "S3"]
LOS_defines = []

def air_symbol(air):
    symbol = ""
    if air[0] == "G":
        symbol += "g_"
    elif air[0] == "S":
        symbol+= "s_"
    return symbol + "ac{}".format(air[1:])

for loc in locations:
    for i in (range(len(aircraft_type))):
        j = i+1
        while j < len(aircraft_type):
            air1 = aircraft_type[i]
            air2 = aircraft_type[j]

            LOS_defines.append(("D_LOS_{}_{}_{}".format(air1, air2, loc), lambda g, loc=loc, air1=air1, air2=air2: EQ(getattr(g, "intent_{}_{}".format(air_symbol(air1), loc))
                                                                                , getattr(g, "intent_{}_{}".format(air_symbol(air2), loc)))))
            j += 1
for i in (range(len(aircraft_type))):
    j = i+1
    while j < len(aircraft_type):
        air1 = aircraft_type[i]
        air2 = aircraft_type[j]
        LOS_defines.append(name_match_define_or("D_LOS_{}_{}".format(air1, air2), ["D_LOS_{}_{}_{}".format(air1, air2, loc) for loc in locations]))
        j += 1

LOS_defines.append(("D_LOS_near", lambda g, t=t, i=i: ALL_DIFFERENT([getattr(g, "intent_{}_ac{}_near".format(t, i)) for i in index for t in types])))
LOS_defines.append(("D_LOS_far", lambda g, t=t, i=i: ALL_DIFFERENT([getattr(g, "intent_{}_ac{}_far".format(t, i)) for i in index for t in types])))
LOS_defines.append(("D_LOS_future", lambda g, t=t, i=i: ALL_DIFFERENT([getattr(g, "intent_{}_ac{}_future".format(t, i)) for i in index for t in types])))
LOS_defines.append(name_match_define_or("D_LOS", ["D_LOS_near", "D_LOS_far", "D_LOS_future"]))

defines += LOS_defines
argument_list.append(("time", "time"))

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

ATC = Module("ATC", inputs, argument_list, defines, rule_list, sub_action_generator=create_sub_actions)
#a = ATC.create_instance("atc")
#a1 = a()
#print(a1.D_LOS_G1_G2_near)

argument_list=  []
rule_list = []
defines =[]

for loc in locations:
    defines.append(("to_atc_{}_resolution_failure".format(loc), lambda g: FALSE()))

for i in index:
    for loc in locations:
        defines.append(name_match_define("ex_intent_g_ac{}_{}".format(i, loc), "intent_g_ac{}_{}".format(i, loc) ))

for t in types:
    for i in index:
        for loc in locations:
            defines.append(name_match_define("ex_sugg_{}_ac{}_{}".format(t, i, loc), "sugg_{}_ac{}_{}".format(t, i, loc)))

for t in types:
    for i in index:
        for loc in locations:
            argument_list.append(("sugg_{}_ac{}_{}".format(t, i, loc), "TRJ-1"))

defines += LOS_defines
argument_list.append(("time", "time"))
rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

ATC_idle = Module("ATC", inputs, argument_list, defines, rule_list, sub_action_generator=create_sub_actions)
