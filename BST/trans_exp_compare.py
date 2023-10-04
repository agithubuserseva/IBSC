import os


import subprocess

def run_exp(command_header):

    if not os.path.exists('results'):
        os.makedirs('results')

    with open(os.path.join(os.getcwd(), "trans_domain_template.txt"), 'r') as domain_template:
        domain_content = domain_template.read()

    with open("trans_rule_template.txt", 'r') as rule_template:
        rule_conetent = rule_template.read()

    timeout = 5000
    # init_values = (1, 2, 4)
    # init value
    eid = 1
    cid = 2
    tid = 4
    amount = 10
    time = 4
    bound = 10
    # for i in range(3):
    #     outfile = "trans_domain_{}.py".format(i)
    #     rule_file = "trans_req_rule_{}.py".format(i)
    #     with open(outfile, 'w') as out_f:
    #         out_f.write(domain_content.format(eid=eid, cid=cid, tid=tid, amount=amount, time=time))
    #     for j in range(1, 4):
    #         with open(rule_file, 'w') as rule_f:
    #             rule_f.write(
    #                 rule_conetent.format(domain_file=outfile[:-3], i=j, vol_bound=bound))
    #
    #         result_file = "results/trans_{}_rule_{}.txt".format(i, j)
    #         print(result_file)
    #         with open(result_file, 'w') as f:
    #             try:
    #                 result = subprocess.run(command_header + [rule_file], stdout=subprocess.PIPE,
    #                                         stderr=subprocess.PIPE,
    #                                         universal_newlines=True,
    #                                         timeout=timeout)
    #             except subprocess.TimeoutExpired as t:
    #                 f.write("timeout {}".format(timeout))
    #                 continue
    #
    #             f.write(result.stdout)
    #             f.write(result.stderr)
    #
    #         with open(rule_file, 'w') as rule_f:
    #             rule_f.write(
    #                 rule_conetent.format(domain_file=outfile[:-3], i=j, vol_bound=bound))
    #
    #         result_file = "results/trans_{}_rule_opt_{}.txt".format(i, j)
    #         print(result_file)
    #         with open(result_file, 'w') as f:
    #             try:
    #                 result = subprocess.run(command_header + [rule_file, "min"], stdout=subprocess.PIPE,
    #                                         stderr=subprocess.PIPE,
    #                                         universal_newlines=True,
    #                                         timeout=timeout)
    #             except subprocess.TimeoutExpired as t:
    #                 f.write("timeout {}".format(timeout))
    #                 continue
    #
    #             f.write(result.stdout)
    #             f.write(result.stderr)
    #
    #     eid = eid * 10
    #     cid = cid * 10
    #     tid = tid * 10
    #     amount = amount * 10
    #     bound = bound * 10
    #     time = time * 10

    outfile = "trans_domain_unbound.py"
    rule_file = "trans_req_rule_unbound.py"
    with open(outfile, 'w') as out_f:
        out_f.write(domain_content.format(eid=None, cid=None, tid=None, amount=None, time=None))
    for j in range(1, 4):
        with open(rule_file, 'w') as rule_f:
            rule_f.write(
                rule_conetent.format(domain_file=outfile[:-3], i=j, vol_bound=10000))

        result_file = "results/trans_unbound_rule_{}.txt".format(j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [rule_file], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

        with open(rule_file, 'w') as rule_f:
            rule_f.write(
                rule_conetent.format(domain_file=outfile[:-3], i=j, vol_bound=10000))

        result_file = "results/trans_unbound_rule_opt_{}.txt".format(j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [rule_file, "min"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

if __name__ == "__main__":
    command_header = ["../../../memtime/memtime", "python3"]
    run_exp(command_header)


