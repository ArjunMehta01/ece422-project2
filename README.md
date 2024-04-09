ECE 422: Reliable and Secure Systems Design 
=============
This repository contains our implementation of a secure file system. Follow the below steps to deploy and use the project.


## Server Deployment
The following steps are to be followed assuming a VM (Cybera VM) is set up for a server.
1. Clone down the repository with the following commands:
    ```bash
    $ wget https://github.com/ArjunMehta01/ece422-project2/archive/refs/heads/master.zip
    $ unzip master.zip -d master
    ```
2. Install pip with the following command. Python3.10 is required for the application:
    ```bash
    $ sudo apt-get -y install python3
    $ sudo apt -y install python-pip
    $ cd server
    $ pip install -r requirements.txt
    ```
3. Create a .secrets and filesystem folder somewhere within the VM. We recommend placing these folders at the same level as src with the following commands. 
    ```bash
    $ mkdir .secrets
    $ mkdir filesystem
    ```
4. Create a .env file at the same level as src containing the path to the .secrets and filesystem folders. The .env file should contain the following:
    ```
    FILESYSTEM_PATH=<Direct_Path_To_Filesystem>
    SECRETS_PATH=<Direct_Path_To_Secrets>
    ```
   
6. Start the server with the following commands:
    ```bash
    $ Python3 src/server.py
    ```

## Client Deployment
The following steps are to be followed assuming a VM (Cybera VM) is set up for a client.
1. Clone down the repository with the following commands:
    ```bash
    $ wget https://github.com/ArjunMehta01/ece422-project2/archive/refs/heads/master.zip
    $ unzip master.zip -d master
    ```
2. Install pip with the following command. Python3.10 is required for the application:
    ```bash
    $ sudo apt-get -y install python3
    $ sudo apt -y install python-pip
    $ cd server
    $ pip install -r requirements.txt
    ```
3. Create a .env file containing the path to the .secrets and filesystem folders as well as the port and IP of the server. The .env file should contain the following:
    ```
    SECRETS_PATH=<Direct_Path_To_Secrets>
    SERVER_IP=<Server_IP>
    SERVER_PORT=<Server_Port>
    ```
4. Start the client application with the following commands:
    ```bash
    $ Python3 src/client.py
    ```
5. Upon system startup, login will be prompted. The admin credentials are listed below
   * Password: admin
   * Username: admin
6. The initial admin user should be logged into the secure file system. See below for the user guide.

## User Guide
The following instructions are written assuming the client connected to the server successfully.
Once logged in a user is placed in their home directory with several commands available. A user will be able to navigate through other directories and files other than their own if another user has shared the files/folders with them. 

### The available commands are listed below:
1. pwd: see what directory you are currently in.
2. ls: list the files in current directory.
3. cd <dir_name>: change directory.
4. mkdir <dir_name>: make a new subdirectory.
5. touch <file_name>: create a new file.
6. cat <file_name>: read a file.
7. echo <file_name> <text>: write to a file, currently our implementation does not allow for spaces in the text. 
8. mv <original_file_name> <new_file_name>: rename a file.
9. chmod <name_of_file> <USER | GROUP | ALL>: Change permissions of a file
10. create_user <username> <password> <group>: Initialize a new user
11. logout: log the current user out of the system.





