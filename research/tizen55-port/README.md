# Vetro / TU7000 Tizen 5.5 investigation

Checked 2026-10-17, America/Phoenix. TV: UN43TU7000FXZA, firmware 2743.0,
T-KTSU2AKUC-REL-202607021959. Vetro source revision:
`45484aaa40d7f4faf3205b8a1996fd92cc2bcd34`.

**Partial helper port only. No working root, full Vetro port, signed installer,
or autonomous startup has been established.** Vetro's checked-out source and
bundled helpers have not been overwritten.

## What now works

`../../tools/build_vetro_net30.ps1` builds the four upstream managed helpers
against Microsoft's .NET Core 3.0 reference assemblies without a system SDK
installation. It uses Roslyn bundled with PowerShell, with deterministic release
compilation, and writes separate DLLs/runtime configs in `payload/`.

Prerequisites used here: PowerShell with Microsoft.CodeAnalysis assemblies;
Microsoft.NETCore.App.Ref 3.0.0 extracted under `tools/netcore30-ref/package`.
The official reference package was downloaded from NuGet's flat-container API.
Do not substitute the host computer's modern runtime reference assemblies.

From the workspace root:

```powershell
pwsh -NoProfile -File tools/build_vetro_net30.ps1
```

Hardware checks through Samsung's existing `dotnet-launcher --standalone`:

- RuntimeProbe ran under .NET 3.0.0; HMAC-SHA256 and ProcessStartInfo.ArgumentList
  were available. It did not start a subprocess or change privileges.
- `TvState` returned live volume, mute and source type, exit 0.
- ArchiveRoot loaded and its invalid-argument guard returned 2. With a valid-shaped
  package name it refused with `CAP_SYS_ADMIN and CAP_SETGID are required`, return
  1, before namespace/mount operations. No archive was created or launched.
- RootAgent and RemoteInputAgent loaded and returned 1 on missing arguments.
  This validates their guard paths only, not connections, command execution,
  remote interception, or privileged functionality.
- Native `DllImport("libc")` resolution worked.

The standard launcher redirects console streams internally. The smoke harness
captures managed output with StringWriter, then saves a temporary report. A
simple executable-name replacement would not provide Vetro's expected stdout or
root behavior. A suitable helper host remains part of the full port.

The upstream helper sources remain in `../vetro/`; consult their retained
licenses and `THIRD_PARTY_NOTICES.md` before distributing compiled artifacts.

## Root findings

1. The SDK shell has inheritable capabilities but no permitted/effective ones.
   Standard dotnet-launcher drops capabilities before managed code. Different
   argv[0] names did not change that result.
2. Disassembly and per-process logs identify Samsung's plugin attaching the
   `dotnetzone`. Profiling injection occurs *after* this transition. The profiling
   hook was reached, but loading our permission-only native probe failed with
   `failed to map segment from shared object`. The probe's constructor did not
   run. This failure is consistent with execution policy; no exact kernel
   enforcement mechanism was proven.
3. The inhouse launcher initializes its CLR and identifies an inhouse app, then
   exits when package metadata cannot establish platform privilege. That explains
   why earlier standalone invocations returned no managed report. The apitest
   launcher has not been traced as fully.
4. A direct syscall-based mmap2 check again returned ENODEV for a single known
   driver-owned DMA page. Slot registration readback succeeded; slot 31 was
   restored and verified. No physical memory was written, no kernel address
   scanning was attempted, and no credentials were changed. This does not prove
   that every variant of this driver route is unusable.
5. Hydra was inspected offline. Its launchpad protocol/callback route remains
   unproven; its file capabilities alone do not establish arbitrary managed
   execution with privileges. No Hydra daemon was launched.
6. The Mali module exposes only a generic version string in the checked sysfs
   metadata; it has not been matched to a specific applicable exploit. The
   QN90F Mali-G510 exploit is not evidence of compatibility with this ARMv7 TV.

## Additional JavaScript runtime blocker

Live `/usr/bin/node` is **4.4.3**. The fetched `/usr/bin/wrt-service` starts with
`#!/usr/bin/env node`, so this also matters to the TV service. Vetro declares
Node >=12.4.0. No usable newer runtime was established.

Live API checks found Buffer.alloc, crypto.generateKeyPairSync, crypto.sign,
crypto.timingSafeEqual, Promise.finally, String.padStart and Object.entries
unavailable. Buffer.from is present in this vendor build; do not infer API
availability solely from the version number.

Parse-only checks covered 37 server scripts. Three failed parsing:

- app/service/package-info.js: async function syntax.
- rooting/service/adb.js: destructuring syntax.
- rooting/service/sdb.js: destructuring syntax.

The remaining 34 passing syntax checks do not establish working execution.
Runtime APIs, native integrations, signing and boot privileges remain separate.
Direct execution of an unsigned probe file was rejected by Node's UEP check;
the parse-only test used `node -e` to read/evaluate our diagnostic wrapper. It
compiled the Vetro sources without running their module bodies.

## Remaining work

First find a demonstrated privilege-preserving host or another root primitive
on this exact firmware. Then adapt the helper invocation and JavaScript backend
(transpile unsupported syntax, replace unavailable APIs without weakening
authentication, or establish a compatible signed runtime). Finally resolve the
owner's app signing profile and validate actual service, root-agent and cold-boot
behavior. Do not install a package and label these prerequisites satisfied.

Evidence is in `../../diagnostics/vetro55-*.json`. Test payloads and reports on
the TV were removed after the checks; local source/build outputs are retained.
No Vetro app was installed, system setting changed, or debloating performed.
