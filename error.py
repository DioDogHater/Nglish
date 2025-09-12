import sys, platform, os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Init colors for terminal in windows
if platform.system() == "Windows":
    os.system("color")

def display_err_msg(msg : tuple):
    print(f"{bcolors.HEADER}{sys.argv[1]}:{bcolors.ENDC} {msg[0]}")
    for i in range(1,len(msg)):
        print(msg[i])

def err_msg(*msg : str):
    display_err_msg(msg)

def error_msg(*msg : str):
    display_err_msg(msg)
    exit(-1)

def get_token_context(tks : list, index : int):
    tokens = ""
    for i in range(index, len(tks)):
        tokens += str(tks[i])
        if tks[i].end_line:
            break
    return tokens