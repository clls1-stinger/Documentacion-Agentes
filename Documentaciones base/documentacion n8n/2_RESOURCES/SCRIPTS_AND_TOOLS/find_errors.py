import json
import sys

def find_errors(data, path=""):
    if isinstance(data, dict):
        if "error" in data:
            print(f"Error at {path}: {data['error']}")
        for k, v in data.items():
            find_errors(v, f"{path}.{k}")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            find_errors(v, f"{path}[{i}]")

try:
    with open('/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/exec_429_raw.json', 'r') as f:
        data = json.load(f)
        find_errors(data)
except Exception as e:
    print(f"Fail: {e}")
