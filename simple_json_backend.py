from flask import Flask, request, jsonify, json, abort
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
# 节点名称、IP地址、主机名、告警级别 "N_APPNAME", "N_NODEIP", "N_OBJ_NAME", "Severity"
metric_finders = {}
metric_readers = {}
annotation_readers = {}
panel_readers = {}

# SQL configuration
# 只查询四级和五级告警，显示按告警级别和最新发生时间排序
SQL_ALL = "select N_APPNAME,LastOccurrence,Severity,N_SummaryCN,Summary,N_NODEIP,N_COMPONENTTYPE,N_OBJ_NAME " \
          "from alerts.status " \
          "where N_CURRENTSTATUS='NEW' " \
          "and Severity in (4,5) " \
          "order by Severity asc,LastOccurrence asc"
SQL_customize = "select N_APPNAME,LastOccurrence,Severity,N_SummaryCN,Summary,N_NODEIP,N_COMPONENTTYPE,N_OBJ_NAME " \
                "from alerts.status " \
                "where N_CURRENTSTATUS='NEW' " \
                "and Severity in (4,5) " \
                "order by Severity asc,LastOccurrence asc"


# 获取数据库连接
def get_cursor():
    conn = jaydebeapi.connect("com.sybase.jdbc3.jdbc.SybDriver",
                              "jdbc:sybase:Tds:10.1.77.238:4100?charset=cp936",
                              ["root", "netcool"],
                              "/opt/python-sybase/lib/jconn3d.jar", )
    return conn.cursor()
    # curs.execute("select * from alerts.status where N_NODEIP='218.1.100.50'")
    # curs.fetchall()  # [["218.1.100.50","告警1"],["218.1.100.50","告警2"]]
    # curs.close()


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
    print(request.headers, request.get_json())
    # 返回输入样例
    return jsonify(['N_APPNAME:节点一', 'N_NODEIP：218.1.101.50', 'N_OBJ_NAME:SHGGT-JYSBPBAK', 'Severity:4'])


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    print(request.headers, request.get_json())
    req = request.get_json()

    results = []
    res = [
        {
            "columns": [
                {"text": "Time", "type": "time"},
                {"text": "Country", "type": "string"},
                {"text": "Number", "type": "number"}
            ],
            "rows": [
                [1234567, "SE", 123],
                [1234567, "DE", 231],
                [1234567, "US", 321]
            ],
            "type": "table"
        }
    ]

    time_range_from = req['range']['from']
    time_range_to = req['range']['to']
    print(time_range_from)
    # 2019-08-02T02:34:32.370Z
    # if 'intervalMs' in req:
    #     freq = str(req.get('intervalMs')) + 'ms'
    # else:
    #     freq = None
    #
    # for target in req['targets']:
    #     if ':' not in target.get('target', ''):
    #         abort(404, Exception('Target must be of type: <finder>:<metric_query>, got instead: ' + target['target']))
    #
    #     req_type = target.get('type', 'table')
    #
    #     finder, target = target['target'].split(':', 1)
    #     query_results = metric_readers[finder](target, ts_range)
    #
    #     if req_type == 'table':
    #         results.extend(dataframe_to_json_table(target, query_results))
    #     else:
    #         results.extend(dataframe_to_response(target, query_results, freq=freq))

    # return jsonify(results)
    pass
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
