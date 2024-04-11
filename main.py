import pickle
from pydoc import render_doc 
from flask import Flask, request,app, jsonify, url_for, render_template
from os import path
import numpy as np
import pandas as pd
import os
import datetime
import uuid
import random

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from wtforms.validators import InputRequired, Length, ValidationError
from sql import db_connection, ProgrammingError

login_manager = LoginManager()

app = Flask(__name__)

load_dotenv()

CORS(app)

# app.secret_key = os.getenv("SECRET_KEY")
login_manager.init_app(app)
app.config['SESSION_TYPE'] = 'filesystem' 
Session(app)
bcrypt = Bcrypt(app)

db_connect = db_connection.cursor()
app.config['SECRET_KEY'] = os.getenv('MY_SECRET_KEY')


# model file path 
modelpath_1 = 'model/random_forest_model.pkl'
modelpath_2 = 'model/decision_tree_model.pkl'
modelpath_3 = 'model/hist_GB_model.pkl'

# we load the pickle file as the model
RANDOM_FOREST = pickle.load(open(modelpath_1, 'rb'))
DECISION_TREE = pickle.load(open(modelpath_2, 'rb'))
HIST_GRADIENTBOOST = pickle.load(open(modelpath_3, 'rb'))


class User(UserMixin):
    def _init_(self, id):
        self.id = id
    def is_authenticated(self):
        return True 
    def is_active(self):
        return True  
    def is_anonymous(self):
        return False  
    def get_id(self):
        return str(self.id)
    

def calculate_age(year_of_birth:int):
    current_year = int(datetime.datetime.today().strftime('%Y'))
    age = current_year - year_of_birth
    return age

def calculate_bmi(weight:float, height:float):
    # Convert height from centimeters to meters
    height = height / 100
    bmi = weight / (height ** 2)
    return bmi

def predict_diabetes(gender,age,urea,cr,hba1c,chol,trigl,hdl,ldl,vldl,BMI):
    
    output= RANDOM_FOREST.predict([gender,age,urea,cr,hba1c,chol,trigl,hdl,ldl,vldl,BMI])[0]
    return output

def convert_gender(gender:str):
    try:
        if gender == 'M' or 'm':
            return 0
        elif gender == 'F' or 'f':
            return 1
    except Exception as e:
        print(e)

def get_user_id():
    return session.get("user_id")


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    id = user_id[0:len(user_id)]
    try:
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM user WHERE id = %s ", (id,))
        get_user = db_cursor.fetchone()
        return jsonify({
        "email": get_user[1],
        "password": get_user[2]
        })
    except Exception as e:
        return (e)

   
    
def check_username_availability(email):

    db_cursor = db_connection.cursor() 
    db_cursor.execute("SELECT * FROM user WHERE email = %s", (email,)) 
    user_record = db_cursor.fetchone()

    return True if user_record else False

def get_diabetes_result(user):
    
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    id = user[0:len(user)]
    try:
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM testresult WHERE user_id = %s ", (id,))
        test_result = db_cursor.fetchone()
        return test_result[2]
    except Exception as e:
        print(f"Error: {e}")
        return {"Error": e}


@app.route('/get-random-meal-plan', methods=['GET'])
def get_random_meal_plan():
    # # Load the diet data from the dataframe
    diet_data = None  # Placeholder value

    # Replace None with the actual diet data after loading it
    diet_data = pd.read_csv('diet.csv')
    
     # Get the list of food items
    food_items = list(diet_data['Food Item'])

    # Generate two random breakfast items
    breakfast1_index = random.randint(0, len(food_items))
    breakfast1 = food_items[breakfast1_index]

    breakfast2_index = random.randint(0, len(food_items))
    while breakfast2_index == breakfast1_index:
        breakfast2_index = random.randint(0, len(food_items))
    breakfast2 = food_items[breakfast2_index]

    # Generate two random lunch items
    lunch1_index = random.randint(0, len(food_items))
    while lunch1_index == breakfast1_index or lunch1_index == breakfast2_index:
        lunch1_index = random.randint(0, len(food_items))
    lunch1 = food_items[lunch1_index]

    lunch2_index = random.randint(0, len(food_items))
    while lunch2_index == breakfast1_index or lunch2_index == breakfast2_index or lunch2_index == lunch1_index:
        lunch2_index = random.randint(0, len(food_items))
    lunch2 = food_items[lunch2_index]

    # Generate two random dinner items
    dinner1_index = random.randint(0, len(food_items))
    while dinner1_index == breakfast1_index or dinner1_index == breakfast2_index or dinner1_index == lunch1_index or dinner1_index == lunch2_index:
        dinner1_index = random.randint(0, len(food_items))
    dinner1 = food_items[dinner1_index]

    dinner2_index = random.randint(0, len(food_items))
    while dinner2_index == breakfast1_index or dinner2_index == breakfast2_index or dinner2_index == lunch1_index or dinner2_index == lunch2_index or dinner2_index == dinner1_index:
        dinner2_index = random.randint(0, len(food_items))
    dinner2 = food_items[dinner2_index]

    meal_plan = {
        'breakfast': [breakfast1, breakfast2],
        'lunch': [lunch1, lunch2],
        'dinner': [dinner1, dinner2]
    }

    return jsonify(meal_plan)


