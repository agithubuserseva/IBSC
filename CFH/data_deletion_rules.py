from covid_rule_ult import *

delete_rules =[]

#the data deletion must have the following precondition
# (1) for dataid, the data must be avao;an;e
delete_rules.append(forall(Delete, lambda delete: is_available(delete.dataid, delete.time -1)))
# (2) for dsid, the person must be an active doctor who is in the same group as the data owner
delete_rules.append(forall(Delete, lambda delete: AND(is_active_doctor(delete.dsid, delete.time),
                                                      once(Collect, lambda collect: AND(EQ(collect.dataid, delete.dataid),
                                                                                        same_group(collect.dsid, delete.dsid, delete.time)
                                                                                        ), delete.time-1)
                                                      )))
# (3) for rid, it is either -1, or an out-standing rid
delete_rules.append(forall(Delete, lambda delete: OR(EQ(delete.rid, Int(-1)), is_deletion_requested(delete))) )


#the data deletion request must have the following precondition
#(1) the data must be available
delete_rules.append(forall(Delection_Request, lambda dr: is_available(dr.dataid, dr.time)))
# (2) the owner must be a data owner
delete_rules.append(forall(Delection_Request, lambda dr: own_data(dr.dataid, dr.dsid, dr.time -1)))
# (3) every rid must be unique
delete_rules.append(forall([Delection_Request, Delection_Request], lambda dr1, dr2: OR(EQ(dr1, dr2), NEQ(dr1.rid, dr2.rid))))
# （4） requested rid must be >= 0
delete_rules.append(forall(Delection_Request, lambda dr: dr.rid >= Int(0)))

#Delete Obligation:
#when an Delete request is made to a group, some active member of the group must process the request within 30 days if possible
delete_rules.append(forall(Delection_Request, lambda dr: Implication(exist(Doctor, lambda d: AND(is_active_doctor(d.dsid, dr.time),
                                                                                              is_group_DB(d.dsid, RC_Group, dr.time),
                                                                                              is_group_patient(dr.dsid, RC_Group, dr.time))),
                                                                  eventually(Delete, lambda delete: AND(EQ(delete.dataid, dr.dataid), delete < delete.time + Request_Delay_Time), dr.time)
                                                                  )))