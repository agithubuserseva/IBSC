from pysmt.typing import INT, BOOL
from pysmt.shortcuts import Equals, NotEquals, Int
from config2 import *

import sys
sys.path.append('../Analyzer')
from type_constructor import create_type

INIT_FUTURE_INTENT = True

if ENABLE_3_GSEP_3_SSEP or ENABLE_PURE_AIRSPACE or ENABLE_PURE_CONTROLLERS:
    TRJ_NUM = 5
elif ENABLE_3_GSEP or ENABLE_3_SSEP:
    TRJ_NUM = 2
else:
    TRJ_NUM = 3

S_COMM_FAILURE_G_ATC = 4
S_COMM_FAILURE_G_ADSB = 0
S_COMM_FAILURE_S_ATC = 4
S_COMM_FAILURE_S_ADSB = 0

COMM_STEPS = 3




type_dict = dict()
ACTION = []
state_action = []
def CT(type_name, upper_bound=None, lower_bound=None, var_type=INT, enum = None):
    return create_type(type_name, type_dict, upper_bound, lower_bound, var_type, enum)

CT("Boolean", var_type=BOOL)
CT("Int")
CT("time", lower_bound= 0, upper_bound=20)
CT("TRJ-0", lower_bound=0, upper_bound=TRJ_NUM)
CT("TRJ-1", lower_bound=-1, upper_bound=TRJ_NUM)
CT("communication_counter", lower_bound=0, upper_bound=COMM_STEPS)
CT("S_COMM_FAILURE_G_ATC-0", lower_bound=0, upper_bound=S_COMM_FAILURE_G_ATC)
CT("S_COMM_FAILURE_G_ADSB-0", lower_bound=0, upper_bound=S_COMM_FAILURE_G_ADSB)
CT("CFG_ATC", lower_bound=0 ,upper_bound=S_COMM_FAILURE_G_ATC)
CT("CFG_ADSB", lower_bound=0 ,upper_bound=S_COMM_FAILURE_G_ADSB)
CT("communication_counter", lower_bound=0, upper_bound=COMM_STEPS)

EQ = Equals
NEQ = NotEquals


def init(g):
    return EQ(g.time , Int(0))