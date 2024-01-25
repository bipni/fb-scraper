import os
import sys
import traceback


def error_handler(error):
    _, exc_obj, exc_tb = sys.exc_info()
    exc_info = sys.exc_info()
    specific_error = traceback.format_exception(*exc_info)[len(traceback.format_exception(*exc_info)) - 2]

    filepath = os.path.abspath(exc_tb.tb_frame.f_code.co_filename)
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    line = exc_tb.tb_lineno

    parts = specific_error.split(', ')
    error_filepath = parts[0].split('"')[1]
    error_filename = error_filepath.split("/")[-1]
    error_line = parts[1].split(' ')[1]

    error_details = [
        f'Exception Name: {type(error).__name__}',
        f'Exception Message: {str(exc_obj)}',
        f'Exception File Path: {filepath}',
        f'Exception File Name: {filename}',
        f'Exception File Line Number: {str(line)}',
        f'Error File Path: {error_filepath}',
        f'Error File Name: {error_filename}',
        f'Error File Line Number: {error_line}'
    ]

    return '\n'.join(error_details)
