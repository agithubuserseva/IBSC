from model_config import *
from model import Model, get_all_rules
from utils import *

import sys
sys.path.append('../Analyzer')

from analyzer import check_property_refining
import time

LOS = lambda g: NOT(ALL_DIFFERENT([g.g_a_1.current_trj, g.g_a_2.current_trj, g.g_a_3.current_trj,
                                        g.s_a_1.current_trj, g.s_a_2.current_trj, g.s_a_3.current_trj]))

LOS_near = lambda g: NOT(ALL_DIFFERENT([g.g_a_1.intent_trj_near, g.g_a_2.intent_trj_near, g.g_a_3.intent_trj_near,
                                        g.s_a_1.intent_trj_near, g.s_a_2.intent_trj_near, g.s_a_3.intent_trj_near]))

LOS_far = lambda g: NOT(ALL_DIFFERENT([g.g_a_1.intent_trj_far, g.g_a_2.intent_trj_far, g.g_a_3.intent_trj_far,
                                        g.s_a_1.intent_trj_far, g.s_a_2.intent_trj_far, g.s_a_3.intent_trj_far]))

LOS_future = lambda g: NOT(ALL_DIFFERENT([g.g_a_1.intent_trj_future, g.g_a_2.intent_trj_future, g.g_a_3.intent_trj_future,
                                        g.s_a_1.intent_trj_future, g.s_a_2.intent_trj_future, g.s_a_3.intent_trj_future]))


def LOS_func(air1, air2, loc, g):
    t1 = air1[0].lower()
    i1 = air1[1]
    t2 = air2[0].lower()
    i2 = air2[1]
    if loc == "current":
        return EQ(getattr(getattr(g, "{}_a_{}".format(t1, i1)), "current_trj"),
                  getattr(getattr(g, "{}_a_{}".format(t2, i2)), "current_trj"))
    else:
        return EQ(getattr(getattr(g, "{}_a_{}".format(t1, i1)), "intent_trj_{}".format(loc)),
                  getattr(getattr(g, "{}_a_{}".format(t2, i2)), "intent_trj_{}".format(loc)))

aircraft = ["G1", "G2", "G3", "S1", "S2", "S3"]
locations = ["near", "far", "future"]
for i in range(len(aircraft)):
    t_locations = ["current", "near", "far", "future"]
    j = i+1
    air1 = aircraft[1]
    while (j < len(aircraft)):
        air2 = aircraft[j]
        for loc in t_locations:
            globals()["LOS_{}_{}_{}".format(air1, air2, loc)] = \
                lambda g, air1=air1, air2=air2, loc=loc: LOS_func(air1, air2, loc, g)
        j += 1

def create_H4_constraint(air, loc, g):
    t = air[0].lower()
    i = air[1]
    x = getattr(getattr(g, "{}_a_{}".format(t, i)), "X_intent_trj_{}".format(loc))
    atc_value = getattr(g.atc, "sugg_{}_ac{}_{}".format(t, i, loc))
    return Implication(x> 0, EQ(x, atc_value))

for air in aircraft:
    t = air[0].lower()
    i = air[1]
    funcs = []
    for loc in locations:
        func =  lambda g, air=air, loc=loc: create_H4_constraint(air, loc, g)
        funcs.append(func)
        globals()["H_4_{}_{}".format(air, loc)] = func
    globals()["H_4_{}".format(air)] = lambda g, air= air: AND([func(g) for func in funcs])


