from lexer import Token
from error import *

import math

variables = {}

"""class Function:
    def __init__(self, start, args, arg_defaults):
        self.start = start
        self.args = args
        self.arg_defaults = arg_defaults
    def start_scope(self, arg_values):
        for i in range()"""

functions = {}

token_index = 0
current_line = 1

def peek_token(tks : list, type = "", i : int = 0):
    global token_index
    if token_index+i >= len(tks):
        return None
    else:
        if tks[token_index+i].type == type or type == "":
            return tks[token_index+i]

def digest_token(tks : list, type = ""):
    global token_index, current_line

    if token_index >= len(tks):
        return False

    if tks[token_index].type == type or type == "":
        if tks[token_index].end_line:
            current_line += 1
        token_index += 1
        return tks[token_index-1]
    else:
        return None

def digest_tokens(tks : list, *types):
    global token_index, current_line

    if token_index+len(types) > len(tks):
        return None

    token_values = []
    for i in range(len(types)):
        token_values.append(tks[token_index+i].value)
        if tks[token_index+i].type != types[i]:
            return None
    
    for tk in token_values:
        if tk.end_line: current_line += 1
    
    token_index += len(types)
    return token_values

def get_precedence(tk : Token):
    if tk.type == "add" or tk.type == "sub":
        return 1
    elif (tk.type == "mult" or 
          tk.type == "div" or
          tk.type == "mod"):
        return 2
    elif tk.type == "pow":
        return 3
    else:
        return 0

def parse_term(tks : list):
    # Constants (literals)
    if peek_token(tks, "num_const") or peek_token(tks,"text_const") or peek_token(tks,"bool_const"):
        return digest_token(tks).value

    # Negative / number
    elif digest_token(tks,"sub") or digest_token(tks,"negative"):
        return -parse_expression(tks)

    # Absolute number
    elif digest_token(tks,"abs") or digest_token(tks, "plus"):
        return abs(parse_expression(tks))

    # Parentheses
    elif digest_token(tks, "("):
        expr = parse_expression(tks)
        if not digest_token(tks, ")"):
            fatal_err_msg(f"Parenthese are never closed at line: {current_line}",get_token_context(tks, token_index))
        return expr

    # Identifier, either variable or function
    elif peek_token(tks,"identifier"):
        identifier = digest_token(tks,"identifier").value
        while peek_token(tks,"identifier"):
            identifier += " " + digest_token(tks, "identifier").value
        if identifier in variables.keys():
            return variables[identifier]
        else:
            fatal_err_msg(f"Identifier {bcolors.BOLD}{identifier}{bcolors.ENDC} does not exist (yet)")

    # Invalid term
    else:
        err_msg(f"Invalid term expression: {peek_token(tks)}")
        return None

def parse_expression(tks : list, min_precedence = 1):
    expr = parse_term(tks)
    if expr != None:
        while True:
            operator = peek_token(tks)
            if not operator:
                break
            op_precedence = get_precedence(operator)
            if op_precedence < min_precedence:
                break
            digest_token(tks)
            
            rhs = parse_expression(tks, op_precedence+1)
            if not rhs:
                fatal_err_msg(f"Missing expression after operator at line {current_line}:",
                              get_token_context(tks, token_index - 1))
            
            if operator.type == "add":
                expr = expr + type(expr)(rhs)
            elif operator.type == "sub":
                expr = expr - type(expr)(rhs)
            elif operator.type == "mult":
                expr = expr * rhs
            elif operator.type == "div":
                expr = expr / rhs
            elif operator.type == "floor div":
                expr = expr // rhs
            elif operator.type == "mod":
                expr = math.fmod(expr, rhs)
            elif operator.type == "pow":
                expr = math.pow(expr, rhs)
            else:
                fatal_err_msg(f"operator {operator} is not implemented!")
        return expr
    else:
        return None
            

def parse(tks : list):
    global token_index
    token_index = 0

    while token_index < len(tks):
        # Variable assignment
        if peek_token(tks, "identifier"):
            var_name = digest_token(tks, "identifier").value
            while peek_token(tks, "identifier"):
                var_name += " " + digest_token(tks, "identifier").value
            if digest_token(tks, "equals"):
                value = parse_expression(tks)
                variables[var_name] = value
        
        # Show output
        elif digest_token(tks,"show"):
            output = []
            while len(output) == 0 or digest_token(tks,","):
                expr = parse_expression(tks)
                if expr == None:
                    fatal_err_msg("Expected valid expression",get_token_context(tks,token_index))
                output.append(str(expr))
            print(f"{bcolors.OKBLUE}SHOW:{bcolors.ENDC} ",", ".join(output))

        # Skip punctuation
        elif digest_token(tks,".") or digest_token(tks,","):
            continue
        
        else:
            fatal_err_msg(f"{bcolors.FAIL}syntax error:{bcolors.ENDC} invalid statement at line {current_line}",get_token_context(tks,token_index))
