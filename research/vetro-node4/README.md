# ClearView for Samsung TV

Tools for Samsung TV diagnostics, cleanup research, and experimental Tizen 5.5 support.

This is the working application source for [ClearView](../../README.md), adapted
from the upstream Vetro revision recorded below. The launcher, browser dashboard,
remote authorization name, MQTT device display name, and application metadata use
ClearView branding.

**A working root route, signed installer, complete service port, and automatic
startup have not been demonstrated on the Samsung TU7000.** See the
[compatibility investigation](../tizen55-port/README.md) for verified progress.

## Development

From this directory:

```sh
node app/tests/run.cjs
node rooting/tests/run.cjs
```

The full suites require Unix shell tools. See the [project README](../../README.md)
for recorded Windows results and setup prerequisites. Host checks do not verify
Samsung's Node 4 runtime or hardware behavior.

The [app guide](app/README.md) describes the standalone application boundary;
[TV integration](rooting/README.md) describes the privileged adapter. These inherited
instructions describe source architecture, rather than a verified TU7000 installer.
Use `CLEARVIEW_PORT` and `CLEARVIEW_SOURCE_REVISION` for new configurations; the
legacy `VETRO_*` variables remain supported.

Installed package IDs, saved-state paths, MQTT topics and diagnostic schema names
are retained to preserve compatibility. Original screenshots, historical release
records and benchmark reports describe upstream Vetro observations on other
hardware. They are not ClearView release verification.

## Upstream attribution

Adapted from [Vetro](https://github.com/andrearicci93/vetro), revision
`45484aaa40d7f4faf3205b8a1996fd92cc2bcd34`. Original Vetro code is MIT licensed;
its copyright notice is preserved in [LICENSE](LICENSE). See
[third-party notices](THIRD_PARTY_NOTICES.md) for additional dependencies and credits.
ClearView is independent and unaffiliated with Samsung or the upstream projects.
