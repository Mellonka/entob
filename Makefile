SRC_FOLDERS = entob tests examples

format:
	.venv/bin/ruff format $(SRC_FOLDERS)
	.venv/bin/ruff check --fix $(SRC_FOLDERS)
	.venv/bin/ruff check --fix --select I $(SRC_FOLDERS)
	.venv/bin/mypy $(SRC_FOLDERS)