@app.route('/api/predict', methods= ['POST'])
def api_predict():

    data = request.json
    gender = convert_gender(gender= data['Gender'])
    age = calculate_age(year_of_birth=data['year'])
    urea = data['Urea']
    cr = data['Cr']
    hba1c = data['HbA1c']
    chol = data['Chol']
    trigl = data['TG']
    hdl = data['HDL']
    ldl = data['LDL']
    vldl = data['VLDL']
    bmi = calculate_bmi(height=data['height'], weight= data['weight'])

    test_data = [gender,age,urea,cr,hba1c,chol,trigl,hdl,ldl,vldl,bmi]
    # print(result)
    new_data_array = np.array(test_data)
    new_data = new_data_array.reshape(1, -1)
    prediction = RANDOM_FOREST.predict(new_data)

    # Predictioon is prediabetic or diabetic
    if prediction[0] == 1.0 or 2.0:
        # Save the test result and prediction in the session
        session['user_gender'] = gender
        session['user_age'] = age
        session['user_prediction'] = prediction[0]
        session['user_urea'] = urea
        session['user_cr'] = cr
        session['user_hba1c'] = hba1c
        session['user_chol'] = chol
        session['user_trigl'] = trigl
        session['user_hdl'] = hdl
        session['user_ldl'] = ldl
        session['user_vldl'] = vldl
        session['user_bmi'] = bmi

        return jsonify({
        "prediction result": prediction[0]
         })
        
    else:
        session.clear()
        return jsonify({"Prediction result" : prediction[0]})
    


@app.route('/')
def home():
    return('Welcome !!!')

# Process login form submission
@app.route('/login', methods= ['POST'])
def login_submit():

    user_data = request.json
    user_email = user_data["email"]
    password = user_data["password"]
    
    # Check if username and password are valid
    db_cursor = db_connection.cursor() 
    db_cursor.execute("SELECT * FROM user WHERE email = %s", (user_email,)) 
    user = db_cursor.fetchone()
   
     
    if not bcrypt.check_password_hash(user[2], password):  # User password authentication   
        return jsonify({"error": "Unauthorized"}), 401
            
    # Set the session ID to the user ID
    session['user_id'] = user[4]
        
    return jsonify({
    "email": user[1],
    "password": user[2]
    })

# User logout route. 
@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user_id")
    return ("User logged out")

# Get user Id for session management. 
@app.route("/@me") # Route to get the logged in user details
def get_current_user():
    try:
        user_id = session["user_id"]
        
        if not user_id:
            return jsonify({"error":"Unauthorized"}), 401
        
        # id = user_id[0:len(user_id)]
        try:
            result = get_diabetes_result(user_id)
            db_cursor = db_connection.cursor()
            db_cursor.execute("SELECT * FROM user WHERE id = %s ", (user_id,))
            get_user = db_cursor.fetchone()
            return jsonify({
            "email": get_user[1],
            "password": get_user[2],
            "Diabetes": result
            })
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e})
    except: return("User logged out or session expired")
    
# Register a user or a patient  
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
    
        form_data = request.json
        id = str(uuid.uuid4())
        first_name = form_data['firstname']
        last_name = form_data['lastname']
        user_email = form_data['email']
        password = form_data['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        id = str(uuid.uuid4())
        print(id)
        print(first_name)
        
        if check_username_availability(user_email):
            print("User email available!")
            return jsonify({'Message':'User with that email Already Exist, register with another email...!'}), 409

        else:
            try:
                sql = "INSERT INTO user (id, firstname, lastname, email, password) VALUES (%s, %s, %s, %s, %s)"
                values =  (id, first_name, last_name, user_email, hashed_password)
            
                db_cursor = db_connection.cursor() # Create a cursor object to execute queries
                
                db_cursor.execute(sql, values)
                db_connection.commit()
                session['user_session_id'] = id

                print({'message':'user details saved'})
                
                try:
                    if 'user_session_id' in session:
                        # Retrieve the test result and prediction from the session
                        user_gender = int(session['user_gender'])
                        user_age = int(session['user_age'])
                        user_prediction = float(session['user_prediction']) 
                        user_urea = float(round(session['user_urea'],2))
                        user_cr = float(round(session['user_cr'],2)) 
                        user_hba1c = float(round(session['user_hba1c'],2)) 
                        user_chol = float(round(session['user_chol'],2)) 
                        user_trigl = float(round(session['user_trigl'],2))
                        user_hdl = float(round(session['user_hdl'],2))
                        user_ldl = float(round(session['user_ldl'],2))
                        user_vldl = float(round(session['user_vldl'] , 2))
                        user_bmi = float(round(session['user_bmi'] , 2))
                        user_id = id
                        
                        print(user_chol)
                        sql_2 = """ INSERT INTO testresult (user_id, hba1c, diabetes_status, age, gender, creatratio, urea, chol, trigliceride, HDL, LDL, VHDL,BMI) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        result_values = (user_id, user_hba1c, user_prediction, user_age, user_gender,user_cr,user_urea,user_chol,user_trigl,user_hdl,user_ldl,user_vldl,user_bmi)
                        db_cursor = db_connection.cursor() 
                        db_cursor.execute(sql_2, result_values)
                        db_connection.commit()
                        session.clear()
                        # return jsonify({'message': 'Registration successful.'})
                        return jsonify({
                        "email": user_email,
                        "message": "Registration successful."
                         })
                        

                except Exception as e:
                    print(e)


            except ProgrammingError as e:
                # Handle the exception
                print(e)
                session.clear()
                return jsonify({'Error saving data to database.'})
            
    return jsonify("1")
        

if __name__ == '__main__':
    app.run(debug=True)