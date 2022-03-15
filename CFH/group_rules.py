from covid_rule_ult import *
from analyzer import *
import time
from type_constructor import union
group_rules = []

#group can not be created if it is already exists
#group 0-2 are default groups
#group must be created by a system administrator
group_rules.append(forall(Create_Group, lambda cg: AND(cg.group > Int(2), is_doctor(cg.creator, cg.time, 0))))
group_rules.append(forall([Create_Group, Create_Group], lambda cg1, cg2: OR(cg1.build_eq_constraint(cg2), NEQ(cg1.group, cg2.group))))



#if a patient is assigned to a group, then
# (1) both the patient and the assignment processor must be available
# (2) if the assignment is the default assignment, then the patient is assigned to the RC group at the time of registration
# by the DB_user 0
# (3) if the assignment is not the default assignment, then the assignment must be processed by a BD user in the same
# group as the patient
group_rules.append(forall(AssignGroup_Patient, lambda agp: AND( group_exist(agp.group, agp.time),
                                            is_patient(agp.user, agp.time),
                                                                NOT(is_group_patient(agp.user, agp.group, agp.time-1)),
                                            OR(AND(is_active_doctor(agp.processor, agp.time),
                                                   same_group(agp.user, agp.processor, agp.time-1)),
                                               AND(EQ(agp.processor, Int(0)),
                                                   EQ(agp.group, Int(2)),
                                                   exist(Patient, lambda p: AND(EQ(p.time, agp.time), EQ(p.dsid, agp.user)))
                                               )))))

# a patient must be assigned to a default group (group 2)
group_rules.append(forall(Patient, lambda p: exist(AssignGroup_Patient, lambda agp: AND(EQ(agp.time, p.time),
                                                                                        EQ(agp.user, p.dsid),
                                                                                        EQ(agp.group, Int(2))))))


# a patient can only be unassigned by a DB user from the same group
group_rules.append(forall(UnAssignGroup_Patient, lambda ugp: AND(same_group(ugp.user, ugp.processor, ugp.time-1),
                                                                 is_active_doctor(ugp.processor, ugp.time )
                                                                 )))


# a DB user can be assigned to a group if:
# (1) the DB user is available and
# (2) the assignment processor is a system administrator
group_rules.append(forall(AssignGroup_DB, lambda agp: AND(group_exist(agp.group, agp.time),
                                                          NOT(is_group_DB(agp.user, agp.group, agp.time-1)),
                                                          doctor_group_consisent(agp.user, agp.group, agp.time),
                                            is_doctor(agp.user, agp.time),
                                            is_active_doctor(agp.processor, agp.time, role=0))))

# a doctor must be assigned to a default group
group_rules.append(forall(Doctor, lambda d: exist(AssignGroup_DB, lambda agd: AND(EQ(agd.time, d.time),
                                                                                  EQ(agd.user, d.dsid),
                                                                                  doctor_role_group_consisent(d.role, agd.group, default=True)))))


# a doctor can be removed from a group by the system administrator
group_rules.append(forall(UnassignGroup_DB, lambda ugd: AND(NEQ(ugd.user, Int(0)),
                                                            is_group_DB(ugd.user, ugd.group, ugd.time - 1),
                                                            is_active_doctor(ugd.processor, ugd.time, role = 0))))





#Invaraint: there is always at least one DB member in the RC group
group_rules.append(forall(union(Update_Request, Delection_Request), lambda request: exist(Var, lambda id: AND(is_active_doctor(id.v, request.time),
                                                                                                              is_group_DB(id.v, RC_Group, request.time)))))




if __name__ == '__main__':
    #property = exist([Var, Var, Var, Var], lambda var1, var2, var3, var4: AND(NEQ(var1.v, var2.v),
    #                                                                          is_group_patient(var3.v, var1.v, var4.v),
    #                                                                          is_group_patient(var3.v, var2.v, var4.v)))

    p = eventually(Use, lambda ur: NOT(eventually(Delete, lambda update: AND(EQ(ur.rid, update.rid), update < ur.time + Request_Delay_Time), ur.time)))
    from COVID.registration_rules import registration_rules
    from COVID.data_collection_rules import data_collection_rules
    from COVID.data_update_rules import update_rules
    from COVID.data_deletion_rules import delete_rules
    from COVID.use_rules import use_rules
    from COVID.consent_rules import consented_rules
    rules = set()
    start = time.time()
    check_property_refining(p, rules, delete_rules + group_rules + registration_rules + data_collection_rules + update_rules + use_rules + consented_rules, ACTION, state_action, True)
    print(time.time() - start)