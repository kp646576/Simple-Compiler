from token import Token
from lexer import Lexer
from gforthTable import gforthTable as gt
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

        self.vt = {}
        self.ft = {}

        self.ifc = 0
        self.whilec = 0

        self.lparen = 0
        self.rparen = 0
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
            self.lparen = 0
            self.rparen = 0
            #print '---------------'
            self.vt = {}
            self.getNextToken()

    # Original Grammar:
    # S   -> () | (S) | SS | expr

    # Transformed Grammar:
    # S   -> (S'S'' | exprS''
    # S'  -> )      | S)
    # S'' -> SS''   | epsilon
    def S(self, d):
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
                self.lparen += 1
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
            self.S(d)
            display(">> SP: " + self.curToken.value, PARSETREE_DEBUG)
        # S) and )
        if self.curToken.value == ')':
            self.rparen += 1
            display(d * self.tab + ')', PARSETREE)
            display('lparen:{0}, rparen:{1}'.format(self.lparen, self.rparen), GFORTH_DEBUG)
            if self.lparen > self.rparen:
                self.getNextToken()

    # S'' -> SS'' | epsilon
    def SPP(self, d):
        # SS''
        if self.curToken.value == '(' or self.isTerminal(self.curToken.id):
            display(">> SPP " + self.curToken.value, PARSETREE_DEBUG)
            self.S(d)
            self.SPP(d)
        # epsilon


    def output(self, s, l):
        if l == '':
            print s,
        else:
            l.append(s)


    # Original Grammar:
    # oper  -> (:= name oper) | (:= name (name paramlist)) | (binops oper oper) | (unops oper) | constants | name

    # Transformed Grammar:
    # oper  -> (operP) | constants | name
    # operP -> := name oper | := name (name paramlist) | binops oper oper | unops oper
    def oper(self, d, l = ''):
        if self.curToken.value:
            if self.curToken.value == '(':
                self.lparen += 1
                display(d * self.tab + '(', PARSETREE)
                self.getNextToken()
                opP = self.operP(d + 1, l)

                # F: self.paramList(d + 1) ?
                if self.curToken.value == ')':
                    self.rparen += 1
                    display(d * self.tab + self.curToken.value, PARSETREE)
                    if self.lparen > self.rparen:
                        self.getNextToken()
                else:
                    # catch cases like (:= cat 33 charlie)
                    self.error()
                return opP


            elif self.isTerminal(self.curToken.id):
                display(d * self.tab + self.curToken.value, PARSETREE)

                # Guarding against adding e to values like 2e10
                if self.curToken.id == "real" and 'e' not in self.curToken.value:
                    self.output('{0}e'.format(self.curToken.value), l)
                elif self.curToken.id == 'string':
                    self.output('s\" {0}'.format(self.curToken.value[1:]), l)

                # Variables
                elif self.curToken.id == 'id':
                    var = self.curToken.value
                    if var in self.vt:
                        self.output('{0} {1}'.format(var, gt[self.vt[var]]['access']), l)
                    elif var + var in self.ft:
                        self.output(var + var, l)
                    else:
                        self.error('using uninitialized variable')
                else:
                    self.output(self.curToken.value, l)

                cur = self.curToken
                self.getNextToken()
                return cur.id if cur.id != 'id' else self.ft[cur.value + cur.value]['type'] if cur.value + cur.value in self.ft  else self.vt[cur.value]
            else:
                self.error('current token is neither beginning of oper nor terminal')
        else:
            self.error('current token is null')


    # paramlist -> oper paramlist | e
    def paramlist(self, d, n, p, l = ''):
        # Expressions as funciton params
        ptype = self.oper(d, n, l)
        if ptype != ft[n]['paramtypes'][p]:
            self.error('type mismatch: expected {0} received {1}'.format(ft[n]['paramtypes'][p], self.curToken.value))
        self.gforthSetVar(n + self.ft[n]['params'][p], ptype)
        self.getNextToken()
        if p <= len(ft[n]['paramtypes']):
            paramlist(d, n, p + 1, l)

    def operP(self, d, l = ''):
        # := name oper | := name (name paramlist)
        if self.curToken.id == 'assign':
            assign = self.curToken.value
            display(d * self.tab + assign, PARSETREE)
            self.getNextToken()

            if self.curToken.id == 'id':
                display(d * self.tab + self.curToken.value, PARSETREE)
                var = self.curToken.value

                self.getNextToken()

                if self.curToken.value == '(':
                    self.lparen += 1
                    display(d * self.tab + self.curToken.value, PARSETREE)
                    self.getNextToken()
                    if self.curToken.id != 'id':
                        self.error('no subsequent name found after parenthesis')

                    n = self.curToken.value

                    self.getNextToken()
                    self.paramlist(d, n, 0, l)
                    if self.curToken.value != ')':
                        self.error('no closing parenthesis to paramlist')
                    self.rparen += 1
                    display(d * self.tab + self.curToken.value, PARSETREE)
                    # call function and store result? inside variable
                    # Initialize variable as same type as function
                    gforthInitVar(var, ft[n]['type'])

                    # Run function and set result to variable
                    # gforthSetVar(var, vt[var]) ???
                    print n,

                    self.getNextToken()
                else:
                    eType = self.oper(d)
                    self.gforthSetVar(var, eType, l)
            else:
                self.error('non-name found after assign in (:= name oper)')





        # Need to deal with - separately
        elif self.curToken.id == 'op':
            op = self.curToken.value
            display(d * self.tab + op, PARSETREE)
            self.getNextToken()
            op1 = self.oper(d, l)

            # (binop, unop, := ) or constants, name
            if (self.curToken.value == '(' and self.isOper(self.peekToken.id) or self.isTerminal(self.curToken.id)):
                op2 = self.oper(d, l)
                return self.gforthBOPS(op1, op2, op, l)
            else:
                self.output('0 swap', l)
                return self.gforthUOPS(op1, op, l)

        elif self.curToken.id == 'bop':
            bop = self.curToken.value
            display(d * self.tab + bop, PARSETREE)
            self.getNextToken()
            # Values can be terminals or expressions
            op1 = self.oper(d, l)
            op2 = self.oper(d, l)
            display('op1: {0} op2: {1}'.format(op1, op2), PARSETREE_DEBUG)
            return self.gforthBOPS(op1, op2, bop, l)

        elif self.curToken.id == 'uop':
            uop = self.curToken.value
            display(d * self.tab + uop, PARSETREE)
            self.getNextToken()
            op1 = self.oper(d, l)
            return self.gforthUOPS(op1, uop, l)
        else:
            self.error('prefix operation {0} not found in grammar of oper'.format(self.curToken.id))

    # stmts -> ifstmts | whilestmts | letstmts | printsmts | (return oper)
    def stmts(self, d, n = '', l = ''):
        if self.curToken.value == '(':
            self.lparen += 1
            display(d * self.tab + self.curToken.value, PARSETREE)

            self.getNextToken()
            print 'STMTS' + self.curToken.value
            self.stmtsP(d + 1, n, l)

            # display(">> stmts -> curToken = " + self.curToken.value, PARSETREE_DEBUG)
            if self.curToken.value == ')':
                self.rparen += 1
                display(d * self.tab + self.curToken.value, PARSETREE)
                if self.lparen > self.rparen:
                    self.getNextToken()
            else:
                self.error('stmts 1 error')
        else:
            self.error('stmts 2 error')

    def stmtsP(self, d, n = '', l = ''):
        # ifstmts -> (if expr expr) | (if expr exp expr)
        if self.curToken.value == 'if':
            stmt = self.curToken.value
            display(d * self.tab + stmt, PARSETREE)
            print ': {0}{1}'.format(stmt, self.ifc),
            self.ifc += 1
            self.getNextToken()
            self.expr(d, l)

            # 'if' needs to be printed after condition for gforth syntax
            print 'if',
            self.expr(d)
            if self.curToken.value and self.curToken.value != ')':
                print 'else',
                self.expr(d, l)

            # Error if more than 3 args
            if self.curToken.value and self.curToken.value != ')':
                self.error('too many arguments given in if statment')

            if n != '':
                print 'endif ;',
                ft[n]['innards'].append('{0}{1}'.format(stmt, self.ifc))
            else:
                print 'endif ; {0}{1}'.format(stmt, self.ifc),

        # whilestmts -> (while expr exprlist)
        elif self.curToken.value == 'while':
            stmt = self.curToken.value
            display(d * self.tab + stmt, PARSETREE)
            print ': {0}{1} begin'.format(stmt, self.whilec),
            self.whilec += 1
            self.getNextToken()
            self.expr(d, l)
            print 'while',
            self.exprlist(d)

            if whilec != '':
                print 'repeat ;',
                ft[n]['innards'].append('{0}{1}'.format(stmt, self.whilec))
            else:
                print 'repeat ; {0}{1}'.format(stmt, self.whilec),

        # Original Grammar:
        # letstmts -> ( let (varlist) ) | ( let ((funlist) (funtype)) exprlist )

        # Transformed Grammar:
        # letstmts  -> ( let (letstmtsP )
        # letstmtsP -> varlist) | (funlist) (funtype)) exprlist
        # * First and last parens taken care of in stmts

        # letstmts -> (let ((funlist) (funtype)) exprlist)
        elif self.curToken.value == 'let':
            display(d * self.tab + self.curToken.value, PARSETREE)
            self.getNextToken()
            if self.curToken.value == '(':
                self.lparen += 1
                display(d * self.tab + self.curToken.value, PARSETREE)
                self.getNextToken()

                self.letstmtsP(d)

            else:
                self.error('no starting parenthesis after let statement')

        elif self.curToken.value == 'stdout':
            display (d * self.tab + self.curToken.value, PARSETREE)
            self.getNextToken()
            eType = self.oper(d)
            self.gforthSTDOUT(eType, l)
            if self.curToken.value and self.curToken.value != ')':
                self.error()
        elif self.curToken.value == 'return':
            if n != '':
                # need variable to set
                #l = []
                self.getNextToken()
                print n
                eType = self.oper(d, self.ft[n]['innards'])#, n)

                #ft[n]['innards'].append(l)

                # create return variable
                # need to append to innards
                print 'this far yest?'
                self.gforthInitVar(n + 'return', eType)

                self.gforthSetVar(n + 'return', eType, self.ft[n]['innards'])
                self.ft[n]['innards'].append('exit')
            #else:
                #self.error('return used without function')
        else:
            self.error()


    # letstmtsP -> varlist) | (funlist) (funtype)) exprlist
    # letstmtsP -> (name type) varlist | (name ...) (funtype)) exprlist
    def letstmtsP(self, d):
        if self.curToken.value == '(':
            self.lparen += 1
            self.getNextToken()

            # factor out the first value (function name)
            if self.curToken.id != 'id':
                self.error('non-name in funlist')

            print 'PEEK' + self.peekToken.value
            # (name ...) (funtype)) exprlist
            if self.peekToken.id == 'id':
                n = self.curToken.value + self.curToken.value
                self.ft[n] = {'params' : [], 'paramtypes' : [], 'innards' : [], n + 'return' : ''}
                self.getNextToken()
                self.letstmtsPP(d, n)

            # (name type) | (name type) varlist
            elif self.isType(self.peekToken.value):
                print 'comes in'
                self.varlist(d)

                # closing inner let )
                if self.curToken.value != ')':
                    self.error('no closing parenthesis after let')
                self.rparen += 1
                self.getNextToken()
            else:
                self.error('neither varlist or letstmtsPP token found')




    # funlist) (funtype)) exprlist
    def letstmtsPP(self, d, n):
        if self.curToken.value != ')':
            self.funlist(d, n)


        if self.curToken.value != ')':
            self.error('no closing parenthesis after funlist')
        self.rparen += 1
        self.getNextToken()

        if self.curToken.value != '(':
            self.error('no starting parenthesis for funtype')
        self.lparen += 1
        display(d * self.tab + self.curToken.value, PARSETREE)
        self.getNextToken()


        self.funtype(d, n)


        if self.curToken.value != ')':
            self.error('no closing parenthesis after funtype')
        self.rparen += 1
        display(d * self.tab + self.curToken.value, PARSETREE)
        self.getNextToken()

        if self.curToken.value != ')':
            self.error('no closing parenthesis after inner let expression')
        self.rparen += 1
        display(d * self.tab + self.curToken.value, PARSETREE)
        self.getNextToken()

        # In case innards is empty
        if self.curToken.value != ')':
            self.exprlist(d, n, self.ft[n]['innards'])
            print ': {0}'.format(n),
            for i in self.ft[n]['innards']:
                print '{0}'.format(i),
            print ' ;',



    # funlist -> name | name funlist
    # 1st name is function name and subsequent names are paremeters
    # Can't loop funlist because don't know how many parameters there will be

    # need to add name
    def funlist(self, d, n):
        if self.curToken.id != 'id':
            self.error('non-name in funlist')
        if self.curToken.value in self.ft[n]['params']:
            self.error('duplicate parameter name')
        self.ft[n]['params'].append([self.curToken.value, ''])
        #print 'curtoken:' + self.curToken.value
        self.getNextToken()
        if self.curToken.id == 'id':
            self.funlist(d, n)

    # funtype -> type | type funtype
    def funtype(self, d, n):
        #print self.ft[n]['params']
        for i in range(len(self.ft[n]['params']) + 1):
            if not self.isType(self.curToken.value):
                self.error('non-type given to funtype')
            try:
                print self.curToken.value
                if i == 0:
                    self.ft[n]['type'] = self.curToken.value
                else:
                    self.ft[n]['paramtypes'].append(self.curToken.value)
                    # May not need to do this
                    self.ft[n]['params'][i - 1][1] = self.curToken.value
                    # Intialize variables
                    self.gforthInitVar(n + self.ft[n]['params'][i - 1][0], self.curToken.value)
                self.getNextToken()
            except IndexError:
                self.error('incorrect number of funlist and funtype')

    # varlist -> (name type) | (name type) varlist
    def varlist(self, d):
        if self.curToken.id == 'id':
            var = self.curToken.value
            self.getNextToken()
            if self.isType(self.curToken.value):
                varType = self.curToken.value
                self.gforthInitVar(var, varType)
                self.getNextToken()
                if self.curToken.value == ')':
                    self.rparen += 1
                    #print d * self.tab + self.curToken.value
                    self.getNextToken()
                    display(">> varlist: " + self.curToken.value, PARSETREE_DEBUG)
                    if self.curToken.value == '(' and self.peekToken.id == 'id':
                        display(">> varlist -> varlist", PARSETREE_DEBUG)
                        self.letstmtsP(d)
                else:
                    self.error()
            else:
                self.error()
        else:
            self.error()


    def exprlist(self, d, n = '', l = ''):
        # expr
        self.expr(d, n, l)
        # expr exprlist
        if l == '':
            print 'nothing'
        display(">> exprlist -> expr -> " + self.curToken.value, PARSETREE_DEBUG )
        if (self.curToken.value == '(' and (self.isOper(self.peekToken.id) or self.peekToken.id == 'stmt')) or self.isTerminal(self.curToken.id):
            display(">> exprlist -> exprlist", PARSETREE_DEBUG)
            self.exprlist(d, n, l)

    def expr(self, d, n = '', l = ''):
        if self.curToken.value == '(' and self.isOper(self.peekToken.id):
            self.oper(d, l)
        elif self.isTerminal(self.curToken.id):
            display(">> expr -> oper", PARSETREE_DEBUG)
            self.oper(d, l)
        elif self.curToken.value == '(' and self.peekToken.id == 'stmt':
            print 'ASDF' + self.peekToken.value
            self.stmts(d, n, l)
            print 'ASDF' + self.peekToken.value
        else:
            self.error()

    def gforthInitVar(self, var, varType):
        if var and self.isType(varType):
            print '{0} {1}'.format(gt[varType]['init'], var),
            # Add variable to variable table
            self.vt[var] = varType
        else:
            self.error('variable {0} undefined and/or illegal type'.format(var))

    def gforthSetVar(self, var, eType, l = ''):
        #print self.vt
        #print self.ft
        if var in self.vt:
            varType = self.vt[var]
            if varType == eType:
                self.output('{0} {1}'.format(var, gt[varType]['assign']), l)
            elif varType == 'real' and eType == 'int':
                self.output('s>f {0} {1}'.format(var, gt[varType]['assign']), l)
            else:
                self.error('Type Mismatch: setting {0} variable to {1}'.format(varType, eType))
        else:
            self.error('variable {0} not initialized'.format(var))

    def gforthUOPS(self, op1, uop, l = ''):
        # print '\nuop:' + str(op1)
        if (uop == 'sin' or uop == 'cos' or uop == 'tan') and op1 != 'real':
            self.output('s>f ' + gt[uop], l)
            return 'real'
        elif op1 == 'real':
            if uop == 'not':
                self.output('f' + gt[uop], l)
            else:
                self.output(gt[uop], l)
        elif uop == 'not':
            self.output(gt[uop], l)
        else:
            self.output(uop, l)
        return op1

    def gforthBOPS(self, op1, op2, bop, l = ''):
        if op1 == 'int' and op2 == 'int':
            # Don't change if-else orderings
            # Case where % is different for ints and floats
            if bop == '%':
                self.output('mod', l)
            elif bop == '^':
                self.output('s>f s>f fswap f** f>s', l)
            elif bop == "!=":
                self.output('<>', l)
            else:
                self.output(bop, l)
            return 'int'
        elif bop == 'and' or bop == 'or':
            if op1 == 'int' and op2 == 'real':
                self.output('f>s ' + bop, l)
            elif op1 == 'real' and op2 == 'int':
                self.output('f>s fswap ' + bop, l)
            elif op1 == 'real' and op2 == 'real':
                self.output('f>s f>s fswap ' + bop, l)
            return 'int'
        elif op1 == 'int' and op2 == 'real':
            self.output('s>f fswap ' + gt[bop], l)
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'real' and op2 == 'int':
            self.output('s>f ' + gt[bop], l)
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'real' and op2 == 'real':
            self.output(gt[bop], l)
            if self.isRelational(bop):
                return 'int'
            else:
                return 'real'
        elif op1 == 'string' and op2 == 'string':
            if bop != '+':
                self.error()
            else:
                self.output('s+', l)
            return 'string'
        else:
            self.output(bop, l)
            return op1

    def gforthSTDOUT(self, op1, l = ''):
        if op1 == 'int':
            self.output('.', l)
        elif op1 =='real':
            self.output('f.', l)
        elif op1 == 'string':
            self.output('type', l)

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
        sys.exit(1)

    def getNextToken(self):
        self.curToken = self.peekToken
        if self.tokenIdx + 1 < len(self.tokens):
            self.tokenIdx += 1
            self.peekToken = self.tokens[self.tokenIdx]
        else:
            self.peekToken = Token(self.curToken.line, '', '')
