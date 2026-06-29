echo "=== Final tree ===" && find . -type f -not -path './__pycache__/*' -not -path '*/__pycache__/*' -not -path './.git/*' | sort
