"""
Erlang C staffing calculator
----------------------------
Estimates how many contact-center agents are needed to reach a
service-level target (e.g. 80% of calls answered within 20 seconds).

Usage:
    python erlang_c.py --calls 300 --aht 240 --interval 30 --target 0.8 --seconds 20
"""

import argparse
import math


def traffic_intensity(calls: float, aht_seconds: float, interval_minutes: float) -> float:
    """Workload in Erlangs: how many agents would be busy 100% of the time."""
    return calls * aht_seconds / (interval_minutes * 60)


def erlang_c(agents: int, traffic: float) -> float:
    """Probability that a contact has to wait (Erlang C formula)."""
    if agents <= traffic:
        return 1.0  # not enough agents: queue grows without limit
    # Sum of A^k / k! for k = 0 .. N-1
    total = sum(traffic ** k / math.factorial(k) for k in range(agents))
    top = (traffic ** agents / math.factorial(agents)) * (agents / (agents - traffic))
    return top / (total + top)


def service_level(agents: int, traffic: float, aht_seconds: float, target_seconds: float) -> float:
    """Share of contacts answered within target_seconds."""
    pw = erlang_c(agents, traffic)
    return 1 - pw * math.exp(-(agents - traffic) * target_seconds / aht_seconds)


def average_speed_of_answer(agents: int, traffic: float, aht_seconds: float) -> float:
    """Average wait in seconds (ASA)."""
    if agents <= traffic:
        return float("inf")
    return erlang_c(agents, traffic) * aht_seconds / (agents - traffic)


def required_agents(calls, aht_seconds, interval_minutes, target_sl, target_seconds, shrinkage=0.0):
    """Smallest number of agents that meets the service-level target."""
    traffic = traffic_intensity(calls, aht_seconds, interval_minutes)
    agents = max(1, math.ceil(traffic))
    while service_level(agents, traffic, aht_seconds, target_seconds) < target_sl:
        agents += 1
    scheduled = math.ceil(agents / (1 - shrinkage)) if shrinkage else agents
    return {
        "traffic_erlangs": round(traffic, 2),
        "agents_on_phone": agents,
        "agents_scheduled": scheduled,
        "service_level": round(service_level(agents, traffic, aht_seconds, target_seconds), 4),
        "asa_seconds": round(average_speed_of_answer(agents, traffic, aht_seconds), 1),
        "occupancy": round(traffic / agents, 4),
    }


def main():
    p = argparse.ArgumentParser(description="Erlang C staffing calculator")
    p.add_argument("--calls", type=float, required=True, help="Contacts expected in the interval")
    p.add_argument("--aht", type=float, required=True, help="Average handle time in seconds")
    p.add_argument("--interval", type=float, default=30, help="Interval length in minutes (default 30)")
    p.add_argument("--target", type=float, default=0.8, help="Service-level target, 0-1 (default 0.8)")
    p.add_argument("--seconds", type=float, default=20, help="Answer-time threshold in seconds (default 20)")
    p.add_argument("--shrinkage", type=float, default=0.0, help="Breaks/absence share, 0-1 (default 0)")
    a = p.parse_args()

    r = required_agents(a.calls, a.aht, a.interval, a.target, a.seconds, a.shrinkage)
    print(f"Workload:            {r['traffic_erlangs']} Erlangs")
    print(f"Agents on phone:     {r['agents_on_phone']}")
    print(f"Agents to schedule:  {r['agents_scheduled']}  (shrinkage {a.shrinkage:.0%})")
    print(f"Service level:       {r['service_level']:.1%} in {a.seconds:.0f}s")
    print(f"Avg speed of answer: {r['asa_seconds']} s")
    print(f"Occupancy:           {r['occupancy']:.1%}")


if __name__ == "__main__":
    main()
