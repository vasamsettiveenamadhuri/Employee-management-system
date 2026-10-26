from datetime import datetime

def get_holidays(year, month):
    holidays = [
        "2025-01-26", "2025-08-15", "2025-10-02"  # Example holidays
    ]
    return [datetime.strptime(date, "%Y-%m-%d").date() for date in holidays if datetime.strptime(date, "%Y-%m-%d").month == month]
