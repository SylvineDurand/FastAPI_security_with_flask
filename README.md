This project is the application of the fastapi tutorial for security with the oauth2 password flow, adapted to a situation closer to my needs for the certification.

improvements from the basic tuto :
- simple flask app as a frontend 
- pages for login, logout 
- users are stored in a sqlite db in the fastapi section. this db is initialized with only admin user using a python script
- creating an endpoint to add more users in the db
- adding a role in the db, to leave possibility to implement permissions


soon : 
- access to endpoints depending on their role
- removing unwanted features, eg disabled in the db.


# start 
### open a terminal for fastapi
cd fastapi
source venv_fastapi/bin/activate
fastapi dev main.py

### open a terminal for flask
cd flask
source venv_flask/bin/activate
flask --app flask_app run --debug