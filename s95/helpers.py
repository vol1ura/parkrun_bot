def min_to_mmss(m) -> str:
    mins = round(m) if abs(m - round(m)) < 0.0166665 else int(m)
    return f'{mins}:{round((m - mins) * 60):02d}'


def time_conv(t):
    arr = list(map(lambda x: int(x), str(t).split(':')))
    return (arr[0] - 21) * 60 + arr[1] + arr[2] / 60
