from flask import Flask, request, redirect, render_template, session, jsonify, url_for
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
FASTAPI_URL = 'http://localhost:8000'


# route to log in using a form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{FASTAPI_URL}/token', data={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('access_token')
            resp = redirect('/protected')
            resp.set_cookie('token', token, httponly=True) 
            return resp
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')



# log out
@app.route('/logout')
def logout():
    resp = redirect(url_for('login'))
    resp.delete_cookie('token') 
    return resp

# admin create a user 
@app.route('/admin/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        disabled = request.form.get('disabled') == 'on'
        user_role = request.form['user_role']  
        
        user_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'password': password,
            'disabled': disabled,
            'user_role': user_role
        }
        
        response = requests.post(f'{FASTAPI_URL}/create_user/', json=user_data)
        if response.status_code == 200:
            return redirect(url_for('create_user'))
        else:
            return jsonify(response.json()), response.status_code
    
    return render_template('create_user.html')

# # admin list of users
# @app.route('/admin/users_list', methods=['GET'])
# def get_users_list():
#     response = requests.get(f'{FASTAPI_URL}/users_list')
#     return 

@app.route('/admin/users_list')
def users_list():
    token = request.cookies.get('token')  
    if not token:
        return redirect('/login')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(f'{FASTAPI_URL}/users_list/', headers=headers)
    if response.status_code == 200:
        users = response.json()
        return render_template('users_list.html', users=users)
    return jsonify({'error': 'Failed to fetch users'}), response.status_code



# protected route accessible only to authorized users and send back their username
@app.route('/welcome')
def protected():
    token = request.cookies.get('token')  
    if not token:
        return redirect('/login')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{FASTAPI_URL}/users/me', headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return render_template('welcome.html', user=user_data)
    return jsonify({'error': 'Invalid token'}), 401


# dummy endpoint to test permissions
@app.route('/admin_only')
def protected_admin_only():
    token = request.cookies.get('token')  
    if not token:
        return redirect('/login')
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{FASTAPI_URL}/admin_only', headers=headers)
    if response.status_code == 200:
        user = response.json()
        return render_template('simple_json.html', user=user)
    if response.status_code == 403:
        return render_template('unauthorized.html')
    
    return jsonify({'error': 'Invalid token'}), 401


# dummy endpoint to test permissions
@app.route('/admin_ai_only')
def protected_admin_ai_only():
    token = request.cookies.get('token')  
    if not token:
        return redirect('/login')
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(f'{FASTAPI_URL}/admin_and_ai_only', headers=headers)
    if response.status_code == 200:
        user = response.json()
        return render_template('simple_json.html', user=user)
    if response.status_code == 403:
        return render_template('unauthorized.html')
    
    return jsonify({'error': 'Invalid token'}), 401


if __name__ == '__main__':
    app.run(debug=True)
