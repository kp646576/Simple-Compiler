import sys
from scanner import Scanner
from token import Token
from symbolTable import symbolTable as st

def isAlpha(c):
    if c:
        c = ord(c)
    return True if c >= 65 and c <= 90 or c >= 97 and c <= 122 else False

def isDigit(c):
    if c:
        c = ord(c)
    return True if  c <= 57 and c >= 48 else False

def isKeyword(c):
    return st[c] if c in st.keys() else ''

class Lexer:

    def __init__(self, file):
        self.line = 1
        self.tokens = []
        self.scanner = Scanner(file)
        self.checkNext(self.scanner.read())

    def checkNext(self, cur):
        if cur == '\n':
            self.line += 1
            cur = self.scanner.read()
            self.checkNext(cur)

        else:
            while cur == ' ' or cur == '\t':
                cur = self.scanner.read()

            if isDigit(cur) or cur == '.':
                self.digitFSA(cur)
            elif cur == '"':
                self.stringFSA(cur)
            elif isAlpha(cur) or cur == '_':
                self.idFSA(cur)
            else:
                self.otherFSA(cur)

        return

    def digitFSA(self, n):
        peek = self.scanner.read()

        if n == '.':
            if isDigit(peek):
                n += peek
                peek = self.scanner.read()
                while isDigit(peek):
                    n +=  peek
                self.tokens.append(Token(self.line, 'real', n))
        else:
            # Get digits before '.'
            while isDigit(peek):
                n += peek
                peek = self.scanner.read()

            # Is real
            if peek == '.':
                n += peek
                peek = self.scanner.read()
                while isDigit(peek):
                    n += peek
                    peek = self.scanner.read()
                if peek == 'e':
                    n += peek
                    peek = self.scanner.read()
                    if peek == '+' or peek == '-':
                        n += peek
                        peek = self.scanner.read()
                    if not isDigit(peek):
                        self.eMessage(peek)
                    while isDigit(peek):
                        n += peek
                        peek = self.scanner.read()
                self.tokens.append(Token(self.line, 'real', n))
            elif peek == 'e':
                n += peek
                peek = self.scanner.read()
                if peek == '+' or peek == '-':
                    n += peek
                    peek = self.scanner.read()
                if not isDigit(peek):
                    self.eMessage(peek)
                while isDigit(peek):
                    n += peek
                    peek = self.scanner.read()
                self.tokens.append(Token(self.line, 'real', n))
            # Is int
            else:
                self.tokens.append(Token(self.line, 'int', n))

        self.checkNext(peek)
        return

    def stringFSA(self, c):
        peek = self.scanner.read()

        while peek != '"' and peek != '\n':
                c += peek
                peek = self.scanner.read()

        if peek == '"':
            c += peek
            self.tokens.append(Token(self.line, 'string', c))
            peek = self.scanner.read()
            self.checkNext(peek)
        else:
            self.eMessage(c)
        return

    def idFSA(self, c):
        peek = self.scanner.read()
        if peek:
            # error when not num alph or _
            while peek and (isAlpha(peek) or isDigit(peek) or peek == '_'):
                c += peek
                peek = self.scanner.read()

        if peek == ' ' or peek == '\n':
            keyword = isKeyword(c)
            if keyword:
                self.tokens.append(Token(self.line, keyword, c))
            else:
                self.tokens.append(Token(self.line, 'id', c))
        else:
            self.eMessage(peek)

        self.checkNext(peek)
        return

    def otherFSA(self, c):
        peek = self.scanner.read()

        if peek:
            k1 = isKeyword(c)
            len2 = c + peek
            k2 = isKeyword(len2)

            # k2 first for longest prefix
            if k2:
                self.tokens.append(Token(self.line, k2, len2))
                self.checkNext(self.scanner.read())
            elif k1:
                self.tokens.append(Token(self.line, k1, c))
                self.checkNext(peek)
            else:
                self.eMessage(c)

        return

    def eMessage(self, e):
        print >> sys.stderr, "Error on line " + str(self.line) + ": " + e + " is invalid."
