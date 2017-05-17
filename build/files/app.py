from flask import Flask
from flask import g
from flask import Response
from flask import request
from flask import jsonify
import json
import MySQLdb
import datetime

app = Flask(__name__)

'''Create an encoder subclassing JSON.encoder. 
Make this encoder aware of our classes (e.g. datetime.datetime objects) 
'''
class Encoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.isoformat()
    else:
      return json.JSONEncoder.default(self, obj)

@app.before_request
def db_connect():
  g.conn = MySQLdb.connect(host='172.17.0.3',
                              user='test',
                              passwd='password',
                              db='test')
  g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
  g.cursor.close()
  g.conn.close()
  return response

def query_db(query, args=(), one=False):
  g.cursor.execute(query, args)
  rv = [dict((g.cursor.description[idx][0], value)
  for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
  return (rv[0] if rv else None) if one else rv

@app.route("/hello")
def hello():
  result = "Hello World!"
  data = json.dumps(result)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/reqint", methods=['GET', 'POST'])
def reqint():
  reqint = int(request.args.get("reqint"))
  if reqint == 0:
    resp = Response("Parameter out of range zero {}".format(reqint), status=416)
    return resp
  if reqint <= 0:
    resp = Response("Parameter out of range low {}".format(reqint), status=416)
    return resp
  if reqint > (24*60*60):
    resp = Response("Parameter out of range high {}".format(reqint), status=416)
    return resp
  data = json.dumps(reqint)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/job-logging/v1/health", methods=['GET'])
def health():
  sql = "SELECT True"
  result = query_db(sql)
  d = dict()
  d = result[0]
  if 1 == d.get("TRUE"):
    resp = Response('{"status":"Ok"}', status=200, mimetype='application/json')
  else:
    resp = Response('{"status":"Bad"}', status=200, mimetype='application/json')
  return resp

@app.route("/crons", methods=['GET'])
def crons():
  sql = "SELECT * FROM pics_live.contractor_cron_log ORDER BY startDate DESC LIMIT 10"
  result = query_db(sql);
  data = json.dumps(result, cls=Encoder)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/count", methods=['GET', 'POST'])
def count():
  age = request.args.get("age")
  if age > 24*60*60:
    resp = Response("Parameter out of range", status=416)
    return resp
  sql = "SELECT count(*) AS Count FROM pics_live.contractor_cron_log WHERE startDate >= DATE_SUB(NOW(), INTERVAL {} SECOND)".format(age)
  result = query_db(sql);
  data = json.dumps(result)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/fake", methods=['GET'])
def fake():
  rows = []
  timenow = datetime.datetime.now()
  timedelta = datetime.timedelta(seconds=1)
  a = ["115730", timenow, "3", "1", "http://fake-tomcat-2:8080/ContractorCronAjax.action?conID=115730&steps=All&button=Run"]
  rows.append(a)
  a = ["125919", timenow-timedelta, "3", "1", "http://fake-tomcat-3:8080/ContractorCronAjax.action?conID=125919&steps=All&button=Run"]
  rows.append(a)
  a = ["100373", timenow-(2*timedelta), "3", "1", "http://fake-tomcat-6:8080/ContractorCronAjax.action?conID=100373&steps=All&button=Run"]
  rows.append(a)
  a = ["56285", timenow-(3*timedelta), "4",  "1", "http://fake-tomcat-1:8080/ContractorCronAjax.action?conID=56285&steps=All&button=Run"]
  rows.append(a)
  sql = "INSERT INTO pics_live.contractor_cron_log (ConID, startDate, runTime, success, server) VALUES (%s,%s,%s,%s,%s)"

  g.cursor.executemany(sql, rows)
  g.conn.commit()
  resp = Response("Updated", status=201, mimetype='application/json')
  return resp

@app.route('/messages', methods = ['POST'])
def api_message():

  if request.headers['Content-Type'] == 'text/plain':
    return "Text Message: " + request.data

  elif request.headers['Content-Type'] == 'application/json':
    return "JSON Message: " + json.dumps(request.json)

  elif request.headers['Content-Type'] == 'application/octet-stream':
    f = open('./binary', 'wb')
    f.write(request.data)
    f.close()
    return "Binary message written!"

  return "415 Unsupported Media Type ;)"

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
