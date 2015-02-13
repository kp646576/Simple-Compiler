from token import Token
from lexer import Lexer
from parseTree import ParseTree
import sys

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
        #self.curNode = ParseNode(Token(0, 'root', 'root'))
        self.S(0)
        #self.parseTree = ParseTree(self.currentNode)

    #S   -> (S'S'' | exprS''
    #S'  -> )      | S)
    #S'' -> SS''   | epsilon
    def S(self, d):
        # (S'S''
        if self.curToken and self.curToken.value == '(':
            #print 'S  : ('
            print d * self.tab + '('
            self.getNextToken()
            self.SP(d)
            self.SPP(d)
        #else:
            # go to expr
            #self.SPP()
        else:
            self.error()

    #S'  -> ) | S)
    def SP(self, d):
        # S)
        if self.curToken and self.curToken.value != ')':
            print 'goes in'
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
        if self.curToken and self.curToken.value == '(': # or is expr
        #or S production?# why do I need? or self.isTerminalType():
            #print 'SPP: '
            self.S(d)
            self.SPP(d)
        elif self.curToken and self.curToken.value == ')':
            self.error()
        # epsilon

    def expr(self):



        # exprS'
        '''
        elif self.currentToken.tokenType == 'stmts':
            self.statement()
            self.SP()

        # expr
        elif self.isOperType():
            self.oper()
            self.Sp()

            Why do I need this?
            elif self.isTerminalType() :
                self.oper()
                self.Sp()
                if self.currentToken.value != ')':
                    self.error()
                else :
                    self.getNextToken()
                self.Sp()
        # Why do I need this?
        elif self.isTerminalType():
            self.oper()
            self.Sp()
        '''








    def error(self):
        print >> sys.stderr,"Parser error line: " + str(self.curToken.line) + ' token value: ' + str(self.curToken.value) + ' token index: ' + str(self.tokenIdx)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            #print "goes in"
            self.peekToken = Token(self.curToken.line, '', '')
