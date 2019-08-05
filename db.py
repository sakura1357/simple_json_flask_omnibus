# /bin/bash/python3
import jaydebeapi

conn = jaydebeapi.connect("com.sybase.jdbc3.jdbc.SybDriver",
                          "jdbc:sybase:Tds:10.1.77.238:4100?charset=cp936",
                          ["root", "netcool"],
                          "/opt/python-sybase/lib/jconn3d.jar", )
# 只查询四级和五级告警，显示按告警级别和最新发生时间排序
sql = "select N_APPNAME,LastOccurrence,Severity,N_SummaryCN,Summary,N_NODEIP,N_COMPONENTTYPE,N_OBJ_NAME " \
      "from alerts.status " \
      "where N_CURRENTSTATUS='NEW' " \
      "and Severity in (4,5) " \
      "order by Severity asc,LastOccurrence asc"
sql_customize = "select LastOccurrence,N_APPNAME,N_NODEIP,N_OBJ_NAME,N_SummaryCN,Summary,Severity " \
                "from alerts.status " \
                "where N_CURRENTSTATUS='NEW' LastOccurrence between 1479285300 and 1479285500" \
                "and Severity in (4,5) "
order_by = "order by Severity asc,LastOccurrence asc"
curs = conn.cursor()
curs.execute("select * from alerts.status where N_NODEIP='218.1.100.50'")
curs.fetchall()  # [["218.1.100.50","告警1"],["218.1.100.50","告警2"]]
curs.close()
