find . -type f -not -path './.venv/*' -not -path './.git/*' -not -path './__pycache__/*' -not -path '*/__pycache__/*' | sort
