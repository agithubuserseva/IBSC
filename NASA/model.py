from model_config import *
from ATC_domain import ATC_idle, ATC
from CDR_domain import CDR
from CommNet_domain import COMM_NET, COMMON_PHASE
from SSEP_domain import SSEP
from SSEP_aircraft_disabled_domain import  SSEP_disabled
from GSEP_domain import GSEP, GSEP_disabled
from utils import *
from Module import Module

import sys
sys.path.append('../Analyzer')
from type_constructor import Delayed_Constraints, union


def create_SSEP_disabled(name, input_list, result_list):
    air = SSEP_disabled.create_instance(name)
    result_list.append((name, air, make_input_list(input_list)))


def create_SSEP(name, input_list, result_list):
    air = SSEP.create_instance(name)
    result_list.append((name, air, make_input_list(input_list)))

locations = ["near", "far", "future"]
types =["g", "s"]
index = ["1", "2", "3"]

inputs = []
argument_list=  [("time", "time")]
rule_list = []
defines =[]
sub_action_list = []




def add_SSEP(index, result):
    index = str(index)
    s_a_1_dict = {}
    s_a_1_dict["init_trj"] = lambda g, index=index: getattr(g, "init_s_ac{}".format(index))
    for i in range(1,4):
        s_a_1_dict["s_a_{}_dict".format(str(i))] = lambda g, i=i: "init_g_ac{}".format(str(i))

    for i in range(1,3):
        s_a_1_dict["intent_trj_future_s_{}".format(str(i))] = lambda g, i=i: getattr(g.comm_net, "ex_intent_s_ac{}_future_ch_{}".format(index, str(i)))

    for i in range(1,4):
        s_a_1_dict["intent_trj_future_g_{}_adsb".format(str(i))] = lambda g, i=i: getattr(g.comm_net, "ex_intent_g_ac{}".format(str(i)))

    for loc in locations:
        s_a_1_dict["sugg_trj_{}".format(loc)] = lambda g, loc=loc: getattr(g.atc, "ex_sugg_s_ac{}_{}".format(index, loc))

    name = "s_a_{}".format(index)
    s_a= GSEP.create_instance(name)
    result.append((name, s_a, s_a_1_dict))

def create_GSP_air_craft(name, inputs, sub_action_list):
    air  = GSEP.create_instance(name)
    sub_action_list.append((name, air, make_input_list(inputs)))

def create_SSEP_disabled(name, inputs, sub_action_list):
    air = SSEP_disabled.create_instance(name)
    sub_action_list.append((name, air, make_input_list(inputs)))

def create_GSEP_disabled(name, inputs, sub_action_list):
    air = GSEP_disabled.create_instance(name)
    sub_action_list.append((name, air, make_input_list(inputs)))

