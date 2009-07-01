import re, time, calendar

############################### SEQUENCES ###############################
def get_sequence():
    i = 0
    while True:
        i = i + 1
        yield i
                            

################################### TIME ##################################
#@memoized
def get_end_of_day(year, month_id, day):
    end_time = (year, month_id, day, 23, 59, 59, 0, 0, -1)
    end_time_epoch = time.mktime(end_time)+1.0
    return end_time_epoch


#@memoized
def print_date(t):
    return time.asctime(time.localtime(t))


#@memoized
def get_day(t):
    return t - get_sec_from_morning(t)


#@memoized
def get_sec_from_morning(t):
    t_lt = time.localtime(t)
    h = t_lt.tm_hour
    m = t_lt.tm_min
    s = t_lt.tm_sec
    return h * 3600 + m * 60 + s


#@memoized
def get_start_of_day(year, month_id, day):
    start_time = (year, month_id, day, 00, 00, 00, 0, 0, -1)
    start_time_epoch = time.mktime(start_time)
    return start_time_epoch

################################# Pythonization ###########################

def to_int(val):
    return int(val)

def to_char(val):
    return val[0]

def to_split(val):
    val = val.split(',')
    if val == ['']:
        val = []
    return val

def to_bool(val):
    return bool(val)
