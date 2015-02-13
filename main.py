from lexer import Lexer
from parser import Parser
import sys

l = Lexer('test.txt')
for i in l.tokens:
    i.printToken()
print '---------------------------------------'
p = Parser(l)

'''
dir = 'tests'

for t in ['proftest.in.txt']:
    lex = lexer.Lexer(dir + '/' + t)
    for i in lex.tokens:
        i.printToken()
    print '---------------------------------------'
'''
