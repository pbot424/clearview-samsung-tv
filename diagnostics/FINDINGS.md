# Samsung TU7000 compatibility checks

Checked 2026-10-17 on the owner's specified TV (local address omitted).

## Confirmed

- TV HTTP API identified UN43TU7000FXZA before Developer Mode was enabled.
- Firmware 2743.0 was supplied in the owner's About TV photo. Live build fingerprint: T-KTSU2AKUC-REL-202607021959.
- SDB connection and `capability` work after the owner enabled Developer Mode.
- Platform: Tizen 5.5.0, ARMv7, Linux 4.1.10.
- `shell 0 applist` works; inventory contains 289 application entries, including platform components. This is not a count of running processes.
- `shell 0 vd_applist` timed out.
- Normal interactive shell and built-in SDB root are reported disabled.
- Bounded SDB package-name execution timing check succeeded. Read commands returned uid=901(sdk), not root. This check uses a public command-injection path and creates temporary gate directories, with temporary capture scripts self-removing.
- Resource snapshot: MemTotal 1129180 kB, MemAvailable 498168 kB (about 486 MiB); writable /opt partition 82% used with df reporting 245M available. Values are a single snapshot, not a benchmark.
- Running process names included adagent-service, media-analytics, pisa-service, and ACRService. Presence does not establish their individual performance cost.

## Root compatibility

Reviewed https://github.com/chris-ritsen/samsung-tv-root, specifically archive_root.py and sdb.py on master as retrieved on the check date.

The archive route is not compatible as shipped: /usr/bin/dotnet and /usr/share/dotnet/dotnet are absent. Available .NET runtime directory names stop at 3.0.0; upstream requires 3.1 or 6+. The signed archive launcher and tar --to-command support exist. Alternative dotnet-launcher binaries have powerful capabilities, but adaptation has not been implemented or tested. Their presence is not proof of an alternate root route.

No root payload, namespace manipulation, root agent, app install/uninstall, service stop, or startup modification was attempted. Existing Vetro integration and a replacement default Home screen have not been verified on this TV. Protected-app removability cannot be established from the inventory alone.

## Local evidence

- latest-check.json: SDB capabilities and raw app inventory; HTTP identity was unavailable during this later check.
- app-inventory.json: parsed app inventory.
- sdk-prerequisites.json: SDK execution, identity, and archive-root prerequisites.
- resources-and-runtimes.json: resource snapshot and process-name checks.
- alternate-runtime.json: alternate runtime paths and launcher capabilities.

## Practical conclusion

SDK diagnostics work on this firmware. No ready-made reversible system-service debloater or default Home replacement has been demonstrated. A further root investigation would need a Tizen 5.5 adaptation or a separately validated route. Removing an installed app is a separate, potentially non-reversible test and was not part of these checks.
