from covidfree_domain import *
from logic_operator import *



def day(num):
    return Int(24*num)

def week(num):
    return Int(24*7* num)


def is_available(dataid, time):
    return since(Collect, lambda col: AND(EQ(col.dataid, dataid), col < time ), Delete, lambda delet: EQ(delet.dataid, dataid) ,time)

def data_values(dataid, data, time):
    return OR(since(Collect, lambda  col: AND(EQ(col.dataid, dataid), EQ(col.data, data), col < time), Update, lambda update:  AND(EQ(update.dataid, dataid), NEQ(update.data, data)), time),
              since(Update, lambda col: AND(EQ(col.dataid, dataid), EQ(col.data, data)), Update,
                    lambda update: AND(EQ(update.dataid, dataid), NEQ(update.data, data)), time - 1))


def own_data(dataid, dsid, time):
    return once(Collect, lambda collect: AND(EQ(collect.dataid, dataid), EQ(collect.dsid, dsid)), time -1)

def is_patient(dsid, time):
    return since(Patient, lambda patient: EQ(patient.dsid, dsid), Leave, lambda leave: EQ(leave.dsid, dsid), time)

def is_active_patient(dsid, time):
    return AND(is_patient(dsid, time), is_active(dsid,time))

def is_doctor(dsid, time, role=-1):
    if role == -1:
        return since(Doctor, lambda patient: EQ(patient.dsid, dsid), Leave, lambda leave: EQ(leave.dsid, dsid), time)
    else:
        return since(Doctor, lambda patient: AND(EQ(patient.dsid, dsid), EQ(patient.role, Int(role))), Leave, lambda leave: EQ(leave.dsid, dsid), time)

def is_active_doctor(dsid, time, role = -1):
    return AND(is_doctor(dsid, time, role = role), is_active(dsid, time))

def is_registered(dsid, time):
    return OR(is_doctor(dsid, time), is_patient(dsid, time))

def is_active_registered(dsid, time):
    return AND(is_registered(dsid, time), is_active(dsid, time))

def group_match(patient, group_id):
    return EQ(patient, group_id)

def is_group_patient(patient, group_id, time):
    return since(AssignGroup_Patient, lambda agp: AND(EQ(agp.user, patient), EQ(agp.group, group_id)),
                                                      UnAssignGroup_Patient,
                 lambda ugp: AND(EQ(ugp.user, patient), EQ(ugp.group, group_id)), time)


def is_group_DB(patient, group_id, time):
    return since(AssignGroup_DB, lambda agp: AND(EQ(agp.user, patient), EQ(agp.group, group_id)),
                                                      UnassignGroup_DB,
                 lambda ugp: AND(EQ(ugp.user, patient), EQ(ugp.group, group_id)), time)

def same_group(patient, doctor, time):
    return exist(Var, lambda var: AND(is_group_patient(patient, var.v, time), is_group_DB(doctor, var.v, time)))

def group_exist(group, time):
    return OR(AND(GE(group, Int(0)), LE(group, Int(2))), once(Create_Group, lambda cg: EQ(group, cg.group), time))

def doctor_role_group_consisent(role, group, default = False):
    if default:
        return AND(Implication(EQ(group, Int(0)), EQ(role, Int(0))),
                  Implication(EQ(group, Int(2)), EQ(role, Int(3))),
                  Implication(EQ(group, Int(1)), OR(EQ(role, Int(3)), EQ(role, Int(2))))
                  )
    else:
        return OR(GT(group, Int(2)),
                  AND(Implication(EQ(group, Int(0)), EQ(role, Int(0))),
                      Implication(EQ(group, Int(2)), EQ(role, Int(3))),
                      Implication(EQ(group, Int(1)), OR(EQ(role, Int(3)), EQ(role, Int(2))))
                      )
                  )

def doctor_group_consisent(dsid, group, time):
    return once(Doctor, lambda d: AND(EQ(dsid, d.dsid),
                                      doctor_role_group_consisent(d.role, group)), time)



def is_inactive(dsid, time):
    return since(Deactivate, lambda da: EQ(da.dsid, dsid), Activate, lambda ac: EQ(ac.dsid, dsid), time)

def is_active(dsid, time):
    return NOT(is_inactive(dsid, time))

def matching_update(update, ur):
    return AND(EQ(ur.rid, update.rid),
               EQ(ur.dataid, update.dataid),
               EQ(ur.data, update.data))

def matching_delete(d1, d2):
    return AND(EQ(d1.rid, d2.rid),
               EQ(d1.dataid, d2.dataid))

#check if an update is requested
def is_updated_requested(update):
    return since(Update_Request, lambda ur: matching_update(update, ur), Update,
                 lambda ur1:  matching_update(update, ur1), update.time
                 )

def is_deletion_requested(delete):
    return since(Delection_Request, lambda ud: matching_delete(delete, ud), Delete,
                 lambda d1:  matching_delete(d1, delete), delete.time
                 )


def is_consented(dsid, time):
    return since(Consent, lambda consent: EQ(consent.dsid, dsid), Revoke, lambda revoke: EQ(revoke.dsid, dsid), time)

AD_Role = 0
Doctor_Role = 1
Nurse_Role = 2
RC_Role =3


AD_Group = Int(0)
CL_Group = Int(1)
RC_Group  = Int(2)

Patient_Inactive_time = day(2)
Request_Delay_Time = day(30)
