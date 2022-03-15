from covidfree_domain import *
from covid_rule_ult import *
from analyzer import *
from type_constructor import union

registration_rules =[]

#no doctor and patient can have the same ID
User = union(Doctor, Patient)
# no two user can have the same ID
registration_rules.append(forall([User, User], lambda user1, user2: OR(EQ(user1, user2), NEQ(user1.dsid, user2.dsid))))

# exists a system administrator at the start of the project
registration_rules.append(exist(Doctor, lambda d: AND(EQ(d.time, Int(0)), EQ(d.dsid, Int(0)), EQ(d.role, Int(0)))))

#leave
registration_rules.append(forall(Leave, lambda leave: is_registered(leave.dsid, leave.time-1)))

#deactivate
#am user may be deactivated if it is an active user
registration_rules.append(forall(Deactivate, lambda da: is_active_registered(da.dsid, da.time -1)))

# a patient become inactive if it has not been collecting data for 2 days
registration_rules.append(forall(union(Patient, Collect), lambda start: Implication(AND(NOT(eventually(Collect, lambda col: AND(col > start,
                                                                                                                EQ(col.dsid,
                                                                                                                   start.dsid),
                                                                                                                col < start.time + day(2)
                                                                                                                ), start.time)), is_active_patient(start.dsid, start.time + day(2) - 1)),
                                                                                       exist(Deactivate, lambda da: AND(EQ(da.dsid, start.dsid),
                                                                                                                        EQ(da.time, start.time + day(2) )))
                                                                                        )))

# a DB user become inactive every 40 days
registration_rules.append(forall(union(Doctor, Activate), lambda start: Implication(AND(NEQ(start.dsid, Int(0)),
                                                                                        NOT(eventually(Deactivate, lambda da:
                                                                                                       AND(EQ(da.dsid, start.dsid),
                                                                                                           da.dsid < start.time + day(40)),
                                                                                                       start.time)),
                                                                                        is_active_doctor(start.dsid, start.time + day(40) - 1)),
                                                                                    exist(Deactivate, lambda da: AND(EQ(da.dsid, start.dsid),
                                                                                                                     EQ(da.time, start.time + day(40))))
                                                                                                       )))



#activate
# a user can be activated if it is in active user
registration_rules.append(forall(Activate, lambda ac: AND(is_registered(ac.dsid, ac.time), is_inactive(ac.dsid, ac.time-1))))

#if an user became inactive for 2 days without activating his account, he will leave the study
registration_rules.append(forall(Deactivate, lambda da: Implication(AND(is_patient(da.dsid, da.time + day(2) -1),
                                                                    NOT(eventually(Activate, lambda ac: AND(
                                                                        EQ(ac.dsid, da.dsid),
                                                                        ac.time < da.time + day(2)
                                                                    ), da.time))),
                                                                    exist(Leave, lambda leave: AND(EQ(leave.time, da.time + day(2)),
                                                                                                   EQ(leave.dsid, da.dsid)))
                                                                    )))

#registratoion rule: At the time of patient's registratoin, the patient will be informed about the study's detail including
#data collection
registration_rules.append(forall(Patient, lambda p: exist(Inform, lambda info: AND(EQ(info.time, p.time),
                                                                                   EQ(info.dsid, p.dsid)))))