# Optional privacy choices: before and after

Date: 2026-10-17 (America/Phoenix).
TV: Samsung UN43TU7000FXZA, Tizen 5.5, firmware 2743.0 from the owner's About screen.

The owner confirmed Viewing Information Services and Interest-Based Advertisements were both enabled and then turned both off using the TV settings. Main service agreements were retained. No root, service termination, or reboot was used for the comparison.

Method: the same non-root top command in each recording, seven displays at two-second intervals, first display excluded. Each mean covers approximately 12 seconds. Memory is an end-of-recording snapshot. The initial after-change recording was busy with menu/graphics activity (88.8% overall CPU); it is retained as privacy-after.json, but not used as the settled comparison. The owner was asked to leave Settings untouched for 30 seconds before the repeat. Exact workload matching and interaction timing were not independently verified.

| Metric | Before | After settling |
| --- | ---: | ---: |
| Overall CPU, four-core capacity | 29.5% | 30.9% |
| ACRService CPU, one-core basis | 8.30% | 0.33% |
| adagent-service CPU, one-core basis | 0.27% | 2.68% |
| bms-service CPU, one-core basis | 26.93% | 28.40% |
| bgrecompd CPU, one-core basis | 10.07% | 7.13% |
| kswapd0 CPU, one-core basis | 11.37% | 13.65% |
| Available RAM | 211.0 MiB | 218.7 MiB |
| Logical swap occupied | 602.9 MiB | 676.1 MiB |
| zram physical memory consumption | 170.2 MiB | 198.6 MiB |

The ACRService process remained present (PID 3162), but its sampled CPU activity fell substantially. This is consistent with the owner's viewing-information opt-out; this short observational test does not establish causality. Advertising-agent CPU is bursty: earlier recordings caught one-core spikes, while this fresh before sample was quiet. Interest-based advertising opt-out does not promise removal of generic ads or termination of the ad agent.

There is no demonstrated reduction in overall CPU load, and the 7.7 MiB difference in available RAM is too small and uncontrolled to establish a meaningful improvement. Swap occupancy increased during the comparison window; without matched workloads and swap event counters this cannot be attributed to the privacy change. bms-service and memory-management activity remain relevant leads. No remote-input latency was directly timed.

## Owner-observed result

After the settings changes and settled measurement, the owner tested Up/Down clicks in Settings and reported **Noticeably faster** response. This is a useful subjective improvement alongside reduced ACR CPU activity, not a controlled latency benchmark or proof that all remaining lag has been resolved. Both privacy opt-outs are retained.

Evidence: privacy-before.json, privacy-after.json, privacy-after-settled.json and their paired raw top/memory files. Raw top files can contain application launch arguments; use summaries when sharing.

Sources for setting behavior:
- https://www.samsung.com/us/support/answer/ANS10010616/
- https://developer.samsung.com/smarttv/develop/guides/unique-identifiers-for-smarttv/tizen-id-for-advertising.html
