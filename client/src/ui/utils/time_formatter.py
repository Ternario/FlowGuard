from datetime import time


def format_or_fact_dt(value: time | None) -> str:
    if not value:
        return '-'
    return value.strftime('%H:%M')
