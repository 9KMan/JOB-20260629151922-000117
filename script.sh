python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('✅ pyproject.toml valid TOML')"
python3 -c "from xml.etree import ElementTree; ElementTree.parse('alembic.ini' if False else '/dev/null'); print('skipped xml check')"
# Just verify alembic.ini is parseable as ini
python3 -c "
import configparser
c = configparser.ConfigParser()
c.read('alembic.ini')
sections = c.sections()
print('✅ alembic.ini has sections:', sections)
"
echo "---"
echo "File sizes:"
ls -la *.toml *.txt *.ini *.yml Dockerfile .env.example .gitignore .python-version README.md
ls -la src/bpa/*.py alembic/*.py alembic/*.mako
