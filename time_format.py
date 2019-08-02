#!/usr/bin/env python
# _*_coding:utf-8_*_

# 本地时间 转换 为时间戳
import time
import pytz
import datetime

dateC1 = datetime.datetime(2015, 11, 30, 15, 55, 00)
timestamp2 = time.mktime(dateC1.timetuple())
print(timestamp2)

# 时间戳转换为本地时间
import datetime
import time

ltime = time.localtime(1470009000)
ltime = time.localtime(1479285300)
timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
print(timeStr)


# UTCS时间转换为时间戳 2016-07-31T16:00:00Z
def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    local_tz = pytz.timezone('Asia/Chongqing')
    local_format = "%Y-%m-%d %H:%M"
    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return int(time.mktime(time.strptime(time_str, local_format)))


# 本地时间转换为UTC
def local_to_utc(local_ts, utc_format='%Y-%m-%dT%H:%MZ'):
    local_tz = pytz.timezone('Asia/Chongqing')
    local_format = "%Y-%m-%d %H:%M"
    time_str = time.strftime(local_format, time.localtime(local_ts))
    dt = datetime.datetime.strptime(time_str, local_format)
    local_dt = local_tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime(utc_format)


# t = u"2016-07-31T16:00:00Z"
t = u"2015-07-31T15:55:00Z"
# t = u"2015-11-30T15:55:00Z"
t1 = u"2015-12-31T15:55:00Z"  # 1470441600   1470095400  1470613800
ret = utc_to_local(t)
ret1 = utc_to_local(t1)
print
ret, ret1  # 1469923200     1470009600