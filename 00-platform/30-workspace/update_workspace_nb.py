import json
import os
import fcntl
import time

env_path = '/Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot/.env'
workspace_file = '/Users/vMac/00-hair-solutions-co/_workspaces/hubspot.code-workspace'

env_dict = {}

# open using low-level os.open so we can handle it non-blocking easily
try:
    fd = os.open(env_path, os.O_RDONLY | os.O_NONBLOCK)
except OSError:
    print("Could not open pipe. Exiting.")
    exit(1)

# read loop with small timeout
retries = 10
data = b""
while retries > 0:
    try:
        chunk = os.read(fd, 8192)
        if chunk:
            data += chunk
            # Once we get data, we keep reading until empty
        elif data:
            break
        else:
            retries -= 1
            time.sleep(0.1)
    except BlockingIOError:
        if data:
            break
        retries -= 1
        time.sleep(0.1)

os.close(fd)

content = data.decode('utf-8')
for line in content.split('\n'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if '=' in line:
        key, val = line.split('=', 1)
        # basic de-quoting
        if val.startswith(('"', "'")) and val.endswith(('"', "'")):
            val = val[1:-1]
        env_dict[key] = val

# Add OP_SERVICE_ACCOUNT_TOKEN if not parsed
token = None
import_path = '/Users/vMac/00-hair-solutions-co/00_engineering/01_workspace/1password/imports/Hair Solutions Unified.import.env'
if os.path.exists(import_path):
    with open(import_path, 'r') as f:
        for line in f:
            if line.startswith('OP_SERVICE_ACCOUNT_TOKEN='):
                token = line.split('=', 1)[1].strip()
                if token.startswith('"'): token = token[1:-1]

if token and 'OP_SERVICE_ACCOUNT_TOKEN' not in env_dict:
    env_dict['OP_SERVICE_ACCOUNT_TOKEN'] = token

with open(workspace_file, 'r') as f:
    ws = json.load(f)

if 'settings' not in ws:
    ws['settings'] = {}
if 'terminal.integrated.env.osx' not in ws['settings']:
    ws['settings']['terminal.integrated.env.osx'] = {}

for k, v in env_dict.items():
    ws['settings']['terminal.integrated.env.osx'][k] = v

with open(workspace_file, 'w') as f:
    json.dump(ws, f, indent=2)

print(f"Successfully injected {len(env_dict)} env vars into workspace.")
