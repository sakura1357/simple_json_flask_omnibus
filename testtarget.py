import time, datetime, pytz


# UTC时间转换为时间戳 2016-07-31T16:00:00Z 2019-08-02T02:34:32.370Z
def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    # pytz.country_timezones('cn')
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M:%S.%f"
    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return time_str, int(time.mktime(time.strptime(time_str, local_format)))


if __name__ == '__main__':
    print(utc_to_local("2019-08-02T02:34:32.370Z"))