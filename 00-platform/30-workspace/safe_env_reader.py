import os

env_path = '/Users/vMac/00-hair-solutions-co/00_engineering/04_hubspot/.env'
if not os.path.exists(env_path):
    print("File not found.")
else:
    with open(env_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if '=' in line:
            key, val = line.strip().split('=', 1)
            # Remove quotes
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            print(f"{key}: **** (length {len(val)})")
