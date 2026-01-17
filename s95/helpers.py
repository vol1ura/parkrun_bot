def min_to_mmss(m) -> str:
    mins = round(m) if abs(m - round(m)) < 0.0166665 else int(m)
    return f'{mins}:{round((m - mins) * 60):02d}'
