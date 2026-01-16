from datetime import datetime, timezone
import os
import sys
from manager import Manager
import sqlite3
from db_init import db_init
import json
manager = Manager()
try:
    with open('state.json', 'r') as f:
        data = json.load(f)
        db_init_flag = data['has_initialised']
    if not db_init_flag:
        db_init()
        with open('state.json', 'w') as fi:
            data['has_initialised'] = 1
            json.dump(data, fi)
except FileNotFoundError:
    raise RuntimeError("Cannot find the state.json file")
while True:
    print("1) Update all data\n2) Dashboard\n3) Export file\n4) Exit\n")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        try:
            manager.update_all_data()
            manager.TimeSlicer.lastupdateupdater()
        except RuntimeError as e:
            print("Error updating the data: ",e)
        except sqlite3.OperationalError as error:
            print(f"error writing to db, error: {error}")
    elif choice == 2:
        days_back = str(input("Enter number of days back: "))
        os.environ['DASHBOARD_DAYS_BACK'] = days_back
        os.system("streamlit run Streamlit/interface.py")
    elif choice == 3:
        while True:
            print("1) Heart Rate\n2) Step counts\n3) Sleep Summaries")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                meas_type = "heart_rate"
                break
            elif choice == 2:
                meas_type = "steps"
                break
            elif choice == 3:
                meas_type = "sleep_summary"
                break
            else:
                print("Please enter a valid choice")
        date_input = input("Enter start date (YYYY-MM-DD): ")
        start_date = datetime.strptime(date_input, "%Y-%m-%d").replace(tzinfo = timezone.utc).timestamp()
        date_input = input("Enter end date (YYYY-MM-DD): ")
        end_date = datetime.strptime(date_input, "%Y-%m-%d").replace(tzinfo = timezone.utc).timestamp()
        while True:
            print("1) .xlxs\n2) .csv\n")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                file_format = "xlsx"
                break
            elif choice == 2:
                file_format = "csv"
                break
            else:
                print("Please enter a valid choice")
        separator = ';'
        file_name = str(input("Enter file name: "))
        manager.export_to_file(start_date = start_date, end_date = end_date, meas_type = meas_type, file_format = file_format, file_name = file_name, separator = separator)
    elif choice == 4:
        sys.exit()
    else:
        print("Please enter a valid choice")

