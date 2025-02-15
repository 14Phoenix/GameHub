Admin usernames and passwords:
------------------------------
Username: viktor, Password: morpheus
Username: tadija, Password: oracle
Username: nemanja, Password: trinity
Username: mihajlo, Password: agentsmith

For chat to work:
-----------------
docker run --rm -p 6379:6379 redis:7

Create database:
----------------
python .\manage.py makemigrations
python .\manage.py migrate

Load sample data into database:
-------------------------------
python .\manage.py loaddata .\GameHubApp\fixtures\gamehub_sample_data.json

Clear data from database:
-------------------------
python manage.py flush

Dump data from database:
------------------------
python .\manage.py dumpdata GameHubApp --output fixtures\gamehub_sample_data.json

Old way to create database and load sample data (can ignore this):
------------------------------------------------------------------
1. database name: gamehub
2. clear all tables
3. delete all files from migrations folder inside project except __init__.py (delete 0001_initial.py etc...)
4. run: python manage.py makemigrations
5. run: python manage.py migrate
6. run: GameHub.sql
7. run: GameHub_Sample_Data.sql

Run test:
---------
python .\manage.py test GameHubApp.tests.<file_name.py>.<class_name>.<function_name>
