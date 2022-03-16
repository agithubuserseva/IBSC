import sys
sys.path.append('../log_generation')
from registration_rules import registration_rules
from data_collection_rules import data_collection_rules
from data_update_rules import update_rules
from data_deletion_rules import delete_rules
from use_rules import use_rules
from consent_rules import consented_rules
from group_rules import group_rules
from covid_rule_ult import *
from logic_operator import *
from analyzer import check_property_refining
import time

# if a data is use, then it should be accurate and update_to_date
rule_1 = eventually(Use, lambda use: OR(exist(Collect, lambda collect: AND(EQ(collect.dataid, use.dataid),
                                                                           NEQ(collect.data, use.data),
                                                                           collect < use,
                                                                           NOT(exist(Collect, lambda collect_1:
                                                                                     AND(EQ(collect_1.dataid, use.dataid),
                                                                                         EQ(collect_1.data, use.data),
                                                                                         collect_1 >= collect,
                                                                                         collect_1 < use)
                                                                                     )),
                                                                            NOT(exist(Update, lambda collect_1:
                                                                                     AND(EQ(collect_1.dataid, use.dataid),
                                                                                         EQ(collect_1.data, use.data),
                                                                                         collect_1 >= collect,
                                                                                         collect_1 < use)
                                                                                     )),
                                                                           )),
                                        OR(exist(Update, lambda collect: AND(EQ(collect.dataid, use.dataid),
                                                                           NEQ(collect.data, use.data),
                                                                           collect < use,
                                                                           NOT(exist(Collect, lambda collect_1:
                                                                                     AND(EQ(collect_1.dataid, use.dataid),
                                                                                         EQ(collect_1.data, use.data),
                                                                                         collect_1 >= collect,
                                                                                         collect_1 < use)
                                                                                     )),
                                                                            NOT(exist(Update, lambda collect_1:
                                                                                     AND(EQ(collect_1.dataid, use.dataid),
                                                                                         EQ(collect_1.data, use.data),
                                                                                         collect_1 >= collect,
                                                                                         collect_1 < use)
                                                                                     )),
                                                                           ))


                                        )))

#individual has the permission to delete their data: if a data is requested to be deleted, it has to be deleted within 30 days
rule_2 = eventually(Delection_Request, lambda dr: AND(once(Collect, lambda collect: AND(EQ(collect.dataid, dr.dataid),
                                                                                        EQ(collect.dsid, dr.dsid),
                                                                                        ), dr.time), NOT(eventually(Delete, lambda delete: AND(
                                                                                                                    delete.time < dr.time + Request_Delay_Time,
                                                                                                                    EQ(delete.dataid, dr.dataid))
                                                                                                                    ), dr)))

#if a data is used ,then it must be consented
rule_3 = eventually(Use, lambda use: exist(Collect, lambda collect: AND( EQ(collect.dataid, use.dataid), NOT(is_consented(collect.dsid, use.time)))))


#individual has the permission to update their data: if a data is requested to be update, it has to be updated within 30 days
rule_4 = eventually(Update_Request, lambda dr: AND(once(Collect, lambda collect: AND(EQ(collect.dataid, dr.dataid),
                                                                                        EQ(collect.dsid, dr.dsid),
                                                                                        ), dr.time), NOT(eventually(Update, lambda delete: AND(
                                                                                                                    delete.time < dr.time + Request_Delay_Time,
                                                                                                                    EQ(delete.dataid, dr.dataid))
                                                                                                                    ), dr.time)))

#GDPR rules
#every data being collected will eventually be used: data minimialisation
rule_5 = NOT(forall(Collect, lambda collect : eventually(Use, lambda use: EQ(use.dataid, collect.dataid), collect.time)))

#every data being collected will eventually eventually be deleted
rule_6 = NOT(forall(Collect, lambda collect : eventually(Delete, lambda delete: EQ(delete.dataid, collect.dataid), collect.time)))

#inform on data collection
rule_7 =NOT(forall(Collect, lambda collect: OR(once(Inform, lambda info: EQ(info.dsid, collect.dsid), collect.time),
                                               exist(Inform, lambda info: AND(EQ(info.dsid, collect.dsid),
                                                                        EQ(info.dsid, collect.dsid + 1)
                                                                              )
                                               ))))
#Right to erasure
rule_8 = NOT(forall(Use, lambda use: NOT(once(Delete, lambda delete: AND(EQ(delete.dataid, use.dataid)), use.time ))))

if __name__ == '__main__':
    args = sys.argv[1:]
    target_rule = globals()["rule_{}".format(args[0])]


    assert len(args) >= 2
    bound = int(args[1])

    if len(args) >= 3 and args[2] == "min":
        min = True
    else:
        min = False



    print(min)
    #volume_bound = int(args[1])
    #property = exist([Var, Var, Var, Var], lambda var1, var2, var3, var4: AND(NEQ(var1.v, var2.v),
    #                                                                          is_group_patient(var3.v, var1.v, var4.v),
    #                                                                          is_group_patient(var3.v, var2.v, var4.v)))

    #p = eventually(Use, lambda ur: NOT(eventually(Delete, lambda update: AND(EQ(ur.rid, update.rid), update < ur.time + Request_Delay_Time), ur.time)))
    complete_rules = delete_rules + group_rules + registration_rules + data_collection_rules + update_rules + use_rules + consented_rules
    rules = set()
    start = time.time()
    check_property_refining(target_rule, rules, complete_rules , ACTION, state_action, True, min_solution=min, final_min_solution=True, vol_bound=bound)
    print(time.time() - start)