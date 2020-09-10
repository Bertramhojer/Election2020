import os
import pandas as pd
import openpyxl

file_directory = '/Users/hojer/Desktop/projects/Election2020/tweets-september'
files = os.listdir(file_directory)

data = pd.DataFrame()
for file in files:
    if file.endswith('.xlsx'):
        filename = f'{file_directory}/{file}'
        data = data.append(pd.read_excel(filename), ignore_index=True)

data = data.sort_values(by = ['name', 'date'])
data = data.iloc[0:, 1:]

data.to_excel(f'{file_directory}/master-tweets-september.xlsx')
