gforthTable = {
    'int'   : {
        'access' : '@',
        'assign' : '!',
        'init'   : 'variable'
    },

    'string' : {
        'access' : '@',
        'assign' : '!',
        'init'   : 'variable'
    },

    'real'  : {
        'access' : 'f@',
        'assign' : 'f!',
        'init'   : 'fvariable',
    },

    # Unary
    'not'   : '0=',

    # Binary
    '!='    : 'f<>',
    'and'   : 'and',
    'or'    : 'or',
    # Floating Point
    '^'     : 'f**',
    'sin'   : 'fsin',
    'cos'   : 'fcos',
    'tan'   : 'ftan',
    '*'     : 'f*',
    '/'     : 'f/',
    '%'     : 'fmod',
    '+'     : 'f+',
    '-'     : 'f-',
    '='     : 'f=',
    '<'     : 'f<',
    '<='    : 'f<=',
    '>'     : 'f>',
    '>='    : 'f>=',

    # Other
    'stdout': '.s'
}
