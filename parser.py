from token import Token
from lexer import Lexer
from gforthTable import gforthTable as gt
from gforthTable import varTable as vt
import sys

debugOn = False
treeOn = False

def debug(on, msg):
    if on:
        print msg

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
        #print ": milestone4",
        self.S(0)
        print ""

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
                debug(debugOn, d * self.tab + '(')
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
            debug(debugOn, d * self.tab + ')')
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
                debug(debugOn, d * self.tab + '(')
                self.getNextToken()
                opP = self.operP(d + 1)
                if self.curToken.value == ')':
                    debug(debugOn, d * self.tab + self.curToken.value)
                    self.getNextToken()
                else:
                    # catch cases like (:= cat 33 charlie)
                    self.error()

                # What is this returning?
                return opP


            elif self.isTerminal(self.curToken.id):
                # detect if floating point value
                # debug(debugOn, d * self.tab + self.curToken.value)
                # Guarding against adding e to values like 2e10

                if self.curToken.id == "real" and 'e' not in self.curToken.value:
                    print self.curToken.value + 'e',
                elif self.curToken.id == 'string':
                    print 's\" ' + self.curToken.value[1:],
                else:
                    print self.curToken.value,

                cur = self.curToken
                self.getNextToken()
                return cur.id
            else:
                self.error()
        else:
            self.error()

    # Converted to postfix
    def operP(self, d):
        if self.curToken.id == 'assign':
            assign = self.curToken.value
            self.getNextToken()
            if self.curToken.id == 'id':
                #print d * self.tab + self.curToken.value
                var = self.curToken.value
                self.getNextToken()
                # self.oper(d)
                # Remove self.oper(d) above and replace with below

                self.gforthSetVar(var, self.oper(d).value)
            else:
                self.error()
            #print d * self.tab + assign
        # Need to deal with - separately
        elif self.curToken.id == 'op':
            op = self.curToken.value
            self.getNextToken()
            op1 = self.oper(d)

            debug(debugOn, d * self.tab + op)

            # (binop, unop, := ) or constants, name
            if (self.curToken.value == '(' and self.isOper(self.peekToken.id) or self.isTerminal(self.curToken.id)):
                op2 = self.oper(d)
                debug(debugOn, d * self.tab + op)
                return self.gforthBOPS(op1, op2, op)
            else:
                print '0 swap',
                return self.gforthUOPS(op1, op)

        elif self.curToken.id == 'bop':
            bop = self.curToken.value
            self.getNextToken()
            # terminal or expression
            op1 = self.oper(d)
            op2 = self.oper(d)
            debug(debugOn, "op1:" + str(op1) + " op2:" + str(op2))
            #print "\nop1:" + str(op1) + " op2:" + str(op2)
            debug(debugOn, d * self.tab + bop)
            # if int float or float int
            return self.gforthBOPS(op1, op2, bop)
        elif self.curToken.id == 'uop':
            uop = self.curToken.value
            self.getNextToken()
            op1 = self.oper(d)
            debug(debugOn, d * self.tab + uop)
            return self.gforthUOPS(op1, uop)
        else:
            self.error()

    # stmts -> ifstmts | whilestmts | letstmts | printsmts
    def stmts(self, d):
        if self.curToken.value == '(':
            debug(debugOn, d * self.tab + self.curToken.value)
            self.getNextToken()
            self.stmtsP(d + 1)
            # debug(debugOn, ">> stmts -> curToken = " + self.curToken.value)
            if self.curToken.value == ')':
                debug(debugOn, d * self.tab + self.curToken.value)
                self.getNextToken()
            else:
                self.error
        else:
            self.error

    def stmtsP(self, d):
        # ifstmts -> (if expr expr) | (if expr exp expr)
        if self.curToken.value == 'if':
            ifToken = self.curToken.value
            self.getNextToken()
            self.expr(d)
            debug(debugOn, d * self.tab + ifToken)
            print ifToken,
            self.expr(d)
            if self.curToken.value and self.curToken.value != ')':
                print 'else',
                self.expr(d)
            # Error if more than 3 args
            if self.curToken.value and self.curToken.value != ')':
                self.error()
            print 'endif',
        elif self.curToken.value == 'while':
            # print d * self.tab + self.curToken.value
            stmt = self.curToken.value
            print ': {0}{1} begin'.format(self.prefix, stmt),
            self.getNextToken()
            self.expr(d)
            print 'while',
            self.exprlist(d)
            print 'repeat ; {0}{1}'.format(self.prefix, stmt),
        # letstmts -> let( (varlist) )
        elif self.curToken.value == 'let':
            # print d * self.tab + self.curToken.value
            self.getNextToken()
            if self.curToken.value == '(':
                self.getNextToken()
                self.varlist(d)
                if self.curToken.value == ')':
                    self.getNextToken()
            else:
                self.error
        elif self.curToken.value == 'stdout':
            #debug (debugOn, d * self.tab + self.curToken.value)
            self.getNextToken()
            id = self.oper(d)
            self.gforthSTDOUT(id)
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

    def gforthInitVar(self, var, varType):
        if var and self.isType(varType):
            if varType == 'real':
                print gt[varType]['init'] + var,
            else:
                print gt['init'] + var,
            # Add variable to variable table
            vt[var] = [varType, '']
        else:
            self.error('var undefined and/or varType not legal type')

    def gforthSetVar(self, var, value):
        if var in vt:
            vt[var][1] = value
            if vt[var][0] == 'real':
                print var + ' ' + gt[varType]['assign'],
            else:
                print var + ' ' + gt['assign'],
        else:
            self.error('variable ' + var + ' not in vt (not initialized)')


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
