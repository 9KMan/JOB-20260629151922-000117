python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print('pyproject.toml parsed OK')
print('Project:', data['project']['name'])
print('Dependencies count:', len(data['project']['dependencies']))
"
