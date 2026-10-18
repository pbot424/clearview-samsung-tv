# CPU and memory observations

Date: 2026-10-17 (America/Phoenix). Target: Samsung UN43TU7000FXZA, Tizen 5.5, firmware 2743.0 from the owner's About TV photo.

## Access and method

Live access confirmed uid=901(sdk), not root. No apps were stopped or changed. Short SDK commands could read /proc and run the installed procps top. A longer staged-shell sampling request failed; the shorter inline commands succeeded. Standard direct SDB shell/sysinfo requests returned no data.

Two top recordings were collected (four and seven displays at two-second intervals). The first display in each recording was excluded from interval CPU averages. The longer recording supplied six measured intervals, approximately 12 seconds. Top used roughly a few percent of one CPU core during the short recording, so the measurement itself was not free.

## Longer recording results

CPU percentages below use one core as 100%; this TV has four cores.

| Process | Mean CPU | Peak CPU |
| --- | ---: | ---: |
| bms-service | 27.7% | 32.2% |
| adagent-service | 25.0% | 102.0% |
| bgrecompd | 16.2% | 23.8% |
| ACRService | 8.8% | 10.0% |
| kswapd0 | 7.8% | 27.3% |
| tv-viewer | 7.2% | 8.0% |
| hbbtv_app | 5.9% | 7.0% |

Overall sampled CPU utilization averaged about 37% of four-core capacity. One core reached approximately 100% during a burst. The shorter recording also caught an adagent-service peak of 101.6% of one core; it was intermittent, not continuously saturated.

End-of-recording memory:

- Kernel-reported RAM: 1,129,180 KiB (about 1.08 GiB).
- Available RAM: 232,756 KiB (227.3 MiB).
- Logical swap occupied: about 623 MiB of 717 MiB.
- zram's reported physical memory consumption: 184,608 KiB (about 180.3 MiB); compressed pages' logical size is larger and must not be added to physical RAM use as another allocation.
- Largest resident process observed: PID 2947, previously shown as csfs.dll / com.samsung.tv.csfs. Resident size ranged from about 127 MiB in the first recording to 102 MiB at the end of the second.
- Other notable resident processes included a web-engine process (about 55 MiB in the earlier recording), hbbtv_app (about 40–44 MiB), and slive-provider-daemon (about 45 MiB at the end).

## Interpretation and limits

There are reproducible advertising-agent CPU bursts and sustained bms-service CPU activity. Compression/reclaim-related kernel work and substantial compressed-swap occupancy suggest memory-management overhead is relevant. These observations do not prove which component causes delayed remote input, do not establish a memory leak, and do not justify killing system services.

The TV's /proc/vmstat omitted pswpin/pswpout and major-fault event counters, so active swap churn was not quantified directly. Per-process resident sizes include shared pages and cannot be summed as unique RAM usage. The high load average also included many uninterruptible kernel tasks and should not be read as a CPU utilization percentage.

Evidence: performance-minimal-access-check.json, performance-summary.json, performance-long-summary.json, top-samples.txt, top-long-samples.txt, memory-now.txt, memory-long-after.txt, vmstat-before.txt, vmstat-after.txt. Raw top captures may include application launch arguments; use the summaries for sharing.
