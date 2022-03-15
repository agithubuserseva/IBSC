from covid_config import b_data, b_dataid, b_dsid
import sys
sys.path.append('../Analyzer')
from type_constructor import create_type, create_action
type_dict = dict()

data = create_type("data", type_dict, lower_bound=0, upper_bound = b_data)
dataid = create_type("dataid", type_dict, lower_bound=0, upper_bound = b_dataid)
dsid = create_type("dsid", type_dict, lower_bound=0, upper_bound = b_dsid)
pid = create_type("pid" , type_dict, lower_bound= 0) # processorid
time = create_type("time", type_dict, lower_bound=0)
rid = create_type("rid", type_dict, lower_bound=-1)
hid = create_type("hid", type_dict, lower_bound=0)
#0: SA, 1, physican, 2 RA
group_id = create_type("gid", type_dict, lower_bound=0)
# 0: SA, 1: DOC, 2: Nurse, 3: RA
role = create_type("role", type_dict, lower_bound=0, upper_bound=3)
var = create_type("var", type_dict)

Var = create_action("Var", [("v", "var"), ("time", "time")],type_dict)

Delection_Request = create_action("Deletion_Request", [("dataid", "dataid"),("dsid", "dsid"),("time", "time"), ("rid", "rid")], type_dict)
Delete  =create_action("Delete", [("dataid", "dataid"), ("dsid", "dsid"),("time", "time"), ("rid", "rid")], type_dict)

Access_Request = create_action("Access_Request", [("accessor", "dsid"), ("time", "time"), ("accessee", "dsid")], type_dict)
Consent = create_action("Consent", [("dsid", "dsid"),("time", "time")], type_dict)
Restrict = create_action("Restrict", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time")], type_dict)
Repeal = create_action("Repeal", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time")], type_dict)
Object = create_action("Object", [("data", "data"), ("dsid", "dsid"),("time", "time")], type_dict)
Legal_ground  =create_action("Legal ground", [("data", "data"), ("dsid", "dsid"),("time", "time")], type_dict)
Revoke  =create_action("Revoke", [("dsid", "dsid"),("time", "time")], type_dict)
Grant_access = create_action("grant access",  [("accessor", "dsid"), ("time", "time"), ("accessee", "dsid")], type_dict)
Share_with = create_action("Share with", [("pid", "pid"), ("dataid", "dataid"),("time", "time")], type_dict)
Inform = create_action("Inform", [("dsid", "dsid"), ("time", "time")], type_dict)
Notify_proce = create_action("Notify proc", [("pid", "pid"), ("dataid", "dataid"),("time", "time")], type_dict)
Use = create_action("Use", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time")], type_dict)
Collect = create_action("Collect", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time")], type_dict)

Update_Request = create_action("Request_Update", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time"), ("rid", "rid")], type_dict)
Update = create_action("Update", [("data", "data"), ("dataid", "dataid"), ("dsid", "dsid"),("time", "time"),  ("rid", "rid")], type_dict)

Doctor = create_action("DBUser", [ ("dsid", "dsid"),("time", "time"), ("role", "role")], type_dict)
Patient = create_action("Register_Patient", [ ("dsid", "dsid"), ("hid", "hid"), ("time", "time")], type_dict)

Assign_Contact = create_action("Assign_Contact", [("dsid", "dsid"), ("hid", "hid"), ("time", "time")], type_dict)

Leave = create_action("Leave", [ ("dsid", "dsid"),("time", "time")], type_dict)

AssignGroup_Patient = create_action("AssignGroup_Patient", [("user", "dsid"), ("group", "gid"), ("processor", "dsid"), ("time", "time")],type_dict)
UnAssignGroup_Patient = create_action("UnAssignGroup_Patient", [("user", "dsid"), ("group", "gid"), ("processor", "dsid"), ("time", "time")],type_dict)
AssignGroup_DB = create_action("AssignGroup_BD", [("user", "dsid"), ("group", "gid"), ("processor", "dsid"), ("time", "time")], type_dict)
UnassignGroup_DB = create_action("UnassignGroup_BD", [("user", "dsid"), ("group", "gid"), ("processor", "dsid"), ("time", "time")], type_dict)

Create_Group = create_action("Create_Group", [("group", "gid"), ("creator", "dsid"), ("time", "time")], type_dict)

Activate = create_action("Activate", [("dsid", "dsid"), ("time", "time")], type_dict)
Deactivate = create_action("Deactivate", [("dsid", "dsid"), ("time", "time")], type_dict)

TimeStamp = create_action("TimeStamp", [("time", "time")],type_dict)


ACTION = [Doctor, Patient, Leave, TimeStamp, Delection_Request,
          Access_Request, Consent, Restrict, Repeal, Object, Legal_ground, Revoke, Delete,
          Grant_access, Share_with, Inform, Notify_proce, Use,
          Collect, Update, Assign_Contact, Update_Request,
          AssignGroup_Patient, UnAssignGroup_Patient,
          AssignGroup_DB, UnassignGroup_DB,
          Deactivate, Activate, Var]
state_action = [TimeStamp]
