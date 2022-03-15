from model_config import *
from utils import is_next
from Module import Module
from utils import *

import sys
sys.path.append('../Analyzer')
from logic_operator import *

def init(g):
    return EQ(g.time , Int(0))

index = ["1", "2", "3"]
locations = ["near", "far", "future"]
types = ["s", "g"]


inputs = []
if COMM_STEPS > 0:
    common_phase_argument_list = [("time", "time"), ("communication_counter", "communication_counter")]
    defines = [("communication_step", lambda g: NEQ(g.communication_counter, Int(COMM_STEPS)))]
    rules = []
    rules.append(assign_init_rule(lambda g: EQ(g.communication_counter, Int(0))))
    rules.append(assign_next_rule(lambda cp1, cp2: Implication(is_next(cp1, cp2),
                                                                      EQ(cp2.communication_counter, ITE(EQ(cp1.communication_counter, Int(COMM_STEPS)),
                                                                                                        Int(0),
                                                                                                     cp1.communication_counter + Int(1))))))
else:
    rules = []
    common_phase_argument_list = []
    defines = [("communication_step", lambda g: FALSE())]


COMMON_PHASE = Module("Common_Phase", inputs, common_phase_argument_list, defines, rules)


input_list =[]
argument_list =[("time", "time")]
defines = []
rule_list = []

for i in index:
    for loc in locations:
        input_list.append(("intent_s_ac{}_{}".format(i, loc), "Int"))

for i in index:
    input_list.append(("intent_g_ac{}_future".format(i), "Int"))

for loc in locations:
    defines.append(name_match_define("ex_intent_s_ac1_{}_ch_1".format(loc), "intent_s_ac2_{}".format(loc)))
    defines.append(name_match_define("ex_intent_s_ac1_{}_ch_2".format(loc), "intent_s_ac3_{}".format(loc)))

    defines.append(name_match_define("ex_intent_s_ac2_{}_ch_1".format(loc), "intent_s_ac1_{}".format(loc)))
    defines.append(name_match_define("ex_intent_s_ac2_{}_ch_2".format(loc), "intent_s_ac3_{}".format(loc)))

    defines.append(name_match_define("ex_intent_s_ac3_{}_ch_1".format(loc), "intent_s_ac1_{}".format(loc)))
    defines.append(name_match_define("ex_intent_s_ac3_{}_ch_2".format(loc), "intent_s_ac2_{}".format(loc)))

for i in index:
    defines.append(name_match_define("ex_intent_g_ac{}".format(i), "intent_g_ac{}_future".format(i)))

COMM_NET = Module("COMM_NET", input_list, argument_list, defines, rule_list)