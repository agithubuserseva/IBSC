from model_config import *
from model import Model, get_all_rules
from utils import *

import sys
sys.path.append('../Analyzer')

from analyzer import check_property_refining
import time



if ENABLE_PURE_AIRSPACE:
    #validation set
    C_steps = forall(Model, lambda g: NOT(AllDifferent([g.g_a_1.communication_step, g.g_a_2.communication_step,
                                       g.g_a_3.communication_step, g.s_a_1.communication_step,
                                       g.s_a_2.communication_step, g.s_a_3.communication_step,
                                       g.atc.communication_step])))


    V1 = eventually(Model, lambda g: AND(NOT(g.communication_step), next(g, lambda g1: ALL_DIFFERENT(g1))))

    V2 = eventually(Model, lambda g: NOT(AllDifferent([g.g_a_1.current_trj, g.g_a_2.current_trj, g.g_a_3.current_trj,
                                                   g.s_a_1.current_trj, g.s_a_2.current_trj, g.s_a_3.current_trj])))



    V3 = eventually(Model, lambda g: next(g, lambda g2: OR([NEQ(g.g_a_1.current_trj, g2.g_a_1.current_trj),
                                         NEQ(g.g_a_2.current_trj, g2.g_a_2.current_trj),
                                         NEQ(g.g_a_3.current_trj, g2.g_a_3.current_trj),
                                         NEQ(g.s_a_1.current_trj, g2.s_a_1.current_trj),
                                         NEQ(g.s_a_2.current_trj, g2.s_a_2.current_trj),
                                         NEQ(g.s_a_3.current_trj, g2.s_a_3.current_trj)])))

    V4 = eventually(Model, lambda g: next(g, lambda g2: OR([EQ(g.g_a_1.current_trj, g2.g_a_1.current_trj),
                                         EQ(g.g_a_2.current_trj, g2.g_a_2.current_trj),
                                         EQ(g.g_a_3.current_trj, g2.g_a_3.current_trj),
                                         EQ(g.s_a_1.current_trj, g2.s_a_1.current_trj),
                                         EQ(g.s_a_2.current_trj, g2.s_a_2.current_trj),
                                         EQ(g.s_a_3.current_trj, g2.s_a_3.current_trj)])))

