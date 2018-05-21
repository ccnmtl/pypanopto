PY_DIRS=panopto examples
OUTPUT_PATH=ve
VE ?= ./ve
FLAKE8 ?= $(VE)/bin/flake8
PYTEST ?= $(VE)/bin/pytest
REQUIREMENTS ?= requirements.txt
SYS_PYTHON ?= python
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.30.0
VIRTUALENV ?= virtualenv.py
SUPPORT_DIR ?= requirements/virtualenv_support/
MAX_COMPLEXITY ?= 7
PY_DIRS ?= $(APP)

all: flake8 test

clean:
	rm -rf $(OUTPUT_PATH)

$(PY_SENTINAL): $(REQUIREMENTS) $(VIRTUALENV) $(SUPPORT_DIR)*
	rm -rf $(VE)
	$(SYS_PYTHON) $(VIRTUALENV) --extra-search-dir=$(SUPPORT_DIR) $(VE)
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS)
	touch $@

test: $(PY_SENTINAL)
	$(PYTEST) $(PY_DIRS)

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS)
