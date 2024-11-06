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

def size(bytes_size):
    """Convert bytes to a human-readable format (e.g., KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

def eval_pick(pick):
    # pick will be one number, a range of numbers('1-5'), or a list of numbers('1,2,3,4,5')
    # need to return a list of numbers
    pick_list = []
    if pick.isdigit():
        pick_list.append(int(pick.strip()) - 1)
    elif "-" in pick:
        start, end = pick.split("-")
        pick_list.extend(range(int(start.strip()) - 1, int(end.strip())))
    elif "," in pick:
        pick_list.extend([int(x) - 1 for x in pick.replace(" ", "").split(",")])
    return pick_list