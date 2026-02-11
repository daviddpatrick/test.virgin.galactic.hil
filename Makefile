ENV ?= venv
VENV ?= venv
PYTHON = $(VENV)/bin/python3
PIP = $(PYTHON) -m pip
default: test

setup:
	rm -rf $(VENV)
	python3.11 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	echo $(CURDIR)/$(VENV)

build: $(VENV)
	clear
	$(PIP) install -r requirements.txt

test: $(VENV)
	clear
	-$(PYTHON) -m pytest tests -W ignore::Warning;

test-hardware: $(VENV)
	clear
	-$(PYTHON) -m pytest -m hardware -W ignore::Warning;

test-api: $(VENV)
	clear
	-$(PYTHON) -m pytest -m api -W ignore::Warning;

report:
	clear
	allure generate allure-results -o allure-report --clean
	allure open allure-report
