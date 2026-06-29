python3 -c "
import ast
import sys

files = [
    'src/bpa/__init__.py',
    'src/bpa/config.py',
    'src/bpa/db.py',
    'src/bpa/logging_setup.py',
    'src/bpa/main.py',
    'alembic/env.py',
]

errors = 0
for f in files:
    try:
        with open(f) as fh:
            ast.parse(fh.read(), filename=f)
        print(f'OK  {f}')
    except SyntaxError as e:
        print(f'FAIL {f}: {e}')
        errors += 1

sys.exit(errors)
"
