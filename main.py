import pandas as pd
import glob
from tabulate import tabulate
from func import is_working_day, calculate_comm, read_json, check_machine_status, calculate_actual_comm

data_path = 'data.json'
folder_path = glob.glob("excel files/*.xls")
combined_df = pd.DataFrame()

for file in folder_path:
    df = pd.read_excel(file)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

combined_df = combined_df[combined_df['حالة الطباعة'] != 'ملغية']
combined_df["تاريخ الاصدار"] = pd.to_datetime(combined_df["تاريخ الاصدار"])
arabic_columns = list(combined_df.columns)
# print(arabic_columns)

english_columns = ["#", "Location", "Machine Code", "Document Type", "Document Number", "Document Owner", "Issue Date",
                   "Applicant", "Kinship", "Printing Status"]
combined_df.columns = english_columns

combined_df["Day"] = combined_df["Issue Date"].dt.strftime('%d-%m-%Y')

json_data = read_json(data_path)
# print(json_data['استمارات']['مول مصر 6 اكتوبر']['DeployDate'])

"""
machines_dict = combined_df.set_index('Location')['Machine Code'].to_dict()
machines_dict = {}
for index, row in combined_df.iterrows():
    key = row['الموقع']
    value = row['كود الماكينة']
    nested_dict = {'code': value, 'DeployDate': '', 'RemoveDate': ''}
    machines_dict[key] = nested_dict
    
sorted_machines = dict(sorted(machines_dict.items(), key=lambda x: x[1]['code']))
"""

tans_per_machine_service = combined_df.groupby(["Machine Code", "Location", "Document Type", "Day"]
                                               ).size().reset_index(name='Printed Count')

tans_per_machine_service["comm"] = tans_per_machine_service.apply(
    lambda row: calculate_comm(row["Document Type"], row['Printed Count']), axis=1)

total_comm_per_machine_per_day = tans_per_machine_service.groupby(["Machine Code", "Location", "Day"])[
    'comm'].sum().reset_index()

total_comm_per_machine_per_day['Machine Code'] = total_comm_per_machine_per_day['Machine Code'].astype(str)

total_comm_per_machine_per_day['Code_Location'] = \
    (total_comm_per_machine_per_day['Machine Code'] + '_' + total_comm_per_machine_per_day['Location'])

total_comm_per_machine_per_day = total_comm_per_machine_per_day.drop(['Machine Code', 'Location'], axis=1)

all_dates = pd.date_range(
    start=total_comm_per_machine_per_day['Day'].min(), end=total_comm_per_machine_per_day['Day'].max(),
    freq='D')

all_machines = total_comm_per_machine_per_day['Code_Location'].unique()

all_combinations = pd.DataFrame(
    [(machine, date) for machine in all_machines for date in all_dates],
    columns=['Code_Location', 'Day'])

all_combinations["Day"] = all_combinations["Day"].dt.strftime('%d-%m-%Y')

merged_df = pd.merge(all_combinations, total_comm_per_machine_per_day, on=['Code_Location', 'Day'],
                     how='left')

merged_df['comm'] = merged_df['comm'].fillna(0)
merged_df['dateformat'] = pd.to_datetime(merged_df['Day'], format='%d-%m-%Y')

merged_df['DayName'] = merged_df['dateformat'].dt.day_name()
merged_df['DayStatus'] = merged_df.apply(lambda x: is_working_day(x['DayName'], x['Day']), axis=1)
merged_df['dateformat'] = merged_df['dateformat'].apply(lambda y: y.date())
# merged_df['sub_comm'] = merged_df.apply(lambda row: sub_comm(row['comm'], row['DayStatus']), axis=1)


unique_months_years = (pd.to_datetime(merged_df['dateformat'])).dt.to_period('M').unique()
if len(unique_months_years) > 1:
    print("More than one unique combination of months and years.")
else:
    # If there is only one, print in the format "Month, Year"
    formatted_date = unique_months_years[0].strftime('%b, %Y')
    print(f"Current Month: {formatted_date}")

merged_df['Machine Status'] = merged_df.apply(lambda z: check_machine_status(z['Code_Location'], z['dateformat'],
                                                                             json_data['استمارات']), axis=1)

merged_df['Actual Comm'] = merged_df.apply(lambda a: calculate_actual_comm(a['comm'], a['Machine Status'],
                                                                           a['DayStatus'], 400.0), axis=1)

table = tabulate(merged_df, headers='keys', tablefmt='psql', showindex=False)
merged_df.to_excel('output_file.xlsx', index=False)
print(table)
total_comm_sum = merged_df['Actual Comm'].sum()
print(f"Total CITC Commission is {total_comm_sum}")

comm_per_machine = merged_df.groupby(['Code_Location'])['Actual Comm'].sum()

grouped = merged_df.groupby(['Code_Location', ])

# Create an Excel writer object
excel_writer = pd.ExcelWriter('output_file8.xlsx', engine='xlsxwriter')
comm_per_machine.to_excel(excel_writer, sheet_name="Total")
# Iterate over groups and save each DataFrame to a separate sheet
for group_name, group_df in grouped:
    # Save each DataFrame to a separate sheet with the name of the group
    group_df = group_df._append(pd.Series({"Actual Comm": group_df["Actual Comm"].sum()}), ignore_index=True)
    # group_df = pd.concat((group_df, pd.DataFrame({"Actual Comm": group_df["Actual Comm"].sum()})), ignore_index=True)
    group_df.to_excel(excel_writer, sheet_name=group_df.iloc[0]["Code_Location"][:31], index=False)

excel_writer.close()

print(comm_per_machine)
