PY = python
PROFTEST = proftest.in
TDIR = ./tests
DRIVER = main.py

default:
	for prof in proftest*; do \
		$(PY) $(DRIVER) $$prof; \
	done

stutest.out:
	for test in $(TDIR)/*.txt; do \
		$(PY) $(DRIVER) $$test; \
	done

proftest.out: $(PROFTEST)
	$(PY) $(DRIVER) $(PROFTEST)

clean:
	rm -f *.pyc