H_5_near = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_near, g.atc.sugg_g_ac2_near, g.atc.sugg_g_ac3_near, g.atc.sugg_s_ac1_near, g.atc.sugg_s_ac2_near, g.atc.sugg_s_ac3_near])
H_5_far = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_far, g.atc.sugg_g_ac2_far, g.atc.sugg_g_ac3_far, g.atc.sugg_s_ac1_far, g.atc.sugg_s_ac2_far, g.atc.sugg_s_ac3_far])
H_5_future_atc = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_future, g.atc.sugg_g_ac2_future, g.atc.sugg_g_ac3_future, g.atc.sugg_s_ac1_future, g.atc.sugg_s_ac2_future, g.atc.sugg_s_ac3_future])
H_5_future_s1 = lambda g: Implication(NOT(g.s_a_1.request_GTM), DIFFERENT_FROM([g.s_a_1.int_sugg_trj_future, g.g_a_1.intent_trj_future_adsb, g.g_a_2.intent_trj_future_adsb, g.g_a_3.intent_trj_future_adsb, g.s_a_2.intent_trj_future_adsb, g.s_a_3.intent_trj_future_adsb], g.s_a_1.int_sugg_trj_future))
H_5_future_s2 = lambda g: Implication(NOT(g.s_a_2.request_GTM), DIFFERENT_FROM([g.s_a_1.int_sugg_trj_future, g.g_a_1.intent_trj_future_adsb, g.g_a_2.intent_trj_future_adsb, g.g_a_3.intent_trj_future_adsb, g.s_a_2.intent_trj_future_adsb, g.s_a_3.intent_trj_future_adsb], g.s_a_2.int_sugg_trj_future))
H_5_future_s3 = lambda g: Implication(NOT(g.s_a_3.request_GTM), DIFFERENT_FROM([g.s_a_1.int_sugg_trj_future, g.g_a_1.intent_trj_future_adsb, g.g_a_2.intent_trj_future_adsb, g.g_a_3.intent_trj_future_adsb, g.s_a_2.intent_trj_future_adsb, g.s_a_3.intent_trj_future_adsb], g.s_a_3.int_sugg_trj_future))

