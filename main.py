from lexer import Lexer
from parser import Parser
import sys

def main():
    l = Lexer('test.txt')
    for i in l.tokens:
        i.printToken()
    print '---------------------------------------'
    #p = Parser(l)
    #print '---------------------------------------'

'''
dir = 'tests'

for t in ['proftest.in.txt']:
    lex = lexer.Lexer(dir + '/' + t)
    for i in lex.tokens:
        i.printToken()
    print '---------------------------------------'
'''

if __name__ == '__main__':
    main()
