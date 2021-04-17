
CFS = {"switch", "if", "for", "else", "for", "while", "do"}
OPERATORS = {'*', '/', '+', '-', '%', '++', '--', '!', '=', '+=', '-=', '/=', '*=', '%=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '?', ':', '&', '|', '^', '~', '<<', '>>', '>>>', '&=', '^=', '|=', '<<=', '>>=', '>>>=', '.'}
ASSIGNMENTS = {'=', '+=', '-=', '/=', '*=', '%=', '&=', '^=', '|=', '<<=', '>>=', '>>>='}

def print_body(body, level=False, tag=False):
    toPrint = ""
    toPrint = [elem.mystr(level, tag) for elem in body]
    toPrint = " ".join(toPrint)
    return toPrint.strip()

def af(s, *args):
    feat = ""
    for f in args:
        feat += "￨" + str(f)
    tmp = [word+feat for word in s.split()]
    return " ".join(tmp)

class Buggy_line():
    def __init__(self, body, level):
        self.body = "<START_BUG> " + " ".join(body) + " <END_BUG>"
        self.level = level
    def mystr(self, level=False, tag=False):
        toRet = self.body
        if level:
            toRet = af(toRet, self.level)
        if tag:
            toRet = af(toRet, "b") # buggy line -> 'b'
        return toRet

class case_elem():
    def __init__(self, val, body, level):
        self.val = val
        self.body = body
        self.level = level
    def get_children(self):
        return self.body
    def mystr(self, level=False, tag=False):
        toRet = self.val
        if level:
            toRet = af(toRet, self.level)
        if tag:
            toRet = af(toRet, "c") # case/condition -> 'c'
        return  toRet + " " + print_body(self.body, level, tag) 

class Switch_elem():
    def __init__(self, var, cases, level):
        self.var = " ".join(var)
        self.cases = cases
        self.level = level
        self.parts = ["switch (", ") {", "}"]
    def get_children(self):
        return cases
    def mystr(self, level=False, tag=False):
        parts = self.parts
        var = self.var
        if level:
            parts = [af(part, self.level) for part in parts]
            var = af(var, self.level)
        if tag:
            parts = [af(part, "s") for part in parts] # switch element -> 's'
            var = af(var, "c") # switch var is considered part of conditional/case element -> 'c'
        return parts[0] + " " + var + " " + parts[1] + " " + print_body(self.cases, level, tag) + " " + parts[2]

class While_elem():
    def __init__(self, cond, body, level):
        self.cond = " ".join(cond)
        self.body = body
        self.level = level
        self.parts = ["while (", ") {", "}"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        cond = self.cond
        if level:
            parts = [af(part, self.level) for part in parts]
            cond = af(cond, self.level+1)
        if tag:
            parts = [af(part, "l") for part in parts] # loop element -> 'l'
            cond = af(cond, "c") # condition -> 'c'
        return parts[0] + " " + cond + " " + parts[1] + " " + print_body(self.body, level, tag) + " " + parts[2]

class DoWhile_elem():
    def __init__(self, cond, body, level):
        self.cond = " ".join(cond)
        self.body = body
        self.level = level
        self.parts = ["do {", "} while (", ") ;"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        cond = self.cond
        if level:
            parts = [af(part, self.level) for part in parts]
            cond = af(cond, self.level+1)
        if tag:
            parts = [af(part, "l") for part in parts] # loop element -> 'l'
            cond = af(cond, "c") # condition -> 'c'
        return parts[0] + " " + print_body(self.body, level, tag) + " " + parts[1] + " " + cond + " " + parts[2]

class For_elem():
    def __init__(self, cond, body, level):
        self.cond = " ".join(cond)
        self.body = body
        self.level = level
        self.parts = ["for (", ") {", "}"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        cond = self.cond
        if level:
            parts = [af(part, self.level) for part in parts]
            cond = af(cond, self.level+1)
        if tag:
            parts = [af(part, "l") for part in parts] # loop element -> 'w'
            cond = af(cond, "c") # condition -> 'c'
        return parts[0] + " " + cond + " " + parts[1] + " " + print_body(self.body, level, tag) + " " + parts[2] 

class If_elem():
    def __init__(self, cond, body, level):
        self.cond = " ".join(cond)
        self.body = body
        self.level = level
        self.parts = ["if (", ") {", "}"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        cond = self.cond
        if level:
            parts = [af(part, self.level) for part in parts]
            cond = af(cond, self.level+1)
        if tag:
            parts = [af(part, "j") for part in parts] # jump element (if/else) -> 'j'
            cond = af(cond, "c") # condition -> 'c'
        return parts[0] + " " + cond + " " + parts[1] + " " + print_body(self.body, level, tag) + " " + parts[2]

class Else_elem():
    def __init__(self, body, level):
        self.body = body
        self.level = level
        self.parts = ["else {", "}"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        if level:
            parts = [af(part, self.level) for part in parts]
        if tag:
            parts = [af(part, "j") for part in parts] # jump element (if/else) -> 'j'
        return parts[0] + " " + print_body(self.body, level, tag) + " " + parts[1]

class ElseIf_elem():
    def __init__(self, cond, body, level):
        self.cond = " ".join(cond)
        self.body = body
        self.level = level
        self.parts = ["else if (", ") {", "}"]
    def get_children(self):
        return body
    def mystr(self, level=False, tag=False):
        parts = self.parts
        cond = self.cond
        if level:
            parts = [af(part, self.level) for part in parts]
            cond = af(cond, self.level+1)
        if tag:
            parts = [af(part, "j") for part in parts] # jump element (if/else) -> 'j'
            cond = af(cond, "c") # condition -> 'c'
        return parts[0] + " " + cond + " " + parts[1] + " " + print_body(self.body, level, tag) + " " + parts[2]

class Expr_elem():
    def __init__(self, body, level):
        self.body = " ".join(body)
        self.level = level
    def mystr(self, level=False, tag=False):
        toRet = self.body
        if level:
            toRet = af(toRet, self.level)
        if tag:
            toRet = af(toRet, "e") # expression -> 'e'
        return toRet

class Def_elem():
    def __init__(self, name, args, body, level):
        self.name = name
        self.args = " ".join(args)
        self.body = body
        self.level = level
        self.parts = ["(", ") {", "}"]
    def get_children(self):
        return self.body
    def mystr(self, level=False, tag=False):
        name = self.name
        parts = self.parts
        args = self.args
        if level:
            name = af(name, self.level)
            parts = [af(part, self.level) for part in parts]
            args = af(args, self.level+1)
        if tag:
            name = af(name, "f") # function definition -> 'f'
            parts = [af(part, "f") for part in parts]
            args = af(args, "p") # parameters -> p
        return name + " " + parts[0] + " " + args + " " + parts[1] + " " + print_body(self.body, level, tag) + " " + parts[2]

class Class_elem():
    def __init__(self, name, body, level):
        self.name = " ".join(name)
        self.body = body
        self.level = level
        self.parts = ["{", "}"]
    def get_children(self):
        return self.body
    def mystr(self, level=False, tag=False):
        name = self.name
        parts = self.parts
        if level:
            name = af(name, self.level)
            parts = [af(part, self.level) for part in parts]
        if tag:
            name = af(name, "d") # class definition -> 'd'
            parts = [af(part, "d") for part in parts]
        return name + " " + parts[0] + " " + print_body(self.body, level, tag) + " " + parts[1]

class Simple_AST():
    def __init__(self, root):
        self.root = root

    def mystr(self, level=False, tag=False):
        return print_body(self.root, level, tag)

    def __str__(self):
        return print_body(self.root)
    # @staticmethod
    # def build_tree(s):

    #     for token_idx in range(len(s)):

    @staticmethod
    def get_statements(code, level=0):
        statements = []
        new_statement = []
        toRead = code
        while len(toRead) > 0:
            idx = 0
            token = toRead[idx]
            toRead = toRead[1:]
            new_statement.append(token)
            if token == "<START_BUG>":
                bug, rest = find_match([token] + toRead, "<END_BUG>")
                statements.append(Buggy_line(bug, level))
                new_statement = []
                toRead = rest
            elif token =="class":
                if "{" in toRead:
                    eoname = toRead.index("{")
                    name = new_statement + toRead[:eoname]
                    body, rest = find_match(toRead[eoname:], "}")
                    statements.append(Class_elem(name, Simple_AST.get_statements(body, level+1), level))
                    new_statement = []
                    toRead = rest
            elif token == ';':
                statements.append(Expr_elem(new_statement, level)) 
                new_statement = []  
            elif token in CFS and len(toRead) > 0:
                next_token = toRead[0]
                # handling all cases
                ## If case
                if token == "if":
                    if next_token == "(":
                        cond, rest = find_match(toRead, ")")
                        # if block
                        if len(rest) > 0 and rest[0] == "{":
                            body, rest = find_match(rest, "}")
                            statements.append(If_elem(cond, Simple_AST.get_statements(body, level+1), level))
                            new_statement = []
                            toRead = rest
                        # if without block -> only one statement is part of the block
                        elif ";" in rest:
                            eos_idx = rest.index(";")
                            statements.append(If_elem(cond, Simple_AST.get_statements(rest[:eos_idx+1], level+1), level))
                            new_statement = []
                            toRead = rest[eos_idx+1:]
                ## Else case
                elif token == "else":                    
                    # else if case -> similar to simple if
                    if next_token == "if":
                        toRead = toRead[1:]
                        if len(toRead) > 0 and toRead[0] == "(":
                            cond, rest = find_match(toRead, ")")
                            if len(rest) > 0 and rest[0] == "{":
                                body, rest = find_match(rest, "}")
                                statements.append(ElseIf_elem(cond, Simple_AST.get_statements(body, level+1), level))
                                new_statement = []
                                toRead = rest
                            elif ";" in rest:
                                eos_idx = rest.index(";")
                                statements.append(ElseIf_elem(cond, Simple_AST.get_statements(rest[:eos_idx+1], level+1), level))
                                new_statement = []
                                toRead = rest[eos_idx+1:]
                    # else block
                    elif next_token == "{":
                        body, rest = find_match(toRead, "}")
                        statements.append(Else_elem(Simple_AST.get_statements(body, level+1), level))
                        new_statement = []
                        toRead = rest
                    # else without block
                    elif ";" in toRead:
                        eos_idx = toRead.index(";")
                        statements.append(Else_elem(Simple_AST.get_statements(toRead[:eos_idx+1], level+1), level))
                        new_statement = []
                        toRead = toRead[eos_idx+1:]
                ## While case
                elif token == "while":
                    if next_token == "(":
                        cond, rest = find_match(toRead, ")")
                        # while block
                        if len(rest) > 0 and rest[0] == "{":
                            body, rest = find_match(rest, "}")
                            statements.append(While_elem(cond, Simple_AST.get_statements(body, level+1), level))
                            new_statement = []
                            toRead = rest
                        # while without block
                        elif ";" in rest:
                            eos_idx = rest.index(";")
                            statements.append(While_elem(cond, Simple_AST.get_statements(rest[:eos_idx+1], level+1), level))
                            new_statement = []
                            toRead = rest[eos_idx+1:]
                ## DoWhile case
                elif token == "do":
                    if next_token == "{":
                        body, rest = find_match(toRead, "}")
                        # do while block
                        if len(rest) > 1 and rest[0] == "while" and rest[1] == "(":
                            cond, rest = find_match(rest[1:], ")")
                            if len(rest) > 0 and rest[0] == ";":
                                statements.append(DoWhile_elem(cond, Simple_AST.get_statements(body, level+1), level))
                                new_statement = []
                                toRead = rest[1:]
                ## For case
                elif token == "for":
                    if next_token == "(":
                        cond, rest = find_match(toRead, ")")
                        # for block
                        if len(rest) > 0 and rest[0] == "{":
                            body, rest = find_match(rest, "}")
                            statements.append(For_elem(cond, Simple_AST.get_statements(body, level+1), level))
                            new_statement = []
                            toRead = rest
                        # for without block
                        elif ";" in rest:
                            eos_idx = rest.index(";")
                            statements.append(For_elem(cond, Simple_AST.get_statements(rest[:eos_idx+1], level+1), level))
                            new_statement = []
                            toRead = rest[eos_idx+1:]
                ## Switch case
                elif token == "switch":
                    if next_token == "(":
                        var, rest = find_match(toRead, ")")
                        # switch block
                        if len(rest) > 0 and rest[0] == "{":
                            body, rest = find_match(rest, "}")
                            ## getting all cases
                            cases_elems = []
                            while len(body) > 0:
                                case_token = body[0]
                                body = body[1:]
                                if case_token == "case" and ":" in body:
                                    end_case_idx = body.index(":")
                                    cases_elems.append(case_elem("case " + " ".join(body[:end_case_idx+1]), [], level+1))
                                    body = body[end_case_idx+1:]
                                elif case_token == "default" and len(body) > 0 and body[0]==":":
                                    cases_elems.append(case_elem("default :", [], level+1))
                                    body = body[1:]
                                elif len(cases_elems) > 0:
                                    cases_elems[-1].body.append(case_token)
                            for case_el in cases_elems:
                                case_el.body = Simple_AST.get_statements(case_el.body, level+2)              
                            
                            statements.append(Switch_elem(var, cases, level))
                            new_statement = []
                            toRead = rest       
            elif token not in OPERATORS and token not in ASSIGNMENTS and len(toRead) > 0:
                next_token = toRead[0]
                # could be class/method definition -> identify patterns
                if next_token == "(": # looking for "name ( args ) { body } rest" pattern
                    args, rest = find_match(toRead, ")")                    
                    if len(rest) > 0 and rest[0] == "{":
                        body, rest = find_match(rest, "}")
                        statements.append(Def_elem(" ".join(new_statement), args, Simple_AST.get_statements(body, level+1), level))
                        new_statement = []
                        toRead = rest
                elif next_token == "{": # looking for "name { body } rest" pattern 
                    body, rest = find_match(toRead, "}")
                    statements.append(Def_elem(" ".join(new_statement), [], Simple_AST.get_statements(body, level+1), level))
                    new_statement = []
                    toRead = rest
        return statements


def find_match(line, end_symbol):
    if len(line) == 0: 
        return [], []
    opened_symbols = 1
    s = []
    remains = []
    start_symbol = line[0]
    found_end = False
    for idx in range(1, len(line)):
        word = line[idx]        
        if word == end_symbol:
            opened_symbols -= 1
            if opened_symbols == 0:
                remains = line[idx+1:]
                break
        elif word == start_symbol:
            opened_symbols += 1
        s.append(word)
    return (s, remains)

def remove_offset(code): 
    def make_feat(feats):
        if len(feats) == 0:
            return ""
        toRet = "￨"
        toRet += "￨".join(feats)
        return toRet
    code = code.split()
    try:
        features = [int(token.split("￨")[1]) for token in code]
    except IndexError:
        print(f"Round token without feature")
    min_feat = min(features)
    code = [code[i].split("￨")[0]+"￨"+str(features[i]-min_feat+1)+make_feat(code[i].split()[2:]) for i in range(len(code))]
    return " ".join(code)

if __name__=="__main__":
    code = "public class Main { static void myStaticMethod ( ) { } public void myPublicMethod ( ) { } public static void main ( String [ ] args ) { if ( 3 < 4 ) Main . myStaticMethod ( ) ; Main myObj = new Main ( ) ; <START_BUG> myObje . myPublicMethod ( ) ; <END_BUG> } }"
    root = Simple_AST.get_statements(code.split())
    myTreeCode = Simple_AST(root)
    print(myTreeCode.mystr(tag=True, level=True))
# a = (a*b)+x*(y+z);
# some_class.some_function((a*b)+x*(y+z), );
#
# control flow: switch (var) {case val:} | while (cond) {} | do {} while(cond) | for(type var:coll) {} | for(type var=val;cond;var++) {} | if (cond) {} | else {} | else if (cond) {}
# declaration statements/expression statements -> always ending with ';'

