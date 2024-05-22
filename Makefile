include config.mk # update DEFAULT_VENV_DIR and DEFAULT_TARGET_DIR

$(DEFAULT_VENV_DIR): requirements.txt
	python3 -m venv $(DEFAULT_VENV_DIR)
	$(DEFAULT_VENV_DIR)/bin/pip install -r requirements.txt --force-reinstall


$(DEFAULT_TARGET_DIR)/h5util: $(DEFAULT_VENV_DIR) h5util.py
	echo #!/bin/bash > $(DEFAULT_TARGET_DIR)/h5util
	cp h5util.py $(DEFAULT_TARGET_DIR)/h5util.py
	echo source $(DEFAULT_VENV_DIR)/bin/activate >> $(DEFAULT_TARGET_DIR)/h5util
	echo python $(DEFAULT_TARGET_DIR)/h5util.py $$@ >> $(DEFAULT_TARGET_DIR)/h5util
	chmod +x $(DEFAULT_TARGET_DIR)/h5util


install: $(DEFAULT_TARGET_DIR)/h5util
