PY_DIRS=panopto examples
VE ?= ./ve
PIP_VERSION ?= 21.2.4
REQUIREMENTS ?= requirements.txt
SYS_PYTHON ?= python3
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.36.2
MAX_COMPLEXITY ?= 7
PY_DIRS ?= $(APP)
FLAKE8 ?= $(VE)/bin/flake8
PIP ?= $(VE)/bin/pip
PYTEST ?= $(VE)/bin/pytest

all: flake8 test

clean:
	rm -rf $(VE) .pytest_cache
	find . -name '*.pyc' -exec rm {} \;

$(PY_SENTINAL):
	rm -rf $(VE)
	$(SYS_PYTHON) -m venv $(VE)
	$(PIP) install pip==$(PIP_VERSION)
	$(PIP) install --upgrade setuptools
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS)
	touch $@

test: $(PY_SENTINAL)
	$(PYTEST) $(PY_DIRS)

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS)
