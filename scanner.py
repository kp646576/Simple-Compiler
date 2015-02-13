class Scanner:

	def __init__(self, file):
		self.f = open(file, 'r')

	def read(self):
		return self.f.read(1)
