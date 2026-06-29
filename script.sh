# Validate requirements.txt (simple parse)
python3 -c "
from pathlib import Path
for f in ['requirements.txt', 'requirements-dev.txt']:
    lines = [l.strip() for l in Path(f).read_text().splitlines() if l.strip() and not l.startswith('#')]
    print(f'OK: {f} ({len(lines)} packages)')
"
