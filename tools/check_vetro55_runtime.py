"""Exercise only the read-only managed probe through explicit launcher modes."""
import datetime
import json
import shlex
from tv_read import ROOT, capture

probe = '/home/owner/share/tmp/sdk_tools/vetro55-runtime.dll'
launches = {
    'default': '/usr/bin/dotnet-launcher --standalone ' + probe,
    'inhouse_argv': "bash -c " + shlex.quote('exec -a dotnet-launcher-inhouse /usr/bin/dotnet-launcher --standalone ' + probe),
    'other_argv': "bash -c " + shlex.quote('exec -a tvmod-runtime-probe /usr/bin/dotnet-launcher --standalone ' + probe),
}
report = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': {}}
for name, launch in launches.items():
    command = (
        'rm -f /tmp/tvmod-vetro55-runtime.txt; ' + launch + ' >/tmp/tvmod-vetro55-launch.log 2>&1 & p=$!; '
        '(sleep 5; kill "$p" 2>/dev/null) & g=$!; wait "$p"; code=$?; kill "$g" 2>/dev/null; '
        'echo launcher_exit=$code; if test -f /tmp/tvmod-vetro55-runtime.txt; then '
        'cat /tmp/tvmod-vetro55-runtime.txt; else echo NO_REPORT; head -c 1000 /tmp/tvmod-vetro55-launch.log; fi'
    )
    entry = {'command': command}
    try:
        entry['output'] = capture(command, 15)
    except Exception as error:
        entry['error'] = str(error)
    report['checks'][name] = entry
    print(name, entry.get('output', entry.get('error')))
(ROOT / 'diagnostics/vetro55-runtime.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
