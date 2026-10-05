# Erlang C Staffing Calculator

A small Python tool that answers a classic contact-center question:
**how many agents do I need to hit my service-level target?**

I worked in contact-center operations (real-time analysis and workforce management for teams of up to 160 agents), where this calculation drives every staffing plan. I built this to understand the math behind the tools I used every day.

## What it calculates

Given the expected volume for an interval, it returns:

- **Workload** in Erlangs
- **Agents needed on the phone** to reach the target
- **Agents to schedule** after shrinkage (breaks, training, absences)
- **Service level** reached (e.g. 83.9% answered in 20s)
- **Average speed of answer** (ASA)
- **Occupancy**

## Usage

Requires Python 3 — no extra libraries.

```bash
python erlang_c.py --calls 300 --aht 240 --interval 30 --target 0.8 --seconds 20 --shrinkage 0.3
```

Example output:

```
Workload:            40.0 Erlangs
Agents on phone:     46
Agents to schedule:  66  (shrinkage 30%)
Service level:       83.9% in 20s
Avg speed of answer: 10.6 s
Occupancy:           87.0%
```

| Parameter | Meaning | Default |
|---|---|---|
| `--calls` | Contacts expected in the interval | required |
| `--aht` | Average handle time (seconds) | required |
| `--interval` | Interval length (minutes) | 30 |
| `--target` | Service-level target (0–1) | 0.8 |
| `--seconds` | Answer-time threshold (seconds) | 20 |
| `--shrinkage` | Share of paid time not available (0–1) | 0 |

## How it works

1. **Workload** = calls × AHT ÷ interval length.
2. The **Erlang C formula** gives the probability a contact waits in queue for a given number of agents.
3. The tool adds agents one at a time until the service level meets the target.
4. Shrinkage converts agents on the phone into agents to schedule.

## Limitations

Erlang C assumes callers never hang up while waiting and that arrivals are random, so it tends to slightly overestimate staffing. It's a planning baseline, not a replacement for a full WFM tool.
