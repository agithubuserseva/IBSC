


import subprocess

def run_exp(command_hear):
    config_template_file = "model_config_template.txt"
    config_tempalte = ""
    with open(config_template_file, 'r') as template_f:
        config_tempalte = template_f.read()

    timeout = 5000
    #init value
    rule_file  = "verification_rules.py"
    for i in range(1,3):
        outfile = "model_config.py"
        with open(outfile, 'w') as out_f:
            out_f.write(config_tempalte.format(config_file="config{}".format(str(i))))

        for j in range(1, 7):
            result_file = "results/NASA_{}_rule_{}.txt".format(i, j)
            print(result_file)
            with open(result_file, 'w') as f:
                try:
                    result = subprocess.run(command_hear + [ rule_file, str(j)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True,
                                            timeout=timeout)
                except subprocess.TimeoutExpired as t:
                    f.write("timeout {}".format(timeout))
                    continue

                f.write(result.stdout)
                f.write(result.stderr)

            result_file = "results/NASA_{}_rule_opt_{}.txt".format(i, j)
            print(result_file)
            with open(result_file, 'w') as f:
                try:
                    result = subprocess.run(command_hear + [ rule_file, str(j), "min"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
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
