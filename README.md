JMS
===
The JMS is  workflow management system and web-based cluster front-end for the Torque resource manager. It provides an interface to Torque that allows users to submit and manage jobs as well as manage, configure and monitor the status of their cluster.

In addition to interfacing with Torque, the JMS provides a fully-functional workflow management system that allows users to create complex computational pipelines via and easy-to-use, web interface. Users can upload their scripts or interface with installed programs on their cluster, or both to build their workflows.

The JMS was originally developed for use in the field of bioinformatics. It is, however, applicable to any scientific field that requires computationally intensive analysis to be performed over a cluster. It can also be used to integrate workflows into 3rd party websites via it's RESTful web API.

The JMS is a Django project. We will welcome any and all help in developing it further.

Installation
---

### Setup a MySQL database

The JMS uses a MySQL database backend. If you haven't got MySQL server installed, install it as follows:

  `sudo apt-get install -y mysql-server`

You will be prompted to enter in a root password during installation. Remember this password as you will need it to connect to the MySQL server in the next step. 

Once MySQL server has installed, connect to the server and create a database and database user for the JMS:

  `mysql -u root -p`
  
  `CREATE DATABASE jms`
  
  `CREATE USER 'jms'@'localhost' IDENTIFIED BY 'password'`
  
  `GRANT ALL PRIVILEGES ON jms . * TO 'jms'@'localhost';`
  

### Setup the Django project

First of all, you will need to download the project from github. We recommend you download the project to the `/srv` directory so you will not need to change paths in the settings file later:

  `cd /srv`
  
  `sudo mkdir JMS`
  
  `sudo chown user:user JMS`

  `git clone https://github.com/RUBi-ZA/JMS.git`

Navigate to the project src directory and setup a virtual environment:

  `cd /srv/JMS/src`
  
  `sudo apt-get install -y libmemcache-dev zlib1g-dev libssl-dev python-dev build-essential`
  
  `virtualenv venv`

  `pip install -r requirements.txt`
