# job-logging

docker build -t job-logging build/.

docker run -d --name job-logging -p 5000:5000 job-logging:latest

curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/messages \
-d '{"ConID":"115730", "startDate":"20170515", "runTime":"3", "success":"1", "server":"http://fake-tomcat-2:8080/ContractorCronAjax.action?conID=115730&steps=All&button=Run"}'
