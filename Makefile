run:
	./env/bin/python main.py

test:
	./env/bin/pytest --cov-report=html --cov=. tests/

checkup:
	./env/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics \
	--exclude env,htmlcov,service_scripts,handlers/__init__.py
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude env,htmlcov,service_scripts
