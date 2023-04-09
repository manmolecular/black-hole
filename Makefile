lint:
	black blackhole/
	mypy blackhole/
	pylint blackhole/

run:
	python3 -m blackhole
