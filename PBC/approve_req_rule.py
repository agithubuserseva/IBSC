from logic_operator import *
from approve_req_domain import *
import time
from analyzer import check_property_refining, prove_by_induction
from random import randint

########################################################################
# Shortcuts
########################################################################

EQ = Equals
NEQ = NotEquals

#now list out the set of invs
#start and end should not happen at the same time
r1 =forall(Accountant_start, lambda acs: forall(Accountant_end, lambda ace: NOT(AND(EQ(acs.id, ace.id), EQ(acs.time, ace.time)))))
r2 =forall(Manager_start, lambda ms: forall(Manager_end, lambda me: NOT(AND(EQ(ms.manager, me.manager), EQ(ms.acc, me.acc), EQ(ms.time, me.time)))))


def same_acc(e1, e2):
    return EQ(e1.id, e2.id)

#inv for acc
r3 =forall(Accountant_end, lambda ace: since(Accountant_start, lambda acs: same_acc(ace, acs), Accountant_end, lambda ace1: NOT(same_acc(ace, ace1)), ace.time))
r4 = forall(Accountant_start, lambda acs: OR(NOT(exist(Accountant_start, lambda acs1: AND(same_acc(acs, acs1), acs1 < acs))),
                                        since(Accountant_end, lambda ace: same_acc(ace, acs), Accountant_start, lambda acs1: NOT(same_acc(acs, acs1)), acs.time)))

def same_management(e1, e2):
    return AND(EQ(e1.acc, e2.acc), EQ(e1.manager, e2.manager))

#inv for manager:
r5 = forall(Manager_end, lambda ace: since(Manager_start, lambda acs: same_management(ace, acs), Manager_end, lambda ace1: same_management(ace, ace1), ace.time))
r6 = forall(Manager_start, lambda acs: OR(NOT(exist(Manager_start, lambda acs1: AND(same_management(acs, acs1), acs1 < acs))),
                                        since(Manager_end, lambda ace: same_management(ace, acs), Manager_start, lambda acs1: same_management(acs, acs1), acs.time)))

def is_account(time, id):
    return since(Accountant_start, lambda acs: EQ(acs.id, id), Accountant_end, lambda ace: EQ(ace.id, id), time)


def is_management(time, manager, acc):
    return since(Manager_start, lambda acs: AND(EQ(acs.acc, acc), EQ(acs.manager, manager)), Manager_end, lambda ace: AND(EQ(ace.acc, acc), EQ(ace.manager, manager)), time)


basin_property = forall(Publish, lambda pb: AND(is_account(pb.time, pb.acc),
                                                once(Approve, lambda ap: AND(ap > (pb.time - Int(11)),
                                                                             is_management(ap.time, ap.manager, pb.acc),
                                                                             EQ(ap.data, pb.data)), pb.time)
                                                ))

violation_basin = eventually(Publish, lambda pb: NOT(AND(is_account(pb.time, pb.acc),
                                                once(Approve, lambda ap: AND(ap > (pb.time - Int(11)),
                                                                             is_management(ap.time, ap.manager, pb.acc),
                                                                             EQ(ap.data, pb.data)), pb.time)
                                                )))

#here are some system specifications
#if a users published a file, then the user must be an account
r7 = forall(Publish, lambda pb: is_account(pb.time, pb.acc))



#if an account publish the file, then the account has a manger's approval
r8 = forall(Publish, lambda pb: once(Approve, lambda ap: AND(is_management(ap.time, ap.manager, pb.acc),
                                                             EQ(ap.data, pb.data)), pb.time))

#cannot self manage
r9 = forall(Manager_start, lambda ms: NOT(EQ(ms.manager, ms.acc)))

#A manager must has to be an account once, and must not be accoutant at the time of being an manager
r10 = forall(Manager_start, lambda ms: OR(EQ(ms.manager, Int(inital_manager)), AND(NOT(is_account(ms.time, ms.manager)), once(Accountant_start, lambda acs: EQ(acs.id, ms.manager), ms.time))))

#A person can become a manager only if it has published something 30 days before, or it has been an accountant for more than 100 days
r11 = forall(Manager_start, lambda ms: OR(once(Publish, lambda pb: AND(EQ(pb.acc, ms.manager), ms > ((pb.time + Int(30)))), ms.time), EQ(ms.manager, Int(inital_manager))))

r12 = forall(Accountant_start, lambda acs: NEQ(acs.id, Int(inital_manager)))

#any file approved by the inital manager has to be published in 2 days
r13 = forall(Approve, lambda ap: Implication(EQ(ap.manager, Int(inital_manager)), eventually(Publish, lambda pb: AND(EQ(pb.data, ap.data), pb <= ap.time+2), ap.time)))

#no data should be republished
r14 = forall([Publish, Publish], lambda p1, p2: Implication(NOT(p1.build_eq_constraint(p2)), NEQ(p1.data, p2.data)))

complete_rules = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14]
if __name__ == '__main__':
    rule_1 = eventually(Publish, lambda pb: TRUE())
    rules = set()
    start = time.time()
    check_property_refining(violation_basin, rules, complete_rules, ACTION, state_action, True)
    print(time.time() - start)
