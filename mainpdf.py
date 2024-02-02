import pandas as pd
import glob
from tabulate import tabulate
from func import is_working_day, calculate_comm, read_json, check_machine_status, calculate_actual_comm


# Functions
def show_table(dataframe):
    table = tabulate(dataframe, headers='keys', tablefmt='psql', showindex=False)
    return table


# Variables
english_to_arabic_day_names = {
    'Monday': 'الاثنين',
    'Tuesday': 'الثلاثاء',
    'Wednesday': 'الأربعاء',
    'Thursday': 'الخميس',
    'Friday': 'الجمعة',
    'Saturday': 'السبت',
    'Sunday': 'الأحد'
}
comm_50, comm_125, comm_175 = 5, 10, 10
data_path = 'data.json'

# Loading data from excel files to DataFrame
folder_files = glob.glob("excel files/*.xls")
raw_df = pd.DataFrame()
for file in folder_files:
    df_file = pd.read_excel(file)
    raw_df = pd.concat([raw_df, df_file], ignore_index=True)

columns = list(raw_df.columns)
# print(columns)
# print(df)

# Cleaning data in the created DataFrame
cleaned_df = raw_df[raw_df['حالة الطباعة'] != 'ملغية']
cleaned_df = cleaned_df[cleaned_df['كود الماكينة'] != 9999]
cleaned_df = cleaned_df.drop(['مقدم الطلب', 'صلة القرابة', 'رقم الوثيقة', 'صاحب الوثيقة', 'م'], axis=1)

columns_cleaned = list(cleaned_df.columns)
# print(columns_cleaned)
# print(cleaned_df)

# Reordering DataFrame adding necessary columns
new_order = ['تاريخ الاصدار', 'الموقع', 'كود الماكينة', 'نوع الوثيقة', 'حالة الطباعة']
reordered_df = cleaned_df[new_order]
reordered_df['تاريخ الاصدار'] = pd.to_datetime(reordered_df['تاريخ الاصدار']).dt.date

final_df = (reordered_df.groupby(['تاريخ الاصدار', 'الموقع', 'كود الماكينة', 'نوع الوثيقة'])
            .size().reset_index(name='عدد الوثائق المطبوعة'))

pivot_df = final_df.pivot_table(index=['تاريخ الاصدار', 'الموقع', 'كود الماكينة'],
                                columns='نوع الوثيقة',
                                values='عدد الوثائق المطبوعة',
                                aggfunc='sum')
pivot_df = pivot_df.fillna(0)
pivot_df.reset_index(inplace=True)
# print(show_table(pivot_df))
pivot_df['Code_Location'] = pivot_df['كود الماكينة'].astype(str) + '_' + pivot_df['الموقع']

all_dates = pd.date_range(
    start=pivot_df['تاريخ الاصدار'].min(), end=pivot_df['تاريخ الاصدار'].max(), freq='D')

all_machines = pivot_df['Code_Location'].unique()

all_combinations = pd.DataFrame(
    [(machine, date) for machine in all_machines for date in all_dates],
    columns=['Code_Location', 'تاريخ الاصدار'])

all_combinations['تاريخ الاصدار'] = pd.to_datetime(all_combinations['تاريخ الاصدار']).dt.date
merged_df = pd.merge(all_combinations, pivot_df, on=['Code_Location', 'تاريخ الاصدار'], how='left')

merged_df[['كود الماكينة', 'الموقع']] = merged_df['Code_Location'].str.split('_', expand=True)
merged_df = merged_df.fillna(0)
merged_df = merged_df.drop(['Code_Location'], axis=1)
merged_df['اجمالى عدد المصدرات'] = (merged_df[['استمارة فئة 125 جنيه', 'استمارة فئة 175 جنيه', 'استمارة فئة 50 جنيه']]
                                    .sum(axis=1))
# print(show_table(merged_df))

# Calculating the Commissions
merged_df['اليوم'] = pd.to_datetime(merged_df['تاريخ الاصدار']).dt.day_name().map(english_to_arabic_day_names)
merged_df.insert(1, 'اليوم', merged_df.pop('اليوم'))
merged_df['حالة اليوم'] = merged_df.apply(lambda x: is_working_day(x['اليوم'], pd.to_datetime(x['تاريخ الاصدار'])),
                                          axis=1)
merged_df.insert(2, 'حالة اليوم', merged_df.pop('حالة اليوم'))

json_data = read_json(data_path)
merged_df['حالة الماكينة'] = merged_df.apply(lambda z: check_machine_status(z['الموقع'], z['تاريخ الاصدار'],
                                                                            json_data['استمارات']), axis=1)
merged_df["النسبة 125"] = merged_df['استمارة فئة 125 جنيه'] * comm_125
merged_df["النسبة 175"] = merged_df['استمارة فئة 175 جنيه'] * comm_175
merged_df["النسبة 50"] = merged_df['استمارة فئة 50 جنيه'] * comm_50
merged_df['اجمالى النسبة'] = (merged_df[['النسبة 50', 'النسبة 175', 'النسبة 125']].sum(axis=1))
merged_df['اجمالى نسبة سيتك'] = merged_df.apply(
    lambda a: calculate_actual_comm(a['اجمالى النسبة'], a['حالة الماكينة'], a['حالة اليوم'], 400.0), axis=1)
print(show_table(merged_df))
total_comm_sum = merged_df['اجمالى نسبة سيتك'].sum()
print(f"Total CITC Commission is {total_comm_sum}")