if ENABLE_PURE_AIRSPACE:
    defines.append(name_match_define("init_g_ac1", Int(0)))
    defines.append(name_match_define("init_g_ac2", Int(1)))
    defines.append(name_match_define("init_g_ac3", Int(2)))

    defines.append(name_match_define("init_s_ac1", Int(3)))
    defines.append(name_match_define("init_s_ac2", Int(4)))
    defines.append(name_match_define("init_s_ac3", Int(5)))

    cp = COMMON_PHASE.create_instance("comm_f")
    sub_action_list.append(("comm_f", cp, []))

    defines.append(("communication_step", lambda g: g.comm_f.communication_step))


    g_a_1_dict = {}

    g_a_1_dict["init_trj"] = lambda g: g.init_g_ac1
    g_a_1_dict["sugg_trj_near"] = lambda g: g.atc.ex_sugg_g_ac1_near
    g_a_1_dict["sugg_trj_far"] = lambda g: g.atc.ex_sugg_g_ac1_far
    g_a_1_dict["sugg_trj_future"] = lambda g: g.atc.ex_sugg_g_ac1_future
    g_a_1 = GSEP.create_instance("g_a_1")
    sub_action_list.append(("g_a_1", g_a_1, g_a_1_dict))

    g_a_2_dict = {}

    g_a_2_dict["init_trj"] = lambda g: g.init_g_ac2
    g_a_2_dict["sugg_trj_near"] = lambda g: g.atc.ex_sugg_g_ac2_near
    g_a_2_dict["sugg_trj_far"] = lambda g:  g.atc.ex_sugg_g_ac2_far
    g_a_2_dict["sugg_trj_future"] = lambda g: g.atc.ex_sugg_g_ac2_future
    g_a_2 = GSEP.create_instance("g_a_2")
    sub_action_list.append(("g_a_2", g_a_2, g_a_2_dict))

    g_a_3_dict = {}

    g_a_3_dict["init_trj"] = lambda g: g.init_g_ac3
    g_a_3_dict["sugg_trj_near"] = lambda g: g.atc.ex_sugg_g_ac3_near
    g_a_3_dict["sugg_trj_far"] = lambda g: g.atc.ex_sugg_g_ac3_far
    g_a_3_dict["sugg_trj_future"] = lambda g: g.atc.ex_sugg_g_ac3_future
    g_a_3 = GSEP.create_instance("g_a_3")
    sub_action_list.append(("g_a_3", g_a_3, g_a_3_dict))

    s_a_1_inputs = ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3"]

    for i in ["1", "2"]:
        s_a_1_inputs.append("comm_net.ex_intent_s_ac1_future_ch_{}".format(i))

    for i in index:
        s_a_1_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_1_inputs.append("atc.ex_sugg_s_ac1_{}".format(loc))

    create_SSEP("s_a_1", s_a_1_inputs, sub_action_list)

    s_a_2_inputs = ["init_s_ac2", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_2_inputs.append("comm_net.ex_intent_s_ac2_future_ch_{}".format(i))

    for i in index:
        s_a_2_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_2_inputs.append("atc.ex_sugg_s_ac2_{}".format(loc))

    create_SSEP("s_a_2", s_a_2_inputs, sub_action_list)

    s_a_3_inputs = ["init_s_ac3", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_3_inputs.append("comm_net.ex_intent_s_ac3_future_ch_{}".format(i))

    for i in index:
        s_a_3_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_3_inputs.append("atc.ex_sugg_s_ac3_{}".format(loc))

    create_SSEP("s_a_3", s_a_3_inputs, sub_action_list)

    atc = ATC_idle.create_instance("atc")
    atc_inputs =[]
    for t in types:
        for i in index:
            atc_inputs.append(lambda g, t=t, i=i:  getattr(g, "init_{}_ac{}".format(t,i)))

    for t in types:
        for i in index:
            for loc in locations:
                atc_inputs.append(lambda g, t=t, i=i, loc=loc: getattr(getattr(g, "{}_a_{}".format(t, i)), "intent_trj_{}_atc".format(loc)))

    for i in index:
        atc_inputs.append(lambda g, i=i: getattr(getattr(g, "s_a_{}".format(i)), "request_GTM"))


    for t in types:
        for i in index:
            atc_inputs.append(lambda g, t=t, i=i: getattr(getattr(g, "{}_a_{}".format(t, i)),
                                                                   "fault_communications_atc.format"))

    sub_action_list.append(("atc", atc, atc_inputs))

if ENABLE_PURE_CONTROLLERS:

    defines.append(name_match_define("init_s_ac1", Int(0)))
    defines.append(name_match_define("init_s_ac2", Int(1)))
    defines.append(name_match_define("init_s_ac3", Int(2)))

    defines.append(name_match_define("init_g_ac1", Int(3)))
    defines.append(name_match_define("init_g_ac2", Int(4)))
    defines.append(name_match_define("init_g_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))
    defines.append(name_match_define("disabled_future_s_ac2", Int(7)))
    defines.append(name_match_define("disabled_future_s_ac3", Int(8)))

    for t in types:
        for i in index:
            for loc in locations:
                argument_list.append(("intent_trj_{}_{}_{}".format(loc, t, i), "TRJ-0"))

    for i in range(1,6):
        argument_list.append(("intent_trj_cdr_{}".format(str(i)), "TRJ-0"))

    for i in index:
        argument_list.append(("request_GTM_s_{}".format(str(i)), "Boolean"))

    for t in types:
        for i in index:
            defines.append(("fault_communications_{}_{}".format(t, i), lambda g: FALSE()))

    cdr_input_list = make_input_list(["intent_trj_cdr_{}".format(str(i)) for i in range(1, 6)])
    cd_r = CDR.create_instance("cd_r")
    sub_action_list.append(("cd_r", cd_r, cdr_input_list))

    common_net_inputs = []
    for i in index:
        for loc in locations:
            common_net_inputs.append(("intent_trj_{}_s_{}".format(loc, i)))

    for i in index:
        common_net_inputs.append("intent_trj_future_g_{}".format(i))

    common_net_inputs = make_input_list(common_net_inputs)
    comm_net = COMM_NET.create_instance("comm_net")
    sub_action_list.append(("comm_net", comm_net, common_net_inputs))

    atc_input_list =[]
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))

    for i in index:
        for _ in range(3):
            atc_input_list.append("init_g_ac{}".format(i))


    for i in index:
        for _ in range(3):
            atc_input_list.append("intent_trj_near_s_{}".format(i))

    for i in index:
            atc_input_list.append("request_GTM_s_{}".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("fault_communications_{}_{}".format(t, i))

    atc_input_list = make_input_list(atc_input_list)
    atc = ATC.create_instance("atc")
    sub_action_list.append(("atc", atc, atc_input_list))




if ENABLE_3_GSEP:

    defines.append(name_match_define("init_g_ac1", Int(0)))
    defines.append(name_match_define("init_g_ac2", Int(1)))
    defines.append(name_match_define("init_g_ac3", Int(2)))

    defines.append(name_match_define("init_s_ac1", Int(3)))
    defines.append(name_match_define("init_s_ac2", Int(4)))
    defines.append(name_match_define("init_s_ac3", Int(5)))



    create_GSP_air_craft("g_a_1", ["init_g_ac1", "atc.ex_sugg_g_ac1_near", "atc.ex_sugg_g_ac1_far", "atc.ex_sugg_g_ac1_future"], sub_action_list)
    create_GSP_air_craft("g_a_2",
                         ["init_g_ac2", "atc.ex_sugg_g_ac2_near", "atc.ex_sugg_g_ac2_far", "atc.ex_sugg_g_ac2_future"],
                         sub_action_list)
    create_GSP_air_craft("g_a_3",
                         ["init_g_ac3", "atc.ex_sugg_g_ac3_near", "atc.ex_sugg_g_ac3_far", "atc.ex_sugg_g_ac3_future"],
                         sub_action_list)

    create_SSEP_disabled("s_a_1", ["init_s_ac1"], sub_action_list)
    create_SSEP_disabled("s_a_2", ["init_s_ac2"], sub_action_list)
    create_SSEP_disabled("s_a_3", ["init_s_ac3"], sub_action_list)

    atc_input_list =[]
    for t in types:
        for i in index:
            atc_input_list.append( "init_{}_ac{}".format(t, i))

    for t in types:
        for i in index:
            for loc in locations:
                atc_input_list.append("{}_a_{}.intent_trj_{}_atc".format(t,i, loc))


    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))


    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))


