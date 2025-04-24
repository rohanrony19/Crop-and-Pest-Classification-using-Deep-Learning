import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template,session,flash,redirect, url_for, session,flash
from werkzeug.utils import secure_filename
#from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from bs4 import BeautifulSoup


# Define a flask app
app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'accounts'

# Intialize MySQL
mysql = MySQL(app)


def bing_search(query, max_results=10):
    """
    Perform a search on Bing and fetch search result titles, links, and descriptions.
    
    :param query: The search query string.
    :param max_results: The maximum number of results to fetch.
    :return: List of dictionaries containing titles, links, and descriptions.
    """
    url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    results = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # Bing results typically use "li" elements with class "b_algo"
        links = soup.find_all("li", class_="b_algo")

        for link in links[:max_results]:
            title_element = link.find("a")
            description_element = link.find("p")  # Description is often in <p> tags

            if title_element:
                title = title_element.get_text()
                href = title_element["href"]
                description = description_element.get_text() if description_element else "No description available."
                results.append({"title": title, "link": href, "description": description})

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return results

def display_results(results):
    """
    Display the search results in a readable format.
    
    :param results: List of result dictionaries.
    """
    link=""
    desc=""

    if not results:
        print("No results found.")
        return

    for index, result in enumerate(results, start=1):
        print(f"Result {index}:")
        print(f"  Title: {result['title']}")
        print(f"  Link: {result['link']}")
        print(f"  Description: {result['description']}\n")
        link=result['link']
        desc=result['description']
        

    return(link,desc)

@app.route('/', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('index.html',title="Crop and Pest Detection")#redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('login.html',title="Login")



@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM accounts WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s)', (username,email, password))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return render_template('login.html',title="Login")

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('login.html',title="Register")

MODEL_PATH ='crop.h5'
MODEL_PATH1 ='pest.h5'
# Load your trained model
cropmodel = load_model(MODEL_PATH)
pestmodel = load_model(MODEL_PATH1)
class_names=['car','jute', 'maize', 'rice', 'sugarcane', 'wheat']



def model_predict(img_path, pestmodel):
    image=cv2.imread(img_path)
    example = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #plt.imshow(example)
    image_resized= cv2.resize(image, (224,224))
    image=np.expand_dims(image_resized,axis=0)
    pred=pestmodel.predict(image)
    preds=np.argmax(pred)#output=class_names[np.argmax(pred)]
    print(preds)
    trt = pred[0][preds] * 100
    
    if preds==0:
        preds="Ants"       
    elif preds==1:
        
        preds="Bees"
        
    elif preds==2:
        
        preds="Beetle"
        
    elif preds==3:
        
        preds="Catterpillar"
    elif preds==4:
        
        preds="Earthworms"
    elif preds==5:
        
        preds="Earwig"
    elif preds==6:
        
        preds="Grasshopper"
    elif preds==7:
        
        preds="Moth"
    elif preds==8:
        
        preds="Slug"
    elif preds==9:
        
        preds="Snail"
    elif preds==10:
        
        preds="Wasp"
    elif preds==11:
        
        preds="Weevil"
        
    
    
    
    
    return (preds,trt)

def predict_img(fpath):
    
    image=cv2.imread(fpath)
    example = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #plt.imshow(example)
    image_resized= cv2.resize(image, (224,224))
    image=np.expand_dims(image_resized,axis=0)
    pred=cropmodel.predict(image)
    output=class_names[np.argmax(pred)]
    print(output)
    return output

@app.route('/home', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['crop']
        f1 = request.files['pest']
        print('testing')

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'static/uploads', secure_filename(f.filename))
        f.save(file_path)
        file_path1 = os.path.join(
            basepath, 'static/uploads', secure_filename(f1.filename))
        f1.save(file_path1)

        pred1 = predict_img(file_path)
        pred2 = predict_img(file_path1)
        if(pred1 != 'car' and pred2 != 'car'):
            pred,trt = model_predict(file_path1, pestmodel)
            print(pred)
            pest=pred
            crop=predict_img(file_path)
            print(pest)
            print(crop)
            query = "Whether is " +pest+" harmful to  "+crop+" Crop"
            print
            search_results = bing_search(query, max_results=1)
            [desc,link]=display_results(search_results)
            print(desc)
            print(link)
            return render_template('result.html',pest=pest,crop=crop,cname=f.filename,pname=f1.filename,desc=desc,link=link)
        else:
            return render_template('result.html',pest="Invalid Input",crop="Invalid Input",cname=f.filename,pname=f1.filename,desc="",link="")
    return render_template('index1.html')

if __name__ == '__main__':
    app.run(port=5001,debug=False,host='0.0.0.0')
