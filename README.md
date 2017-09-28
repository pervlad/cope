# cope
Flask minimal rest api for user management

# Setup
## Install Potgreql Create Cope Superuser
create postgesql sql super user cope

```bash
sudo apt-get install postgresql postgresql-contrib
sudo su - postgres
psql
create role cope with superuser login createdb password '123';
/d
sudo nano /etc/postgresql/9.5/main/pg_hba.conf

# "local" is for Unix domain socket connections only
local   all             all                                     peer->md5

psql template1 -U cope
create database cope;

\c cope  #use cope;
```
## app installation
Download zip or clone directory 
create venv  `python3.6 venv emv3.6` or 
go to Cope folder
acivate venv
`source path/to/venv/bin/activate`

```pip install requirements.txt```

create databse by using `cope.db.p.sql` or `python createdb.py`

go to inner cope dir start the app `python app.py`

use provided postman collection backup to restore colection for testing
