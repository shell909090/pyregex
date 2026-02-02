unittest:
	python3 -m unittest discover . "*_test.py"

test:
	python3 test.py

lint:
	ruff check .

lint-fix:
	ruff check --fix .

run:
	python3 main.py
