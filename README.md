JMS
===
JMS is a workflow management system and web-based cluster front-end for High Performance Computing (HPC) environments. It provides an interface to Torque (or similar resource managers) that allows users to submit and manage jobs as well as manage, configure and monitor the status of their cluster.

In addition to interfacing with a resource manager, JMS provides a fully-functional workflow management system that allows users to create complex computational pipelines via an easy-to-use, web interface. Users can upload their scripts, interface with installed programs on their cluster, or both, to build their workflows.

JMS was originally developed for use in the field of bioinformatics. It is, however, applicable to any scientific field that requires computationally intensive analysis to be performed over a cluster. It can also be used to integrate workflows into 3rd party websites via it's RESTful web API. JMS is is also a useful tool for system administrators who simply want to monitor and manage their cluster.

JMS is a Django project. We will welcome any and all help in developing it further.

JMS has been published [here](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0134273).

Installation
---
*Note: The following instructions are for Ubuntu 14.04, but can be used as a guideline for other Linux flavours.*

### Prerequisites
- [MySQL server](https://github.com/RUBi-ZA/JMS/wiki/Set-up-a-database-for-the-JMS)
- [NFS (or similar) mounted on all nodes of the cluster](https://github.com/RUBi-ZA/JMS/wiki/Set-up-NFS)
- [Torque Resource Manager](https://github.com/RUBi-ZA/JMS/wiki/Set-up-Torque)

### 1. Download and setup the JMS project

First of all, you will need to download the project from github. We recommend you download the project to the `/srv` directory so you will not need to change paths in the settings file later:
``` bash
cd /srv
sudo mkdir JMS
sudo chown user:user JMS
git clone https://github.com/RUBi-ZA/JMS.git
sudo chown user:user JMS -R
```

Navigate to the project src directory and setup a virtual environment:
``` bash
cd /srv/JMS/src
sudo apt-get install -y libmemcache-dev zlib1g-dev libssl-dev python-dev build-essential
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Edit the `/srv/JMS/src/JMS/settings.py` file to include your database login credentials (you should have set these when [creating your database](https://github.com/RUBi-ZA/JMS/wiki/Set-up-a-database-for-the-JMS)) and the path to the [NFS share](https://github.com/RUBi-ZA/JMS/wiki/Set-up-NFS):

``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'JMS',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost', 
        'PORT': '',                      # Set to empty string for default.
    }
}


JMS_SETTINGS = {
    "JMS_shared_directory": "/NFS/JMS/",
    "resource_manager": {
        "name": "torque",
        "log_file": os.path.join(BASE, "logs/torque.log")
    }
}

IMPERSONATOR_SETTINGS = {
    "key": os.path.join(BASE_DIR, "impersonator/pub.key"),
    "url": "127.0.0.1:8124"
}

```

With the settings.py file set up with your database details and the path to your shared directory, run the following commands:
``` bash
cd /srv/JMS/src
source venv/bin/activate
python manage.py syncdb
python manage.py setup
```

### 2. Start the queue daemon

The queue daemon is responsible for updating the JMS job history with details from the resource manager. If you don't start the queue_daemon, your job history will not be updated after the a job has been submitted i.e. no changes in state will be tracked during the job. To start the queue daemon, run the following command:
```
sudo venv/bin/python manage.py queue_daemon start
```

To restart or stop the queue daemon, run the following commands respectively:
```
sudo venv/bin/python manage.py queue_daemon restart
sudo venv/bin/python manage.py queue_daemon stop
```

### 3. Start the impersonator server

The impersonator allows JMS to submit jobs as you. It is also used for a number of other reasons. If you are unable to login, chances are the impersonator is not running. To start it, run the following commands:
```
cd impersonator
sudo su
nohup python server.py 8124 &
```

You can set which port JMS communicates with the impersonator on in the settings.py file:

```
IMPERSONATOR_SETTINGS = {
    "key": os.path.join(BASE_DIR, "impersonator/pub.key"),
    "url": "127.0.0.1:8124"
}
```

### 4. Test the JMS

To test that your installation is working, run the Django development web server:
```
python manage.py runserver ip.address:8000
```

For improved performance, [host the JMS with Apache](https://github.com/RUBi-ZA/JMS/wiki/Hosting-with-Apache) or some other production web server.
