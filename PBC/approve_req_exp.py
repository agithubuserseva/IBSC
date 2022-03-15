

import subprocess

def run_exp(command_header):
    with open("approve_req_domain_template.txt", 'r') as domain_template:
        domain_content = domain_template.read()

    with open("approve_req_rule_template.txt", 'r') as rule_template:
        rule_conetent = rule_template.read()

    if not os.path.exists('results'):
        os.makedirs('results')

    timeout = 5000
    init_values = (1, 2, 4)
    #init value
    id = 1
    data = 2
    time = 4
    for i in range(3):
        outfile = "approve_req_domain_{}.py".format(i)
        rule_file = "approve_req_rule_{}.py".format(i)
        with open(outfile, 'w') as out_f:
            out_f.write(domain_content.format(id =id, data =data, time = time))

        with open(rule_file, 'w') as rule_f:
            rule_f.write(
                rule_conetent.format(domain_file=outfile[:-3],))

        result_file = "results/approve_req_{}.txt".format(i)
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

        result_file = "results/approve_req_opt_{}.txt".format(i)
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

        id = id * 10
        data = data *10
        time = time * 10

    outfile = "approve_req_domain_unbound.py".format(i)
    rule_file = "approve_req_rule_unbound.py".format(i)
    with open(outfile, 'w') as out_f:
        out_f.write(domain_content.format(id=None, data=None, time=None))

    with open(rule_file, 'w') as rule_f:
        rule_f.write(
            rule_conetent.format(domain_file=outfile[:-3], ))

    result_file = "results/approve_req_unbound.txt"
    print(result_file)
    with open(result_file, 'w') as f:
        try:
            result = subprocess.run(command_header + [ rule_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True,
                                    timeout=timeout)
        except subprocess.TimeoutExpired as t:
            f.write("timeout {}".format(timeout))


        f.write(result.stdout)
        f.write(result.stderr)

    result_file = "results/approve_req_unbound_opt.txt"
    print(result_file)
    with open(result_file, 'w') as f:
        try:
            result = subprocess.run(command_header + [rule_file, "min"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True,
                                    timeout=timeout)
        except subprocess.TimeoutExpired as t:
            f.write("timeout {}".format(timeout))


        f.write(result.stdout)
        f.write(result.stderr)


if __name__ == "__main__":
    command_header = ["memtime", "python3"]
    run_exp(command_header)
