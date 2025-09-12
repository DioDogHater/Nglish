from lexer import Token

variables = {}
functions = {} #token index of start of function

token_index = 0

def peek_token(tks : list, type = "", i : int = 0):
    global token_index
    if token_index+i >= len(tks):
        return None
    else:
        if tks[token_index+i].type == type or type == "":
            return tks[token_index+i]

def digest_token(tks : list, type = ""):
    global token_index

    if tks[token_index].type == type or type == "":
        token_index += 1
        return tks[token_index-1]
    else:
        return None

def digest_tokens(tks : list, *types):
    global token_index

    if token_index+len(types) > len(tks):
        return None

    token_values = []
    for i in range(len(types)):
        token_values.append(tks[token_index+i].value)
        if tks[token_index+i].type != types[i]:
            return None
    
    token_index += len(types)
    return token_values

def get_precedence(tk : Token):
    if tk.type == "add" or tk.type == "sub":
        return 1
    elif (tk.type == "mult" or 
          tk.type == "div" or
          tk,type == "mod"):
        return 2
    elif tk.type == "pow":
        return 3
    else:
        return None

def parse_term(tks : list):
    if peek_token(tks, "num_const"):
        return digest_token(tks, "num_const").value
    if peek_token(tks,"identifier"):
        try:
            return variables[digest_token(tks,"identifier").value]
        except:
            raise Exception("Variable does not exist!")
    return False

def parse(tks : list):
    global token_index
    token_index = 0
    line = 1
    while token_index < len(tks):
        # Variable assignment
        if peek_token(tks, "identifier"):
            var_name = digest_token(tks,"identifier").value
            if digest_token(tks, "equals"):
                value = parse_term(tks)
                variables[var_name] = value
        # Output
        elif digest_token(tks,"show"):
            output = parse_term(tks)
            print("---output: ",output)

        # Line end
        elif digest_token(tks,"dot"):
            line +=1
            continue
        
        else:
            raise Exception(f"syntax error: invalid statement at line {line}")