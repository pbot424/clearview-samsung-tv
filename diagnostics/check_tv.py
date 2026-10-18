"""Read-only identity, port, and SDB inventory checks for this TV."""
import datetime
import json
import os
from pathlib import Path
import socket
import subprocess
import urllib.request

HOST = os.environ.get('TV_HOST')
if not HOST:
    raise SystemExit('Set TV_HOST to the address of your TV')
ROOT = Path(__file__).resolve().parents[1]
SDB = ROOT / 'tools' / 'sdb' / 'sdb.exe'
report = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'host': HOST}
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
    connection.connect((HOST, 8001))
    report['controller_ip'] = connection.getsockname()[0]
try:
    with urllib.request.urlopen(f'http://{HOST}:8001/api/v2/', timeout=5) as response:
        device = json.load(response)['device']
    report['device'] = {key: device.get(key) for key in (
        'modelName', 'model', 'OS', 'firmwareVersion', 'developerMode', 'developerIP', 'PowerState')}
except Exception as error:
    report['identity_error'] = str(error)
report['ports'] = {}
for port in (8001, 8002, 26101):
    try:
        with socket.create_connection((HOST, port), timeout=2):
            report['ports'][str(port)] = True
    except OSError:
        report['ports'][str(port)] = False
if report['ports']['26101'] and SDB.is_file():
    report['sdb'] = {}
    commands = [('connect', ['connect', f'{HOST}:26101']),
                ('capability', ['-s', f'{HOST}:26101', 'capability']),
                ('applist', ['-s', f'{HOST}:26101', 'shell', '0', 'applist']),
                ('vd_applist', ['-s', f'{HOST}:26101', 'shell', '0', 'vd_applist'])]
    for label, arguments in commands:
        try:
            result = subprocess.run([str(SDB), *arguments], capture_output=True,
                                    encoding='utf-8', errors='replace', timeout=12)
            report['sdb'][label] = {'returncode': result.returncode,
                                    'stdout': result.stdout, 'stderr': result.stderr}
        except subprocess.TimeoutExpired:
            report['sdb'][label] = {'error': 'Timed out after 12 seconds'}
output = ROOT / 'diagnostics' / 'latest-check.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
