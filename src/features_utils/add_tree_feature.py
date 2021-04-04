import sys
import numpy as np
from collections import Counter


### GLOBAL VARIABLES

KEYWORDS = {'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'exports', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'module', 'native', 'new', 'open', 'opens', 'package', 'private', 'protected', 'provides', 'public', 'requires', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'to', 'transient', 'transitive', 'try', 'uses', 'void', 'volatile', 'while', 'with'} 
SPECIAL_SYMBOLS = {'[', ']', '(', ')', '{', '}', ',', ';', '@'}
OPERATORS = {'*', '/', '+', '-', '%', '++', '--', '!', '=', '+=', '-=', '/=', '*=', '%=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '?', ':', '&', '|', '^', '~', '<<', '>>', '>>>', '&=', '^=', '|=', '<<=', '>>=', '>>>=', '.'}
ASSIGNMENTS = {'=', '+=', '-=', '/=', '*=', '%=', '&=', '^=', '|=', '<<=', '>>=', '>>>='}
requiring_vocab = []
requiring_custom_embedding = []

### FEATURES

def build_feats(features, splitted_line):
    if "indent" in features:
        indent.counter = 0
    if "kmost" in features:    
        tmp_counter = Counter([word for word in splitted_line if identify_tag(word)=='i'])
        kmost.counter = { x[0]:(len(tmp_counter) - i) for i, x in enumerate(tmp_counter.most_common())}
    if "distbug" in features:
        distbug.counter = 0
        distbug.array = make_distbug(splitted_line)
    if "line_index" in features:
        line_index.counter = 0
        lidx = [0]
        forcount = [-1]
        startbug = [False]
        line_index.array = [get_inc_line_index(lidx, word, forcount, startbug) for word in splitted_line ]
    if "number" in features:
        number.counter = 0
        numcnt = [0]
        forcount = [-1]
        startbug = [False]
        number.array = [get_inc_line_index(numcnt, word, forcount, startbug, True) for word in splitted_line ]
    if "uniqueid" in features:
        count = 1
        uniqueid.dic = dict()
        for token in sorted(set(splitted_line), key=lambda x: x.lower()):
            uniqueid.dic[token] = count
            count += 1

def tag(word):
    return "￨" + identify_tag(word)

def indent(word):
    if word=="}":
        indent.counter -= 1
    toRet = "￨" + str(indent.counter) 
    if word=="{":
        indent.counter += 1    
    return toRet

def number(word):
    toRet = "￨" + str(number.array[number.counter])    
    number.counter += 1
    return toRet

def kmost(word):   
    return "￨" + (str(kmost.counter[word]) if word in kmost.counter else str(-1) )

def line_index(word):
    toRet = "￨" + str(line_index.array[line_index.counter]) 
    line_index.counter += 1    
    return toRet

def distbug(word):
    toRet = "￨" + str(distbug.array[distbug.counter])
    distbug.counter += 1
    return toRet

def uniqueid(word):
    return "￨" + str(uniqueid.dic[word]) 

### MAIN

def main(argv):
    tokenized_lines = open(argv[0], 'r').readlines()
    tokenized_lines_with_tree_feature = ""
    features = argv[2:]
    for i, feat in enumerate(features):
        if feat in ['indent', 'number', 'kmost', 'line_index', 'distbug', 'uniqueid']:
            numerical_feature(i, vocab=True)
        
    for line in tokenized_lines:    
        splitted_line = line.strip("\n").split(" ")
        build_feats(features, splitted_line)
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

def numerical_feature(i, vocab=False):
    feat_name = 'src_feat_'+str(i)
    if vocab:
        global requiring_vocab
        requiring_vocab.append(feat_name)

def identify_tag(word):
    isVal = (len(word) > 0) and ((word[0]=='"' and word[-1]=='"') or (word[0]=="'" and word[-1]=="'") or is_number(word) or (word in ['true', 'false']))
    tag = 'i' #identifier
    if word in KEYWORDS:
        tag = 'k'
    elif word in SPECIAL_SYMBOLS:
        tag = 's'
    elif word in OPERATORS:
        tag = 'o'
    elif word in ASSIGNMENTS:
        tag = 'a'
    elif isVal: # Value
        tag = 'v'
    elif word in ["<START_BUG>", "<END_BUG>"]: #delimiters
        tag = 'd'
    return tag

def get_inc_line_index(line_index, word, forcounter, bugstart, number=False ):
    toRet = line_index[0]
    if number:
        line_index[0] += 1
    if forcounter[0] != -1:
        if word == '(':
            forcounter[0] += 1
        elif word == ')':
            forcounter[0] -= 1
            if forcounter[0] == 0:
                forcounter[0] = -1
    elif word == "for":
        forcounter[0] = 0

    if forcounter[0] == -1 and ((not bugstart[0] and word in ["{", "}", ";", "<END_BUG>"]) or (bugstart[0] and word == "<END_BUG>")) :
        bugstart[0] = False
        if word == "<START_BUG>":
            bugstart[0] = True
        if number:
            line_index[0] = 0
        else:
            line_index[0] += 1   
    return toRet

def make_distbug(line):

    def get_inc_count(count, word):
        if word=="}":
            count[0] -= 1
        toRet = count[0]
        if word=="{":
            count[0] += 1    
        return toRet

    def find_match(line_to_p):
        open_parentheses = 1
        next_word = None
        for word in reversed(line_to_p):
            if open_parentheses == 0:
                next_word = word
                break
            if word == "(":
                open_parentheses -= 1
            elif word == ")":
                open_parentheses += 1
        if next_word is not None and next_word not in ["if", "for", "while"]:
            return True
        return False

    if len(line) == 0:
        return []
    count = [0]
    indents = [ get_inc_count(count, word) for word in line ]
    bug_index = len(line)//2
    if '<START_BUG>' in line:
        bug_index = line.index("<START_BUG>")
    elif '<END_BUG>' in line:
        bug_index = line.index("<END_BUG>")
    max_indent = None
    for idx in range(bug_index, 2, -1):
        if line[idx] == "{" and line[idx-1] == ")" and find_match(line[:idx-1]):
            max_indent = indents[idx-2]
            break
    line_index = [0]
    forcount = [-1]
    startbug = [False]
    line_indexes = [ get_inc_line_index(line_index, word, forcount, startbug) for word in line ]
    bug_line = line_indexes[bug_index]
    line_indexes = [ bug_line-x for x in line_indexes ]
    if max_indent is not None:
        num_arr = np.array(indents)
        mask_arr = num_arr > max_indent
        line_indexes = [ line_indexes[x] if mask_arr[x] else 1 for x in range(len(line_indexes)) ]
    return line_indexes



if __name__=="__main__":
    main(sys.argv[1:])