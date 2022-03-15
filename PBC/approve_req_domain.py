from type_constructor import create_type, create_action, create_pair_action
type_dict = dict()
id = create_type("id", type_dict, lower_bound=0, upper_bound=100000)
data = create_type("data", type_dict, lower_bound=0, upper_bound=1000000)
time = create_type("time", type_dict, lower_bound=0, upper_bound=10000000)

Accountant_start = create_action("Account_start", [("id", "id"), ("time", "time")],type_dict)
Accountant_end = create_action("Account_end", [("id", "id"), ("time", "time")],type_dict)

Manager_start = create_action("Manager_start", [("manager", "id"), ("acc", "id"), ("time", "time")],type_dict)
Manager_end = create_action("Manager_end", [("manager", "id"), ("acc", "id"), ("time", "time")],type_dict)

Publish = create_action("Publish", [("acc", "id"), ("data", "data"), ("time", "time")] ,type_dict)
Promote = create_action("Promote", [("acc", "id"), ("time", "time")] ,type_dict)
Approve = create_action("Approve", [("manager", "id"), ("data", "data"), ("time", "time")], type_dict)
TimeStamp = create_action("TimeStamp", [("time", "time")],type_dict)

ACTION = [TimeStamp, Accountant_start, Accountant_end, Manager_start, Manager_end, Publish, Approve]
state_action = [TimeStamp]

inital_manager = 0