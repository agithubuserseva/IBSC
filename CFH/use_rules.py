from covid_rule_ult import *
use_rules = []

#precondition for using a patient's data
#(1) the data nee to be available,
use_rules.append(forall(Use, lambda use: is_available(use.dataid, use.time)))
#(2) the data being use for must be update-to-date
use_rules.append(forall(Use, lambda use: data_values(use.dataid, use.data, use.time)))
#(3) the data user must be an active doctor, and in the same group as the patient
use_rules.append(forall(Use, lambda use: AND(is_active_doctor(use.dsid, use.time),
                                             once(Collect, lambda collect:
                                                  AND( EQ(collect.dataid, use.dataid),
                                                      same_group(collect.dsid, use.dsid, use.time))
                                                  , use.time -1
                                                  ))))