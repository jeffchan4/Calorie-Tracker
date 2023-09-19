# Python standard libraries
import json
import os
import sqlite3
import pandas as pd ##csv library
from datetime import date, timedelta
import time
import threading

# Third party libraries
from flask import Flask, redirect, request, url_for, render_template,jsonify
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User


today = None

# Function to update the date in the background
def update_date():
    global today  # Use the global variable
    
    while True:
        today = date.today()  # Update the global variable
        # print("Today's date:", today)
        time.sleep(600)

# Create a separate thread for date updating
date_update_thread = threading.Thread(target=update_date)
date_update_thread.daemon = True
date_update_thread.start()

df = pd.read_csv('foodandcalories.csv')


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
# Configuration
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

GOOGLE_CLIENT_ID = '933991065946-eitvj152481hamaebbajn64jn7bjraov.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        
        return render_template('usercart.html', id=current_user.id, name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic)

            
    else:
        return render_template('user_login.html')


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    
    
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)
    
    if User.get_calendar(today) is None:
        User.create_calendar(today)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/current_cart")
def current_cart():
    user = User(
        id_=current_user.id, name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic
    )
    # print(current_user.id,current_user.name,current_user.email)
    allusers = User.get_all_users()
    # allfoods= User.get_all_food()
    
    user_list = [dict(row) for row in allusers]
    
    # Serialize the list of dictionaries to JSON
    json_string = json.dumps(user_list)
    
    # Now, you can print the JSON string
    # print(json_string)
    # print(allfoods)
        
    current_cart = User.get_cart(today, current_user.id)  # Assuming `today` is correctly defined
    
    cart_list = [{"foodname": foodname, "serving": serving, "cal":calc_total_cal(foodname,serving), "id":id} for foodname, serving, id in current_cart]
    return jsonify(data=cart_list)

        

@app.route("/insert_items", methods=['POST'])
def insert_items():
    
    user = User(
        id_=current_user.id, name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic
    )
    
    try:
        data = request.get_json()
        user_id = data['userId']
        item_names = data['items']
        
        
        
        # conn=db_connection()
        # cursor = conn.cursor()
        user_id_to_query=user_id
        
        
        

        # Assuming you have a "items" table with "user_id" and "item_name" columns
        for item_name in item_names:
            items = item_name.split(':')
            
            food_name = items[0]
            
            serving_num = items[1].replace("servings",'').strip()
            
            User.insert(user_id_to_query,food_name,serving_num,today)
            
        print('successfully inserrted')
        return jsonify(message='Items inserted successfully')
    except Exception as e:
        return jsonify(error=str(e))
    
@app.route("/calculate", methods=['POST'])
def calculate():
    user = User(
        id_=current_user.id, name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic
    )
    
    data = request.get_json()
    range = data['range']
    print(range)
    start = today - timedelta(days=range)
    

    fetched_data= User.calculate(start, today, current_user.id)
    
    
    total=0
    total_cal_days={}
    response = {}
    for date, food_name, servings in fetched_data:
        
        date=str(date)
        if date not in response:
            total_cal_days[date]=[]
            response[date] = []
        response[date].append({'food_name': food_name, 'servings': servings, 'totalcal': calc_total_cal(food_name,int(servings))})
        total_cal_days[date].append(calc_total_cal(food_name,int(servings)))
    
    
    avgcalories=[{date:sum(total_cal_days[date])} for date in total_cal_days]
    
    
    for item in avgcalories:
        for date in item:
            total+=item[date]
    
    total=total/len(avgcalories)
    

    
    return jsonify({'Food Log':response,'Total Calories':avgcalories,'avg calorie per day':total})
    # except Exception as e:
    #     return jsonify({'error': str(e)})

@app.route("/delete_food", methods=['POST'])
def delete_food():
    user = User(
        id_=current_user.id, name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic
    )
    data=request.get_json()
    print(data)
    foodid=data['itemId']
    
    # food=data['foodName']
    # serving=data['foodServing']
    # print(food)
    # print(serving)

    User.delete_food(foodid)
    print('the items were deleted')
    return(jsonify(message="successful deletion"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def calc_total_cal(food,servings):
    
    startindex=0
    
    while startindex<=len(df):
        if  df.loc[startindex]['Food']== food:
            break
        startindex+=1
    
    totalcal= int(df.loc[startindex]['Calories'].split()[0] )
    
    return totalcal*servings
    
## testing

# if __name__ == "__main__":
#     app.run(debug=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)