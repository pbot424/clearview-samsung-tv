# Vetro compatibility investigation

Follow-up: see `../research/tizen55-port/README.md`. Separate .NET 3.0 builds
now compile and load on the TV, including a successful live TvState read. Root
remains unavailable through the tested routes. A further confirmed blocker is
the TV's Node 4.4.3 service runtime versus Vetro's Node >=12.4.0 requirement.
The original findings below are retained as the initial assessment.

Checked 2026-10-17 (America/Phoenix), against Vetro revision
`45484aaa40d7f4faf3205b8a1996fd92cc2bcd34` (version 0.2.3).

Target: Samsung UN43TU7000FXZA, firmware 2743.0, live build
T-KTSU2AKUC-REL-202607021959, Tizen 5.5.0, ARMv7, Linux 4.1.10.

## Result

Vetro is not operational on this TV. The current integration cannot run as
shipped, and no working replacement privileged launch path was demonstrated.
This is a platform port/root prerequisite problem, not just a missing installer.

## Confirmed blockers

1. `rooting/service/platform.js` invokes `/usr/bin/dotnet` for both the archive
   helper and root agent. This executable is absent on the TV.
2. Bundled archive, root and remote-input helpers, plus `app/native/TvState`,
   declare .NET Core 3.1. The installed runtime directories stop at 3.0.0.
   Directory presence does not itself prove that an alternative host can use them.
3. `SamsungTvArchiveRoot.cs` explicitly requires CAP_SYS_ADMIN and CAP_SETGID
   before creating its private mount namespace. A fresh harmless managed-code
   diagnostic through `/usr/bin/dotnet-launcher --standalone` ran as UID/EUID 901
   with CapPrm=0 and CapEff=0. File capabilities on the launcher do not carry
   through to this managed payload. Changing the executable path or the helper's
   runtime declaration cannot resolve this prerequisite by itself.
4. No author/distributor signing profile was found in the usual user certificate
   or Tizen Studio directories checked. Only SDB keys were found under `.tizen`;
   these are not app signing certificates. Other user-selected locations were
   not exhaustively searched. Partner/on-boot entitlement remains untested.

## Checks and limits

- Live SDB and the SDK command foothold work; identity remains UID 901, not root.
- Signed archive launcher and tar `--to-command` are present, but insufficient.
- The same harmless managed diagnostic was attempted with
  `dotnet-launcher-inhouse` and `dotnet-launcher-inhouse-apitest`, with four-second
  kill guards. Both exited without producing a managed report; that invocation
  did not demonstrate an alternative. This does not establish that every mode
  of those binaries is unusable.
- Hydra's strings suggest another launcher loading mechanism; it was not executed
  or established as a working privileged path. It remains an unproven research
  candidate, not an installation recommendation.
- REA could not open the ARM ELF with its installed Windows providers. Ordinary
  source inspection, existing binary strings and live diagnostics supplied the
  findings; no successful native decompilation is claimed.
- No Vetro/root payload was installed, no service flags were changed, and no
  application or platform component was removed. Diagnostic scripts stage
  temporary files through the existing SDK capture transport. Launcher-test logs
  were removed and the previous capability report restored afterward.

## What is needed to proceed

First demonstrate a bounded diagnostic retaining the two required capabilities,
or validate a separate root route on this exact TV/firmware. Then adapt and test
the managed helpers and host invocation for the available runtime, create the
owner's TV-bound signing profile, and install/verify the integration. Autonomous
cold-boot recovery must be checked separately from manual startup.

Do not copy an unsigned `dotnet` executable into a writable directory and assume
it acquires Samsung's capabilities. Do not upgrade system runtimes or modify
firmware merely to satisfy these checks. No ready-made fix was established.

Evidence: `vetro-prerequisites.json`, `vetro-runtime-paths.json`,
`vetro-launcher-proof.json`, `vetro-cleanup.json`.

Upstream documentation:
- https://github.com/andrearicci93/vetro
- https://github.com/andrearicci93/vetro/blob/main/app/docs/INSTALLATION.md
- https://github.com/chris-ritsen/samsung-tv-root#archive-root-route
