from lexer import tokenize
# from parser 

import sys

def open_file(path : str, mode : str = "r"):
    try:
        file = open(path, mode)
        return file
    except OSError as e:
        print(e)
        return e

def read_file(path : str):
    try:
        file = open(path, "r")
        data = file.read()
        file.close()
        return data
    except OSError as e:
        print(e)
        return e

if len(sys.argv) < 2:
    raise Exception("")

path = sys.argv[1]
code = read_file(path)
tokens = tokenize(code) # the lexer will tokenize all the words

for tk in tokens:
    print(tk)