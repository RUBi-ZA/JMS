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
```
sudo apt-get install -y mysql-server
```
You will be prompted to enter in a root password during installation. Remember this password as you will need it to connect to the MySQL server in the next step. 

Once MySQL server has installed, connect to the server and create a database and database user for the JMS:
```
mysql -u root -p
CREATE DATABASE jms
CREATE USER 'jms'@'localhost' IDENTIFIED BY 'password'
GRANT ALL PRIVILEGES ON jms . * TO 'jms'@'localhost';
``` 
### Setup NFS share

The JMS requires that an NFS is mounted on all nodes of the cluster that it manages (including the master node). This is so that each node in the cluster has access to the files required to run jobs. If you are installing the JMS on a single machine, this is obviously not necessary.

Setting up NFS may be different depending on the linux distribution you are using. On Ubuntu 14.04, the following process can be followed:

Set up one of the machines as the NFS server:
```
sudo apt-get install nfs-kernel-server
sudo mkdir -p /NFS/JMS
sudo chmod 777 /NFS/JMS -R
```

Add the following line to `/etc/exports` with the IP addresses of the nodes you want to mount the NFS on:
```
/NFS/JMS node1.ip.address(rw,fsid=0,insecure,no_subtree_check,async) node2.ip.address(rw,fsid=0,insecure,no_subtree_check,async)
```

Restart the NFS server:
```
sudo service nfs-kernel-server restart
```
  
On each client node, do the following:
```
sudo apt-get install nfs-common
sudo mkdir -p /NFS/JMS
sudo chmod 777 /NFS/JMS -R
```
  
Edit the /etc/fstab file on each client node to add the filesystem from the NFS server:
```
server.ip.address:/NFS/JMS	/NFS/JMS	nfs auto,noatime,nolock,bg,nfsvers=3,intr,tcp,actimeo=1800 0 0
```
  
Mount the NFS:
```
mount -a
```

### Setup the Django project

First of all, you will need to download the project from github. We recommend you download the project to the `/srv` directory so you will not need to change paths in the settings file later:
```
cd /srv
sudo mkdir JMS
sudo chown user:user JMS
git clone https://github.com/RUBi-ZA/JMS.git
```

Navigate to the project src directory and setup a virtual environment:
```
cd /srv/JMS/src
sudo apt-get install -y libmemcache-dev zlib1g-dev libssl-dev python-dev build-essential
virtualenv venv
pip install -r requirements.txt
```

Edit the `/srv/JMS/src/JMS/settings.py` file to include your database login details and the path to the NFS share:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'JMS',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'jms',
        'PASSWORD': 'password',
        'HOST': 'localhost', 
        'PORT': '',                      # Set to empty string for default.
    }
}


JMS_SETTINGS = {
    "JMS_shared_directory": "/NFS/JMS/"
}
```

### Run the server
```
cd /srv/JMS/src
source venv/bin/activate
python manage.py syncdb
python manage.py runserver
```
