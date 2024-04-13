from datetime import datetime


def percentage(curr, total):
    if not (isinstance(curr, (int, float)) and isinstance(total, (int, float))):
        raise ValueError("Both curr and total should be numerical values")
    if total == 0:
        raise ValueError("Total can not be zero")
    num = curr / total
    return f"{num:.2%}"


def get_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def get_folder_time():
    now = datetime.now()
    return now.strftime("%d%m%Y%H%M%S")


def convert_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h == 0:
        return f"{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
