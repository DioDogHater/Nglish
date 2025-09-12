from lexer import tokenize
from parser import parse
# from parser 

import sys

def open_file(path : str, mode : str = "r"):
    try:
        file = open(path, mode)
        return file
    except OSError as e:
        print(e)
        return None

def read_file(path : str):
    try:
        file = open(path, "r")
        data = file.read()
        file.close()
        return data
    except OSError as e:
        print(e)
        return None

def print_usage():
    print("Usage: python main.py <input file>")
    print("\t-h, --help : print this message")

if len(sys.argv) < 2:
    print_usage()
    print("MISSING INPUT FILE!")
    exit(-1)

arg = sys.argv[1]

if arg == "-h" or arg == "--help":
    print_usage()
    exit(0)

code = read_file(arg)

if not code:
    exit(0)

tokens = tokenize(code) # the lexer will tokenize all the words

#for tk in tokens:
#    print(tk)

parse(tokens)