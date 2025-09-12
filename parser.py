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
        if tks[token_index+i] != types[i]:
            return None
    
    token_index += len(types)
    return token_values

def parse_term(tks : list):
    if peek_token(tks, "num_const"):
        return digest_token(tks, "num_const").value

def parse(tks : list):
    global token_index
    token_index = 0
    while token_index < len(tks):
        # Variable assignment
        if digest_token(tks, "identifier"):
            if digest_token(tks, "equals"):
                value = parse_expression()