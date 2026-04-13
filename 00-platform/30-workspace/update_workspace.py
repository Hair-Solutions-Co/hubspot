import json
import os

env_path = '/Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot/.env'
workspace_file = '/Users/vMac/00-hair-solutions-co/_workspaces/hubspot.code-workspace'

# Read env
env_dict = {}
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            # basic de-quoting
            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                val = val[1:-1]
            env_dict[key] = val

# Add OP token if not present but we need it. Let's get it from the import file or just rely on env_dict
token = None
import_path = '/Users/vMac/00-hair-solutions-co/00_engineering/01_workspace/1password/imports/Hair Solutions Unified.import.env'
if os.path.exists(import_path):
    with open(import_path, 'r') as f:
        for line in f:
            if line.startswith('OP_SERVICE_ACCOUNT_TOKEN='):
                token = line.split('=', 1)[1].strip()
                if token.startswith('"'): token = token[1:-1]

if token:
    env_dict['OP_SERVICE_ACCOUNT_TOKEN'] = token

# Load workspace
with open(workspace_file, 'r') as f:
    ws = json.load(f)

# Update workspace
if 'settings' not in ws:
    ws['settings'] = {}
if 'terminal.integrated.env.osx' not in ws['settings']:
    ws['settings']['terminal.integrated.env.osx'] = {}

for k, v in env_dict.items():
    ws['settings']['terminal.integrated.env.osx'][k] = v

with open(workspace_file, 'w') as f:
    json.dump(ws, f, indent=2)

print("Successfully injected env vars into workspace.")
