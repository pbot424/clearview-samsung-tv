# Non-root cleanup assessment

Target: Samsung UN43TU7000FXZA, owner-reported firmware T-KTSU2AKUC-2743.0, live platform Tizen 5.5.
Assessment date: 2026-10-17 (America/Phoenix).

## Checks performed for this request

Used standard SDB device, capability, and application-list operations only. No command injection, root payload, or privileged helper was used in this pass. The device remains connected and lists 289 application entries including platform services. Standard `appinfo` dispatcher requests returned no metadata, so they do not establish whether a package is removable.

No app or service was removed or disabled. No settings were changed by the agent. Current per-app storage and CPU use were not measured in this pass. The earlier 245M free-storage measurement is historical and cannot establish present pressure or the result of a cleanup.

## Subsequent owner choices and verified actions

The owner uses all listed streaming/casting apps except Samsung TV Plus, Instagram, and Glance, and wants those three removed/disabled. They emphasized delayed remote response as the primary symptom.

- Standard `shell 0 execute qtMHjALHus.TVDeviceCare` reported a successful app launch (PID 1173). On-screen scan and storage results are awaiting owner input.
- Standard `sdb uninstall zigzSWa1hy` for Instagram returned `can not uninstall app` despite process exit code 0. Fresh inventory confirmed Instagram remains installed.
- Standard `sdb uninstall HupEmjIB4I` for Glance returned `can not uninstall app` despite process exit code 0. Fresh inventory confirmed Glance remains installed.
- The final inventory still contains 289 entries and no baseline app IDs are missing. All streaming/casting entries remain present.
- No protected system-service removal was attempted. Instagram and Glance cannot be described as removable through the tested standard route on this firmware.

Removal results: no-root-uninstall-results.json. Preservation verification: no-root-after-attempts.json.

### Successful deletion through the TV menu

The owner subsequently deleted Instagram, Glance, and Samsung Promotion through Device Care/Manage Storage. A fresh standard SDB inventory verified 285 entries, down from 289. Missing entries are exactly InstagramAirwave, Glance, PromotionApp, and the associated PromotionService. Streaming/casting entries remain installed. This supersedes the assumption that the standard SDB refusal means these apps cannot be removed without root: the TV menu permits their deletion even though `sdb uninstall` refused it.

The owner reports all displayed app caches are already zero. Pre-deletion free space was reported as 132.65 MB, with 1.16 GB used, from the TV's storage UI. Post-deletion free space and any improvement in remote responsiveness have not yet been measured.

Verification evidence: no-root-after-menu-deletions.json.

## Supported cleanup candidates

1. If unused, disable Samsung TV Plus using Home -> Samsung TV Plus -> Down -> Remove -> Disable, where offered. Samsung documents this path for 2020-2021 sets; US firmware/menu availability still needs on-screen confirmation. This is distinct from merely removing its home shortcut.
2. Turn off unwanted Autorun Smart Hub and Autorun Last App under Settings -> General -> Smart Features, where present. These settings alter startup behavior, not package installation.
3. Run Settings -> Support -> Device Care -> Start Device Care. Samsung describes this as closing unused background apps and clearing cached memory.
4. In Manage Storage, inspect View Details. Clear Cache when available; do not use Clear Data unless app login/settings reset is intended.
5. Delete unused user-facing apps only when the normal app menu enables Delete. Inventory candidates include Instagram, Glance, Hulu, Disney+, and other streaming services the owner does not use. Their presence does not prove uninstall is permitted. Check store availability first if future reinstall matters.

## Preserve

Do not remove platform packages, advertising/analytics daemons through unsupported commands, shared app engines, HDMI/CEC, audio/video services, keyboard, Smart Hub, account/authentication, networking, accessibility, Device Care, or update components. Do not interpret multiple YouTube or Apple TV entries as redundant packages: the firmware has wrappers and shared/native components.

## Awaiting owner information

- Current Device Care scan result, free storage, and largest app/cache sizes from Manage Storage.
- Availability of the supported Samsung TV Plus Disable option on the owner's current US firmware UI.

After a selected cleanup, re-list apps to verify actual removal and compare the same Device Care storage reading. Evaluate perceived speed using the same home/app-launch actions. No speed increase has yet been demonstrated.

## Sources

- https://www.samsung.com/us/support/answer/ANS10005205/ (Delete vs Remove from Home)
- https://www.samsung.com/au/support/tv-audio-video/disable-samsung-tv-plus/ (2020-2021 TV Plus disable path; regional differences apply)
- https://www.samsung.com/ph/support/tv-audio-video/how-to-use-the-device-care-on-my-samsung-smart-tv/ (Device Care and storage management)
- https://www.samsung.com/au/support/tv-audio-video/free-up-tv-storage/ (cache/data options for 2020+ compatible TVs)

Machine-readable local evidence: no-root-baseline.json and no-root-metadata.json.
