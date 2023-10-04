
import os
import subprocess

def run_exp(command_header):
    with open("baby_domain_template.txt", 'r') as domain_template:
        domain_content = domain_template.read()

    with open("baby_rule_template.txt", 'r') as rule_template:
        rule_conetent = rule_template.read()

    timeout = 50000
    init_values = (1, 2, 4)
    #init value

    if not os.path.exists('results'):
        os.makedirs('results')

    time = 5000
    sid = 2
    aid = 2
    pid = 5
    vol_bound = 10
    # for i in range(3):
    #     outfile = "baby_domain_{}.py".format(i)
    #     rule_file = "baby_rule_{}.py".format(i)
    #     with open(outfile, 'w') as out_f:
    #         out_f.write(domain_content.format(pid =pid, sid =sid, aid= aid, time = time))
    #
    #     for j in range(1,8):
    #         with open(rule_file, 'w') as rule_f:
    #             rule_f.write(
    #                 rule_conetent.format(domain_file=outfile[:-3],i=j, vol_bound = vol_bound))
    #
    #         result_file = "results/baby_{}_rule_{}.txt".format(i, j)
    #         print(result_file)
    #         with open(result_file, 'w') as f:
    #             try:
    #                 result = subprocess.run(command_header + [ rule_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    #                                         universal_newlines=True,
    #                                         timeout=timeout)
    #             except subprocess.TimeoutExpired as t:
    #                 f.write("timeout {}".format(timeout))
    #                 continue
    #
    #             f.write(result.stdout)
    #             f.write(result.stderr)
    #
    #         result_file = "results/baby_{}_rule_opt_{}.txt".format(i, j)
    #         print(result_file)
    #         with open(result_file, 'w') as f:
    #             try:
    #                 result = subprocess.run(command_header +[rule_file, "min"], stdout=subprocess.PIPE,
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
    #     time = time * 10
    #     sid = sid * 10
    #     aid = aid * 10
    #     pid = pid * 10
    #     vol_bound = vol_bound * 10

    outfile = "baby_domain_unbounded.py"
    rule_file = "baby_rule_unbounded.py"
    with open(outfile, 'w') as out_f:
        out_f.write(domain_content.format(pid="None", sid="None", aid="None", time="None"))

    for j in range(1, 8):
        with open(rule_file, 'w') as rule_f:
            rule_f.write(
                rule_conetent.format(domain_file=outfile[:-3], i=j, vol_bound=vol_bound))

        result_file = "results/baby_unbounded_rule_{}.txt".format(j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

        result_file = "results/baby_unbounded_rule_opt_{}.txt".format(j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file, "min"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

if __name__ == "__main__":
    command_header = ["../../memtime/memtime", "python3"]
    run_exp(command_header)
