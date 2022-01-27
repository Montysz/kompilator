from sly import Lexer, Parser
from structures import Symbols, Array, Variable
from code import Code
import sys

class MyLexer(Lexer):
    tokens = {
            VAR, BEGIN, END, PID, NUM, 
            IF, THEN, ELSE, ENDIF, 
            WHILE, DO, ENDWHILE, REPEAT, UNTIL, 
            FOR, FROM, TO, DOWNTO, 
            ENDFOR, READ, WRITE, GETS,
            EQ, NEQ, GE, LE, GEQ, LEQ, 
            PLUS,MINUS,TIMES,DIV,MOD, ASSIGN
            }

    literals = {',' ,':', ';', '(', ')','[',']'}
    ignore = ' \t'

    @_(r'\([^\)]*\)')
    def ignore_comment(self,t):
        self.lineno += t.value.count('\n')
    
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    @_(r'\-?\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        raise Exception(f"Zly symbol, '{t.value[0]}'")
    
    VAR = r"VAR"
    BEGIN = r"BEGIN"
    ENDIF = r"ENDIF"

    WRITE = r"WRITE"
    READ = r"READ"
    ASSIGN = r"ASSIGN"

    PLUS = r"PLUS"
    MINUS = r"MINUS"
    TIMES = r"TIMES"
    DIV = r"DIV"
    MOD = r"MOD"


    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"

    EQ = r"EQ"
    NEQ = r"NEQ"
    GEQ = r"GEQ"
    LEQ = r"LEQ"
    GE = r"GE"
    LE = r"LE"

    WHILE = r"WHILE"
    ENDWHILE = r"ENDWHILE"
    FOR = r"FOR"
    ENDFOR = r"ENDFOR"
    
    DOWNTO = r"DOWNTO"
    DO = r"DO"
    TO = r"TO"

    FROM = r"FROM"
    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"

    PID = r"[_a-z]+"

    END = r"END"

class MyParser(Parser):
    tokens = MyLexer.tokens
    symbols = Symbols()
    code = None

    @_('VAR declarations BEGIN commands END', 'BEGIN commands END')
    def program(self, p):
        self.code = Code(p.commands, self.symbols)
        return self.code
    
    @_('declarations "," PID', 'PID')
    def declarations(self, p):
        self.symbols.add_variable(p[-1])

    @_('declarations "," PID "[" NUM ":" NUM "]" ')
    def declarations(self, p):
        self.symbols.add_array(p[2], p[4], p[6])

    @_('PID "[" NUM ":" NUM "]"')
    def declarations(self, p):
        self.symbols.add_array(p[0], p[2], p[4])
    
    @_('PID "[" PID "]"')
    def identifier(self, p):
        if p[0] in self.symbols and type(self.symbols[p[0]]) == Array:
            if p[2] in self.symbols and type(self.symbols[p[2]]) == Variable:
                return "array", p[0], ("load", p[2])
            else:
                return "array", p[0], ("load", ("undeclared", p[2]))
        else:
            raise Exception(f"Niezadeklarowanna tablica {p[0]}")
   
    @_('PID "[" NUM "]"')
    def identifier(self, p):
        if p[0] in self.symbols and type(self.symbols[p[0]]) == Array:
            return "array", p[0], p[2]
        else:
            raise Exception(f"Niezadeklarowanna tablica {p[0]}")

    def error(self, token):
        raise Exception(f"syntax error, '{token.value}' w linni {token.lineno}")


    @_('commands command')
    def commands(self, p):
        #print("ddp", p[0][0])
        return p[0] + [p[1]]
    
    @_('identifier')
    def value(self, p):
        return "load", p[0]
    
    @_('identifier ASSIGN expression ";"')
    def command(self, p):
        return "assign", p[0], p[2]
    
    @_('identifier GETS expression ";"')
    def command(self, p):
        return "assign", p[0], p[2]

    @_('command')
    def commands(self, p):
        #print("p", p[0][0])
        return [p[0]]
    
    @_('value')
    def expression(self, p):
        return p[0]

    @_('READ identifier ";"')
    def command(self, p):
        #print("p", p[0][0])
        return "read", p[1]

    @_('PID')
    def identifier(self, p):
        #print("PID1")
        if p[0] in self.symbols:
            #print("PID2", p[0])
            return p[0]
        else:
            #print("PID3")
            return "undeclared", p[0]

    @_('WRITE value ";"')
    def command(self, p):
        return "write", p[1]

    @_('NUM')
    def value(self, p):
        return "const", p[0]

    @_('value PLUS value')
    def expression(self, p):
        return "add", p[0], p[2]

    @_('value MINUS value')
    def expression(self, p):
        return "sub", p[0], p[2]

    @_('value TIMES value')
    def expression(self, p):
        return "mul", p[0], p[2]

    @_('value DIV value')
    def expression(self, p):
        return "div", p[0], p[2]

    @_('value MOD value')
    def expression(self, p):
        return "mod", p[0], p[2]

    @_('value EQ value')
    def condition(self, p):
        #print("eq ", p[0], p[2])
        return "eq", p[0], p[2]

    @_('value NEQ value')
    def condition(self, p):
        return "neq", p[0], p[2]

    @_('value LE value')
    def condition(self, p):
        return "le", p[0], p[2]

    @_('value GE value')
    def condition(self, p):
        return "ge", p[0], p[2]

    @_('value LEQ value')
    def condition(self, p):
        return "leq", p[0], p[2]

    @_('value GEQ value')
    def condition(self, p):
        return "geq", p[0], p[2]


    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        ret = "if", p[1], p[3]
        return ret

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        ret = "ifelse", p[1], p[3], p[5]
        return ret

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        ret = "while", p[1], p[3]
        return ret

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        return "until", p[3], p[1]

    @_('FOR PID FROM value TO value DO commands ENDFOR')
    def command(self, p):
        ret = "forup", p[1], p[3], p[5], p[7]
        self.symbols.add_variable(p[1], True)
        #print("ADD ITERATOR", p[1])
        return ret

    @_('FOR PID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        ret = "fordown", p[1], p[3], p[5], p[7]
        self.symbols.add_variable(p[1], True)
        return ret

sys.tracebacklimit = 0
lex = MyLexer()
pars = MyParser()
with open(sys.argv[1]) as in_f:
    text = in_f.read()

pars.parse(lex.tokenize(text))
code_gen = pars.code
#print("pars", pars)
#print("code", pars.code)

code_gen.generate_code()
with open(sys.argv[2], 'w') as f:
    for l in code_gen.code:
        print(l, file=f)