from token import Token
from lexer import Lexer
import sys

debugOn = False

def debug(on, msg):
    if on:
        print msg

class Parser:
    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.curToken = Token(0, '', '')
        self.peekToken = Token(0, '', '')
        self.tokenIdx = 1
        if len(self.tokens) == 1:
            self.curToken = self.tokens[0]
        elif len(self.tokens) > 1:
            self.curToken = self.tokens[0]
            self.peekToken = self.tokens[1]
        else:
            self.error()
        self.tab = '    '
        self.S(0)

    # S   -> (S'S'' | exprS''
    # S'  -> )      | S)
    # S'' -> SS''   | epsilon
    def S(self, d):
        if self.curToken.value and self.curToken.value == '(':
            # exprS'' expr starting with '('
            if self.peekToken.value and self.isOper(self.peekToken.id):
                self.oper(d)
                self.SPP(d)
                if self.curToken.value:
                    self.error()
            # exprS'' stmt starting with '('
            elif self.peekToken.value and self.peekToken.id == 'stmt':
                debug(debugOn, '>> S -> stmts')
                self.stmts(d)
                debug(debugOn, '>> S -> SPP')
                self.SPP(d)
                if self.curToken.value:
                    self.error()
            # (S'S''
            else:
                print d * self.tab + '('
                self.getNextToken()
                self.SP(d)
                self.SPP(d)
        # exprS'' terminals
        elif self.curToken.value and self.isTerminal(self.curToken.id):
            self.oper(d)
            self.SPP(d) #fails on ((1 2)) without this SPP
        else:
            self.error()

    #S' -> ) | S)
    def SP(self, d):
        # S)
        if self.curToken.value and self.curToken.value != ')':
            self.S(d + 1)
            debug(debugOn, ">> SP: " + self.curToken.value)
        # S) and )
        if self.curToken.value == ')':
            print d * self.tab + ')'
            self.getNextToken()
        else:
            self.error()

    # S'' -> SS'' | epsilon
    def SPP(self, d):
        # SS''
        if self.curToken.value == '(' or self.isTerminal(self.curToken.id):
            debug(debugOn, ">> SPP " + self.curToken.value)
            self.S(d)
            self.SPP(d)
        # epsilon

    # oper  -> (:= name oper) | (binops oper oper) | (unops oper) | constants | name
    # oper  -> (operP | constants | name
    # operP -> := name oper | binops oper oper | unops oper
    def oper(self, d):
        if self.curToken.value:
            if self.curToken.value == '(':
                print d * self.tab + '('
                self.getNextToken()
                self.operP(d + 1)
                if self.curToken.value == ')':
                    print d * self.tab + self.curToken.value
                    self.getNextToken()
                else:
                    # catch cases like (:= cat 33 charlie)
                    self.error()
            elif self.isTerminal(self.curToken.id):
                print d * self.tab + self.curToken.value
                self.getNextToken()
            else:
                self.error()
        else:
            self.error()

    def operP(self, d):
        if self.curToken.id == 'assign':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.id == 'id':
                print d * self.tab + self.curToken.value
                self.getNextToken()
                self.oper(d)
            else:
                self.error()

        # Need to deal with - separately
        elif self.curToken.id == 'op':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
            # (binop, unop, := ) or constants, name
            if (self.curToken.value == '(' and self.isOper(self.peekToken.id) or self.isTerminal(self.curToken.id)):
                self.oper(d)
        elif self.curToken.id == 'bop':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
            # need to get token?
            self.oper(d)
        elif self.curToken.id == 'uop':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
        else:
            self.error()


    # stmts -> ifstmts | whilestmts | letstmts | printsmts
    def stmts(self, d):
        if self.curToken.value == '(':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.stmtsP(d + 1)
            debug(debugOn, ">> stmts -> curToken = " + self.curToken.value)
            if self.curToken.value == ')':
                print d * self.tab + self.curToken.value
                self.getNextToken()
            else:
                self.error
        else:
            self.error

    def stmtsP(self, d):
        # ifstmts -> (if expr expr) | (if expr exp expr)
        if self.curToken.value == 'if':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.expr(d)
            self.expr(d)
            if self.curToken.value and self.curToken.value != ')':
                self.expr(d)
            # Error if more than 3 args
            if self.curToken.value and self.curToken.value != ')':
                self.error()
        elif self.curToken.value == 'while':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.expr(d)
            debug(debugOn, ">> while -> expr ->")
            self.exprlist(d)
        # letstmts -> let( (varlist) )
        elif self.curToken.value == 'let':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.value == '(':
                self.getNextToken()
                self.varlist(d)
            else:
                self.error
        elif self.curToken.value == 'stdout':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
            if self.curToken.value and self.curToken.value != ')':
                self.error()
        else:
            self.error()

    # varlist -> (name type) | (name type) varlist
    def varlist(self, d):
        if self.curToken.value == '(':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.id == 'id':
                print (d + 1) * self.tab + self.curToken.value
                self.getNextToken()
                if self.isType(self.curToken.value):
                    print (d + 1) * self.tab + self.curToken.value
                    self.getNextToken()
                    if self.curToken.value == ')':
                        print d * self.tab + self.curToken.value
                        self.getNextToken()
                        debug(debugOn, ">> varlist: " + self.curToken.value)
                        if self.curToken.value == '(' and self.peekToken.id == 'id':
                            debug(debugOn, ">> varlist -> varlist")
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
        debug(debugOn, ">> exprlist -> expr -> " + self.curToken.value)
        if (self.curToken.value == '(' and (self.isOper(self.peekToken.id) or self.peekToken.id == 'stmt')) or self.isTerminal(self.curToken.id):
            debug(debugOn, ">> exprlist -> exprlist")
            self.exprlist(d)

    def expr(self, d):
        debug(debugOn, ">> expr: " + self.curToken.value + self.peekToken.value)
        if self.curToken.value == '(' and self.isOper(self.peekToken.id):
            self.oper(d)
        elif self.isTerminal(self.curToken.id):
            debug(debugOn, ">> expr -> oper")
            self.oper(d)
        elif self.curToken.value == '(' and self.peekToken.id == 'stmt':
            self.stmts(d)
        else:
            self.error()


    def isOper(self, id):
        return True if id in ['assign', 'bop', 'uop', 'op'] else False

    def isTerminal(self, id):
        return True if id in ['bool', 'id', 'int', 'real', 'string'] else False

    def isType(self, value):
        return True if value in ['bool', 'int', 'real', 'string'] else False

    def error(self):
        print >> sys.stderr,"Parser error line: " + str(self.curToken.line) + ' token value: ' + str(self.curToken.value)
        sys.exit(0)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            self.peekToken = Token(self.curToken.line, '', '')
