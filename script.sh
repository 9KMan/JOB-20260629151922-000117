python3 -c "
from pathlib import Path
files = ['docs/PROJECT_OVERVIEW.md', 'docs/GLOSSARY.md', 'README.md', 'docs/PHASE_LOG.md']
for f in files:
    p = Path(f)
    print(f'{f}: exists={p.exists()} size={p.stat().st_size if p.exists() else 0}')
"
