default:
	python main.py > stutest.out
	cat stutest.out

clean:
	rm -f stutest.out
	rm -f *.pyc
