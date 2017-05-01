from flask import Flask
from flask import g
from flask import Response
from flask import request
from flask import jsonify
import json
import MySQLdb

app = Flask(__name__)

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

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/job-logging/v1/health", methods=['GET'])
def health():
  d = dict()
  result = query_db("SELECT True")
  d = result[0]
  if 1 == d.get("TRUE"):
    resp = Response('{"status":"Ok"}', status=200, mimetype='application/json')
  else:
    resp = Response('{"status":"Bad"}', status=200, mimetype='application/json')
  return resp

@app.route("/names", methods=['GET'])
def names():
  result = query_db("SELECT firstname,lastname FROM test.name")
  data = json.dumps(result)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/crons", methods=['GET'])
def crons():
  result = query_db("SELECT * FROM pics_live.contractor_cron_log LIMIT 10")
  data = json.dumps(result)
  resp = Response(data, status=200, mimetype='application/json')
  return resp

@app.route("/fake", methods=['GET'])
def fake():
  b = []
  a = ["115730", "2017-04-14 00:00:00", "3", "1", "http://fake-tomcat-2:8080/ContractorCronAjax.action?conID=115730&steps=All&button=Run"]
  b.append(a)
  a = ["125919", "2017-04-14 00:00:01", "3", "1", "http://fake-tomcat-3:8080/ContractorCronAjax.action?conID=125919&steps=All&button=Run"]
  b.append(a)
  a = ["100373", "2017-04-14 00:00:02", "3", "1", "http://fake-tomcat-6:8080/ContractorCronAjax.action?conID=100373&steps=All&button=Run"]
  b.append(a)
  a = ["56285", "2017-04-14 00:00:03", "4",  "1", "http://fake-tomcat-1:8080/ContractorCronAjax.action?conID=56285&steps=All&button=Run"]
  b.append(a)

  g.cursor.execute("INSERT INTO pics_live.contractor_cron_log (ConID, startDate, runTime, success, server) VALUES (%s,%s,%s,%s,%s)", (a[0], a[1], a[2], a[3], a[4]))
  g.conn.commit()
  resp = Response("Updated", status=201, mimetype='application/json')
  return resp

@app.route("/add", methods=['POST'])
def add():
  req_json = request.get_json()
  g.cursor.execute("INSERT INTO test.name (firstname, lastname) VALUES (%s,%s)", (req_json['firstname'], req_json['lastname']))
  g.conn.commit()
  resp = Response("Updated", status=201, mimetype='application/json')
  return resp

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
