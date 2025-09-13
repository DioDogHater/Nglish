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

def fatal_err_msg(*msg : str):
    display_err_msg(msg)
    exit(-1)

def get_token_context(tks : list, index : int):
    tokens = []

    # Find all tokens after last line
    start = index - 1
    while start >= 0 and not tks[start].end_line:
        tokens.insert(0, tks[start])
        start -= 1

    # Add the token we want the context of
    tokens.append(tks[index])

    # Get all tokens after, until end of line
    end = index + 1
    while end < len(tks) and not tks[end-1].end_line:
        tokens.append(tks[end])
        end += 1

    # Make accumulated tokens readable
    result = ""
    for tk in tokens:
        if result != "":
            result += " "

        if tk == tks[index]:
            result += bcolors.WARNING + str(tk) + bcolors.ENDC
        else:
            result += str(tk)

    return result




