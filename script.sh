# Sanity-check the mako template by attempting to parse with mako if available, else just cat it.
python3 -c "
content = open('alembic/script.py.mako').read()
# Strip mako substitutions to a no-op for syntax check purposes
import re
cleaned = re.sub(r'\\\$\\{[^}]*\\}', 'None', content)
cleaned = re.sub(r'\\\$[a-zA-Z_][a-zA-Z0-9_]*', 'None', cleaned)
compile(cleaned, 'script.py.mako', 'exec')
print('mako template embedded python: OK')
"
