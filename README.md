# What is drf?
1. blah
2. blah

# How to setup

1. Setup and run virtualenv.
- python3 -m venv venv
- source venv/bin/activate

2. Install mandatory packages
- (venv) pip install -r requirements.txt

3. Configure environment
- Added new properties file like /drf/properties/properties-develop-my.ini
- Configure Redis and PostgreSQL properly and fill out.
- Added OS variable for 'DJANGO_PROPERTY_MODE' as what you just created. (ex. 'develop-my')

3. Build models and migrate
- (venv) python manage.py makemigrations
- (venv) python manage.py migrate

4. That's all. just run.
- (venv) python manage.py runserver

 
<hr/>
 
BORA Co., Ltd. is supported by JetBrains Open Source License.

Also drf project is granted by All-In-One-Estate Open Source License.

<https://www.jetbrains.com/>
