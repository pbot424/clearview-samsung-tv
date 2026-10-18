"""Explicit-target SDK diagnostics; commands are supplied by the operator."""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reviewed_tv_sdb', ROOT / 'research/samsung-tv-root/sdb.py')
sdb = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sdb
spec.loader.exec_module(sdb)

def capture(command, timeout=15):
    host = os.environ.get('TV_HOST')
    if not host:
        raise ValueError('Set TV_HOST to the address of your TV')
    client = sdb.SdbClient(ROOT / 'tools/sdb/sdb.exe', host, timeout=8)
    return client.capture(command, timeout=timeout).output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label')
    parser.add_argument('command')
    parser.add_argument('--timeout', type=float, default=15)
    args = parser.parse_args()
    result = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'command': args.command}
    try:
        result['output'] = capture(args.command, args.timeout)
    except Exception as error:
        result['error'] = str(error)
    path = ROOT / 'diagnostics' / (args.label + '.json')
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
