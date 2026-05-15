from datetime import date, datetime


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 2026-03-26 15:45:27


def today():
    return date.today()  # 2026-03-26
