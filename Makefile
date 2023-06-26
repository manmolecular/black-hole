default: install run

install:
	python3 setup.py install

install_dev: install
	python3 -r requirements.dev.txt

uninstall:
	pip3 uninstall black-hole -y

reinstall: uninstall install

run:
	python3 -m blackhole

lint:
	black blackhole/ *.py
	mypy blackhole/ *.py
	pylint blackhole/ *.py

.PHONY: default $(MAKECMDGOALS)