if ENABLE_PURE_CONTROLLERS:
    different_near = lambda g: ALL_DIFFERENT([g.intent_trj_near_g_1, g.intent_trj_near_g_2, g.intent_trj_near_g_3,
                                              g.intent_trj_near_s_1, g.intent_trj_near_s_2, g.intent_trj_near_s_1])

    different_far = lambda g: ALL_DIFFERENT([g.intent_trj_far_g_1, g.intent_trj_far_g_2, g.intent_trj_far_g_3,
                                              g.intent_trj_far_s_1, g.intent_trj_far_s_2, g.intent_trj_far_s_1])

    different_future = lambda g: ALL_DIFFERENT([g.intent_trj_future_g_1, g.intent_trj_future_g_2, g.intent_trj_future_g_3,
                                              g.intent_trj_future_s_1, g.intent_trj_future_s_2, g.intent_trj_future_s_1])

    different = lambda g: OR(different_near(g), different_far(g), different_future(g))


    different_sugg_near_atc = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_near, g.atc.sugg_g_ac2_near, g.atc.sugg_g_ac3_near,
                                                       g.atc.sugg_s_ac1_near, g.atc.sugg_s_ac2_near, g.atc.sugg_s_ac3_near])

    different_sugg_far_atc = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_far, g.atc.sugg_g_ac2_far, g.atc.sugg_g_ac3_far,
                                                       g.atc.sugg_s_ac1_far, g.atc.sugg_s_ac2_far, g.atc.sugg_s_ac3_far])

    different_sugg_future_atc = lambda g: ALL_DIFFERENT([g.atc.sugg_g_ac1_future, g.atc.sugg_g_ac2_future, g.atc.sugg_g_ac3_future,
                                                       g.atc.sugg_s_ac1_future, g.atc.sugg_s_ac2_future, g.atc.sugg_s_ac3_future])

    different_sugg_atc = lambda g: OR(different_sugg_near_atc(g), different_sugg_far_atc(g), different_sugg_future_atc(g))

    different_sugg_cdr = lambda g: DIFFERENT_FROM([g.cd_r.sugg_trj_future, g.intent_trj_cdr_1, g.intent_trj_cdr_2, g.intent_trj_cdr_3,
                                                   g.intent_trj_cdr_4, g.intent_trj_cdr_5], g.cd_r.sugg_trj_future)

    cdr_internal_failure = lambda g: g.cd_r.internal_failure

    def s_aci_loc_ch_j(i, j, loc, g):
        if i == 1:
            intent_num = i + j
        elif i == 2:
            if j == 1:
                intent_num =1
            elif j == 2:
                intent_num = 3
        elif i == 3:
            intent_num = j
        return EQ(getattr(g.comm_net, "ex_intent_s_ac{}_{}_ch_{}".format(str(i), loc, str(j))), getattr(g, "intent_trj_near_s_{}".format(str(intent_num))))


    s_ac1_near_ch_1 = lambda g: s_aci_loc_ch_j(1, 1, "near", g)
    s_ac1_near_ch_2 = lambda g: s_aci_loc_ch_j(1, 2, "near", g)

    s_ac2_near_ch_1 = lambda g: s_aci_loc_ch_j(2, 1, "near", g)
    s_ac2_near_ch_2 = lambda g: s_aci_loc_ch_j(2, 2, "near", g)

    s_ac3_near_ch_1 = lambda g: s_aci_loc_ch_j(3, 1, "near", g)
    s_ac3_near_ch_2 = lambda g: s_aci_loc_ch_j(3, 2, "near", g)

    s_ac1_far_ch_1 = lambda g: s_aci_loc_ch_j(1, 1, "far", g)
    s_ac1_far_ch_2 = lambda g: s_aci_loc_ch_j(1, 2, "far", g)

    s_ac2_far_ch_1 = lambda g: s_aci_loc_ch_j(2, 1, "far", g)
    s_ac2_far_ch_2 = lambda g: s_aci_loc_ch_j(2, 2, "far", g)

    s_ac3_far_ch_1 = lambda g: s_aci_loc_ch_j(3, 1, "far", g)
    s_ac3_far_ch_2 = lambda g: s_aci_loc_ch_j(3, 2, "far", g)

    s_ac1_future_ch_1 = lambda g: s_aci_loc_ch_j(1, 1, "future", g)
    s_ac1_future_ch_2 = lambda g: s_aci_loc_ch_j(1, 2, "future", g)

    s_ac2_future_ch_1 = lambda g: s_aci_loc_ch_j(2, 1, "future", g)
    s_ac2_future_ch_2 = lambda g: s_aci_loc_ch_j(2, 2, "future", g)

    s_ac3_future_ch_1 = lambda g: s_aci_loc_ch_j(3, 1, "future", g)
    s_ac3_future_ch_2 = lambda g: s_aci_loc_ch_j(3, 2, "future", g)

    g_ac1_future = lambda g: EQ(g.comm_net.ex_intent_g_ac1, g.intent_trj_future_g_1)
    g_ac2_future = lambda g: EQ(g.comm_net.ex_intent_g_ac2, g.intent_trj_future_g_2)
    g_ac3_future = lambda g: EQ(g.comm_net.ex_intent_g_ac3, g.intent_trj_future_g_3)

    eq_signals = lambda g: AND([g_ac1_future(g),g_ac2_future(g), g_ac3_future(g)] + [s_aci_loc_ch_j(i,j,loc, g) for i in [1,2,3] for j in [1,2] for loc in ["near", "far", "future"]])


    V_1_a = forall(Model, different)
    V_1_b = eventually(Model, lambda g: NOT(different(g)))
    V_1_atc_1 = forall(Model, lambda g: NOT(different_sugg_atc))
    V_1_cdr_1 = eventually(Model, lambda g: NOT(different_sugg_cdr(g)))
    V_1_cdr_2 = eventually(Model, lambda g: NOT(Implication(NOT(cdr_internal_failure(g), different_sugg_cdr(g)))))

    V_1_comm_net = eventually(Model, lambda g: NOT(eq_signals(g)))

if __name__ == '__main__':
    rules = [AND(get_all_rules())]
    t_rules = set()
    start = time.time()
    #p = exist(aircraft, lambda g1: next(g1, lambda g2: AND(NOT(g1.fault_communications_adsb), NOT(g2.fault_communications_adsb)) ))
    check_property_refining(V4, t_rules, rules, ACTION, state_action, True, disable_minimization=False)
    print(time.time() - start)
