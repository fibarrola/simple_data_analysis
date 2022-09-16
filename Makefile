pretty:
	black --config black.toml .

lint:
	black --config black.toml --check .
	flake8 --config setup.cfg .

run:
	python3 main.py