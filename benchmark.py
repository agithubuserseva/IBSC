memtime_available = True

### define your command_hear here

if memtime_available:
    command_header = ["memtime", "python3"]
else:
    command_header = ["python3"]


from BST import trans_exp
from CFH import covid_exp
from NASA import NASA_exp
from PBC import approve_req_exp
from PHIM import baby_exp

if __name__ == "__main__":
    import os
    from os import path
    os.chdir(path.join("BST"))
    trans_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "CFH" ))
    covid_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "NASA" ))
    NASA_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "PBC" ))
    approve_req_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "PHIM" ))
    baby_exp.run_exp(command_header)

