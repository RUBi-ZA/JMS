JMS
===
The JMS is  workflow management system and web-based cluster front-end for the Torque resource manager. It provides an interface to Torque that allows users to submit and manage jobs as well as manage, configure and monitor the status of their cluster.

In addition to interfacing with Torque, the JMS provides a fully-functional workflow management system that allows users to create complex computational pipelines via and easy-to-use, web interface. Users can upload their scripts or interface with installed programs on their cluster, or both to build their workflows.

The JMS was originally developed for use in the field of bioinformatics. It is, however, applicable to any scientific field that requires computationally intensive analysis to be performed over a cluster. It can also be used to integrate workflows into 3rd party websites via it's RESTful web API.

The JMS is a Django project. We will welcome any and all help in developing it further.

Installation
---
First of all, you will need to download the project from github. Create a directory on the master node (or what will be the master node) of your cluster to host the project. We recommend you create the directory at the following path so you will not need to change paths in the settings file later:

  `mkdir /srv/JMS`
  
Navigate to the directory and set the permissions:

  `cd /srv/JMS`
  `chmod 775 .`
  
Now you can download the project with the following command:

  `git clone https://github.com/RUBi-ZA/JMS.git`

