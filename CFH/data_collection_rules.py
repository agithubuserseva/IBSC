from covid_rule_ult import *


data_collection_rules = []
#collision rule, no collection of the same data
data_collection_rules.append(forall([Collect, Collect], lambda c1, c2: OR(EQ(c1, c2), NEQ(c1.dataid, c2.dataid))))

#precondition
#on dsid, - dsid must be an active patient
data_collection_rules.append(forall(Collect, lambda collect: is_active_patient(collect.dsid, collect.time)))