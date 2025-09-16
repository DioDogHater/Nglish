from error import *

WHITESPACE = [" ","\t"]
SPECIAL_CHARACTERS : list = [',','{','}',':','(',')','.',"'",'+','-','/','*','%','^','<','>','=','!',]

class Token: 
    def __init__(self, type:str, value = None, end_line = False):
        self.type, self.value = (type, value)
        self.end_line = end_line
    def __str__(self):
        if self.value != None:
            return str(self.value) if self.type != "text_const" else '"'+self.value+'"'
        else:
            return self.type
    def __repr__(self): return self.__str__()
    
    #TOKEN TYPES:
    # equals, identifier, in, with, as
    # text_const, num_const, bool_const, list_const, 
    # add, abs, sub, negative, mult, div, floor div, mod, pow, ceil, floor, sin, cos, tan, atan, acos, asin, atan2
    # show, ask
    # to text, to number, to bool

def is_special_character(char:str):
    return char in SPECIAL_CHARACTERS

def get_lines(code : str):
    return code.split("\n")

def get_words(line : str):
    words = []
    current_word = ""
    end_index = -1

    for letter in range(len(line)):
        # Skip to the next character we want
        if letter <= end_index:
            continue
        
        # Get a whole string
        if line[letter] == '"':
            if len(current_word) > 0: words.append(current_word)
            current_word = '"'
            for i in range(letter+1, len(line)):
                if line[i] != '"':
                    current_word += line[i]
                else:
                    words.append(current_word)
                    current_word = ""
                    end_index = i
                    break
            if end_index > 0: continue
            fatal_err_msg(f"Missing closing quotes: {current_word}","TOKENIZER ERROR")
        
        # Whitespace
        if line[letter] in WHITESPACE:
            if len(current_word) > 0:
                words.append(current_word)
            
            current_word = ""
            continue
        
        # Ignore character if its not printable
        if not line[letter].isprintable():
            continue
        
        # Special characters 
        if is_special_character(line[letter]):
            if len(current_word) > 0: words.append(current_word)
            current_word = ""
            words.append(line[letter]) #appends the special character as a word
            continue
        
        current_word += line[letter]

    # Add leftover word
    if len(current_word) > 0:
        words.append(current_word)

    return words

last_words = []

# Returns next word or checks if its the right word
def peek_word(words : list, val = "", i : int = 0):
    if len(words) > i:
        if val == "":
            return True
        return (val(words[i]) if callable(val) else words[i] == val)
    else:
        return False

# Pop word if its the right word
def consume_word(words : list, req = ""):
    global last_words
    
    if req == "":
        last_words.append(words.pop(0))
        return True
    elif (req(words[0]) if callable(req) else words[0] == req):
        last_words.append(words.pop(0))
        return True
    else:
        return False

# Pop word sequence if it matches exactly
def consume_words(words : list, *required : str):
    global last_words

    # Check if the words list holds enough words
    if len(words) < len(required):
        return False
    
    # Check if a word is not equal in the required sequence
    for i in range(len(required)):
        if (not required[i](words[i]) if callable(required[i]) else words[i] != required[i]):
            return False
    
    # Pop and save the last tokens
    for i in range(len(required)):
        last_words.append(words.pop(0))
    
    return True


