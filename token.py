class Token:

    def __init__(self, line, id, value):
        self.line = line
        self.id = id
        self.value = value

    def printToken(self):
        print '[' + str(self.line) + ', ' + str(self.id) + ', ' + str(self.value) + ']'
