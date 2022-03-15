from CDR_domain import CDR
from CommNet_domain import *

input_list = []
argument_list = [("time", "time")]
defines = []
rule_list = []

input_list.append(("init_trj", "Int"))
#cdr.to_fault_future_resolve := FALSE;
#defines.append(("cdr.to_fault_future_resolve", lambda g: FALSE()))
for loc in locations:
    defines.append(("to_fault_apply_{}".format(loc), lambda g: FALSE()))

defines.append(("to_fault_communications_atc", lambda g: FALSE()))
defines.append(("to_fault_communications_atc_par", lambda g: FALSE()))
defines.append(("to_fault_communications_atc_tot", lambda g: FALSE()))
defines.append(("to_fault_communications_adsb", lambda g: FALSE()))
#cdr.to_fault_resolve_detection := FALSE;
#defines.append(("cdr.to_fault_resolve_detection", lambda g: FALSE()))
defines.append(("fault_communications_atc", lambda g: FALSE()))

defines.append((name_match_define("current_trj", "init_trj")))
defines.append((name_match_define("intent_trj_near", "init_trj")))
defines.append((name_match_define("intent_trj_far", "init_trj")))
defines.append((name_match_define("intent_trj_future", "init_trj")))
defines.append((name_match_define("intent_trj_near_atc", "init_trj")))
defines.append((name_match_define("intent_trj_far_atc", "init_trj")))
defines.append((name_match_define("intent_trj_future_atc", "init_trj")))

defines.append((name_match_define("intent_trj_near_adsb", "init_trj")))
defines.append((name_match_define("intent_trj_far_adsb", "init_trj")))
defines.append((("intent_trj_future_adsb", lambda g: Int(-1))))

defines.append((name_match_define("X_current_trj", "init_trj")))
defines.append((name_match_define("X_intent_trj_near", "init_trj")))
defines.append((name_match_define("X_intent_trj_far", "init_trj")))
defines.append((name_match_define("X_intent_trj_future", "init_trj")))

defines.append((name_match_define("int_sugg_trj_future", "init_trj")))

defines.append(("request_GTM", lambda g: FALSE()))

rule_list.append(lambda Type: forall([Type, Type], lambda g1, g2: Implication(NOT(EQ(g1, g2)), NEQ(g1.time, g2.time))))

SSEP_disabled = Module("SSEP_disabled", input_list,
                       argument_list, defines, rule_list)