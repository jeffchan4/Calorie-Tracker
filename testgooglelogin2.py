from flask import Flask, redirect, url_for, session, request
from requests_oauthlib import OAuth2Session
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
client_id = '933991065946-3t6b7cttpfchkj6g6akbt20ohrpt8h81.apps.googleusercontent.com'

client_secret = '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'

redirect_uri = 'http://127.0.0.1:5000/login/authorized'  # Should match the one you specified in the Google API Console
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'  # Endpoint to get user info

google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email'])

@app.route('/')
def index():
    return 'Welcome to the Flask Google Login App!'

@app.route('/login')
def login():
    authorization_url, _ = google.authorization_url(authorization_base_url)
    return redirect(authorization_url)

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
    session['google_token'] = token

    # Fetch user data using the access token
    response = google.get(user_info_url)
    user_data = json.loads(response.content)
    return f"Logged in as: {user_data['name']}"

if __name__ == '__main__':
    app.run()
