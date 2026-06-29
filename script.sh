python3 -c "
import ast, pathlib
for p in pathlib.Path('.').rglob('*.py'):
    if 'venv' in str(p) or '.venv' in str(p):
        continue
    try:
        ast.parse(p.read_text())
        print(f'OK  {p}')
    except SyntaxError as e:
        print(f'FAIL {p}: {e}')
"
