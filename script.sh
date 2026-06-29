echo "=== FILE INVENTORY ==="
find . -type f -not -path '*/__pycache__/*' | sort
