import pandas as pd
import glob

from func import is_working_day, calculate_comm, sub_comm


folder_path = glob.glob("excel files/*.xls")

combined_df = pd.DataFrame()

for file in folder_path:
    df = pd.read_excel(file)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

combined_df["تاريخ الاصدار"] = pd.to_datetime(combined_df["تاريخ الاصدار"])
combined_df["اليوم"] = combined_df["تاريخ الاصدار"].dt.strftime('%d-%m-%Y')

tansactions_per_machine_service = combined_df.groupby(["الموقع", "نوع الوثيقة", "اليوم"]).size().reset_index(
    name='عدد الاستمارات المطبوعة')

tansactions_per_machine_service["comm"] = tansactions_per_machine_service.apply(
    lambda row: calculate_comm(row["نوع الوثيقة"], row['عدد الاستمارات المطبوعة']), axis=1)

total_commission_per_machine_per_day = tansactions_per_machine_service.groupby(["الموقع", "اليوم"])[
    'comm'].sum().reset_index()

all_dates = pd.date_range(start=total_commission_per_machine_per_day['اليوم'].min(),
                          end=total_commission_per_machine_per_day['اليوم'].max(), freq='D')

all_machines = total_commission_per_machine_per_day['الموقع'].unique()

all_combinations = pd.DataFrame([(machine, date) for machine in all_machines for date in all_dates],
                                columns=['الموقع', 'اليوم'])
all_combinations["اليوم"] = all_combinations["اليوم"].dt.strftime('%d-%m-%Y')

merged_df = pd.merge(all_combinations, total_commission_per_machine_per_day, on=['الموقع', 'اليوم'], how='left')
merged_df['comm'] = merged_df['comm'].fillna(0)
merged_df['dateformat'] = pd.to_datetime(merged_df['اليوم'], format='%d-%m-%Y')

merged_df['DayName'] = merged_df['dateformat'].dt.day_name()
merged_df['DayStatus'] = merged_df.apply(lambda row: is_working_day(row['DayName'], row['اليوم']),
                                         axis=1)
merged_df['sub_comm'] = merged_df.apply(lambda row: sub_comm(row['comm'], row['DayStatus']),
                                        axis=1)
#table = tabulate(merged_df, headers='keys', tablefmt='psql', showindex=False)

# print(merged_df.info())
print(all_machines)
