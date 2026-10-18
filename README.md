# ClearView for Samsung TV

Tools for Samsung TV diagnostics, cleanup research, and experimental Tizen 5.5 support.

ClearView brings together the work so far on understanding background activity,
checking compatibility, and adapting an existing TV control application for older
Samsung TVs. The current target is the **Samsung UN43TU7000FXZA**, running
**Tizen 5.5, firmware 2743.0**.

**This is an experimental source snapshot. A working root route, signed installer,
full application port, and automatic startup have not been demonstrated on this TV.**

## Progress so far

- Developer Mode and SDB diagnostics work, with SDK access rather than root.
- CPU, memory, privacy-setting comparisons, and cleanup findings are documented.
- .NET Core 3.0 helper builds compile and load; TvState successfully read live volume,
  mute, and source information.
- An experimental Node 4 compatibility branch adapts parts of the application to
  Samsung's older JavaScript runtime. Full service operation remains unverified.
- Normal TV menu deletion removed selected unwanted apps while preserving the
  inventoried streaming and casting apps.

## Explore the project

| Location | Contents |
| --- | --- |
| [Compatibility investigation](research/tizen55-port/README.md) | Verified checks, blockers, and remaining port work |
| [Diagnostic findings](diagnostics/FINDINGS.md) | Initial device and SDK assessment |
| [Performance report](diagnostics/PERFORMANCE-REPORT.md) | Bounded CPU and memory observations |
| [Privacy comparison](diagnostics/PRIVACY-COMPARISON.md) | Measurements and their limits |
| [Cleanup assessment](diagnostics/NO-ROOT-ASSESSMENT.md) | Normal-menu cleanup results |
| `research/vetro-node4/` | Modified application source and compatibility shims |
| `research/vetro/` | Upstream baseline used by the helper build |
| `tools/` | Diagnostic, inspection, and helper-build scripts |

## Development

The working application in `research/vetro-node4/` uses ClearView branding. Original
directory names, installed package IDs, saved-state paths, MQTT topics and diagnostic
schema identifiers are retained for compatibility. `CLEARVIEW_PORT` and
`CLEARVIEW_SOURCE_REVISION` are the preferred environment variables; the legacy
`VETRO_*` equivalents still work. Downloaded diagnostic files use the ClearView name.
The unchanged source in `research/vetro/`, license notices, historical test records
and original screenshots retain upstream branding and provenance. Upstream claims
about other TVs are not verification on the TU7000 or on a ClearView release.

Local application and integration checks, with a current Node.js installation:

```powershell
node research/vetro-node4/app/tests/run.cjs
node research/vetro-node4/rooting/tests/run.cjs
```

These host checks do not establish Node 4 or TV runtime compatibility.
The full suites require a Unix environment with `sh` and `/bin/sh`. On the
publication host (Windows, Node 25.9.0), 53 of 57 suites passed individually;
four could not complete because the required shell was unavailable:
`home-order-transaction`, `leftovers`, `injection`, and `launcher-release`.
Python diagnostic/tool source and the two compatibility modules passed syntax checks.

For hardware diagnostics, install Samsung's SDB from Tizen Studio at
`tools/sdb/sdb.exe`, enable Developer Mode on your own TV, and set its address:

```powershell
$env:TV_HOST = 'YOUR_TV_IP'
python diagnostics/check_tv.py
```

`tools/tv_read.py` supplies the SDK capture transport to the other scripts.
Scripts that stage or launch probes require their separately built payloads;
review their commands and prerequisites before running them. See the compatibility
investigation for the .NET Core 3.0 reference-package and PowerShell build setup.
Optional ELF inspection uses `capstone` and `pyelftools`.

## Publication contents

This repository contains source and written findings. Raw local device captures,
credentials, downloaded toolchains, compiled payloads, extracted Samsung binaries,
and external driver research without verified redistribution provenance stay local.
Historical notes reference some of those excluded evidence files; those raw captures
are not available in this public snapshot.

## Attribution

The application baseline is [Vetro](https://github.com/andrearicci93/vetro), revision
`45484aaa40d7f4faf3205b8a1996fd92cc2bcd34`, under its retained MIT license.
Samsung TV root transport and helpers derive from
[samsung-tv-root](https://github.com/chris-ritsen/samsung-tv-root), under the retained
Unlicense. See [third-party notices](THIRD_PARTY_NOTICES.md) for license locations.

ClearView is an independent project and is not affiliated with Samsung.