if ENABLE_3_GSEP:
    D_LOS = lambda g: g.atc.D_LOS
    D_LOS_ALL = lambda g: g.atc.D_LOS

    H_4 = lambda g: AND(H_4_G1(g), H_4_G2(g), H_4_G3(g))

    H_5 = lambda g: AND(H_5_near(g), H_5_far(g), H_5_future_atc(g))

    BR_1 = eventually(Model, lambda g: forall(Model, lambda g1: Implication(g1 >= g, OR(Implication(g.g_a_1.X_current_trj >= 0,  EQ(g.g_a_1.current_trj, g.g_a_1.X_current_trj)),
                                                                                        Implication(g.g_a_2.X_current_trj >= 0,  EQ(g.g_a_2.current_trj, g.g_a_2.X_current_trj)),
                                                                                        Implication(g.g_a_3.X_current_trj >= 0,  EQ(g.g_a_3.current_trj, g.g_a_3.X_current_trj)) ))))



    S_1 =lambda g: AND(Implication(LOS_G1_G2_future(g), NOT(LOS_G1_G2_far(g))),
                       Implication(LOS_G1_G2_far(g), NOT(LOS_G1_G2_near(g))),
                       Implication(LOS_G1_G2_near(g), NOT(LOS_G1_G2(g))),
                       Implication(LOS_G1_G3_future(g), NOT(LOS_G1_G3_far(g))),
                       Implication(LOS_G1_G3_far(g), NOT(LOS_G1_G3_near(g))),
                       Implication(LOS_G1_G3_near(g), NOT(LOS_G1_G3(g))),
                       Implication(LOS_G2_G3_future(g), NOT(LOS_G2_G3_far(g))),
                       Implication(LOS_G2_G3_far(g), NOT(LOS_G2_G3_near(g))),
                       Implication(LOS_G2_G3_near(g), NOT(LOS_G2_G3(g)))
    )

    LOS_C_1 = lambda g : count([LOS_G1_G2(g), LOS_G1_G3(g)])
    LOS_C_1_near = lambda g: count([LOS_G1_G2_near(g), LOS_G1_G3_near(g)])
    LOS_C_1_far = lambda g: count([LOS_G1_G2_far(g), LOS_G1_G3_far(g)])
    LOS_C_1_future = lambda g: count([LOS_G1_G2_future(g), LOS_G1_G3_future(g)])

    LOS_C_2 = lambda g: count([LOS_G1_G2(g), LOS_G2_G3(g)])
    LOS_C_2_near = lambda g: count([LOS_G1_G2_near(g), LOS_G2_G3_near(g)])
    LOS_C_2_far = lambda g: count([LOS_G1_G2_far(g), LOS_G2_G3_far(g)])
    LOS_C_2_future = lambda g: count([LOS_G1_G2_future(g), LOS_G2_G3_future(g)])

    LOS_C_3 = lambda g: count([LOS_G2_G3(g), LOS_G1_G3(g)])
    LOS_C_3_near = lambda g: count([LOS_G2_G3_near(g), LOS_G1_G3_near(g)])
    LOS_C_3_far = lambda g: count([LOS_G2_G3_far(g), LOS_G1_G3_far(g)])
    LOS_C_3_future = lambda g: count([LOS_G2_G3_future(g), LOS_G1_G3_future(g)])

    MAN_C = lambda g: count([AND(g.g_a_1.X_current_trj >=0, NEQ(g.g_a_1.current_trj, g.g_a_1.X_current_trj)),
                             AND(g.g_a_2.X_current_trj >=0, NEQ(g.g_a_2.current_trj, g.g_a_2.X_current_trj)),
                             AND(g.g_a_3.X_current_trj >=0, NEQ(g.g_a_3.current_trj, g.g_a_2.X_current_trj))])

    MAN_C_near = lambda g: count([AND(g.g_a_1.X_intent_trj_near >=0, NEQ(g.g_a_1.intent_trj_near, g.g_a_1.X_intent_trj_near)),
                             AND(g.g_a_2.X_intent_trj_near >=0, NEQ(g.g_a_2.intent_trj_near, g.g_a_2.X_intent_trj_near)),
                             AND(g.g_a_3.X_intent_trj_near >=0, NEQ(g.g_a_3.intent_trj_near, g.g_a_2.X_intent_trj_near))])

    MAN_C_far = lambda g: count([AND(g.g_a_1.X_intent_trj_far >=0, NEQ(g.g_a_1.intent_trj_far, g.g_a_1.X_intent_trj_far)),
                             AND(g.g_a_2.X_intent_trj_far >=0, NEQ(g.g_a_2.intent_trj_far, g.g_a_2.X_intent_trj_far)),
                             AND(g.g_a_3.X_intent_trj_far >=0, NEQ(g.g_a_3.intent_trj_far, g.g_a_2.X_intent_trj_far))])

    MAN_C_future = lambda g: count([AND(g.g_a_1.X_intent_trj_future >=0, NEQ(g.g_a_1.intent_trj_future, g.g_a_1.X_intent_trj_future)),
                             AND(g.g_a_2.X_intent_trj_future >=0, NEQ(g.g_a_2.intent_trj_future, g.g_a_2.X_intent_trj_future)),
                             AND(g.g_a_3.X_intent_trj_future >=0, NEQ(g.g_a_3.intent_trj_future, g.g_a_2.X_intent_trj_future))])

    S_2 = lambda g: AND(EQ(LOS_C_1(g), MAN_C(g)), EQ(LOS_C_1_near(g), MAN_C_near(g)), EQ(LOS_C_1_far(g), MAN_C_far(g)), EQ(LOS_C_1_future(g), MAN_C_future(g)),
                        EQ(LOS_C_2(g), MAN_C(g)), EQ(LOS_C_2_near(g), MAN_C_near(g)), EQ(LOS_C_2_far(g), MAN_C_far(g)),
                        EQ(LOS_C_2_future(g), MAN_C_future(g)),
                        EQ(LOS_C_3(g), MAN_C(g)), EQ(LOS_C_3_near(g), MAN_C_near(g)), EQ(LOS_C_3_far(g), MAN_C_far(g)),
                        EQ(LOS_C_3_future(g), MAN_C_future(g))
                        )

if ENABLE_3_GSEP_1_SSEP:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict)
    D_LOS_ALL = lambda g: AND(g.atc.D_LOS , g.s_a_1.cdr.future_conflict)

    H_4 = lambda g: AND(H_4_G1(g), H_4_G2(g), H_4_G3(g), H_4_S1(g))
    H_5_future = lambda g: AND(H_5_future_atc(g), H_5_future_s1(g))
    H_5 = lambda g: AND(H_5_near(g), H_5_far(g), H_5_future(g))

