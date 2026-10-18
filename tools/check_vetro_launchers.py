"""Bounded permission-only checks; does not invoke a root payload."""
import datetime
import json
from tv_read import capture, ROOT

command = r'''
test ! -f /tmp/tvmod-capability-proof-20261017.txt || mv /tmp/tvmod-capability-proof-20261017.txt /tmp/tvmod-capability-proof-20261017.previous
for launcher in /usr/bin/dotnet-launcher /usr/bin/dotnet-launcher-inhouse /usr/bin/dotnet-launcher-inhouse-apitest; do
  echo LAUNCHER="$launcher"
  "$launcher" --standalone /home/owner/share/tmp/sdk_tools/tvmod-capability-proof.dll >/tmp/tvmod-vetro-launcher-check.log 2>&1 &
  probe_pid=$!
  (sleep 4; kill "$probe_pid" 2>/dev/null) & guard_pid=$!
  wait "$probe_pid"
  echo exit=$?
  kill "$guard_pid" 2>/dev/null
  if test -f /tmp/tvmod-capability-proof-20261017.txt; then
    cat /tmp/tvmod-capability-proof-20261017.txt
    mv /tmp/tvmod-capability-proof-20261017.txt /tmp/tvmod-vetro-launcher-last.txt
  else
    echo NO_MANAGED_REPORT
    head -c 1200 /tmp/tvmod-vetro-launcher-check.log
  fi
done
'''.strip()
# The existing capture transport writes Windows text files; keep shell control
# syntax on one line so CRLF does not split compound statements on the TV.
command = '; '.join(line.strip() for line in command.splitlines())
command = command.replace('do; ', 'do ').replace('then; ', 'then ').replace('else; ', 'else ').replace('&; ', '& ')
result = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'command': command}
try:
    result['output'] = capture(command, 25)
except Exception as error:
    result['error'] = str(error)
(ROOT / 'diagnostics/vetro-launcher-proof.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