if ENABLE_3_GSEP_1_SSEP:
    defines.append(name_match_define("init_g_ac1", Int(0)))
    defines.append(name_match_define("init_g_ac2", Int(1)))
    defines.append(name_match_define("init_g_ac3", Int(2)))

    defines.append(name_match_define("init_s_ac1", Int(3)))
    defines.append(name_match_define("init_s_ac2", Int(4)))
    defines.append(name_match_define("init_s_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))


    create_GSP_air_craft("g_a_1", ["init_g_ac1", "atc.ex_sugg_g_ac1_near", "atc.ex_sugg_g_ac1_far", "atc.ex_sugg_g_ac1_future"] ,sub_action_list)
    create_GSP_air_craft("g_a_2", ["init_g_ac2", "atc.ex_sugg_g_ac2_near", "atc.ex_sugg_g_ac2_far", "atc.ex_sugg_g_ac2_future"] ,sub_action_list)
    create_GSP_air_craft("g_a_3", ["init_g_ac3", "atc.ex_sugg_g_ac3_near", "atc.ex_sugg_g_ac3_far", "atc.ex_sugg_g_ac3_future"] ,sub_action_list)


    create_SSEP("s_a_1", ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3", "comm_net.ex_intent_s_ac1_future_ch_1",
                          "comm_net.ex_intent_s_ac1_future_ch_2", "comm_net.ex_intent_g_ac1", "comm_net.ex_intent_g_ac2",
                          "comm_net.ex_intent_g_ac3", "atc.ex_sugg_s_ac1_near", "atc.ex_sugg_s_ac1_far", "atc.ex_sugg_s_ac1_future"
                          ], sub_action_list)

    create_SSEP_disabled("s_a_2", ["init_s_ac2"], sub_action_list)
    create_SSEP_disabled("s_a_3", ["init_s_ac3"], sub_action_list)

    atc_input_list = []
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))

    for i in ["1", "2", "3"]:
        for loc in locations:
            atc_input_list.append("g_a_{}.intent_trj_{}_atc".format(i, loc))


    for i in index:
        for loc in locations:
            atc_input_list.append("s_a_{}.intent_trj_{}_atc".format(i, loc))

    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))

    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))


