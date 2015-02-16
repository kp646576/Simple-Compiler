from token import Token
from lexer import Lexer
from parseTree import ParseTree
from parseTree import ParseNode
import sys

debugOn = True

def debug(on, msg):
    if on:
        print msg
# change floats to reals again
# need to use peek to determine
class Parser:
    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.curToken = Token(0, '', '')
        self.peekToken = ''
        if len(self.tokens) > 1:
            self.curToken = self.tokens[0]
            self.peekToken = self.tokens[1]
        self.tokenIdx = 1
        self.depth = 0
        self.tab = '    '
        self.curNode = ParseNode(Token(0, 'root', 'root'))
        self.S(0)
        self.parseTree = ParseTree(self.curNode)

    def isOper(self, id):
        return True if id in ['assign', 'bop', 'uop'] else False
    #S   -> (S'S'' | exprS''
    #S'  -> )      | S)
    #S'' -> SS''   | epsilon
    def S(self, d):
        if self.curToken and self.curToken.value == '(':
            if self.peekToken and self.isOper(self.peekToken.id):
                self.oper(d)
                self.SPP(d)
            elif self.peekToken and self.peekToken.id == 'stmt':
                debug(debugOn, '>> S -> stmts')
                self.stmts(d)
                self.SPP(d)
            else:
                print d * self.tab + '('
                self.getNextToken()
                self.SP(d)
                self.SPP(d)
        elif self.curToken and self.isTerminal(self.curToken.id):
            self.oper(d)
            #print self.curToken.value
            self.SPP(d) #fails on ((1 2)) without this SPP
        else:
            self.getNextToken()
            self.error()

    #S' -> ) | S)
    def SP(self, d):
        # S)
        if self.curToken and self.curToken.value != ')':
            self.S(d + 1)
        # S) and )
        if not self.curToken:
            self.error()
        elif self.curToken.value == ')':
            #print 'SP : )'
            print d * self.tab + ')'
            self.getNextToken()

    # S'' -> SS'' | epsilon
    def SPP(self, d):
        # SS''
        if self.curToken and (self.curToken.value == '(' or self.isTerminal(self.curToken.id)): # or is expr
        #or S production?# why do I need? or self.isTerminalType():
            #print 'SPP: '
            self.S(d)
            self.SPP(d)
        # epsilon

    # expr -> oper | stmts
    # def expr(self):

    # string, int, floats
    def isTerminal(self, id):
        return True if id in ['string', 'int', 'float', 'id'] else False



    # oper -> (:= name oper) | (binops oper oper) | (unops oper) | constants | name
    # oper  -> (operP | constants | name
    # operP -> := name oper | binops oper oper | unops oper
    def oper(self, d):
        if self.curToken:
            if self.curToken.value == '(':
                print d * self.tab + '('
                self.getNextToken()
                self.operP(d)
                if self.curToken.value == ')':
                    print d * self.tab + self.curToken.value
                    self.getNextToken()
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
                self.oper(d + 1)
            else:
                self.error()

        # Need to deal with - separately
        elif self.curToken.id == 'bop':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d + 1)
            # need to get token?
            self.oper(d + 1)
        elif self.curToken.id == 'uop':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d + 1)
        else:
            self.error()



    # stmts -> ifstmts | whilestmts | letstmts | printsmts
    #def stmts(self):
    # Go back and add the print stmts
    # TEST TEST TEST

    def stmts(self, d):
        if self.curToken.value == '(':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.stmtsP(d)
            if self.curToken.value == ')':
                print d * self.tab + self.curToken.value
                self.getNextToken()
            else:
                self.error
        else:
            self.error

    def stmtsP(self, d):
        if self.curToken.value == 'if':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.expr(d)
            self.expr(d)
            if self.curToken.value != ')':
                self.expr(d)
        elif self.curToken.value == 'while':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.expr(d)
            debug(debugOn, ">> while -> expr ->")
            self.exprlist(d)
        elif self.curToken.value == 'let':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.value == '(':
                print d * self.tab + self.curToken.value
                self.getNextToken()
                self.varlist()
                if self.curToken.value == ')':
                    print d * self.tab + self.curToken.value
                    self.getNextToken()
                else:
                    self.error
            else:
                self.error
        elif self.curToken.value == 'stdout':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
        else:
            self.error()

    def isType(self, value):
        return True if value in ['bool', 'int', 'real', 'string'] else False

    def varlist(self, d):
        if self.curToken.value == '(':
            print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.id == 'id':
                print d * self.tab + self.curToken.value
                self.getNextToken()
                if self.isType(self.curToken.value):
                    print d * self.tab + self.curToken.value
                    self.getNextToken()
                    if self.curToken.value == ')':
                        print d * self.tab + self.curToken.value
                        self.getNextToken()
                        if self.curToken.value == '(' and self.peekToken.id == 'id':
                            self.varlist(d + 1)
                    # need additional error cases?
                    else:
                        self.error()
            else:
                self.error
    def exprlist(self, d):
        # expr
        self.expr(d)
        # expr exprlist
        debug(debugOn, ">> exprlist -> expr -> " + self.curToken.value)
        if (self.curToken.value == '(' and (self.isOper(self.peekToken.id) or self.peekToken.id == 'stmt')) or self.isTerminal(self.curToken.id):
            debug(debugOn, ">> exprlist -> exprlist")
            self.exprlist(d + 1)



    def expr(self, d):
        debug(debugOn, ">> expr")
        if self.curToken == '(' and self.isOper(self.peekToken.id):
            print d * self.tab + self.curToken.value
            self.getNextToken()
            self.oper(d)
        elif self.isTerminal(self.curToken.id):
            debug(debugOn, ">> expr -> oper")
            self.oper(d)
        elif self.curToken == '(' and self.peekToken.id == 'stmt':
            self.stmt(d)
        else:
            self.error()
        # opers
        # stmts



    def error(self):
        print >> sys.stderr,"Parser error line: " + str(self.curToken.line) + ' token value: ' + str(self.curToken.value) + ' token index: ' + str(self.tokenIdx)
        sys.exit(0)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            self.peekToken = Token(self.curToken.line, '', '')
