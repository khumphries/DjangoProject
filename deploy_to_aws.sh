#!/bin/bash

# @ Martin Kellogg, November 2015

# This file contains instructions for deploying secure witness share to an Amazon AWS Ec2 instance

# In addition to instructions, it contains the commands to run on the cloud machine to prep it; you should run this file once you have the cloud machine up and running

##################################################################

# First, you need to make an EC2 T2.micro (free tier) instance. There are plenty of examples on the web of how to do this.
# Use the key swskeypem.pem (found in the git repo) and modify the security group to allow TCP connections on port 8000

# login to the instance using swskeypem.pem:
#      > ssh -i swskey.pem ec2-user@1.2.3.4, where 1.2.3.4 is the public IP of your EC2 instance

# install git:
#      > sudo yum install -y git

# clone the repository, so that this file is on the cloud machine:
#      > git clone https://github.com/linahe/cs3240-f15-team5.git

# run this file:
#      > sudo bash deploy_to_aws.sh

sudo yum install -y gcc
sudo yum install -y python34
sudo yum install -y python34-pip
sudo yum install -y python34-devel
sudo pip-3.4 install django
sudo pip-3.4 install pycrypto

# finally, to run the server, use the aws_run_server.sh script in the root directory of the repo:
#     > sh aws_run_server.sh
