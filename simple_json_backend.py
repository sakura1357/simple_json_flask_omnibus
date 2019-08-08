from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
import jaydebeapi
import jpype
import time
import datetime
import pytz

# Flask configuration
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
methods = ('GET', 'POST')


# 获取数据库连接
def get_conn():
    if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
        jpype.attachThreadToJVM()
        jpype.java.lang.Thread.currentThread().setContextClassLoader(jpype.java.lang.ClassLoader.getSystemClassLoader())
    conn = jaydebeapi.connect("com.sybase.jdbc3.jdbc.SybDriver",
                              "jdbc:sybase:Tds:127.0.0.1:4100?charset=cp936",
                              ["Username", "Password"],
                              "/opt/simple_json_flask_omnibus/jconn3d.jar")
    return conn


# 时间戳转换为本地时间
def timestamp_to_local(timestamp_int, local_format='%Y-%m-%d %H:%M:%S.%f'):
    # local_format "%Y-%m-%d %H:%M:%S"
    local_time = time.localtime(timestamp_int)
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
    return jsonify(['N_APPNAME:节点一', 'Severity:4'])


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    sql_customize = "select to_int(LastOccurrence)*1000,N_APPNAME,N_NODEIP,N_OBJ_NAME,N_SummaryCN,Severity " \
                    "from alerts.status " \
                    "where N_CURRENTSTATUS='NEW' "\
                    "and Severity in (4,5)"
    order_by = " order by Severity asc,LastOccurrence asc"
    sql_all = "select to_int(LastOccurrence)*1000,N_APPNAME,N_NODEIP,N_OBJ_NAME,N_SummaryCN,Severity " \
                        "from alerts.status " \
                        "where N_CURRENTSTATUS='NEW' " \
                        "and Severity in (4,5) order by Severity asc,LastOccurrence asc"
    sql_conditions = []
    # print(request.headers, request.get_json())
    req = request.get_json()

    timestamps_from = utc_to_local(req['range']['from'])
    timestamps_to = utc_to_local(req['range']['to'])
    time_condition = ' and LastOccurrence between \'' + str(timestamps_from) + '\' and \'' + str(timestamps_to) + '\' '

    if req['targets'][0].get('target', '') == 'all':
        sql_customize = sql_all
    else:
        for target in req['targets']:
            if ":" not in target.get('target', ''):
                abort(404, Exception("输入格式错误，参考样例: N_APPNAME:节点一, Severity:4"))
            # req_type = target.get('type', 'table')    # Grafana panel 请求类型需为 table，而不是 timeseries
            field, value = target['target'].split(':', 1)
            if field == 'Severity':
                sql_conditions.append(field + '=' + value + ' ')
            else:
                sql_conditions.append(field + '=\'' + value + '\'')
        # 拼接SQL语句
        for condition in sql_conditions:
            sql_customize = sql_customize + " and " + condition
        # sql_customize = sql_customize + time_condition + order_by     # 实际未使用时间查询条件
        sql_customize = sql_customize + order_by      

    print(sql_customize)
    
    query_results = []
    try:
        conn = get_conn()
        curs = conn.cursor()
        curs.execute(sql_customize)
        query_results = curs.fetchall()
    except Exception as e:
        print(e)
        abort(404, Exception("查询失败，请检查输入条件!"))
    finally:
        curs.close()
        conn.close()

    res = [
        {
            "columns": [
                {"text": "Time", "type": "time"},       # 返回第一列数据必须为Time字段，数据类型为time，实际数据为 timestamp 毫秒数*1000
                {"text": "所属节点", "type": "string"},
                {"text": "IP地址", "type": "string"},
                {"text": "主机名", "type": "string"},
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
    app.run(host='0.0.0.0', port=3003)