if ENABLE_2_GSEP_2_SSEP:

    defines.append(name_match_define("init_g_ac1", Int(0)))
    defines.append(name_match_define("init_s_ac1", Int(1)))
    defines.append(name_match_define("init_s_ac2", Int(2)))

    defines.append(name_match_define("init_s_ac3", Int(3)))
    defines.append(name_match_define("init_g_ac2", Int(4)))
    defines.append(name_match_define("init_g_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))
    defines.append(name_match_define("disabled_future_s_ac2", Int(7)))
    defines.append(name_match_define("disabled_future_s_ac3", Int(8)))



    create_GSP_air_craft("g_a_1", ["init_g_ac1", "atc.ex_sugg_g_ac1_near", "atc.ex_sugg_g_ac1_far", "atc.ex_sugg_g_ac1_future"], sub_action_list)
    create_GSEP_disabled("g_a_2", ["init_g_ac2"], sub_action_list)
    create_GSEP_disabled("g_a_3", ["init_g_ac3"], sub_action_list)

    s_a_1_inputs = ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_1_inputs.append("comm_net.ex_intent_s_ac1_future_ch_{}".format(i))

    for i in index:
        s_a_1_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_1_inputs.append("atc.ex_sugg_s_ac1_{}".format(loc))

    create_SSEP("s_a_1", s_a_1_inputs, sub_action_list)

    s_a_2_inputs = ["init_s_ac2", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_2_inputs.append("comm_net.ex_intent_s_ac2_future_ch_{}".format(i))

    for i in index:
        s_a_2_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_2_inputs.append("atc.ex_sugg_s_ac2_{}".format(loc))

    create_SSEP("s_a_2", s_a_2_inputs, sub_action_list)

    create_SSEP_disabled("s_a_3", ["init_s_ac3"], sub_action_list)

    atc_input_list = []
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))

    for loc in locations:
        atc_input_list.append("g_a_1.intent_trj_{}".format(loc))

    for loc in locations:
        atc_input_list.append("g_a_2.intent_trj_{}".format(loc))

    for _ in range(3):
        atc_input_list.append("init_g_ac3")


    for i in index:
        for loc in locations:
            atc_input_list.append("s_a_{}.intent_trj_{}_atc".format(i, loc))

    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))

    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))


if ENABLE_1_GSEP_3_SSEP:

    defines.append(name_match_define("init_g_ac1", Int(0)))
    defines.append(name_match_define("init_s_ac1", Int(1)))
    defines.append(name_match_define("init_s_ac2", Int(2)))

    defines.append(name_match_define("init_s_ac3", Int(3)))
    defines.append(name_match_define("init_g_ac2", Int(4)))
    defines.append(name_match_define("init_g_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))
    defines.append(name_match_define("disabled_future_s_ac2", Int(7)))
    defines.append(name_match_define("disabled_future_s_ac3", Int(8)))


    create_GSP_air_craft("g_a_1", ["init_g_ac1", "atc.ex_sugg_g_ac1_near", "atc.ex_sugg_g_ac1_far", "atc.ex_sugg_g_ac1_future"], sub_action_list)
    create_GSEP_disabled("g_a_2", ["init_g_ac2"], sub_action_list)
    create_GSEP_disabled("g_a_3", ["init_g_ac3"], sub_action_list)


    s_a_1_inputs = ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3"]

    for i in ["1", "2"]:
        s_a_1_inputs.append("comm_net.ex_intent_s_ac1_future_ch_{}".format(i))

    for i in index:
        s_a_1_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_1_inputs.append("atc.ex_sugg_s_ac1_{}".format(loc))

    create_SSEP("s_a_1", s_a_1_inputs, sub_action_list)

    s_a_2_inputs = ["init_s_ac2", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_2_inputs.append("comm_net.ex_intent_s_ac2_future_ch_{}".format(i))

    for i in index:
        s_a_2_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_2_inputs.append("atc.ex_sugg_s_ac2_{}".format(loc))

    create_SSEP("s_a_2", s_a_2_inputs, sub_action_list)


    s_a_3_inputs = ["init_s_ac3", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_3_inputs.append("comm_net.ex_intent_s_ac3_future_ch_{}".format(i))

    for i in index:
        s_a_3_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_3_inputs.append("atc.ex_sugg_s_ac3_{}".format(loc))

    create_SSEP("s_a_3", s_a_3_inputs, sub_action_list)

    atc_input_list = []
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))

    for loc in locations:
        atc_input_list.append("g_a_1.intent_trj_{}".format(loc))

    for _ in range(3):
        atc_input_list.append("init_g_ac2")

    for _ in range(3):
        atc_input_list.append("init_g_ac3")


    for i in index:
        for loc in locations:
            atc_input_list.append("s_a_{}.intent_trj_{}_atc".format(i, loc))

    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))

    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))

