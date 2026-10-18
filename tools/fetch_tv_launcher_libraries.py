"""Read only the specified Samsung launcher libraries for offline analysis."""
import base64
import hashlib
from tv_read import capture, ROOT

for remote in ('/usr/bin/wrt-service',):
    name = remote.rsplit('/', 1)[1]
    result = capture('base64 ' + remote, 20)
    encoded, marker = result.rsplit('[exit:', 1)
    if not marker.startswith('0]'):
        raise RuntimeError('Read failed: ' + name)
    data = base64.b64decode(encoded, validate=False)
    output = ROOT / 'research/tv-binaries' / name
    output.write_bytes(data)
    print(name, len(data), hashlib.sha256(data).hexdigest())
