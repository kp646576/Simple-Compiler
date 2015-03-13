from token import Token
from lexer import Lexer
from gforthTable import gforthTable as gt
from gforthTable import varTable as vt
import sys

# Constants for controlling output
GFORTH = 0
GFORTH_DEBUG = 1
PARSETREE = 2
PARSETREE_DEBUG = 3

# Current display setting
DISPLAY = GFORTH

def display(msg, n=0):
    if n == DISPLAY:
        print msg,

class Parser:
    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.curToken = Token(0, '', '')
        self.peekToken = Token(0, '', '')
        self.tokenIdx = 1
        self.prefix = 'kp'
        if len(self.tokens) == 1:
            self.curToken = self.tokens[0]
        elif len(self.tokens) > 1:
            self.curToken = self.tokens[0]
            self.peekToken = self.tokens[1]
        else:
            self.error()
        self.tab = '    '
        self.start()
        #self.S(0)
        print ""

    def start(self):
        while self.curToken.value:
            self.S(0)
            vt = {}
            #self.getNextToken()

    # Original Grammar:
    # S   -> () | (S) | SS | expr

    # Transformed Grammar:
    # S   -> (S'S'' | exprS''
    # S'  -> )      | S)
    # S'' -> SS''   | epsilon
    def S(self, d):
        my = self.curToken.value
        if 'x' in vt:
            print my + ':why x in vt?'
        if self.curToken.value and self.curToken.value == '(':
            # exprS'' expr starting with '('
            if self.peekToken.value and self.isOper(self.peekToken.id):
                self.oper(d)
                self.SPP(d)
            # exprS'' stmt starting with '('
            elif self.peekToken.value and self.peekToken.id == 'stmt':
                display('>> S -> stmts', PARSETREE_DEBUG)
                self.stmts(d)
                display('>> S -> SPP', PARSETREE_DEBUG )
                self.SPP(d)
            # (S'S''
            else:
                display(d * self.tab + '(', PARSETREE)
                self.getNextToken()
                self.SP(d)
                self.SPP(d)
        # exprS'' terminals
        elif self.curToken.value and self.isTerminal(self.curToken.id):
            self.oper(d)
            self.SPP(d) #fails on ((1 2)) without this SPP
        else:
            self.error('S error')

    #S' -> ) | S)
    def SP(self, d):
        # S)
        if self.curToken.value and self.curToken.value != ')':
            self.S(d + 1)
            display(">> SP: " + self.curToken.value, PARSETREE_DEBUG)
        # S) and )
        if self.curToken.value == ')':
            display(d * self.tab + ')', PARSETREE)
            if d > 0:
                self.getNextToken()

    # S'' -> SS'' | epsilon
    def SPP(self, d):
        # SS''
        if self.curToken.value == '(' or self.isTerminal(self.curToken.id):
            display(">> SPP " + self.curToken.value, PARSETREE_DEBUG)
            self.S(d)
            self.SPP(d)
        # epsilon

    # Original Grammar:
    # oper  -> (:= name oper) | (binops oper oper) | (unops oper) | constants | name

    # Transformed Grammar:
    # oper  -> (operP | constants | name
    # operP -> := name oper | binops oper oper | unops oper
    def oper(self, d):
        if self.curToken.value:
            if self.curToken.value == '(':
                display(d * self.tab + '(', PARSETREE)
                self.getNextToken()
                opP = self.operP(d + 1)

                # F: self.paramList(d + 1) ?
                if self.curToken.value == ')':
                    display(d * self.tab + self.curToken.value, PARSETREE)
                    self.getNextToken()
                else:
                    # catch cases like (:= cat 33 charlie)
                    self.error()
                return opP


            elif self.isTerminal(self.curToken.id):
                display(d * self.tab + self.curToken.value, PARSETREE)

                # Guarding against adding e to values like 2e10
                if self.curToken.id == "real" and 'e' not in self.curToken.value:
                    print '{0}e'.format(self.curToken.value),
                elif self.curToken.id == 'string':
                    print 's\" {0}'.format(self.curToken.value[1:]),

                # Variables
                elif self.curToken.id == 'id':
                    var = self.curToken.value
                    if var in vt:
                        print '{0} {1}'.format(var, gt[vt[var]]['access']),
                    else:
                        self.error('using uninitialized variable')
                else:
                    print self.curToken.value,

                cur = self.curToken
                self.getNextToken()
                return cur.id if cur.id != 'id' else vt[cur.value]
            else:
                self.error('current token is neither beginning of oper nor terminal')
        else:
            self.error('current token is null')



    def operP(self, d):
        if self.curToken.id == 'assign':
            assign = self.curToken.value
            display(d * self.tab + assign, PARSETREE)
            self.getNextToken()

            if self.curToken.id == 'id':
                display(d * self.tab + self.curToken.value, PARSETREE)
                var = self.curToken.value
                self.getNextToken()

                eType = self.oper(d)
                self.gforthSetVar(var, eType)
            else:
                self.error('non-name found after assign in (:= name oper)')

        # Need to deal with - separately
        elif self.curToken.id == 'op':
            op = self.curToken.value
            display(d * self.tab + op, PARSETREE)
            self.getNextToken()
            op1 = self.oper(d)

            # (binop, unop, := ) or constants, name
            if (self.curToken.value == '(' and self.isOper(self.peekToken.id) or self.isTerminal(self.curToken.id)):
                op2 = self.oper(d)
                return self.gforthBOPS(op1, op2, op)
            else:
                print '0 swap',
                return self.gforthUOPS(op1, op)

        elif self.curToken.id == 'bop':
            bop = self.curToken.value
            display(d * self.tab + bop, PARSETREE)
            self.getNextToken()
            # Values can be terminals or expressions
            op1 = self.oper(d)
            op2 = self.oper(d)
            display('op1: {0} op2: {1}'.format(op1, op2), PARSETREE_DEBUG)
            return self.gforthBOPS(op1, op2, bop)

        elif self.curToken.id == 'uop':
            uop = self.curToken.value
            display(d * self.tab + uop, PARSETREE)
            self.getNextToken()
            op1 = self.oper(d)
            return self.gforthUOPS(op1, uop)
        else:
            self.error('prefix operation {0} not found in grammar of oper'.format(self.curToken.id))

    # stmts -> ifstmts | whilestmts | letstmts | printsmts
    def stmts(self, d):
        if self.curToken.value == '(':
            display(d * self.tab + self.curToken.value, PARSETREE)
            self.getNextToken()
            self.stmtsP(d + 1)
            # display(">> stmts -> curToken = " + self.curToken.value, PARSETREE_DEBUG)
            if self.curToken.value == ')':
                display(d * self.tab + self.curToken.value, PARSETREE)
                self.getNextToken()
            else:
                self.error('stmts 1 error')
        else:
            self.error('stmts 2 error')

    def stmtsP(self, d):
        # ifstmts -> (if expr expr) | (if expr exp expr)
        if self.curToken.value == 'if':
            stmt = self.curToken.value
            display(d * self.tab + stmt, PARSETREE)
            print ': {0}{1}'.format(self.prefix, stmt),
            self.getNextToken()
            self.expr(d)

            # 'if' needs to be printed after condition for gforth syntax
            print 'if',
            self.expr(d)
            if self.curToken.value and self.curToken.value != ')':
                print 'else',
                self.expr(d)

            # Error if more than 3 args
            if self.curToken.value and self.curToken.value != ')':
                self.error('too many arguments given in if statment')
            print 'endif ; {0}{1}'.format(self.prefix, stmt),

        # whilestmts -> (while expr exprlist)
        elif self.curToken.value == 'while':
            stmt = self.curToken.value
            display(d * self.tab + stmt, PARSETREE)
            print ': {0}{1} begin'.format(self.prefix, stmt),
            self.getNextToken()
            self.expr(d)
            print 'while',
            self.exprlist(d)
            print 'repeat ; {0}{1}'.format(self.prefix, stmt),

        # letstmts -> ( let (varlist) )
        elif self.curToken.value == 'let':
            display(d * self.tab + self.curToken.value, PARSETREE)
            self.getNextToken()
            if self.curToken.value == '(':
                self.getNextToken()
                self.varlist(d)
                if self.curToken.value == ')':
                    self.getNextToken()
            else:
                self.error('let syntax error ( let (varlist) )')
        elif self.curToken.value == 'stdout':
            display (d * self.tab + self.curToken.value, PARSETREE)
            self.getNextToken()
            eType = self.oper(d)
            self.gforthSTDOUT(eType)
            if self.curToken.value and self.curToken.value != ')':
                self.error()
        else:
            self.error()

    # varlist -> (name type) | (name type) varlist
    def varlist(self, d):
        if self.curToken.value == '(':
            #print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.id == 'id':
                #print (d + 1) * self.tab + self.curToken.value
                var = self.curToken.value
                self.getNextToken()
                if self.isType(self.curToken.value):
                    #print (d + 1) * self.tab + self.curToken.value
                    varType = self.curToken.value
                    self.gforthInitVar(var, varType)
                    self.getNextToken()
                    if self.curToken.value == ')':
                        #print d * self.tab + self.curToken.value
                        self.getNextToken()
                        display(">> varlist: " + self.curToken.value, PARSETREE_DEBUG)
                        if self.curToken.value == '(' and self.peekToken.id == 'id':
                            display(">> varlist -> varlist", PARSETREE_DEBUG)
                            self.varlist(d)
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()
        else:
            self.error()

    def exprlist(self, d):
        # expr
        self.expr(d)
        # expr exprlist
        display(">> exprlist -> expr -> " + self.curToken.value, PARSETREE_DEBUG )
        if (self.curToken.value == '(' and (self.isOper(self.peekToken.id) or self.peekToken.id == 'stmt')) or self.isTerminal(self.curToken.id):
            display(">> exprlist -> exprlist", PARSETREE_DEBUG)
            self.exprlist(d)

    def expr(self, d):
        display(">> expr: " + self.curToken.value + self.peekToken.value, PARSETREE_DEBUG)
        if self.curToken.value == '(' and self.isOper(self.peekToken.id):
            self.oper(d)
        elif self.isTerminal(self.curToken.id):
            display(">> expr -> oper", PARSETREE_DEBUG)
            self.oper(d)
        elif self.curToken.value == '(' and self.peekToken.id == 'stmt':
            self.stmts(d)
        else:
            self.error()

    def gforthInitVar(self, var, varType):
        if var and self.isType(varType):
            print '{0} {1}'.format(gt[varType]['init'], var),
            # Add variable to variable table
            vt[var] = varType
        else:
            self.error('variable {0} undefined and/or illegal type'.format(var))

    # Q: Is there a need to store the value?
    def gforthSetVar(self, var, eType):
        if var in vt:
            varType = vt[var]
            if varType == eType:
                print '{0} {1}'.format(var, gt[varType]['assign']),
            else:
                self.error('Type Mismatch: setting {0} variable to {1}'.format(varType, eType))
        else:
            self.error('variable {0} not initialized'.format(var))

    def gforthUOPS(self, op1, uop):
        # print '\nuop:' + str(op1)
        if (uop == 'sin' or uop == 'cos' or uop == 'tan') and op1 != 'real':
            print 's>f ' + gt[uop],
            return 'real'
        elif op1 == 'real':
            if uop == 'not':
                print 'f' + gt[uop],
            else:
                print gt[uop],
        elif uop == 'not':
            print gt[uop],
        else:
            print uop,
        return op1

    def gforthBOPS(self, op1, op2, bop):
        if op1 == 'int' and op2 == 'int':
            # Don't change if-else orderings
            # Case where % is different for ints and floats
            if bop == '%':
                print 'mod',
            elif bop == '^':
                print 's>f s>f fswap f** f>s',
            elif bop == "!=":
                print '<>',
            else:
                print bop,
            return 'int'
        elif bop == 'and' or bop == 'or':
            if op1 == 'int' and op2 == 'real':
                print 'f>s ' + bop,
            elif op1 == 'real' and op2 == 'int':
                print 'f>s fswap ' + bop,
            elif op1 == 'real' and op2 == 'real':
                print 'f>s f>s fswap ' + bop,
            return 'int'
        elif op1 == 'int' and op2 == 'real':
            print 's>f fswap ' + gt[bop],
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'real' and op2 == 'int':
            print 's>f ' + gt[bop],
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'real' and op2 == 'real':
            print gt[bop],
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'string' and op2 == 'string':
            if bop != '+':
                self.error()
            else:
                print 's+',
            return 'string'
        else:
            print bop,
            return op1

    def gforthSTDOUT(self, op1):
        if op1 == 'int':
            print '.',
        elif op1 =='real':
            print 'f.',
        elif op1 == 'string':
            print 'type',

    def isRelational(self, bop):
        return True if bop in ['=', '<', '<=', '>', '>=', '!='] else False

    def isOper(self, id):
        return True if id in ['assign', 'bop', 'uop', 'op'] else False

    def isTerminal(self, id):
        return True if id in ['bool', 'id', 'int', 'real', 'string'] else False

    def isType(self, value):
        return True if value in ['bool', 'int', 'real', 'string'] else False

    def error(self, msg=''):
        print >> sys.stderr, 'parser error line: ' + str(self.curToken.line) + ' token value: ' + str(self.curToken.value) + ' msg: ' + msg
        sys.exit(0)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            self.peekToken = Token(self.curToken.line, '', '')
