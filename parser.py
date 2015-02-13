from token import Token
from lexer import Lexer
from parseTree import ParseTree

class Parser:
    def __init__(self, lexer):
        self.tokens = lexer.tokens
        self.curToken = ''
        self.peekToken = ''
        if len(self.tokens) > 1:
            self.curToken = self.tokens[0]
            self.peekToken = self.tokens[1]
        self.tokenIdx = 1
        #self.curNode = ParseNode(Token(0, 'root', 'root'))
        self.S()
        #self.parseTree = ParseTree(self.currentNode)

#S   -> (S'S'' | exprS''
#S'  -> ) | S)
#S'' -> SS'' | epsilon
    def S(self):
        # (S'S''
        if self.curToken and self.curToken.value == '(':
            print 'S  : ('
            self.getNextToken()
            self.SP()
            self.SPP()
        #else:
            # go to expr
            #self.SPP()

    def SP(self):
        # S)
        if self.curToken and self.curToken.value != ')':
            self.S()
        # S) and )
        if self.curToken.value == ')':
            print 'SP : )'
            self.getNextToken()

    # S'' -> SS'' | epsilon
    def SPP(self):
        # SS''
        if self.curToken and self.curToken.value == '(': # or is expr
        #or S production?# why do I need? or self.isTerminalType():
            print 'SPP: '
            self.S()
            self.SPP()
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
        print >> sys.stderr,"Parser error on line " + str(self.curToken.line) + ' with token value ' + str(self.curToken.value) + ' token index ' + str(self.tokenIdx)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            #print "goes in"
            self.peekToken = ''
