JMS
===
The JMS is  workflow management system and web-based cluster front-end for the Torque resource manager. It provides an interface to Torque that allows users to submit and manage jobs as well as manage, configure and monitor the status of their cluster.

In addition to interfacing with Torque, the JMS provides a fully-functional workflow management system that allows users to create complex computational pipelines via and easy-to-use, web interface. Users can upload their scripts or interface with installed programs on their cluster, or both to build their workflows.

The JMS was originally developed for use in the field of bioinformatics. It is, however, applicable to any scientific field that requires computationally intensive analysis to be performed over a cluster. It can also be used to integrate workflows into 3rd party websites via it's RESTful web API.

The JMS is a Django project. We will welcome any and all help in developing it further.

Installation
---
*Note: The following instructions are for Ubuntu 14.04, but can be used as a guideline for other Linux flavours.*

### Prerequisites
- [MySQL server](https://github.com/RUBi-ZA/JMS/wiki/Set-up-NFS)
- [NFS (or similar) mounted on all nodes of the cluster](https://github.com/RUBi-ZA/JMS/wiki/Set-up-a-database-for-the-JMS)
- [Torque Resource Manager](https://github.com/RUBi-ZA/JMS/wiki/Set-up-Torque)

### Setup the JMS

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

Edit the `/srv/JMS/src/JMS/settings.py` file to include your database login details and the path to the NFS share:

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
    "JMS_shared_directory": "/NFS/JMS/"
}
```

### Create and populate the database tables
``` bash
cd /srv/JMS/src
source venv/bin/activate
python manage.py syncdb
python manage.py populate_db
```

### Start the queue daemon
```
python manage.py queue_daemon --start
```

### Test the JMS
```
python manage.py runserver
```