if ENABLE_3_SSEP:

    defines.append(name_match_define("init_s_ac1", Int(0)))
    defines.append(name_match_define("init_s_ac2", Int(1)))
    defines.append(name_match_define("init_s_ac3", Int(2)))

    defines.append(name_match_define("init_g_ac1", Int(3)))
    defines.append(name_match_define("init_g_ac2", Int(4)))
    defines.append(name_match_define("init_g_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))
    defines.append(name_match_define("disabled_future_s_ac2", Int(7)))
    defines.append(name_match_define("disabled_future_s_ac3", Int(8)))


    create_SSEP_disabled("g_a_1", ["init_g_ac1"], sub_action_list)
    create_SSEP_disabled("g_a_2", ["init_g_ac2"],sub_action_list)
    create_SSEP_disabled("g_a_3", ["init_g_ac3"], sub_action_list)

    s_a_1_inputs = ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_1_inputs.append("comm_net.ex_intent_s_ac1_future_ch_{}".format(i))

    for i in index:
        s_a_1_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_1_inputs.append("atc.ex_sugg_s_ac1_{}".format(loc))

    create_SSEP("s_a_1", s_a_1_inputs, sub_action_list)

    s_a_2_inputs = ["init_s_ac2", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_2_inputs.append("comm_net.ex_intent_s_ac2_future_ch_{}".format(i))

    for i in index:
        s_a_2_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_2_inputs.append("atc.ex_sugg_s_ac2_{}".format(loc))

    create_SSEP("s_a_2", s_a_2_inputs, sub_action_list)

    s_a_3_inputs = ["init_s_ac3", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_3_inputs.append("comm_net.ex_intent_s_ac3_future_ch_{}".format(i))

    for i in index:
        s_a_3_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_3_inputs.append("atc.ex_sugg_s_ac3_{}".format(loc))

    create_SSEP("s_a_3", s_a_3_inputs, sub_action_list)

   #TODO ATC ATC_receipt

    atc_input_list = []
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))

    for _ in range(3):
        atc_input_list.append("init_g_ac1")

    for _ in range(3):
        atc_input_list.append("init_g_ac2")

    for _ in range(3):
        atc_input_list.append("init_g_ac3")

    for i in index:
        for loc in locations:
            atc_input_list.append("s_a_{}.intent_trj_{}_atc".format(i, loc))

    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))

    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))

