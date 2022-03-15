from logic_operator import *
from trans_domain import *
import time
from analyzer import check_property_refining, prove_by_induction

EQ = Equals
NEQ = NotEquals

large_instance_report = forall(Trans, lambda ts: Implication(GT(ts.amount, Int(thresh)), eventually(Report, lambda report: AND (EQ(report.tid, ts.tid), report < ts.time + Int(6)), ts.time)))
large_instance_authorize = forall(Trans, lambda ts: Implication(GT(ts.amount, Int(thresh)), once(Authorize, lambda au: AND(EQ(au.tid, ts.tid),  EQ(au.cid, ts.cid), au > (ts.time - Int(21))), ts.time - Int(2))))
def suspicious_trans(ts):
    return eventually(Report, lambda report: AND(EQ(report.tid, ts.tid), report < ts.time + Int(6)), ts.time)

sss = forall(Trans, lambda ts: Implication(exist(Trans, lambda ts1: AND((suspicious_trans(ts1), (ts >= ts1), NEQ(ts1.tid, ts.tid), EQ(ts.cid, ts1.cid),(ts1 < ts.time - Int(30))))),
                                           eventually(Report, lambda report: AND(EQ(report.tid, ts.tid), report < ts.time + Int(3)))))


def inRange(act, start, end):
    return AND(act >= start, act <= end)

#no empty trans
r1 = forall(Trans, lambda ts: ts.amount > Int(0))

def warning_trans(ts):
    return OR(ts.amount > Int(thresh), exist([Trans, Trans], lambda ts1, ts2: AND(EQ(ts1.cid, ts.cid), EQ(ts2.cid, ts.cid), inRange(ts1, ts.time - Int(7), ts.time),
                                                                           inRange(ts2, ts.time- Int(7), ts.time),
                                                                           ts > ts1,
                                                                           ts1 > ts2,
                                                                           (ts.amount + ts1.amount + ts2.amount) > Int(thresh))))


#if there are three transication took place within a week, and the sum is greater than the thresh hold, then the last transication will be reported
r2 = forall(Report, lambda report: once(Trans, lambda ts: AND(EQ(report.tid, ts.tid), warning_trans(ts)), report.time))
r10 = forall(Trans, lambda ts: Implication(warning_trans(ts), eventually(Report, lambda report: AND(EQ(report.tid, ts.tid), report < ts.time + Int(6)), ts.time)))


#no reuse of the same tid
r3 = forall([Trans, Trans], lambda ts1, ts2: Implication(NOT(ts1.build_eq_constraint(ts2)), NEQ(ts1.tid, ts2.tid)))
r4 = forall([Report, Report], lambda ts1, ts2: Implication(NOT(ts1.build_eq_constraint(ts2)), NEQ(ts1.tid, ts2.tid)))

#no authorization is allowed for customer with suspecious transition in the last 10 days
r5 = forall(Authorize, lambda au: NOT(once(Trans, lambda ts: AND(suspicious_trans(ts), EQ(ts.cid, au.cid)), au.time)))


#authorize is only given to customer with more than 5 trans, whose value sum is greater than 2 * threshold
r6 = forall(Authorize, lambda au: exist([Trans, Trans, Trans, Trans, Trans], lambda trans1, trans2, trans3, trans4, trans5:
                                        AND(inRange(trans1, au.time - Int(100), au.time- Int(6)),
                                            inRange(trans1, au.time - Int(100), au.time- Int(6)),
                                            inRange(trans1, au.time - Int(100), au.time- Int(6)),
                                            inRange(trans1, au.time - Int(100), au.time- Int(6)),
                                            inRange(trans1, au.time - Int(100), au.time- Int(6)),
                                            trans1.tid > trans2.tid,
                                            trans2.tid > trans3.tid,
                                            trans3.tid > trans4.tid,
                                            trans4.tid > trans5.tid,
                                            ((trans1.amount + trans2.amount + trans3.amount + trans4.amount + trans5.amount) > Int(2 * thresh)),
                                            EQ(au.cid, trans1.cid),
                                            EQ(au.cid, trans2.cid),
                                            EQ(au.cid, trans3.cid),
                                            EQ(au.cid, trans4.cid),
                                            EQ(au.cid, trans5.cid)
                                            )
                                        ))
r7 = forall([Trans, Trans], lambda trans1, trans2: Implication(trans1.tid > trans2.tid, trans1 > trans2))


# a user can have at most one transication per day
r8 = NOT(exist([Trans, Trans], lambda trans1, trans2: AND(EQ(trans1.cid, trans2.cid), EQ(trans1.time, trans2.time), NEQ(trans1.tid, trans2.tid))))

# any employee can authorize at most two transication per week
r9 = forall(Authorize, lambda au3: NOT(exist([Authorize, Authorize], lambda au2, au1: AND(
    EQ(au1.eid, au2.eid), EQ(au1.eid, au3.eid), inRange(au2, au1.time - Int(7), au1.time), inRange(au3, au1.time -Int(7), au1),
    au1.tid < au2.eid
))))


complete_rules = [large_instance_report, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, large_instance_authorize]
if __name__ == '__main__':
    rule_1 = NOT(sss)
    rules = set()
    start = time.time()
    check_property_refining(rule_1, rules, complete_rules, ACTION, state_action, True)
    print(time.time() - start)
