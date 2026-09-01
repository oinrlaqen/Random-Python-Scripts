'''

This script converts raw unstructured file with financial data into a regular CSV

Logic: 

1. Create column headers. Column width is the width in characters for each header from the column_name list 
2. Filter out data which should not be imported into the system
3. Create new columns and populate them with financial amounts from the columns 'AMOUNT' and 'FAMILY TOTAL' using mapper
4. Group duplicated rows into a single row

'''



import pandas as pd
import glob

column_name = [
    "MEMBER_SSN",
    "PERSON_CODE",
    "DATE_OF_BIRTH",
    "LAST_NAME",
    "FIRST_NAME",
    "GENDER",
    "RELATION",
    "PLAN_CODE",
    "ACCUMULATOR_NAME",
    "ACCUMULATOR_DESCRIPTION",
    "UNITS_MEASURE",
    "CONTROL_DATE",
    "UNITS",
    "AMOUNT",
    "ALTERNATE_ID",
    "CLIENT CODE",
    "Blank",
    "FAMILY TOTAL",
]

column_width = [
    (0, 9),
    (9, 11),
    (11, 19),
    (19, 69),
    (69, 99),
    (99, 100),
    (100, 101),
    (101, 109),
    (109, 129),
    (129, 159),
    (159, 160),
    (160, 168),
    (168, 174),
    (174, 184),
    (184, 199),
    (199, 204),
    (204, 205),
    (205, 215),
]

import_link = glob.glob("./*FILENAME*.txt")[0]
export_link = import_link.replace("txt", "csv")

file = pd.read_fwf(import_link, colspecs=column_width, names=column_name)

file = file.astype(object)

file = file[
    (file['ACCUMULATOR_NAME'] != 'RXOP') & 
    (file['CONTROL_DATE'] == 20260101)
]

file[['In Network out of pocket YTD amount individual', 
    'In Network out of pocket YTD amount family',
    'In Network deductible YTD amount individual',
    'In Network deductible YTD amount family',
    'Out of network out of pocket YTD amount individual',
    'Out of network out of pocket YTD amount family',
    'Out of network deductible YTD amount individual',
    'Out of network deductible YTD amount family']] = None

accumulator_mapping = {
    'MIOP': 'In Network out of pocket YTD amount',
    'DEDI': 'In Network deductible YTD amount',
    'MOOP': 'Out of network out of pocket YTD amount',
    'DEDU': 'Out of network deductible YTD amount',
}

for accumulator, column_prefix in accumulator_mapping.items():
    mask = file['ACCUMULATOR_NAME'].eq(accumulator)

    file[f'{column_prefix} individual'] = file['AMOUNT'].where(mask, 0)
    file[f'{column_prefix} family'] = file['FAMILY TOTAL'].where(mask, 0)

file.drop(columns=[
    'ACCUMULATOR_NAME', 
    'ACCUMULATOR_DESCRIPTION',
    'UNITS',
    'AMOUNT',
    'Blank',
    'FAMILY TOTAL'
    ], inplace=True)

grouping_columns = [
    col for col in file.columns
    if not any(string in col for string in accumulator_mapping.values())
]

file = file.groupby(grouping_columns, as_index=False).sum()

file.to_csv(export_link, index=False)