if ENABLE_2_GSEP_2_SSEP:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict, g.s_a_2.cdr.future_conflict)
    D_LOS_ALL = lambda g: AND(g.atc.D_LOS, g.s_a_1.cdr.future_conflict)

    H_4 = lambda g: AND(H_4_G1(g), H_4_G2(g), H_4_S1(g), H_4_S2(g))
    H_5_future = lambda g: AND(H_5_future_atc(g), H_5_future_s1(g), H_5_future_s2(g))
    H_5 = lambda g: AND(H_5_near(g), H_5_far(g), H_5_future(g))

if ENABLE_1_GSEP_3_SSEP:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict, g.s_a_2.cdr.future_conflict, g.s_a_3.cdr.future_conflict)
    D_LOS_ALL = lambda g: AND(g.atc.D_LOS, g.s_a_1.cdr.future_conflict)

    H_4 = lambda g: AND(H_4_G1(g), H_4_S1(g), H_4_S2(g), H_4_S3(g))
    H_5_future = lambda g: AND(H_5_future_atc(g), H_5_future_s1(g), H_5_future_s2(g), H_5_future_s3(g))
    H_5 = lambda g: AND(H_5_near(g), H_5_far(g), H_5_future(g))

if ENABLE_3_SSEP:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict, g.s_a_2.cdr.future_conflict, g.s_a_3.cdr.future_conflict)
    H_4 = lambda g: AND(H_4_S1(g), H_4_S2(g), H_4_S3(g))
    H_5 = lambda g: TRUE()

if ENABLE_3_GSEP_3_SSEP:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict, g.s_a_2.cdr.future_conflict, g.s_a_3.cdr.future_conflict)
    H_4 = lambda g: AND(H_4_S1(g), H_4_S2(g), H_4_S3(g), H_4_G1(g), H_4_G2(g), H_4_G3(g))

    H_3 = lambda g: TRUE()
    H_5 = lambda g: TRUE()

if ENABLE_PURE_AIRSPACE:
    D_LOS = lambda g: OR(g.atc.D_LOS, g.s_a_1.cdr.future_conflict, g.s_a_2.cdr.future_conflict, g.s_a_3.cdr.future_conflict)

    H_4 = lambda g: AND(H_4_S1(g), H_4_S2(g), H_4_S3(g), H_4_G1(g), H_4_G2(g), H_4_G3(g))

    H_3 = lambda g: TRUE()
    H_5 = lambda g: TRUE()


def H_1(g):
    return NOT(LOS(g))

def H_1_b(g):
    return NOT(OR(LOS_near(g), LOS_far(g), LOS_future(g)))

def H_2():
    return forall(Model, lambda g: Implication(LOS(g), previous(g, lambda g1: D_LOS(g1))))

def H_2_n(g):
    return Implication(NOT(D_LOS(g)), next(g, lambda g1: NOT((LOS(g1)))))

def H_3(g):
    return Implication(OR(LOS_near(g), LOS_far(g), LOS_future(g)), D_LOS(g))

def H_3_n(g):
    return Implication(NOT(D_LOS(g)), OR(LOS_near(g), LOS_far(g), LOS_future(g)))



rule_1 = eventually(Model, lambda g: NOT(H_1(g)))
rule_2 = eventually(Model, lambda g: NOT(H_1_b(g)))
rule_3 = eventually(Model, lambda g: NOT(H_3(g)))
rule_4 = NOT(H_2())
rule_5 = eventually(Model, lambda g: NOT(H_5(g)))
rule_6 = eventually(Model, lambda g: NOT(H_4(g)))

if __name__ == '__main__':

    args = sys.argv[1:]

    if len(args) >= 2:
        mymin = True
    else:
        mymin = False

    print(mymin)

    args = sys.argv[1:]
    target_rule = globals()["rule_{}".format(args[0])]

    rules = [AND(get_all_rules())]
    t_rules = set()
    start = time.time()
    #p = exist(aircraft, lambda g1: next(g1, lambda g2: AND(NOT(g1.fault_communications_adsb), NOT(g2.fault_communications_adsb)) ))
    check_property_refining(target_rule, t_rules, rules, ACTION, state_action, True, disable_minimization=False, min_solution=mymin, final_min_solution=True)
    print(time.time() - start)
