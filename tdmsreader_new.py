from nptdms import TdmsFile
import pandas as pd
import os

# Read the TDMS file
#join with current path
#file_path = os.path.join(os.getcwd(), "1_1.tdms")
file_path = r"C:\Users\U436445\Downloads\NDB_With load motor\35deg\500.tdms"
tdms_file = TdmsFile.read(file_path)

# Convert TDMS data to a dictionary of DataFrames
data = {group.name: group.as_dataframe() for group in tdms_file.groups()}

# Display the data as an organized DataFrame
for group_name, df in data.items():
    print(f"Group: {group_name}")
    print(df.columns)
    print(df)
    if 'HST_Case-flow_LPM ' in df.columns:
        print(f"Information about 'X' column in DataFrame: {df['HST_Case-flow_LPM '].describe()}")
    
#/'Data'/'Time'	/'Data'/'Inlet_temp'
