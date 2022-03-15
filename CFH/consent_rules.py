from covid_rule_ult import *

consented_rules = []

#consent is given only when patients are registered
consented_rules.append(forall(Consent, lambda cons: exist(Patient, lambda p: AND(EQ(p.dsid, cons.dsid), EQ(cons.time, p.time)))))

#every registered patient must have an consent
consented_rules.append(forall(Patient, lambda cons: exist(Consent, lambda p: AND(EQ(p.dsid, cons.dsid), EQ(cons.time, p.time)))))

#a consented patient can revoke his consent
consented_rules.append(forall(Revoke, lambda revoke: is_consented(revoke.dsid, revoke.time -1)))

#when a user reovke his consent, he leaves the study
consented_rules.append(forall(Revoke, lambda revoke: exist(Leave, lambda leave: AND(EQ(revoke.dsid, leave.dsid),
                                                                                    EQ(revoke.time, leave.time)))))

#when a user reovke his consent, he requests all his data being deleted
consented_rules.append(forall(Revoke, lambda revoke: forall(Collect, lambda collect: Implication(EQ(collect.dsid, revoke.dsid), exist(Delection_Request, lambda dr:
                                                                                                                                      AND(EQ(dr.dsid, revoke.dsid),
                                                                                                                                          EQ(dr.dataid, collect.dataid),
                                                                                                                                          dr <= revoke)
                                                                                                                                      )))))