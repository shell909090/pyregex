unittest:
	python3 -m unittest discover . "*_test.py"

test:
	python3 test.py

test-regex:
	python3 test.py --impl regex

test-nfa:
	python3 test.py --impl nfa

lint:
	ruff check .

lint-fix:
	ruff check --fix .

run:
	python3 main.py
