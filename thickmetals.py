import pandas as pd
import numpy as np
import xlsxwriter

# Specify your file paths
first_sheet_path = 'path/to/first_sheet.xlsx'  # Replace with the path to your first Excel file
second_sheet_path = 'path/to/second_sheet.xlsx'  # Replace with the path to your second Excel file

# Read the Excel files using pandas
first_df = pd.read_excel(first_sheet_path, sheet_name='Sheet1')
second_df = pd.read_excel(second_sheet_path, sheet_name='Sheet2')

# Get the list of items from the second sheet
items_to_match = set(second_df.iloc[:, 0].dropna().astype(str))

# Specify the column to check in the first sheet
column_to_check = 'B'

# Create a new Excel file to save the modified data
output_path = 'modified_first_sheet.xlsx'
writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
workbook = writer.book
worksheet = workbook.add_worksheet('Sheet1')
red_format = workbook.add_format({'font_color': 'red'})

# Write headers
for col_num, header in enumerate(first_df.columns):
    worksheet.write(0, col_num, header)

# Function to safely write cell values, converting NaN and INF to None
def safe_write(worksheet, row, col, value):
    if pd.isna(value) or np.isinf(value):
        worksheet.write(row, col, None)
    else:
        worksheet.write(row, col, value)

# Write data with conditional formatting
for row_num, (index, row) in enumerate(first_df.iterrows(), start=1):
    for col_num, cell_value in enumerate(row):
        # Check if the current column is the specified column
        if first_df.columns[col_num] == column_to_check:
            if isinstance(cell_value, str) and cell_value.startswith('{') and cell_value.endswith('}'):
                items = cell_value.strip('{}').split(', ')
                new_items = []
                for item in items:
                    clean_item = item.strip("'")
                    if clean_item in items_to_match:
                        # Append the matched item with red format
                        new_items.append(red_format)
                        new_items.append(f"'{clean_item}'")
                        new_items.append(', ')
                    else:
                        new_items.append(f"'{clean_item}'")
                        new_items.append(', ')
                # Remove the last comma and space
                if new_items:
                    new_items.pop()
                # Write the cell with formatted items
                worksheet.write_rich_string(row_num, col_num, *new_items)
            else:
                safe_write(worksheet, row_num, col_num, cell_value)
        else:
            # Write other columns without modification
            safe_write(worksheet, row_num, col_num, cell_value)

# Save the modified workbook
writer.save()

