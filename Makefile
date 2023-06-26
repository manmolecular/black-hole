default: install run

install:
	python3 setup.py install

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
