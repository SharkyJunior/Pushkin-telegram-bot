def progress_bar(current, total, bar_length=20):
    fraction = current / total

    arrow = int(fraction * bar_length) * '#'
    padding = int(bar_length - len(arrow)) * ' '

    return f'[{arrow}{padding}] {int(fraction*100)}%'
