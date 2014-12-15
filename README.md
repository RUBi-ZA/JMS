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
    "JMS_shared_directory": "/NFS/JMS/"
}
```

### 2. Create and populate the database tables

With the settings.py file set up with your database details, you can now create and populate the JMS database tables:
``` bash
cd /srv/JMS/src
source venv/bin/activate
python manage.py syncdb
python manage.py populate_db
```

### 3. Start the queue daemon

The queue daemon is responsible for updating the JMS job history with details from Torque. If you don't start the queue_daemon, your job history will only be updated when a job starts or finishes i.e. no changes in state will be tracked during the job. To start the queue daemon, run the following command:
```
python manage.py queue_daemon --start
```

To restart or stop the queue daemon, run the following commands respectively:
```
python manage.py queue_daemon --restart
python manage.py queue_daemon --stop
```

### 4. Set up the prologue and epilogue scripts

**NB: The following must be done corectly or the JMS will not function properly**

The JMS prologue and epilogue scripts can be located in the `bin` directory in the root of the project (e.g. `/srv/JMS/bin`). These scripts are used to update the state of jobs in the job history and should be copied to the mom\_priv directory of your Torque setup on each and every slave node of the cluster. By default, this directory is located at `/var/spool/torque/mom_priv` on the cluster node.

You will need root privileges to copy the scripts to the `mom_priv` directory. If you can log into your nodes with the root user, you can use the following commands to copy the scripts across:
```
scp /srv/bin/prologue root@node.ip.address:/var/spool/torque/mom_priv/
scp /srv/bin/epilogue root@node.ip.address:/var/spool/torque/mom_priv/
```
See '[Set up Torque nodes]()' for more details.

### Test the JMS

To test that your installation is working, run the Django development web server:
```
python manage.py runserver
```
You should now be able to browse to the JMS at http://127.0.0.1:8000

For improved performance, [host the JMS with Apache](https://github.com/RUBi-ZA/JMS/wiki/Host-with-Apache) or some other production web server.
