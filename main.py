from lexer import Lexer
from parser import Parser
import sys

def main():
    l = Lexer(sys.argv[1])
    print '-----------------Tokens-----------------'
    for i in l.tokens:
        i.printToken()
    print '---------------Parse Tree---------------'
    p = Parser(l)
    print '------------------Done------------------'

if __name__ == '__main__':
    main()