if ENABLE_3_GSEP_3_SSEP:

    defines.append(name_match_define("init_s_ac1", Int(0)))
    defines.append(name_match_define("init_s_ac2", Int(1)))
    defines.append(name_match_define("init_s_ac3", Int(2)))

    defines.append(name_match_define("init_g_ac1", Int(3)))
    defines.append(name_match_define("init_g_ac2", Int(4)))
    defines.append(name_match_define("init_g_ac3", Int(5)))

    defines.append(name_match_define("disabled_future_s_ac1", Int(6)))
    defines.append(name_match_define("disabled_future_s_ac2", Int(7)))
    defines.append(name_match_define("disabled_future_s_ac3", Int(8)))



    create_GSP_air_craft("g_a_1", ["init_g_ac1", "atc.ex_sugg_g_ac1_near", "atc.ex_sugg_g_ac1_far", "atc.ex_sugg_g_ac1_future"], sub_action_list)
    create_GSP_air_craft("g_a_2",
                         ["init_g_ac2", "atc.ex_sugg_g_ac2_near", "atc.ex_sugg_g_ac2_far", "atc.ex_sugg_g_ac2_future"], sub_action_list)
    create_GSP_air_craft("g_a_3",
                         ["init_g_ac3", "atc.ex_sugg_g_ac3_near", "atc.ex_sugg_g_ac3_far", "atc.ex_sugg_g_ac3_future"],sub_action_list)

    s_a_1_inputs = ["init_s_ac1", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_1_inputs.append("comm_net.ex_intent_s_ac1_future_ch_{}".format(i))

    for i in index:
        s_a_1_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_1_inputs.append("atc.ex_sugg_s_ac1_{}".format(loc))

    create_SSEP("s_a_1", s_a_1_inputs, sub_action_list)

    s_a_2_inputs = ["init_s_ac2", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_2_inputs.append("comm_net.ex_intent_s_ac2_future_ch_{}".format(i))

    for i in index:
        s_a_2_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_2_inputs.append("atc.ex_sugg_s_ac2_{}".format(loc))

    create_SSEP("s_a_2", s_a_2_inputs, sub_action_list)

    s_a_3_inputs = ["init_s_ac3", "init_g_ac1", "init_g_ac2", "init_g_ac3"]
    for i in ["1", "2"]:
        s_a_3_inputs.append("comm_net.ex_intent_s_ac3_future_ch_{}".format(i))

    for i in index:
        s_a_3_inputs.append("comm_net.ex_intent_g_ac{}".format(i))

    for loc in locations:
        s_a_3_inputs.append("atc.ex_sugg_s_ac3_{}".format(loc))

    create_SSEP("s_a_3", s_a_3_inputs, sub_action_list)


    atc_input_list = []
    for t in types:
        for i in index:
            atc_input_list.append("init_{}_ac{}".format(t, i))


    for _ in range(3):
        atc_input_list.append("init_g_ac1")

    for _ in range(3):
        atc_input_list.append("init_g_ac2")

    for _ in range(3):
        atc_input_list.append("init_g_ac3")

    for i in index:
        for loc in locations:
            atc_input_list.append("s_a_{}.intent_trj_{}_atc".format(i, loc))

    for i in index:
        atc_input_list.append("s_a_{}.request_GTM".format(i))

    for t in types:
        for i in index:
            atc_input_list.append("{}_a_{}.fault_communications_atc".format(t, i))

    sub_action_list.append(("atc", ATC.create_instance("atc"), make_input_list(atc_input_list)))

if not ENABLE_PURE_CONTROLLERS:
    comm_net = COMM_NET.create_instance("comm_net")
    comm_net_inputs = []
    for i in index:
        for loc in locations:
            comm_net_inputs.append("s_a_{}.intent_trj_{}_adsb".format(i, loc))

    for i in index:
        comm_net_inputs.append("g_a_{}.intent_trj_future_adsb".format(i))

    sub_action_list.append(("comm_net", comm_net, make_input_list(comm_net_inputs)))


def create_sub_actions(name, sub_action_list=sub_action_list):
    return sub_action_list


rule_list.append(lambda Model: forall(Model, lambda g:  Implication(g > Int(0), previous(g, lambda g1: TRUE()))))



Model_module = Module("model", inputs, argument_list, defines, rule_list, create_sub_actions)
Model = Model_module.create_instance("Model")




def get_all_rules():
    rules = Model_module.define_constraints() + ATC.define_constraints() + ATC_idle.define_constraints() +  GSEP.define_constraints() + GSEP_disabled.define_constraints() + CDR.define_constraints() + SSEP_disabled.define_constraints() +  SSEP.define_constraints() + COMM_NET.define_constraints() + COMMON_PHASE.define_constraints()

    for _, sub_action_type, _ in sub_action_list:
        rules.append(forall(sub_action_type, lambda g: same_time_events(g, Model)))

    #clock sync
    CP_union = union(list(COMMON_PHASE.instances.values()))
    rules.append(forall([CP_union, CP_union], lambda cp1, cp2: Implication(EQ(cp1.time, cp2.time), EQ(cp1.communication_counter, cp2.communication_counter))))

    return rules