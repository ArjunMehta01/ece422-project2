ECE 422: Reliable and Secure Systems Design 
=============
This repository contains our implementation of a secure file system. Follow the below steps to deploy and use the project.


## Server Deployment
The following steps are to be followed assuming a VM (Cybera VM) is set up for a server.
1. Clone down the repository with the following commands:
    ```bash
    $ what 
    ```
2. Install pip with the following command:
    ```bash
    $ sudo apt-get -y install python3.10
    $ sudo apt -y install python-pip
    $ cd server
    $ pip install -r requirements.txt
    ```
3. Create a .secrets and filesystem folder somewhere within the VM. We recommend placing these folders at the same level as src with the following commands. 
    ```bash
    $ mkdir .secrets
    $ mkdir filesystem
    ```
4. Create a .env file containing the path to the .secrets and filesystem folders. The .env file should contain the following:
    ```
    FILESYSTEM_PATH=<Direct_Path_To_Filesystem>
    SECRETS_PATH==<Direct_Path_To_Secrets>
    ```
   
6. Start the server with the following commands:
    ```bash
    $ Python src/server.py
    ```

## Client Deployment
The following steps are to be followed assuming a VM (Cybera VM) is set up for a client.
1. Clone down the repository with the following commands:
    ```bash
    $ what 
    ```
2. Install pip with the following command:
    ```bash
    $ sudo apt-get -y install python3.10
    $ sudo apt -y install python-pip
    $ cd server
    $ pip install -r requirements.txt
    ```
3. Start the client application with the following commands:
    ```bash
    $ Python client.py
    ```
4. Upon system startup, login will be prompted. The admin credentials are listed below
   * Password: admin
   * Username: admin
5. The initial admin user should be logged into the secure file system. See below for the user guide.

## User Guide
The following instructions are written assuming the client connected to the server successfully. 



