from covid_rule_ult import *

update_rules = []


#the data update must have the following precondition
# (1) for dataid, the data must be available
update_rules.append(forall(Update, lambda update: is_available(update.dataid, update.time)))
# (2) for dsid, the person must be an active doctor who is in the same group as the data owner
update_rules.append(forall(Update, lambda update: AND(is_active_doctor(update.dsid, update.time),
                                                      once(Collect, lambda collect: AND(EQ(collect.dataid, update.dataid),
                                                                                        same_group(collect.dsid, update.dsid, update.time)
                                                                                        ), update.time-1)
                                                      )))
# (3) for rid, it is either -1, or an out-standing rid
update_rules.append(forall(Update, lambda update: OR(EQ(update.rid, Int(-1)), is_updated_requested(update))) )





#the data update request must have the following precondition
#(1) the data must be available
update_rules.append(forall(Update_Request, lambda ur: is_available(ur.dataid, ur.time)))
# (2) the owner must be a data owner
update_rules.append(forall(Update_Request, lambda ur: own_data(ur.dataid, ur.dsid, ur.time -1)))
# (3) every rid must be unique
update_rules.append(forall([Update_Request, Update_Request], lambda ur1, ur2: OR(EQ(ur1, ur2), NEQ(ur1.rid, ur2.rid))))
# （4） requested rid must be >= 0
update_rules.append(forall(Update_Request, lambda ur: ur.rid >= Int(0)))



#Update Obligation:
#when an update request is made to a group, some active member of the group must process the request within 30 days if possible
update_rules.append(forall(Update_Request, lambda ur: Implication(exist(Doctor, lambda d: AND(is_active_doctor(d.dsid, ur.time),
                                                                                              is_group_DB(d.dsid, RC_Group, ur.time),
                                                                                              is_group_patient(ur.dsid, RC_Group, ur.time))),
                                                                  eventually(Update, lambda update: AND(EQ(update.rid, ur.rid), update < ur.time + Request_Delay_Time), ur.time)
                                                                  )))