"""Bounded, non-root CPU/memory sampling through existing SDK access."""
import argparse
import datetime
import json
from pathlib import Path
import re
import statistics
from tv_read import capture, ROOT

def parse_top(raw):
    samples = []
    for block in re.split(r'(?m)^top - ', raw)[1:]:
        sample = {'header': block.splitlines()[0], 'cores': {}, 'processes': []}
        for line in block.splitlines():
            match = re.match(r'%Cpu(\d+)\s*:\s*([\d.]+)/([\d.]+)\s+([\d.]+)', line)
            if match:
                sample['cores'][match[1]] = float(match[4])
            cols = line.strip().split(None, 10)
            if len(cols) != 11 or not cols[0].isdigit():
                continue
            try:
                command = re.sub(r'^[\s`|+\\-]+', '', cols[10])
                name = command if command.startswith('[') else command.split()[0].rsplit('/', 1)[-1]
                memory = re.fullmatch(r'([\d.]+)([kKmMgGtT]?)', cols[5])
                rss = float(memory[1]) * {'': 1/1024, 'k': 1/1024, 'm': 1, 'g': 1024, 't': 1048576}[memory[2].lower()] if memory else None
                sample['processes'].append({'pid': int(cols[0]), 'name': name, 'cpu': float(cols[6]), 'rss_mib': rss})
            except (ValueError, IndexError):
                continue
        samples.append(sample)
    if len(samples) != 7 or any(len(sample['cores']) != 4 for sample in samples):
        raise ValueError('Expected seven top displays with four CPU cores; incomplete or unfamiliar format')
    measured = samples[1:]
    processes = []
    for pid in {p['pid'] for s in measured for p in s['processes']}:
        values = [p for s in measured for p in s['processes'] if p['pid'] == pid]
        processes.append({'pid': pid, 'name': values[-1]['name'],
                          'mean_cpu_one_core': round(sum(v['cpu'] for v in values)/len(measured), 2),
                          'peak_cpu_one_core': max(v['cpu'] for v in values),
                          'rss_mib_last': values[-1]['rss_mib']})
    return {'sample_headers': [s['header'] for s in samples],
            'cpu_busy_all_cores_percent': round(statistics.mean(v for s in measured for v in s['cores'].values()), 2),
            'measurement_intervals': len(measured), 'interval_seconds': 2,
            'processes': sorted(processes, key=lambda p: p['mean_cpu_one_core'], reverse=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', args.label):
        raise ValueError('Use a simple lowercase label')
    directory = ROOT/'diagnostics'
    prefix = directory/args.label
    top = capture('top -b -n 7 -d 2 -w 140 -c', 23)
    prefix.with_suffix('.top.txt').write_text(top, encoding='utf-8')
    memory = capture('cat /proc/meminfo', 6)
    prefix.with_suffix('.memory.txt').write_text(memory, encoding='utf-8')
    report = parse_top(top)
    report['checked_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    mem = {k: int(v) for k, v in re.findall(r'(?m)^(\w+):\s+(\d+) kB', memory)}
    report['memory_kib'] = mem
    report['available_ram_mib'] = round(mem['MemAvailable']/1024, 1)
    report['logical_swap_used_mib'] = round((mem['SwapTotal']-mem['SwapFree'])/1024, 1)
    zram = re.search(r'zram0: (.*)', memory)
    report['zram_kib'] = {k: int(v) for v, k in re.findall(r'(\d+) kB (\w+)', zram[1])} if zram else {}
    prefix.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'processes'}, indent=2))
    print('Highest sampled CPU processes:', json.dumps(report['processes'][:8], indent=2))
