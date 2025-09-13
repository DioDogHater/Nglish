from error import *

WHITESPACE = [" ","\t"]
SPECIAL_CHARACTERS : list = [',','{','}',':','(',')','.',"'",'+','-','/','*','%','^']

class Token: 
    def __init__(self, type:str, value = None, end_line = False):
        self.type, self.value = (type, value)
        self.end_line = end_line
    def __str__(self): return str(self.value) if self.value != None else self.type
    def __repr__(self): return self.__str__()
    
    #TOKEN TYPES:
    # equals, identifier, 
    # text_const, num_const, bool_const, list_const, 
    # add, abs, sub, negative, mult, div, floor div, mod, pow, ceil, floor, sin, cos, tan, atan, acos, asin
    # show, ask

def is_special_character(char:str):
    return char in SPECIAL_CHARACTERS

def get_lines(code : str):
    return code.split("\n")

def get_words(line : str):
    words = []
    current_word = ""
    end_index = -1
    word_count = 0
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
                    word_count += 1
                    break
            if end_index > 0: continue
            error_msg("Missing closing quotes")
        
        # Whitespace
        if line[letter] in WHITESPACE:
            if len(current_word) > 0:
                words.append(current_word)
                word_count += 1
            elif word_count == 0: #no words yet
                # Find the last whitespace
                for i in range(letter+1, len(line)):
                    if not line[i] in WHITESPACE:
                        current_word = " " * (i - letter)
                        words.append(current_word)
                        end_index = i
                        break
            
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
            word_count += 1
            continue
        
        current_word += line[letter]
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
        #print(words)

        if len(words) == 0:
            continue

        while len(words) != 0:
            last_words = []
                
            # In case of an empty word
            if consume_word(words, lambda x: len(x) == 0):
                continue
            
            ### KEYWORDS AND OPERATORS ###
            # Equality / assignment
            if (consume_word(words, "equals") or
                consume_words(words, "is", "equal", "to") or
                consume_word(words, "=")):
                tokens.append(Token("equals"))
            
            # Show
            elif consume_word(words,"show"):
                tokens.append(Token("show"))

            # Addition
            elif (consume_word(words,"plus") or
                  consume_word(words,"+")):
                tokens.append(Token("add"))
            
            # Abs / Positive
            elif (consume_word(words,"positive") or
                  consume_words(words,"abs","of") or
                  consume_word(words,"abs")):
                tokens.append(Token("abs"))
            
            # Substraction
            elif (consume_word(words,"minus") or
                  consume_word(words,"-")):
                tokens.append(Token("sub"))
            
            # Negative
            elif consume_word(words,"negative"):
                tokens.append(Token("negative"))

            # Multiplication
            elif (consume_word(words,"times") or
                  consume_words(words,"multiplied","by") or
                  consume_word(words,"*")):
                tokens.append(Token("mult"))
            
            # Division
            elif (consume_words(words,"divided","by") or
                  consume_word(words,"/") or
                  consume_words(words,"over")):
                tokens.append(Token("div"))
            
            # Floor division
            elif (consume_words(words,"floor","divided","by") or
                  consume_words(words,"floor","divide","by") or
                  consume_word(words,"//")):
                tokens.append(Token("floor div"))
            
            # Modulo
            elif (consume_words(words,"modulo","of") or
                  consume_word(words,"modulo") or
                  consume_word(words,"%")):
                tokens.append(Token("mod"))
            
            # Power
            elif (consume_words(words,"to","the","power","of") or
                  consume_words(words,"power","of") or
                  consume_word(words,"exponent") or
                  consume_words(words,"raised","by") or
                  consume_word(words,"^")):
                tokens.append(Token("pow"))
            
            ### MATH FUNCTIONS ###
            # Floor
            elif consume_word(words,"floor"):
                consume_word(words,"of")
                tokens.append(Token("floor"))
            
            # Ceiling
            elif consume_word(words,"ceiling"):
                consume_word(words,"of")
                tokens.append(Token("ceil"))
            
            # Sin
            elif (consume_word(words,"sin") or consume_word(words,"sine")):
                consume_word(words,"of")
                tokens.append(Token("sin"))

            # Cos
            elif (consume_word(words,"cos") or consume_word(words,"cosine")):
                consume_word(words,"of")
                tokens.append(Token("cos"))

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
            
            elif consume_word(words, "true") or consume_word(words, "false"):
                value = last_words[0] == "true"
                tokens.append(Token("bool_const", value))
            
            # In case of a special character, just make the type be the character itself
            elif consume_word(words, lambda x: x in SPECIAL_CHARACTERS):
                tokens.append(Token(last_words[0]))

            # Whitespace indentation
            elif consume_word(words,str.isspace):
                tokens.append(Token("indentation",len(last_words[0])))
            
            # Identifier
            else:
                tokens.append(Token("identifier", words[0]))
                consume_word(words)
        
        tokens[len(tokens)-1].end_line = True

    return tokens
