from lexer import Token
from error import *

import math

foreground_attributes = {
    "black": "\033[30m", "red": "\033[31m", "blue": "\033[34m", "green": "\033[32m",
    "yellow": "\033[33m", "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m",
    "bold": "\033[1m", "italic": "\033[3m", "underlined": "\033[4m", "normal": "\033[0m"
}

background_attributes = {
    "black": "\033[40m", "red": "\033[41m", "blue": "\033[44m", "green": "\033[42m",
    "yellow": "\033[43m", "magenta": "\033[45m", "cyan": "\033[46m", "white": "\033[47m"
}

variables = {}

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
        else:
            return None

def digest_token(tks : list, type = ""):
    global token_index, current_line

    if token_index >= len(tks):
        return False

    if tks[token_index].type == type or type == "":
        if token_index > 0 and tks[token_index-1].end_line:
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
    elif (tk.type == "to text" or
          tk.type == "to number" or
          tk.type == "to bool"):
        return 3
    elif tk.type == "pow":
        return 4
    else:
        return 0

def parse_term(tks : list):
    global token_index

    # Dictionary to simplify / clean up the code
    math_functions = {
        # Negation
        "sub": lambda x: -x,
        "negative": lambda x: -x,
        # Abs
        "plus": abs,
        "abs": abs,
        # Ceil / floor
        "ceil": math.ceil,
        "floor": math.floor,
        # Trigonometry
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan
    }

    # Numeric / boolean constants
    if peek_token(tks, "num_const") or peek_token(tks,"bool_const"):
        return digest_token(tks).value

    # Text constants
    elif peek_token(tks, "text_const"):
        text = digest_token(tks).value
        was_text_const = True

        # We combine every value between text as a single piece of text
        while peek_token(tks,"text_const") or (was_text_const and
              (peek_token(tks,"num_const") or
               peek_token(tks,"bool_const") or
               peek_token(tks,"identifier"))):
            was_text_const = (peek_token(tks,"text_const") != None)
            expr = parse_expression(tks)
            if expr != None:
                text += str(expr)
            else:
                fatal_err_msg(f"Expected expression at line {current_line}",get_token_context(tks, token_index))
        return text

    # Negative / number
    elif digest_token(tks,"sub") or digest_token(tks,"negative"):
        expr = parse_expression(tks)
        if expr == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        return -expr

    # Absolute number
    elif digest_token(tks,"abs") or digest_token(tks, "plus"):
        expr = parse_expression(tks)
        if expr == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        return abs(expr)

    # Parentheses
    elif digest_token(tks, "("):
        expr = parse_expression(tks)
        if not digest_token(tks, ")"):
            fatal_err_msg(f"Parenthese are never closed at line: {current_line}",get_token_context(tks, token_index))
        if expr == None:
            fatal_err_msg(f"Expression is invalid, line: {current_line}",get_token_context(tks, token_index))
        return expr

    # Identifier, either variable or function
    elif peek_token(tks,"identifier"):
        identifier = digest_token(tks).value
        while peek_token(tks,"identifier"):
            identifier += " " + digest_token(tks, "identifier").value
        if identifier in variables.keys():
            return variables[identifier]
        else:
            fatal_err_msg(f"Identifier {bcolors.BOLD}{identifier}{bcolors.ENDC} does not exist (yet)",get_token_context(tks,token_index-1))

    # Ask
    elif digest_token(tks,"ask"):
        prompt = parse_term(tks)
        if prompt == None or type(prompt) != str:
            fatal_err_msg(f"Expected valid text as prompt at line {current_line}",get_token_context(tks,token_index))
        answer = ""
        try:
            answer = input(bcolors.OKBLUE+bcolors.BOLD+prompt+bcolors.ENDC+" ")
        except KeyboardInterrupt:
            print(f"\n{bcolors.BOLD}{bcolors.WARNING}INPUT FAILED:{bcolors.ENDC} keyboard interrupt")
            sys.exit(130)
        except Exception:
            fatal_err_msg(f"\n{bcolors.WARNING}INPUT EXCEPTION:{bcolors.ENDC} {e}")
        return answer

    # Math function
    elif tks[token_index].type in math_functions:
        func = math_functions[digest_token(tks).type]
        expr = parse_expression(tks)
        if expr == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        try:
            return func(expr)
        except Exception as e:
            fatal_err_msg(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {e} at line {current_line}",get_token_context(tks, token_index-2))

    # Atan2 (two arguments)
    elif digest_token(tks, "atan2"):
        x = parse_expression(tks)
        if x == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        if not digest_token(tks, ","):
            fatal_err_msg(f"Expected second argument for atan2 at line {current_line}",get_token_context(tks,token_index))
        y = parse_expression(tks)
        if y == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        try:
            return math.atan2(x,y)
        except Exception as e:
            fatal_err_msg(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {e} at line {current_line}",get_token_context(tks, token_index-4))

    # Invalid term
    else:
        err_msg(f"Invalid term expression: {peek_token(tks)}")
        return None

def parse_expression(tks : list, min_precedence = 1):
    # Initial term
    expr = parse_term(tks)

    # Check if it's an actual expression
    if expr != None:
        while True:
            # Check if operator
            operator = peek_token(tks)
            if operator == None:
                break

            # If it's a conversion, just convert and continue to next term
            if digest_token(tks,"to text"):
                expr = str(expr)
                continue
            elif digest_token(tks,"to number"):
                try:
                    expr = float(expr)
                    if expr.is_integer():
                        expr = int(expr)
                except:
                    print(f'{bcolors.WARNING}Failed to convert "{str(expr)}" to float:, defaulting to 0.{bcolors.ENDC}')
                    expr = 0
                continue
            elif digest_token(tks,"to bool"):
                expr = bool(expr)
                continue

            # Check operator precedence (PEMDAS)
            op_precedence = get_precedence(operator)
            if op_precedence < min_precedence:
                break

            # Digest the operator
            digest_token(tks)
            
            # Get the right hand side
            rhs = parse_expression(tks, op_precedence+1)
            if rhs == None:
                fatal_err_msg(f"Missing expression after operator at line {current_line}:",
                              get_token_context(tks, token_index - 1))

            # Text operations
            if type(expr) == str or type(rhs) == str:
                try:
                    if operator.type == "add":
                        expr = str(expr) + str(rhs)
                    elif operator.type == "mult" and type(expr) == str:
                        expr = expr * rhs
                    elif operator.type == "mult" and type(rhs) == str:
                        expr = rhs * expr
                    else:
                        fatal_err_msg(f"invalid operator {operator} for text at line {current_line}",get_token_context(tks, tks.index(operator)))
                except Exception as e:
                    fatal_err_msg(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {e} at line {current_line}",get_token_context(tks, tks.index(operator)))
            else:
                # Convert boolean
                if type(expr) == bool: expr = int(expr)
                if type(rhs) == bool: rhs = int(rhs)

                try:
                    # Operations
                    if operator.type == "add":
                        expr = expr + rhs
                    elif operator.type == "sub":
                        expr = expr - rhs
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
                except Exception as e:
                    fatal_err_msg(f"{bcolors.FAIL}ERROR:{bcolors.ENDC} {e} at line {current_line}",get_token_context(tks, tks.index(operator)))

        # Return resulting expression
        return expr
    else:
        return None

def get_logical_precedence(tk : Token):
    if tk.type == "not":
        return 1
    elif tk.type == "and":
        return 2
    elif tk.type == "or" or tk.type == "xor":
        return 3
    elif tk.type == "implies":
        return 4
    elif tk.type == "biconditional":
        return 5
    else:
        return 0

def parse_term_proposition(tks : list):
    comparisons = {
        "compare equal": lambda x, y: x == y,
        "not equal to": lambda x, y: x != y,
        "greater than": lambda x, y: x > y,
        "greater or equal to": lambda x, y: x >= y,
        "lower than": lambda x, y: x < y,
        "lower or equal to": lambda x, y: x <= y
    }

    if digest_token(tks,"not"):
        prop = parse_term_proposition(tks)
        if prop == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        return not prop

    # Left hand side
    lhs = parse_expression(tks)
    if lhs == None:
        fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
    
    # Comparison
    if peek_token(tks, lambda x: x in comparisons.keys()):
        operator = digest_token(tks)
        rhs = parse_expression(tks)
        if rhs == None:
            fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks,token_index-1))
        try:
            return comparisons[operator.type](lhs,rhs)
        except Exception as e:
            fatal_err_msg(f"{bcolors.WARNING}Failed to evaluate comparison:{bcolors.ENDC} {e}",get_token_context(tks,tks.index(operator)))
    else:
        err_msg(f"Invalid proposition term at line {current_line}",get_token_context(tks,token_index-1))
        return None


def parse_proposition(tks : list, min_precedence = 1):
    # boolean expression (proposition)
    prop = parse_term_proposition(tks)
    
    if prop != None:
        while True:
            operator = peek_token(tks)
            if operator == None:
                break
            if get_logical_precedence(operator) < min_precedence:
                break
            digest_token(tks)

            rhs = parse_term_proposition(tks)
            if rhs == None:
                fatal_err_msg(f"Missing proposition after logical operator at line {current_line}",get_token_context(tks,tks.index(operator)))
            
            if operator.type == "and":
                return prop and rhs
            elif operator.type == "or":
                return prop or rhs
            elif operator.type == "xor":
                return (prop or rhs) and not (prop and rhs)
            elif operator.type == "implication":
                return (prop or rhs) and rhs
            elif operator.type == "biconditional":
                return not (prop or rhs) or (prop and rhs)

        return prop
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
                if value == None:
                    fatal_err_msg(f"Expected valid expression at line {current_line}",get_token_context(tks, token_index-1))
                variables[var_name] = value
            if not digest_token(tks, "."):
                fatal_err_msg(f"Expected dot at the end of sentence at line {current_line}",get_token_context(tks, token_index-1))
        
        # Show output
        elif digest_token(tks,"show"):
            output = []
            while len(output) == 0 or digest_token(tks,","):
                expr = parse_expression(tks)
                if expr == None:
                    fatal_err_msg("Expected valid expression",get_token_context(tks,token_index))
                output.append(str(expr))
            if not digest_token(tks, "."):
                fatal_err_msg(f"Expected dot at the end of sentence at line: {current_line}",get_token_context(tks, token_index-1))
            print(f"{bcolors.OKBLUE}>{bcolors.ENDC} ",", ".join(output))

        # Skip unecessary punctuation
        elif digest_token(tks,".") or digest_token(tks,","):
            continue

        # In case we just have a loose expression
        elif parse_expression(tks):
            continue
        
        else:
            fatal_err_msg(f"Invalid statement at line {current_line}",get_token_context(tks,token_index))
