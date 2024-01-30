import pandas as pd

comm_50, comm_125, comm_175 = 5, 10, 10
services_config = {"استمارة فئة 50 جنيه": 5,
                   "استمارة فئة 125 جنيه": 10,
                   "استمارة فئة 175 جنيه": 10}
day_off = ['Friday']
min_value = 400
holiday_list = [pd.to_datetime('2024-01-01'), pd.to_datetime('2024-01-25')]


def is_working_day(day_name, holiday):
    formatted_holidays = [date.strftime('%d-%m-%Y') for date in holiday_list]
    if day_name in day_off or holiday in formatted_holidays:
        return 'Off'
    else:
        return 'Working'


def calculate_comm(service_type, total_count):
    commission_rate = services_config.get(service_type)
    return total_count * commission_rate


def sub_comm(amount, day_status):
    if day_status == "off":
        return amount
    else:
        if amount < min_value:
            return min_value
        else:
            return amount
