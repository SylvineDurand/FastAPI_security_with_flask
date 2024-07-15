This project is the application of the fastapi tutorial for security with the oauth2 password flow, adapted to a situation closer to my needs for the certification.
Link to the tutorial :
https://fastapi.tiangolo.com/tutorial/security/


Improvements from the basic tuto :
- simple flask app as a frontend 
- pages for login, logout 
- users are stored in a sqlite db in the fastapi section. this db is initialized with a single admin user using a python script
- creating an endpoint to add more users in the db
- adding a role in the db, to leave possibility to implement permissions
- access to endpoints depending on their role
- admin page to see all users
- removing unwanted features from the fastapi tutorial, eg disabled in the db.

 

# Installation 
### Open a terminal for fastapi
```bash
cd fastapi
python -m venv venv_fastapi
source venv_fastapi/bin/activate

# initialize the database
python initialize_db.py

# start the API in dev mode
fastapi dev main.py
```


### Open a terminal for flask
```bash
cd flask
python -m venv venv_flask
source venv_flask/bin/activate
flask --app flask_app run --debug
```