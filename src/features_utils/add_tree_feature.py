import sys
from collections import Counter


### GLOBAL VARIABLES

KEYWORDS = {'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'exports', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'module', 'native', 'new', 'open', 'opens', 'package', 'private', 'protected', 'provides', 'public', 'requires', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'to', 'transient', 'transitive', 'try', 'uses', 'void', 'volatile', 'while', 'with'} 
SPECIAL_SYMBOLS = {'[', ']', '(', ')', '{', '}', ',', ';', '@'}
OPERATORS = {'*', '/', '+', '-', '%', '++', '--', '!', '=', '+=', '-=', '/=', '*=', '%=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '?', ':', '&', '|', '^', '~', '<<', '>>', '>>>', '&=', '^=', '|=', '<<=', '>>=', '>>>=', '.'}
requiring_vocab = []
requiring_custom_embedding = []

### FEATURES

def tag(word):
    isVal = (word[0]=='"' and word[-1]=='"') or (word[0]=="'" and word[-1]=="'") or is_number(word) or (word in ['true', 'false'])
    if word in KEYWORDS:
        return "￨" + 'k'
    elif word in SPECIAL_SYMBOLS:
        return "￨" + 's'
    elif word in OPERATORS:
        return "￨" + 'o'
    elif isVal: # Value
        return "￨" + 'v'
    elif word in ["<START_BUG>", "<END_BUG>"]: #delimiters
        return "￨" + 'd'
    else: # Identifier
        return "￨" + 'i'

def indent(word):
    if word=="}":
        indent.counter -= 1
    toRet = "￨" + str(indent.counter) 
    if word=="{":
        indent.counter += 1    
    return toRet

def number(word):
    toRet = toRet = "￨" + str(number.counter) 
    number.counter += 1
    if word in ["{", "}", ";"]:
        number.counter = 0    
    return toRet

def kmost(word):   
    return "￨" + str(kmost.counter[word]) 


### MAIN

def main(argv):
    tokenized_lines = open(argv[0], 'r').readlines()
    tokenized_lines_with_tree_feature = ""
    features = argv[2:]
    for i, feat in enumerate(features):
        if feat in ['indent', 'number', 'kmost']:
            numerical_feature(i, vocab=True)
        
    for line in tokenized_lines:
        indent.counter = 0
        number.counter = 0
        splitted_line = line.strip("\n").split(" ")

        if "kmost" in features:
            tmp_counter = Counter(splitted_line)
            kmost.counter = { x[0]:(len(tmp_counter) - i) for i, x in enumerate(tmp_counter.most_common())}

        new_line_with_tree_feature = ""
        for word in splitted_line:
            toAdd = word
            for feature in features:                
                try:
                    toAdd += globals()[feature](word)
                except KeyError:
                    print(f"Unknown feature: {feature}")
                    sys.exit(1)

            new_line_with_tree_feature += toAdd + " "
        tokenized_lines_with_tree_feature += new_line_with_tree_feature + "\n"
    
    tokenized_file_with_tree_feature = open(argv[1], "w")
    tokenized_file_with_tree_feature.write(tokenized_lines_with_tree_feature)
    tokenized_file_with_tree_feature.close()
    print(requiring_vocab)
    print("-")
    print(requiring_custom_embedding)
    sys.exit(0)



### UTILITARY FCTS


def is_number(s):
    if (len(s) > 1) and (s[-1] in ['f', 'F', 'd', 'D', 'l', 'L']):
        s = s[:-1]
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def numerical_feature(i, vocab=False, embedding=True):
    feat_name = 'src_feat_'+str(i)
    if vocab:
        global requiring_vocab
        requiring_vocab.append(feat_name)
    if embedding:
        global requiring_custom_embedding
        requiring_custom_embedding.append(feat_name)

if __name__=="__main__":
    main(sys.argv[1:])