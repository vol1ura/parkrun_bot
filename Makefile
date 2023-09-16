run:
	./venv/bin/python main.py

test:
	./venv/bin/pytest --cov-report=html --cov=. tests/

checkup:
	./venv/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics \
	--exclude venv,htmlcov,service_scripts,handlers/__init__.py
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude venv,htmlcov,service_scripts

publish:
	./venv/bin/ansible-playbook -i deploy/inventory deploy/deploy.yml --private-key=~/.ssh/id_ed25519