# Transforms code into tokens
def tokenize(code : str):
    global last_words
    #//LORE:// lore accurately the Nglish tokenizer is a dog who eats your english homework and digests it into the parser
    
    tokens = []

    for line in get_lines(code):
        words = get_words(line)

        if len(words) == 0:
            tokens.append(Token(".",end_line=True))
            continue

        while len(words) != 0:
            last_words = []
                
            # In case of an empty word
            if consume_word(words, lambda x: len(x) == 0):
                continue
            
            ### KEYWORDS AND OPERATORS ###
            # Equality / assignment
            if (consume_word(words,"equals") or
                consume_words(words,"is","equal","to") or
                consume_word(words,"=")):
                tokens.append(Token("equals"))
            
            # Show
            elif (consume_word(words,"show") or
                  consume_word(words,"display") or
                  consume_word(words,"print") or
                  consume_word(words,"say")):
                tokens.append(Token("show"))

            # Ask
            elif (consume_words(words,"ask","question") or
                  consume_word(words,"ask") or
                  consume_word(words,"prompt") or
                  consume_words(words,"the","answer","of") or
                  consume_words(words,"answer","of")):
                tokens.append(Token("ask"))
            
            # If
            elif consume_word(words,"if"):
                tokens.append(Token("if"))
            
            # Then
            elif (consume_word(words,"then") or
                  consume_words(words,",","then")):
                tokens.append(Token("then"))
            
            # Else if
            elif (consume_words(words,"else", "if") or
                  consume_words(words,"else",",","if")):
                tokens.append(Token("else if"))
            
            # Else
            elif (consume_words(words,"else") or
                  consume_words(words,"otherwise")):
                tokens.append(Token("else"))
            
            # End
            elif (consume_word(words,"end") or
                  consume_words(words,"finish")):
                tokens.append(Token("end"))

            # Addition
            elif (consume_word(words,"plus") or
                  consume_word(words,"+")):
                tokens.append(Token("add","+"))
            
            # Abs / Positive
            elif (consume_word(words,"positive") or
                  consume_words(words,"abs","of") or
                  consume_word(words,"abs")):
                tokens.append(Token("abs"))
            
            # Substraction
            elif (consume_word(words,"minus") or
                  consume_word(words,"-")):
                tokens.append(Token("sub","-"))
            
            # Negative
            elif consume_word(words,"negative"):
                tokens.append(Token("negative","-"))

            # Multiplication
            elif (consume_word(words,"times") or
                  consume_words(words,"multiplied","by") or
                  consume_word(words,"*")):
                tokens.append(Token("mult","*"))
            
            # Division
            elif (consume_words(words,"divided","by") or
                  consume_word(words,"/") or
                  consume_words(words,"over")):
                tokens.append(Token("div","/"))
            
            # Floor division
            elif (consume_words(words,"floor","divided","by") or
                  consume_words(words,"floor","divide","by") or
                  consume_word(words,"//")):
                tokens.append(Token("floor div","//"))
            
            # Modulo
            elif (consume_words(words,"modulo","of") or
                  consume_word(words,"modulo") or
                  consume_word(words,"%")):
                tokens.append(Token("mod","%"))
            
            # Power
            elif (consume_words(words,"to","the","power","of") or
                  consume_words(words,"power","of") or
                  consume_word(words,"exponent") or
                  consume_words(words,"raised","by") or
                  consume_word(words,"^")):
                tokens.append(Token("pow","^"))
            
            ### LOGICAL / COMPARISON OPERATORS ###
            # Equality check
            elif (consume_words(words,"=","=") or
                  consume_words(words,"is","the","same","as") or
                  consume_words(words,"is","equivalent","to")):
                tokens.append(Token("compare equal","equal to"))
            
            # Inequality check
            elif (consume_words(words,"!","=") or
                  consume_words(words,"not","equal","to") or
                  consume_words(words,"not","equal") or
                  consume_words(words,"is","not","equal","to") or
                  consume_words(words,"is","not","the","same","as") or
                  consume_words(words,"is","not","equivalent","to")):
                tokens.append(Token("not equal to"))
            
            # Greater than
            elif (consume_word(words,">") or
                  consume_words(words,"greater","than") or
                  consume_words(words,"is","greater","than")):
                tokens.append(Token("greater than"))
            
            # Greater or equal to
            elif (consume_words(words,">","=") or
                  consume_words(words,"greater","or","equal","to") or
                  consume_words(words,"is","greater","or","equal","to")):
                tokens.append(Token("greater or equal to"))
            
            # Lower than
            elif (consume_word(words,"<") or
                  consume_words(words,"lower","than") or
                  consume_words(words,"lesser","than") or
                  consume_words(words,"is","lower","than") or
                  consume_words(words,"is","lesser","than")):
                tokens.append(Token("lower than"))
            
            # Lower or equal to
            elif (consume_words(words,"<","=") or
                  consume_words(words,"lesser","or","equal","to") or
                  consume_words(words,"lower","or","equal","to") or
                  consume_words(words,"lesser","or","equal","to") or
                  consume_words(words,"is","lower","or","equal","to") or
                  consume_words(words,"is","lesser","or","equal","to")):
                tokens.append(Token("lower or equal to"))
            
            # NOT
            elif (consume_word(words,"not") or
                  consume_word(words,"!")):
                tokens.append(Token("not"))

            # AND
            elif consume_word(words,"and"):
                tokens.append(Token("and"))
            
            # XOR
            elif (consume_word(words,"xor") or
                  consume_words(words,"or","else") or
                  consume_words(words,"exclusive or")):
                tokens.append(Token("xor"))

            # OR
            elif (consume_word(words,"or") or
                  consume_words(words,"and","/","or") or
                  consume_words(words,"inclusive or")):
                tokens.append(Token("or"))
            
            # IMPLICATION
            elif (consume_word(words,"implies") or
                  consume_words(words,"implies","that")):
                tokens.append(Token("implies"))
            
            # BICONDITIONAL
            elif (consume_word(words,"biconditional")):
                tokens.append(Token("biconditional"))
            
            ### MATH FUNCTIONS ###
            # Floor
            elif consume_word(words,"floor"):
                consume_word(words,"of")
                tokens.append(Token("floor"))
            
            # Ceiling
            elif (consume_word(words,"ceiling") or
                  consume_word(words,"ceil")):
                consume_word(words,"of")
                tokens.append(Token("ceil"))
            
            # Sin
            elif (consume_word(words,"sin") or
                  consume_word(words,"sine") or
                  consume_words(words,"the","sine")):
                consume_word(words,"of")
                tokens.append(Token("sin"))

            # Cos
            elif (consume_word(words,"cos") or
                  consume_word(words,"cosine") or
                  consume_words(words,"the","cosine")):
                consume_word(words,"of")
                tokens.append(Token("cos"))

            # Tan
            elif (consume_word(words,"tan") or
                  consume_word(words,"tangent") or
                  consume_words(words,"the","tangent")):
                consume_word(words,"of")
                tokens.append(Token("tan"))

            # Arc sine / asin
            elif (consume_word(words,"asin") or
                  consume_words(words,"arc","sine") or
                  consume_words(words,"the","arc","sine")):
                consume_word(words,"of")
                tokens.append(Token("asin"))

            # Arc cosine / acos
            elif (consume_word(words,"acos") or
                  consume_words(words,"arc","cosine") or
                  consume_words(words,"the","arc","cosine")):
                consume_word(words,"of")
                tokens.append(Token("acos"))

            # Arc tangent / atan
            elif (consume_word(words,"atan") or
                  consume_words(words,"arc","tangent") or
                  consume_words(words,"the","arc","tangent")):
                consume_word(words,"of")
                tokens.append(Token("atan"))

            # Atan2 / Angle to
            elif (consume_word(words,"atan2") or
                  consume_words(words,"angle","to") or
                  consume_words(words,"the","angle","to")):
                consume_word(words,"of")
                tokens.append(Token("atan2"))

            ### SYNTAX AND CONSTANTS (LITERALS) ###
            # Strings (text)
            elif consume_word(words,lambda x: str.startswith(x,'"')): 
                tokens.append(Token("text_const", last_words[0].removeprefix('"')))
            
            # Numbers
            elif consume_word(words, str.isnumeric):
                if peek_word(words, ".") and peek_word(words, str.isnumeric, 1):
                    consume_word(words)
                    consume_word(words)
                num_lit = float("".join(last_words))
                if num_lit.is_integer(): num_lit = int(num_lit)
                tokens.append(Token("num_const", num_lit))
            
            # Boolean constants (true or false)
            elif consume_word(words, "true") or consume_word(words, "false"):
                value = (last_words[0] == "true")
                tokens.append(Token("bool_const", value))

            # Text conversion
            elif (consume_words(words,"to","text") or
                  consume_words(words,"as","text") or
                  consume_words(words,"converted","to","text")):
                tokens.append(Token("to text"))

            # Number conversion
            elif (consume_words(words,"to","number") or
                  consume_words(words,"as","number") or
                  consume_words(words,"converted","to","number")):
                tokens.append(Token("to number"))

            # Boolean conversion
            elif (consume_words(words,"to","bool") or
                  consume_words(words,"to","boolean") or
                  consume_words(words,"as","bool") or
                  consume_words(words,"as","boolean") or
                  consume_words(words,"converted","to","bool") or
                  consume_words(words,"converted","to","boolean")):
                tokens.append(Token("to bool"))
            
            # In case of a special character, just make the type be the character itself
            elif consume_word(words, lambda x: x in SPECIAL_CHARACTERS):
                tokens.append(Token(last_words[0]))

            # Identifier
            else:
                tokens.append(Token("identifier", words[0]))
                consume_word(words)
        
        tokens[len(tokens)-1].end_line = True

    return tokens
