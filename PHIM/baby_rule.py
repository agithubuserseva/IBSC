from logic_operator import *
from baby_ddomain import *
from analyzer import check_property_refining, prove_by_induction
import time

########################################################################
# Shortcuts
########################################################################

EQ = Equals
NEQ = NotEquals

########################################################################
# Declarative model
########################################################################

def get_action_name(action_id):
    if action_id == 1:
        return "access"
    elif action_id == 2:
        return "disclose"

action_iteration_bound = 1000

#pid starts with pid 0
root_pid = forall(Collect, lambda collect1 : Implication(GT(collect1.pid, Int(0)),
                                                             exist(Collect, lambda collect2: AND(EQ(collect2.pid, Int(0)), collect2 < collect1))))

# patient id unique and increasing
incrementing_pid = forall(Collect, lambda collect1 : Implication(GT(collect1.pid, Int(0)),
                                                             OR(exist(Collect, lambda collect2: And(
                                                                 (EQ(collect1.pid, Plus(collect2.pid, Int(1)))),
                                                             collect2 < collect1)))))

#pids are collected in order
increasing_pid = forall(Collect, lambda collect1 : forall(Collect, lambda collect2: Implication(collect1 > collect2,
                                                                                                 GT(collect1.pid, collect2.pid))))

# A data can be collected only once
no_double_collect = forall(Collect, lambda c1: forall(Collect, lambda c2: Implication(NOT(c1.build_eq_constraint(c2)),
                                                                                      NEQ(c1.pid, c2.pid))))

#update after collection but before deletion
update_after_collection = forall(Request_Update, lambda update: once(Collect, lambda collect: AND(
                                                                                           EQ(collect.pid, update.pid),
                                                                                           EQ(collect.subject, update.subject),
                                                                                                   NOT(exist(Erase, lambda erase: AND(
                                                                                                             erase <= update,
                                                                                                             erase >= collect,
                                                                                                             EQ(erase.pid, collect.pid))
                                                                                                             ))), update.time))

#a pid can be accessed only if it has been collected
access_after_collection = forall(Access, lambda access: exist(Collect, lambda collect: AND(collect < access,
                                                                                           EQ(collect.pid, access.pid))))

#the value of access is the most update to date
access_up_to_date_u =  forall(Access, lambda access: forall(Update, lambda update: Implication(AND(update < access,
                                                                                           EQ(update.pid, access.pid),
                                                                                      NEQ(update.pvalue, access.pvalue)),
                                                                                              exist(Update, lambda update1:
                                                                                                    AND(update1 < access,
                                                                                                        update1 > update,
                                                                                                        EQ(update1.pid,
                                                                                                               access.pid),
                                                                                                        EQ(update1.pvalue,
                                                                                                               access.pvalue))))))

access_up_to_date_c =  forall(Access, lambda access: forall(Collect, lambda update: Implication(AND(update < access,
                                                                                           EQ(update.pid, access.pid),
                                                                                      NEQ(update.pvalue, access.pvalue)),
                                                                                              exist(Update, lambda update1:
                                                                                                    AND(update1 < access,
                                                                                                        update1 > update,
                                                                                                        EQ(update1.pid,
                                                                                                               access.pid),
                                                                                                        EQ(update1.pvalue,
                                                                                                               access.pvalue))))))
access_up_to_date = AND(access_up_to_date_c, access_up_to_date_u)

access_not_deleted = forall([Access, Erase], lambda ac, er: Implication(EQ(ac.pid, er.pid),
                                                                        ac < er))

request_to_update_fullfilled = forall(Request_Update, lambda ur: exist(Update, lambda update:
                                                                       AND(EQ(ur.pid, update.pid),
                                                                           EQ(ur.subject, update.subject),
                                                                           EQ(ur.pvalue, update.pvalue),
                                                                           LT(update.time, ur.time + Int(30)),
                                                                           update > ur)))

no_random_update = forall(Update, lambda update: exist(Request_Update, lambda ur:
                                                                       AND(EQ(ur.pid, update.pid),
                                                                           EQ(ur.subject, update.subject),
                                                                           EQ(ur.pvalue, update.pvalue),
                                                                           ur < update)))

no_two_collect_with_time = NOT(exist([Collect, Collect], lambda c1, c2: AND(NEQ(c1.pid, c2.pid), EQ(c1.subject, c2.subject),
                                                                            c1 > c2,
                                                                            LT(Minus(c1.time, c2.time), Int(5)))))


erase_own_data = forall(Erase,lambda erase : exist(Collect, lambda collect: AND(collect < erase, EQ(collect.pid, erase.pid),
                                                                                 EQ(collect.subject, erase.subject))))

balance_of_same_subject = lambda b1, b2: EQ(b1.subject, b2.subject)
erase_with_balence = forall(Erase, lambda erase : exist(Balance, lambda b1:
                                                       AND(EQ(b1.subject, erase.subject), GE(b1.balance, Plus(Int(5), b1.time)),
                                                           EQ(b1.time, erase.time),
                                                           next(Balance, balance_of_same_subject, lambda b2:
                                                                AND(EQ(b1.subject, b2.subject),
                                                                    EQ(b2.balance, Minus(b1.balance, Plus(Int(5), b1.time)))), b1.time))))





