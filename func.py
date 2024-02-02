import pandas as pd
import json

comm_50, comm_125, comm_175 = 5, 10, 10
services_config = {"استمارة فئة 50 جنيه": 5,
                   "استمارة فئة 125 جنيه": 10,
                   "استمارة فئة 175 جنيه": 10}
day_off = ['الجمعة']
min_value = 400.0
holiday_list = [pd.to_datetime('2024-01-07'), pd.to_datetime('2024-01-25')]


def is_working_day(day_name, holiday):
    formatted_holidays = [date.strftime('%d-%m-%Y') for date in holiday_list]
    if day_name in day_off:
        status = 'عطلة اسبوعية'
    elif holiday.strftime('%d-%m-%Y') in formatted_holidays:
        status = 'أجازة رسمية'
    else:
        status = 'يوم شغل'

    return status


def calculate_comm(service_type, total_count):
    commission_rate = services_config.get(service_type)
    return total_count * commission_rate


def sub_comm(amount, day_status):
    if day_status == 'عطلة اسبوعية' or day_status == 'أجازة رسمية':
        return amount
    else:
        if amount < min_value:
            return min_value
        else:
            return amount


def read_json(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as file:
        data = json.load(file)
    return data


def check_machine_status(location, date, j_data):
    date_reformat = pd.to_datetime(date)

    for key, value in j_data.items():
        if key == location:
            if (pd.to_datetime(value['DeployDate'], dayfirst=True) <= date_reformat and
                    (not value['RemoveDate'] or pd.to_datetime(value['RemoveDate'], dayfirst=True) >= date_reformat)):
                status = "نشطة"
            else:
                status = "غير نشطة"

            return status


def calculate_actual_comm(comm, m_status, d_status, min_comm=min_value):
    if m_status == "غير نشطة":
        actual_comm = 0
    elif d_status != "يوم شغل" or comm > min_comm:
        actual_comm = comm
    else:
        actual_comm = min_comm
    return actual_comm
