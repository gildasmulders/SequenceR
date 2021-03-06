import sys

KEYWORDS = {'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'exports', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'module', 'native', 'new', 'open', 'opens', 'package', 'private', 'protected', 'provides', 'public', 'requires', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'to', 'transient', 'transitive', 'try', 'uses', 'void', 'volatile', 'while', 'with'} 
SPECIAL_SYMBOLS = {'[', ']', '(', ')', '{', '}', ',', ';', '@'}
OPERATORS = {'*', '/', '+', '-', '%', '++', '--', '!', '=', '+=', '-=', '/=', '*=', '%=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '?', ':', '&', '|', '^', '~', '<<', '>>', '>>>', '&=', '^=', '|=', '<<=', '>>=', '>>>=', '.'}

def main(argv):
    tokenized_lines = open(argv[0], 'r').readlines()
    tokenized_lines_with_tree_feature = ""
    both = (argv[2] == "both")
    indent = (argv[2] == "indent") or both
    tag = (argv[2] == "tag") or both
    for line in tokenized_lines:
        indentation_count = 0
        new_line_with_tree_feature = ""
        for word in line.strip("\n").split(" "):
            toAdd = word
            if tag:
                isVal = (word[0]=='"' and word[-1]=='"') or (word[0]=="'" and word[-1]=="'") or is_number(word) or (word in ['true', 'false'])
                if word in KEYWORDS:
                    toAdd += "￨" + 'k'
                elif word in SPECIAL_SYMBOLS:
                    toAdd += "￨" + 's'
                elif word in OPERATORS:
                    toAdd += "￨" + 'o'
                elif isVal: # Value
                    toAdd += "￨" + 'v'
                elif word in ["<START_BUG>", "<END_BUG>"]: #delimiters
                    toAdd += "￨" + 'd'
                else: # Identifier
                    toAdd += "￨" + 'i'

            if indent:
                if word=="}":
                    indentation_count -= 1

                toAdd += "￨" + str(indentation_count) 

                if word=="{":
                    indentation_count += 1

            new_line_with_tree_feature += toAdd + " "
        tokenized_lines_with_tree_feature += new_line_with_tree_feature + "\n"
    
    tokenized_file_with_tree_feature = open(argv[1], "w")
    tokenized_file_with_tree_feature.write(tokenized_lines_with_tree_feature + '\n')
    tokenized_file_with_tree_feature.close()
    sys.exit(0)

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

if __name__=="__main__":
    main(sys.argv[1:])