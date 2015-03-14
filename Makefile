PY = python
PROFTEST = proftest.in
TDIR = ./tests
DRIVER = main.py
TEST = test.py

default:
	for prof in proftest*; do \
		$(PY) $(DRIVER) $$prof; \
	done

integral:
	$(PY) $(DRIVER) $(TDIR)/integral.txt

proftest.out: $(PROFTEST)
	$(PY) $(DRIVER) $(PROFTEST)

stutest.out:
	for tt in $(TDIR)/*.txt; do \
		$(PY) $(DRIVER) $$tt; \
	done

unittests:
	$(PY) $(TEST) -v

clean:
	rm -f *.pyc