no_conflicting_balance = forall([Balance, Balance], lambda b1, b2: Implication(EQ(b1.subject, b2.subject), Or(NEQ(b1.time, b2.time), b1.build_eq_constraint(b2))))

valid_balance = forall(Balance, lambda b1: OR(And(EQ(b1.time, Int(0)), EQ(b1.balance, Int(0))),
                                              previous(Balance, balance_of_same_subject, lambda b2: AND(EQ(b1.subject, b2.subject),
                                                                                                        OR(EQ(b1.balance, Int(0)),
                                                                                                           exist(Collect, lambda collect:
                                                                                                           AND(
                                                                                                                 EQ(collect.subject, b2.subject),
                                                                                                                 EQ(collect.time, b2.time),
                                                                                                                 EQ(Plus(b2.balance, Int(4)), b1.balance )
                                                                                                           )
                                                                                                                 ),

                                                                                                           exist(Erase, lambda erase:
                                                                                                           AND(
                                                                                                                 EQ(erase.subject, b2.subject),
                                                                                                                 EQ(erase.time, b2.time),
                                                                                                                 EQ(Minus(b2.balance, Plus(Int(5), b2.time)), b1.balance )
                                                                                                           )
                                                                                                                 ),

                                                                                                        exist(Update, lambda update:
                                                                                                           AND(
                                                                                                                 EQ(update.subject, b2.subject),
                                                                                                                 EQ(update.time, b2.time),
                                                                                                                 EQ(Plus(b2.balance, Int(3)), b1.balance )
                                                                                                           )
                                                                                                                 ),



                                                                                                           )), b1.time)))



One_data_per_person = forall(Collect, lambda c1: forall(Collect, lambda c2:
                                                        Implication(NEQ(c1.pid, c2.pid),
                                                                    NEQ(c1.subject, c2.subject))))


access_consented = forall(Access, lambda access: once(Authorize, lambda au:
AND(EQ(access.pid, au.pid), EQ(access.a1, au.a1), EQ(au.permission, Int(1))),access.time))


access_right_purpose = forall(Access, lambda access: once(Collect, lambda collect: AND(EQ(access.pid, collect.pid),
                                                                                       once(Assign_Expertise,
                                                                                            lambda ae: AND(EQ(ae.a1, access.a1),
                                                                                                           exist(Has_Expertise, lambda he:
                                                                                                                 AND(EQ(he.time, Int(0)),
                                                                                                                     EQ(he.purpose, collect.purpose),
                                                                                                                     EQ(ae.expertise, he.expertise)
                                                                                                                     )
                                                                                                                 )) ,access.time)), access.time))
                  
complete_rules = [access_consented, access_right_purpose,  no_two_collect_with_time, increasing_pid, One_data_per_person, incrementing_pid, root_pid, update_after_collection, access_up_to_date,
             request_to_update_fullfilled, no_random_update, access_after_collection, no_double_collect, erase_own_data, erase_with_balence,
                  no_conflicting_balance, valid_balance, access_not_deleted]
                  
########################################################################
## Rules
########################################################################
    
# test rule
rule_0 = exist(Update, lambda collect : EQ(collect.pid, Int(90)))

# violation against permission to update
rule_1 = exist(Request_Update, lambda ru: exist(Collect, lambda collect:
													exist(TimeStamp, lambda ts:
														  AND(GT(ts.time, ru.time + Int(30)),
															EQ(collect.subject, ru.subject),
															EQ(collect.pid, ru.pid),
															collect < ru,
																NOT(exist(Update, lambda update:
																		  AND(EQ(update.pid, ru.pid),
																			  EQ(update.subject, ru.subject),
																			  EQ(update.pvalue, ru.pvalue),
																			  update >= ru,
																			  update <= ts)
																		  ))
															  ))))

# unordered pids
rule_2 = exist(Collect, lambda collect: AND(EQ(collect.pid, Int(5)),
                                               exist(Collect, lambda collect1: AND(collect1 < collect,
                                                                                   GE(collect1.pid, collect.pid)))))
# invalid_access
rule_3 =  exist(Update, lambda update: forall(Collect, lambda  collect: Implication(collect < update, NEQ(collect.pid, update.pid))))

# out of order pids 
rule_4 = exist([Collect, Collect], lambda collect1, collect2: AND(collect2 > collect1, LT(collect2.pid, collect1.pid)))

# access a given big pid
rule_5 = eventually(Access, lambda cl: GT(cl.pid, Int(50)))

# access after data deleted
rule_6 = eventually(Access,  lambda access : once(Collect, lambda collect: 
	                                         AND (EQ(collect.pid, access.pid), 
	                                              exist(Erase, lambda erase: 
														AND (erase < access,
														erase >= collect,
														EQ(erase.pid, collect.pid))
														)),
											access.time))

rule_7 = eventually(Erase, lambda erase: EQ(erase.pid, Int(10)))

# data minimisation

########################################################################
## Main
########################################################################
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rules = set()
    start = time.time()
    check_property_refining(rule_7, rules, complete_rules, ACTION, state_action, True)
    print(time.time() - start)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# find trace
# 156.51184964179993 for completes set
