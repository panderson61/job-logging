FROM centos:7.2.1511

MAINTAINER Paul Anderson "panderson@avetta.com"

# Install needed packages
RUN yum -y install epel-release
RUN yum -y groupinstall "Development Tools"
RUN yum -y install git
RUN yum -y install python
RUN yum -y install python-pip python-dev python-devel build-essential
RUN yum -y install mysql-lib mysql-devel python-mysqldb
RUN pip install mysql-python
RUN yum -y update
RUN yum clean all

WORKDIR /opt/app
COPY files/requirements.txt /opt/app/requirements.txt
RUN pip install -r requirements.txt

COPY files/app.py /opt/app/app.py

EXPOSE 5000
CMD ["python", "/opt/app/app.py"]
