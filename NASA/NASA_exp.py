import os


import subprocess

def run_exp(command_hear):
    config_template_file = "model_config_template_compare.txt"
    config_tempalte = ""
    with open(config_template_file, 'r') as template_f:
        config_tempalte = template_f.read()

    if not os.path.exists('results'):
        os.makedirs('results')

    timeout = 5000
    #init value
    rule_file  = "verification_rules.py"
    configs = os.listdir("config")
    for config_file in configs:
        outfile = "model_config.py"
        with open(outfile, 'w') as out_f:
            out_f.write(config_tempalte.format(config_file="{}".format(str(config_file).rstrip('.py'))))

        for j in range(1, 7):
            result_file = "results/NASA_{}_rule_{}.txt".format(config_file, j)
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

            # result_file = "results/NASA_{}_rule_opt_{}.txt".format(config_file, j)
            # print(result_file)
            # with open(result_file, 'w') as f:
            #     try:
            #         result = subprocess.run(command_hear + [ rule_file, str(j), "min"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            #                                 universal_newlines=True,
            #                                 timeout=timeout)
            #     except subprocess.TimeoutExpired as t:
            #         f.write("timeout {}".format(timeout))
            #         continue
            #
            #     f.write(result.stdout)
            #     f.write(result.stderr)

if __name__ == "__main__":
    command_header = ["python"]
    run_exp(command_header)
