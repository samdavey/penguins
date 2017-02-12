# imports
import pandas as pd
import os
import numpy as np
import datetime
import time

# helper functions

def log(message):
    '''
    Prints message to the standard output with a formatted timestamp andflushes the buffer.
    '''
    print('{0} - {1}'.format(str(time.ctime()), message), flush=True)

    
def read_file_handler_start(file_path, file_description):
    '''
    Prints the user-friendly messages at the start of reading a data file to csv:
        '<timestamp> Loading the <file_description> data file.'
        '<timestamp> <file_description> file is <file size> MB.'
        '<timestamp> Loading into memory. Please be patient.'
    Variables:
        file_path: the location of the file to be read. Requires an os.path.normpath object.
        file_description: String description of what the file is / name of the file.
    '''
    log('Loading the {0} data file.'.format(file_description))

    file_size = os.path.getsize(file_path)
    log('{0} file is {1:.3f} MB.'.format(file_description, (file_size/1000000)))

    if file_size > 5000000: # over 5mb
        log('Loading into memory. Please be patient.')
    else:
        log('Loading into memory.')

        
def read_file_handler_end(file_path, file_description, df, df_var_name):
    '''
    Prints the user-friendly messages at the end of reading a data file to csv:
        '<timestamp> Success: loaded <number of records> records.'
        On fail: 
            '<timestamp> ### FAILED! ###'
            '<timestamp> <df_var_name> was not created. Exiting.'
            Exits the script.
    Variables:
        file_path: the location of the file to be read. Requires an os.path.normpath object.
        file_description: String description of what the file is / name of the file.
        df: a Pandas dataframe that should have resulted from the read_csv() call.
        df_var_name: the variable name for the dataframe as a string.
    '''
    if df is not None:
        log('Success: loaded {0:,} records.'.format(len(df)))
    else:
        log('### FAILED! ###')
        log('{0} was not created. Exiting.'.format(df_var_name))
        sys.exit(0)

        
def season(date):
    '''
    Returns the (Southern Hemisphere) season based on the month of a datetime object.
    '''
    if date.month >= 3 and date.month <= 5:
        return 'AUTUMN'
    elif date.month >= 6 and date.month <= 8:
        return 'WINTER'
    elif date.month >= 9 and date.month <= 11:
        return 'SPRING'
    elif (date.month >= 1 and date.month <= 2) or date.month == 12:
        return 'SUMMER'
    else:
        return None

    
def temp_bucket(temp_c):
    '''
    Returns buckets ever 10C from <0, 0-10, 10-20 .. to 100+.
    '''
    result = None
    if temp_c < 0:
        result = 'temp_<0'
    elif temp_c >= 100:
        result = 'temp_100+'
    else:
        floor = (temp_c // 10) * 10
        ceiling = floor + 10
        result = 'temp_{0:.0f}-{1:.0f}'.format(floor, ceiling)
    return result


def humidity_bucket(humidity):
    '''
    Returns buckets every 20% from 0 to 160+
    '''
    result = None
    if humidity < 20: # lung & eye irritation in humans
        result = 'RH%_<20'
    elif humidity >= 160: # dripping; probably underwater
        result = 'RH%_160+'
    else:
        floor = (humidity // 20) * 20
        ceiling = floor + 20
        result = 'RH%_{0:.0f}-{1:.0f}'.format(floor, ceiling)
    return result


def average_activity_phase(sensor_datetime):
    '''
    Returns the current phase of breeding based on per-nest observations. Phases are generally:
    1 Jan - 31 Mar: moulting
    1 Apr - 31 May: nest building
    1 Jun - 30 Jun: laying
    1 Jul - 7 Aug: incubating
    8 Aug - 30 Sep: rearing
    1 Oct - 30 Oct: fledging
    1 Nov - 31 Dec: post-fledging
    There can be two lays per season. The second lay is not considered in the average timeframes 
    above.
    '''
    if sensor_datetime is None:
        return None
    elif sensor_datetime.month >= 1 and sensor_datetime.month <= 3:
        return 'moulting'
    elif sensor_datetime.month >= 4 and sensor_datetime.month >= 5:
        return 'nest building'
    elif sensor_datetime.month == 6:
        return 'laying'
    elif sensor_datetime.month == 7:
        return 'incubating'
    elif sensor_datetime.month == 8 and date(sensor_datetime.year, sensor_datetime.month, sensor_datetime.day) <= date(sensor_datetime.year, 8, 7):
        return 'incubating'
    elif sensor_datetime.month == 8 and date(sensor_datetime.year, sensor_datetime.month, sensor_datetime.day) > date(sensor_datetime.year, 8, 7):
        return 'rearing'
    elif sensor_datetime.month >= 9:
        return 'rearing'
    elif sensor_datetime.month >= 10:
        return 'fledging'
    elif sensor_datetime.month in [11, 12]:
        return 'post-fledging'
    else:
        return 'unknown'