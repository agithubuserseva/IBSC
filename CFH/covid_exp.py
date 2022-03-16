config_template_file = "covid_config.txt"

import subprocess
import os

def run_exp(command_header):
    if not os.path.exists('results'):
        os.makedirs('results')

    config_tempalte = ""
    with open(config_template_file, 'r') as template_f:
        config_tempalte = template_f.read()

    timeout = 5000
    init_values = (1, 2, 4)
    #init value
    data = 5
    dataid = 5
    dsid = 2
    vol_bound = 10
    rule_file  = "covidfree_rules.py"
    for i in range(3):
        outfile = "covid_config.py"
        with open(outfile, 'w') as out_f:
            out_f.write(config_tempalte.format(b_data = data, b_dataid =dataid, b_dsid = dsid))

        for j in range(1, 8):
            result_file = "results/covid_{}_rule_{}.txt".format(i, j)
            print(result_file)
            with open(result_file, 'w') as f:
                try:
                    result = subprocess.run(command_header + [ rule_file, str(j), str(vol_bound)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True,
                                            timeout=timeout)
                except subprocess.TimeoutExpired as t:
                    f.write("timeout {}".format(timeout))
                    continue

                f.write(result.stdout)
                f.write(result.stderr)

            result_file = "results/covid_{}_rule_opt_{}.txt".format(i, j)
            print(result_file)
            with open(result_file, 'w') as f:
                try:
                    result = subprocess.run(command_header + [ rule_file, str(j), str(vol_bound), "min"], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True,
                                            timeout=timeout)
                except subprocess.TimeoutExpired as t:
                    f.write("timeout {}".format(timeout))
                    continue

                f.write(result.stdout)
                f.write(result.stderr)

        data = data * 10
        dataid = dataid * 10
        dsid = dsid * 10
        vol_bound = vol_bound * 10

    outfile = "covid_config.py"
    with open(outfile, 'w') as out_f:
        out_f.write(config_tempalte.format(b_data="None", b_dataid="None", b_dsid="None"))

    for j in range(1, 8):
        result_file = "results/covid_unbound_rule_{}.txt".format(str(j))
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file, str(j), "10000"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

        result_file = "results/covid_unbound_rule_opt_{}.txt".format(str(j))
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file, str(j), "10000", "min"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue

            f.write(result.stdout)
            f.write(result.stderr)

if __name__ == "__main__":
    command_header = ["memtime", "python3"]
    run_exp(command_header)

