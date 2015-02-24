symbolTable = {
    'true'  : 'bool',
    'false' : 'bool',
    'and'   : 'bop',
    'or'    : 'bop',
    'not'   : 'uop',

    '-' : 'op',

    '+' : 'bop',
    '*' : 'bop',
    '/' : 'bop',
    '%' : 'bop',
    '^' : 'bop',

    '='  : 'bop',
    '<'  : 'bop',
    '>'  : 'bop',
    '<=' : 'bop',
    '>=' : 'bop',
    '!=' : 'bop',

    'sin' : 'uop',
    'cos' : 'uop',
    'tan' : 'uop',

    'if'     : 'stmt',
    'else'   : 'stmt',
    'while'  : 'stmt',
    'let'    : 'stmt',
    'stdout' : 'stmt',

    '('  : 'lparen',
    ')'  : 'rparen',
    ':=' : 'assign',

    'bool'   : 'type',
    'int'    : 'type',
    'real'   : 'type',
    'string' : 'type',
}
