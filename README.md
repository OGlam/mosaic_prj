# Setup instructions

* Fork this repo.
* Clone this repo.
* Create a virtualenv:
 goto pycharrm preferences define pyton point to local vervion

        mkvirtualenv xtracker

* activate virtualenv
        
        source nameOfVirtualEnv/bin/activate

* Install requirements:

        pip install -r requriments.txt

* Create tables:

        python manage.py migrate

* Create some sample data:

        python manage.py create_expenses 100


* Run your server:

        python manage.py runserver

* Enjoy: http://localhost:8000/

* Create User
        python manage.py createsuperuser
*tanya user:tania psw:mokumi8998
