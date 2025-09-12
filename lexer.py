END_LINE_SYMBOL = '.'
WORD_SEPARATOR = ' '
SPECIAL_CHARACTERS : list = [',','{','}',":","(",")"]

class Token:
    IDENTIFIER = 0
    EQ = 1
    NUMBER_CONST = 2
    TEXT_CONST = 3
    BOOL_CONST = 5
    LIST_OPEN = 6
    LIST_CLOSE = 7

    """
    NOT_EQ
    IF
    ELSE 
    REPEAT
    WHILE
    """
    
    def __init__(self, type, value = None):
        self.type, self.value = (type, value)

def is_special_character(char:str):
    return char in SPECIAL_CHARACTERS

def get_sentences(code : str):
    return code.split(END_LINE_SYMBOL)

def get_words(sentence : str):
    words = []
    current_word = ""
    end_string = -1
    for letter in range(len(sentence)):
        if letter <= end_string:
            continue

        if sentence[letter] == "'" or sentence[letter] == '"':
            if len(current_word) > 0: words.append(current_word)
            words.append(sentence[letter])
            skip = False
            for i in range(letter+1, len(sentence)):
                if i != sentence[letter]:
                    current_word += sentence[i]
                else:
                    words.append(current_word)
                    current_word = ""
                    words.append(sentence[i])
                    end_string = i
                    break
            if end_string > 0: continue
            raise Exception("No closing quotes for text!")
        
        if sentence[letter] == WORD_SEPARATOR:
            if len(current_word) > 0: words.append(current_word)
            current_word = ""
            continue

        if is_special_character(sentence[letter]):
            if len(current_word) > 0: words.append(current_word)
            current_word = ""
            words.append(sentence[letter]) #appends the special character as a word
        
        current_word += sentence[letter]

last_tokens = []

def consume_words(words : list, *required : str):
    global last_tokens

    # Check if the words list holds enough words
    if len(words) < len(required):
        return False
    
    # Check if a word is not equal in the required sequence
    for i in range(len(required)):
        if words[i] != required[i]:
            return False
    
    # Pop and save the last tokens
    for i in range(len(required)):
        last_tokens.append(words.pop(0))
    
    return True

def consume_words_until(words : list, end : str):
    global last_tokens

    for i in range(len(words)):
        if words[i] == end:
            for _ in range(i+1):
                last_tokens.append(words.pop(0))
            return True
    
    return False


def tokenize(code : str):
    global last_tokens

    code_tokens = []
    for sentence in get_sentences(code):
        tokens = []

        words = get_words(sentence)

        while len(words) != 0:
            last_tokens = []
            if (consume_words(words, "equals") or
                consume_words(words, "is", "equal", "to") or
                consume_words(words, "=") or
                consume_words(words, "==")):
                # Equality / assignment
                tokens.append(Token(Token.EQ))
            elif consume_words(words, '"'):
                
                tokens.append(Token(Token.TEXT_CONST, " ".join()))
            else:
                # Identifier
                tokens.append(Token(Token.IDENTIFIER, words[0]))
        
        code_tokens.append(tokens)
    return sentence