python3 -c "
import ast, pathlib
files = [
    'src/bpa/__init__.py',
    'src/bpa/config.py',
    'src/bpa/db.py',
    'src/bpa/logging_setup.py',
    'src/bpa/main.py',
    'alembic/env.py',
]
for f in files:
    src = pathlib.Path(f).read_text()
    try:
        ast.parse(src, filename=f)
        print(f'OK   {f}')
    except SyntaxError as e:
        print(f'FAIL {f}: {e}')
"
