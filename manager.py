from api_dialog import RequestWrap, TimeSlicer
from file_dialog import FileDialog
from dataprocessors import *
from config import request_config
class Manager:
    def __init__(self):
        self.FileDialog = FileDialog()
        self.RequestMaker = RequestWrap()
        self.TimeSlicer = TimeSlicer()
    def update_all_data(self):
        for day in self.TimeSlicer.time_slices_generator():
            hr =process_heart_rate(self.RequestMaker.request(request_config['heart_rate'], *day))
            steps = process_steps(self.RequestMaker.request(request_config['steps'], *day), *day)
            sleep = process_sleep_summary(self.RequestMaker.request(request_config['sleep_summary'], *day))
            self.FileDialog.write_to_db('heart_rate', hr)
            self.FileDialog.write_to_db('steps', steps)
            self.FileDialog.write_sleep_summary_to_db(sleep)

        print("Updated all data")
    def export_to_file(self, meas_type, start_date, end_date, file_name, file_format, separator = ';'):
        data = self.FileDialog.read_from_db(meas_type, start_date, end_date)
        if file_format == "csv":
            data.to_csv(file_name + '.csv', index=False, sep = separator)
        elif file_format == "xlsx":
            data.to_excel((file_name + '.xlsx'), index=False, sheet_name = meas_type)


