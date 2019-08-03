from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
import jaydebeapi
import time
import datetime
import pytz

# Flask configuration
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
methods = ('GET', 'POST')

# request metric configuration
# metric_finders = {}
# metric_readers = {}
# annotation_readers = {}
# panel_readers = {}
sql_conditions = []


# 获取数据库连接
def get_cursor():
    conn = jaydebeapi.connect("com.sybase.jdbc3.jdbc.SybDriver",
                              "jdbc:sybase:Tds:10.1.77.238:4100?charset=cp936",
                              ["root", "netcool"],
                              "/opt/python-sybase/lib/jconn3d.jar", )
    return conn.cursor()


# 时间戳转换为本地时间
def timestamp_to_local(timestamp_int, local_format='%Y-%m-%d %H:%M:%S.%f'):
    # local_format "%Y-%m-%d %H:%M:%S"
    local_time = time.localtime(timestamp_int)
    # ltime = time.localtime(1479285300)
    return time.strftime(local_format, local_time)


# UTC时间转换为时间戳 2019-08-02T02:34:32.370Z
def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    # 时区: pytz.country_timezones('cn')
    local_tz = pytz.timezone('Asia/Shanghai')
    # 格式: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    local_format = "%Y-%m-%d %H:%M:%S.%f"
    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)  # UTC时间转本地时间
    return int(time.mktime(time.strptime(time_str, local_format)))


# 本地时间转换为UTC
def local_to_utc(local_ts, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M:%S.%f"
    time_str = time.strftime(local_format, time.localtime(local_ts))
    dt = datetime.datetime.strptime(time_str, local_format)
    local_dt = local_tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime(utc_format)


@app.route('/', methods=methods)
@cross_origin()
def hello_world():
    # print(request.headers, request.get_json())
    return 'python omnibus grafana datasource'


@app.route('/search', methods=methods)
@cross_origin()
def find_metrics():
    # print(request.headers, request.get_json())
    # 返回输入样例
    return jsonify(['N_APPNAME:节点一', 'N_NODEIP：218.1.101.50', 'N_OBJ_NAME:SHGGT-JYSBPBAK'])


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    sql_customize = "select LastOccurrence,N_APPNAME,N_NODEIP,N_OBJ_NAME,N_SummaryCN,Summary,Severity " \
                    "from alerts.status " \
                    "where N_CURRENTSTATUS='NEW'" \
                    "and Severity in (4,5) "
    order_by = " order by Severity asc,LastOccurrence asc"

    print(request.headers, request.get_json())
    req = request.get_json()

    timestamps_from = utc_to_local(req['range']['from'])
    timestamps_to = utc_to_local(req['range']['to'])

    for target in req['targets']:
        if ":" not in target.get('target', ''):
            abort(404, Exception("输入格式错误，参考样例:"
                                 "'N_APPNAME:节点一', "
                                 "'N_NODEIP：218.1.101.50', "
                                 "'N_OBJ_NAME:SHGGT-JYSBPBAK'"))
        # req_type = target.get('type', 'table')    # 默认请求类型为table

        field, value = target['target'].split(':', 1)
        sql_conditions.append(field + '= \'' + value + '\'')

    # 拼接SQL语句
    for condition in sql_conditions:
        sql_customize = sql_customize + " and " + condition
    sql_customize = sql_customize + order_by        # 没有添加时间范围条件: timestamp_from, timestamp_to

    try:
        curs = get_cursor()
        # print(sql_customize)
        curs.execute(sql_customize)
        query_results = curs.fetchall()  # 没有验证返回 LastOccurrence 的时间格式
    except Exception as e:
        print(e)
        abort(404, Exception("查询失败，请检查输入条件!"))
    finally:
        curs.close()

    res = [
        {
            "columns": [
                {"text": "最后发生时间", "type": "time"},
                {"text": "所属节点", "type": "string"},
                {"text": "IP地址", "type": "string"},
                {"text": "主机名", "type": "string"},
                {"text": "告警内容", "type": "string"},
                {"text": "告警内容", "type": "string"},
                {"text": "级别", "type": "number"}
            ],
            "rows": query_results,
            "type": "table"
        }
    ]

    return jsonify(res)


@app.route('/annotations', methods=methods)
@cross_origin(max_age=600)
def query_annotations():
    print(request.headers, request.get_json())
    req = request.get_json()
    results = []
    pass

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003, debug=True)
