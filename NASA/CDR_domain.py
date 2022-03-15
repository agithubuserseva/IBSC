from model_config import *
from Module import Module
from utils import *

import sys
sys.path.append('../Analyzer')
from logic_operator import *

argument_list = [("time", "time")]
input_list =[]
defines =[]
rule_list =[]
for i in range(1,4):
    input_list.append(("intent_trj_future_g_{}".format(str(i)), "Int"))

for i in range(1,3):
    input_list.append(("intent_trj_future_s_{}".format(str(i)), "Int"))


argument_list.append(("sugg_trj_future", "TRJ-0"))
argument_list.append(("internal_failure", "Boolean"))

argument_list.append(("fault_future_resolve", "Boolean"))
argument_list.append(("fault_resolve_detection", "Boolean"))


defines.append(("to_fault_future_resolve", lambda g: g.fault_future_resolve))
defines.append(("to_fault_resolve_detection", lambda g: g.fault_resolve_detection))

if not EXTENDED_MODEL and not ENABLE_PURE_CONTROLLERS:
    rule_list.append(inv_rules(lambda g: AND(NOT(g.fault_future_resolve), NOT(g.fault_resolve_detection)) ))

if ENABLE_PURE_CONTROLLERS:
    rule_list.append(inv_rules(lambda g: NOT(g.fault_resolve_detection)))

for i in range(1,4):
    intent = "intent_trj_future_g_{}".format(str(i))
    defines.append(("future_conflict_w_g_{}".format(str(i)), lambda g: AND(NEQ(getattr(g, intent), Int(-1)), EQ(g.sugg_trj_future, getattr(g, intent )))))

for i in range(1,3):
    intent = "intent_trj_future_s_{}".format(str(i))
    defines.append(("future_conflict_w_s_{}".format(str(i)), lambda g: AND(NEQ(getattr(g, intent), Int(-1)), EQ(g.sugg_trj_future, getattr(g, intent)))))

defines.append(("future_conflict", lambda g: OR(g.future_conflict_w_g_1, g.future_conflict_w_g_2, g.future_conflict_w_g_3,
                                                g.future_conflict_w_s_1, g.future_conflict_w_s_2)))


if not ENABLE_PURE_AIRSPACE:
    rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_future_resolve), NOT(g.future_conflict))))
    rule_list.append(inv_rules(lambda g: Implication(NOT(g.fault_resolve_detection), IFF(g.fault_future_resolve, g.internal_failure))))



CDR = Module("CDR", input_list, argument_list, defines, rule_list, None)