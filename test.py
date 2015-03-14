import sys
import unittest
from lexer import Lexer
from parser import Parser

def run(f):
	p = Parser(Lexer(f))

class Case(unittest.TestCase):

	# Fail Conditions
	# Scoping let statement test
	# Set int variable to string
	# Set real to int
	def test_fvars(self):
		numtests = 3
		for i in range(numtests):
			with self.assertRaises(SystemExit) as cm:
				run('./tests/fvars{0}.txt'.format(i + 1))
			self.assertEqual(cm.exception.code, 1)

################################################################################

	# Pass Conditions
	def test_assign(self):
		run('./tests/assign.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = 'variable x 5 x ! variable x fvariable x variable x'
		self.assertEquals(output, exp)

	def test_uops(self):
		run('./tests/bops.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = '2 2.0e 2 3 1 0 swap - - s>f s>f fswap f** f>s 4e s>f fswap f/ f** 1 s>f f** 4 s>f f/ s>f fswap f** 0 s>f fmod f.'
		self.assertEquals(output, exp)

	def test_bops(self):
		run('./tests/bops.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = '2 2.0e 2 3 1 0 swap - - s>f s>f fswap f** f>s 4e s>f fswap f/ f** 1 s>f f** 4 s>f f/ s>f fswap f** 0 s>f fmod f.'
		self.assertEquals(output, exp)

	def test_if(self):
		run('./tests/if.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip() # because stdout is an StringIO instance
		exp = ': kpif 2 3 < 2e 4 s>f f<> or true if 1 2 + else 4 5 - endif ; kpif'
		self.assertEquals(output, exp)

	def test_stdout(self):
		run('./tests/stdout.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = '4.2e f. 3 . s" hello" s" world!" s+ type'
		self.assertEquals(output, exp)

	def test_stdout(self):
		run('./tests/while.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = ': kpwhile begin 2 3 < while s" hello world!" type repeat ; kpwhile'
		self.assertEquals(output, exp)

	def test_integral(self):
		run('./tests/integral.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = 'variable n fvariable a fvariable b fvariable area fvariable width fvariable x 100 n ! 0 s>f a f! 1 s>f b f! 0 s>f area f! a f@ x f! b f@ a f@ f- n @ s>f f/ width f! : kpwhile begin x f@ b f@ f< while area f@ x f@ 2 s>f f** width f@ f* f+ area f! x f@ width f@ f+ x f! repeat ; kpwhile area f@ f.'
		self.assertEquals(output, exp)

	def test_var1(self):
		run('./tests/var1.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = 'variable x 0 x ! : kpwhile begin x @ 5 < while s" hello world!" type x @ 1 + x ! repeat ; kpwhile'
		self.assertEquals(output, exp)

	def test_var2(self):
		run('./tests/var2.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = 'fvariable x 5 s>f x f!'
		self.assertEquals(output, exp)

	def test_var3(self):
		run('./tests/var3.txt')
		if not hasattr(sys.stdout, "getvalue"):
			self.fail("need to run in buffered mode")
		output = sys.stdout.getvalue().strip()
		exp = 'variable x s" hello" x ! x @ type'
		self.assertEquals(output, exp)

if __name__ == '__main__':
	unittest.main(module=__name__, buffer=True, exit=False)
