# Let's try this...
FROM ubuntu:16.04
MAINTAINER Dane Kennedy <dkennedy1@csir.co.za>
RUN apt update && apt install -y \
    libmemcached-dev \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    nginx \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-9.5 \
    python3-dev \
    python3-pip \
    python3-software-properties \
    software-properties-common \
    wget

#RUN add-apt-repository ppa:git-core/ppa

#RUN apt update && apt install -y git

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN pip3 install --upgrade pip
run pip install virtualenv

RUN useradd --create-home --shell /bin/bash jms

USER jms
WORKDIR /home/jms

RUN virtualenv -p python3 JMS_env

RUN wget --quiet https://raw.githubusercontent.com/RUBi-ZA/JMS/dane/dockerfile/src/requirements.txt

RUN source /home/jms/JMS_env/bin/activate \
  && pip install -r requirements.txt


